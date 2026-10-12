// Generated; requires nlohmann/json.hpp.
#pragma once
#include <nlohmann/json.hpp>
#include "capability_transport.hpp"
#include <functional>
#include <string>
namespace airdeck::com_example_counter_counter {
using json=nlohmann::json;
using Transport=airdeck::Transport;
struct Empty {};
inline void to_json(json& j,const Empty&){j=json::object();} inline void from_json(const json&,Empty&){}
struct Count {int64_t value{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Count,value)
struct Provider { virtual ~Provider()=default;
virtual Count getCount(Empty)=0;
};
inline json dispatch(Provider& p,const std::string& method,const json& q){
if(method=="getCount") return p.getCount(q.get<Empty>());
throw std::runtime_error("unknown method");}
struct Client { Transport& t;
Count getCount(Empty q){return t.call("com.example.counter.counter","getCount",q).get<Count>();}
std::function<void()> subscribeCount(std::function<void(Count)> fn){return this->t.subscribe("com.example.counter.counter","count",[fn](json j){fn(j.get<Count>());});}
};
}
