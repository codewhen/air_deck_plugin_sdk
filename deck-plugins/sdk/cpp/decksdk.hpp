// AirDeck plugin API v2. C++17, nlohmann JSON (vendored under vendor/).
#pragma once
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <mutex>
#include <future>
#include <atomic>
#include <nlohmann/json.hpp>
#include "../../../capabilities/generated/cpp/media.hpp"
#include "../../../capabilities/generated/cpp/pointer.hpp"
#include "../../../capabilities/generated/cpp/keyboard.hpp"
#include "../../../capabilities/generated/cpp/apps.hpp"
namespace decksdk {
using json=nlohmann::json;
struct Button {std::string id,title,icon_key;int columns=1,rows=1;std::string action,plugin_id;bool editor_tap=false,editor_toggle=false;};
class Host;
class DeckPlugin {public:virtual ~DeckPlugin()=default;virtual void init(Host&){};virtual void poll(){};virtual std::vector<Button> catalog()=0;virtual void invoke(const std::string&,const std::string&,const std::string&,const std::string&)=0;};
struct CapabilityError:std::runtime_error {std::string code;CapabilityError(std::string c,std::string m):std::runtime_error(m),code(c){}};
class Host:public airdeck::Transport {
 std::mutex mutex,writer;std::atomic<uint64_t> sequence{0};
 std::map<std::string,std::shared_ptr<std::promise<json>>> pending;
 std::map<std::string,std::function<void(json)>> subscriptions;
 std::map<std::string,std::function<json(std::string,json)>> providers;
 void send(json q){std::lock_guard<std::mutex> lock(writer);std::cout<<q.dump()<<std::endl;}
 json exchange(json q){std::string id=q.value("ipc_id",std::string("plugin-")+std::to_string(++sequence));q["ipc_id"]=id;auto promise=std::make_shared<std::promise<json>>();auto result=promise->get_future();{std::lock_guard<std::mutex> lock(mutex);pending[id]=promise;}try{send(q);if(result.wait_for(std::chrono::seconds(4))!=std::future_status::ready){send({{"op","capability.cancel"},{"action",id}});throw CapabilityError("timeout","Host request timed out");}auto response=result.get();{std::lock_guard<std::mutex> lock(mutex);pending.erase(id);}if(!response.value("error",std::string()).empty())throw CapabilityError(response.value("code",std::string("provider_failed")),response["error"]);return response;}catch(...){std::lock_guard<std::mutex> lock(mutex);pending.erase(id);throw;}}
 public:
 json call(std::string cap,std::string method,json payload)override{return exchange({{"op","capability.call"},{"capability",cap},{"action",method},{"payload",payload}}).value("value",json::object());}
 std::function<void()> subscribe(std::string cap,std::string topic,std::function<void(json)> cb)override{auto id="subscription-"+std::to_string(++sequence);{std::lock_guard<std::mutex> lock(mutex);subscriptions[id]=cb;}auto stop=[this,id](){ {std::lock_guard<std::mutex> lock(mutex);subscriptions.erase(id);}send({{"op","capability.unsubscribe"},{"action",id}});};try{exchange({{"op","capability.subscribe"},{"ipc_id",id},{"capability",cap},{"topic",topic}});}catch(...){stop();throw;}return stop;}
 void provide(std::string cap,std::function<json(std::string,json)> dispatch){std::lock_guard<std::mutex> lock(mutex);providers[cap]=dispatch;}
 void publish(std::string cap,std::string topic,json value){exchange({{"op","capability.publish"},{"capability",cap},{"topic",topic},{"value",value}});}
 void loop(DeckPlugin& plugin){std::vector<std::future<void>> jobs;auto ready=std::async(std::launch::async,[&](){plugin.init(*this);}).share();std::string line;
  while(std::getline(std::cin,line)){json q;try{q=json::parse(line);}catch(...){continue;}if(!q.is_object()||!q.contains("op")||!q["op"].is_string()||(q.contains("ipc_id")&&!q["ipc_id"].is_string()))continue;auto op=q.value("op",std::string()),id=q.value("ipc_id",std::string());
   if(op=="capability.result"){std::lock_guard<std::mutex> lock(mutex);auto p=pending.find(id);if(p!=pending.end()){try{p->second->set_value(q);}catch(const std::future_error&){};}continue;}
   if(op=="capability.state"){std::function<void(json)> cb;{std::lock_guard<std::mutex> lock(mutex);cb=subscriptions[id];}if(cb)jobs.push_back(std::async(std::launch::async,[cb,q](){cb(q.at("value").at("value"));}));continue;}
   jobs.push_back(std::async(std::launch::async,[&,q,ready](){json r={{"op","ok"},{"ipc_id",q.value("ipc_id",std::string())}};try{ready.get();auto op=q.value("op",std::string());if(op=="catalog"){r["buttons"]=json::array();for(const auto& b:plugin.catalog())r["buttons"].push_back({{"id",b.id},{"title",b.title},{"icon_key",b.icon_key},{"columns",b.columns},{"rows",b.rows},{"action",b.action},{"plugin_id",b.plugin_id},{"editor",{{"tap",b.editor_tap},{"toggle",b.editor_toggle}}}});}else if(op=="invoke"){plugin.invoke(q.value("type",std::string()),q.value("action",std::string()),q.value("body",json::object()).dump(),q.value("payload",json::object()).dump());}else if(op=="capability.invoke"){std::function<json(std::string,json)> p;{std::lock_guard<std::mutex> lock(mutex);p=providers[q.at("capability").get<std::string>()];}if(!p)throw CapabilityError("capability_unavailable","Provider not registered");r["value"]=p(q.at("action"),q.value("payload",json::object()));}else if(op=="poll"){plugin.poll();}else throw CapabilityError("invalid_arguments","Unknown operation");}catch(const CapabilityError& e){r["op"]="error";r["code"]=e.code;r["error"]=e.what();}catch(const std::exception& e){r["op"]="error";r["code"]="provider_failed";r["error"]=e.what();}if(q.value("ack",true))send(r);}));
   for(auto it=jobs.begin();it!=jobs.end();){if(it->wait_for(std::chrono::seconds(0))==std::future_status::ready){try{it->get();}catch(...){}it=jobs.erase(it);}else ++it;}
  }
  {std::lock_guard<std::mutex> lock(mutex);for(auto& p:pending){try{p.second->set_exception(std::make_exception_ptr(CapabilityError("provider_failed","Host disconnected")));}catch(...){};}subscriptions.clear();}
  for(auto& job:jobs){try{job.get();}catch(...){}}
 }
};
inline void run(DeckPlugin& plugin){Host host;host.loop(plugin);}
}
