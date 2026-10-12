#include "decksdk.hpp"
#include <memory>
struct Plugin:decksdk::DeckPlugin {
 std::unique_ptr<airdeck::media::Client> client;
 void init(decksdk::Host& h)override{client=std::make_unique<airdeck::media::Client>(airdeck::media::Client{h});}
 std::vector<decksdk::Button> catalog()override{return {};}
 void invoke(const std::string&,const std::string& action,const std::string&,const std::string&)override{if(action=="subscribe"){std::promise<airdeck::media::Playback> promise;auto result=promise.get_future();auto stop=client->subscribePlayback([&](auto v){promise.set_value(v);});if(result.wait_for(std::chrono::seconds(2))!=std::future_status::ready)throw std::runtime_error("state timeout");auto v=result.get();stop();if(v.status!=airdeck::media::PlaybackStatus::playing||!v.available)throw std::runtime_error("wrong state");return;}auto v=client->getPlayback({});if(v.status!=airdeck::media::PlaybackStatus::playing||!v.available)throw std::runtime_error("wrong typed response");}
};
int main(){Plugin p;decksdk::run(p);}
