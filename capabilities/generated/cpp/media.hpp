// Generated; requires nlohmann/json.hpp.
#pragma once
#include <nlohmann/json.hpp>
#include "capability_transport.hpp"
#include <functional>
#include <string>
#include <vector>
namespace airdeck::media {
using json=nlohmann::json;
using Transport=airdeck::Transport;
struct Empty {};
inline void to_json(json& j,const Empty&){j=json::object();} inline void from_json(const json&,Empty&){}
enum class PlaybackStatus {playing,paused,stopped,unknown};
NLOHMANN_JSON_SERIALIZE_ENUM(PlaybackStatus, {{PlaybackStatus::playing,"playing"},{PlaybackStatus::paused,"paused"},{PlaybackStatus::stopped,"stopped"},{PlaybackStatus::unknown,"unknown"}})
struct Playback {PlaybackStatus status{}; bool available{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Playback,status,available)
struct Track {std::string title{}; std::string artist{}; std::string album{}; std::string app{}; bool available{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Track,title,artist,album,app,available)
struct Volume {double level{}; bool muted{}; bool available{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Volume,level,muted,available)
struct SetVolume {double level{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(SetVolume,level)
struct AdjustVolume {double delta{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(AdjustVolume,delta)
struct Mute {bool muted{};};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Mute,muted)
struct Provider { virtual ~Provider()=default;
virtual Playback getPlayback(Empty)=0;
virtual Track getTrack(Empty)=0;
virtual Volume getVolume(Empty)=0;
virtual Empty togglePlayback(Empty)=0;
virtual Empty play(Empty)=0;
virtual Empty pause(Empty)=0;
virtual Empty next(Empty)=0;
virtual Empty previous(Empty)=0;
virtual Empty setVolume(SetVolume)=0;
virtual Empty adjustVolume(AdjustVolume)=0;
virtual Empty setMute(Mute)=0;
};
inline json dispatch(Provider& p,const std::string& method,const json& q){
if(method=="getPlayback") return p.getPlayback(q.get<Empty>());
if(method=="getTrack") return p.getTrack(q.get<Empty>());
if(method=="getVolume") return p.getVolume(q.get<Empty>());
if(method=="togglePlayback") return p.togglePlayback(q.get<Empty>());
if(method=="play") return p.play(q.get<Empty>());
if(method=="pause") return p.pause(q.get<Empty>());
if(method=="next") return p.next(q.get<Empty>());
if(method=="previous") return p.previous(q.get<Empty>());
if(method=="setVolume") return p.setVolume(q.get<SetVolume>());
if(method=="adjustVolume") return p.adjustVolume(q.get<AdjustVolume>());
if(method=="setMute") return p.setMute(q.get<Mute>());
throw std::runtime_error("unknown method");}
struct Client { Transport& t;
Playback getPlayback(Empty q){return t.call("core.media","getPlayback",q).get<Playback>();}
Track getTrack(Empty q){return t.call("core.media","getTrack",q).get<Track>();}
Volume getVolume(Empty q){return t.call("core.media","getVolume",q).get<Volume>();}
Empty togglePlayback(Empty q){return t.call("core.media","togglePlayback",q).get<Empty>();}
Empty play(Empty q){return t.call("core.media","play",q).get<Empty>();}
Empty pause(Empty q){return t.call("core.media","pause",q).get<Empty>();}
Empty next(Empty q){return t.call("core.media","next",q).get<Empty>();}
Empty previous(Empty q){return t.call("core.media","previous",q).get<Empty>();}
Empty setVolume(SetVolume q){return t.call("core.media","setVolume",q).get<Empty>();}
Empty adjustVolume(AdjustVolume q){return t.call("core.media","adjustVolume",q).get<Empty>();}
Empty setMute(Mute q){return t.call("core.media","setMute",q).get<Empty>();}
std::function<void()> subscribePlayback(std::function<void(Playback)> fn){return this->t.subscribe("core.media","playback",[fn](json j){fn(j.get<Playback>());});}
std::function<void()> subscribeTrack(std::function<void(Track)> fn){return this->t.subscribe("core.media","track",[fn](json j){fn(j.get<Track>());});}
std::function<void()> subscribeVolume(std::function<void(Volume)> fn){return this->t.subscribe("core.media","volume",[fn](json j){fn(j.get<Volume>());});}
};
}
