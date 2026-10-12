// Generated; requires nlohmann/json.hpp.
#pragma once
#include <nlohmann/json.hpp>
#include "capability_transport.hpp"
#include <functional>
#include <string>
#include <vector>
namespace airdeck::pointer {
using json=nlohmann::json;
using Transport=airdeck::Transport;
struct Empty {};
inline void to_json(json& j,const Empty&){j=json::object();} inline void from_json(const json&,Empty&){}
struct Motion {double dx{}; double dy{}; double sensitivity{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Motion,dx,dy,sensitivity)
enum class ClickButton {left,right};
NLOHMANN_JSON_SERIALIZE_ENUM(ClickButton, {{ClickButton::left,"left"},{ClickButton::right,"right"}})
struct Click {ClickButton button{}; bool double_click{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Click,button,double_click)
struct Provider { virtual ~Provider()=default;
virtual Empty move(Motion)=0;
virtual Empty scroll(Motion)=0;
virtual Empty click(Click)=0;
};
inline json dispatch(Provider& p,const std::string& method,const json& q){
if(method=="move") return p.move(q.get<Motion>());
if(method=="scroll") return p.scroll(q.get<Motion>());
if(method=="click") return p.click(q.get<Click>());
throw std::runtime_error("unknown method");}
struct Client { Transport& t;
Empty move(Motion q){return t.call("core.pointer","move",q).get<Empty>();}
Empty scroll(Motion q){return t.call("core.pointer","scroll",q).get<Empty>();}
Empty click(Click q){return t.call("core.pointer","click",q).get<Empty>();}
};
}
