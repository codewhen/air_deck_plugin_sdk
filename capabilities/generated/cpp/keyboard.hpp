// Generated; requires nlohmann/json.hpp.
#pragma once
#include <nlohmann/json.hpp>
#include "capability_transport.hpp"
#include <functional>
#include <string>
#include <vector>
namespace airdeck::keyboard {
using json=nlohmann::json;
using Transport=airdeck::Transport;
struct Empty {};
inline void to_json(json& j,const Empty&){j=json::object();} inline void from_json(const json&,Empty&){}
struct Key {std::string key{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Key,key)
struct Combo {std::string combo{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Combo,combo)
struct Provider { virtual ~Provider()=default;
virtual Empty press(Key)=0;
virtual Empty hotkey(Combo)=0;
};
inline json dispatch(Provider& p,const std::string& method,const json& q){
if(method=="press") return p.press(q.get<Key>());
if(method=="hotkey") return p.hotkey(q.get<Combo>());
throw std::runtime_error("unknown method");}
struct Client { Transport& t;
Empty press(Key q){return t.call("core.keyboard","press",q).get<Empty>();}
Empty hotkey(Combo q){return t.call("core.keyboard","hotkey",q).get<Empty>();}
};
}
