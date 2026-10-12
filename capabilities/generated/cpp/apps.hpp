// Generated; requires nlohmann/json.hpp.
#pragma once
#include <nlohmann/json.hpp>
#include "capability_transport.hpp"
#include <functional>
#include <string>
#include <vector>
namespace airdeck::apps {
using json=nlohmann::json;
using Transport=airdeck::Transport;
struct Empty {};
inline void to_json(json& j,const Empty&){j=json::object();} inline void from_json(const json&,Empty&){}
struct Launch {std::string target{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Launch,target)
struct Application {std::string id{}; std::string name{}; std::string target{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Application,id,name,target)
struct Applications {std::vector<Application> apps{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Applications,apps)
struct Provider { virtual ~Provider()=default;
virtual Empty launch(Launch)=0;
virtual Applications list(Empty)=0;
};
inline json dispatch(Provider& p,const std::string& method,const json& q){
if(method=="launch") return p.launch(q.get<Launch>());
if(method=="list") return p.list(q.get<Empty>());
throw std::runtime_error("unknown method");}
struct Client { Transport& t;
Empty launch(Launch q){return t.call("core.apps","launch",q).get<Empty>();}
Applications list(Empty q){return t.call("core.apps","list",q).get<Applications>();}
};
}
