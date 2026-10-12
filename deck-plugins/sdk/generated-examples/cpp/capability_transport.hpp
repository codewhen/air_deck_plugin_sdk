#ifndef AIRDECK_CAPABILITY_TRANSPORT_HPP
#define AIRDECK_CAPABILITY_TRANSPORT_HPP
#include <nlohmann/json.hpp>
#include <functional>
#include <string>
namespace airdeck { struct Transport {virtual nlohmann::json call(std::string,std::string,nlohmann::json)=0;virtual std::function<void()> subscribe(std::string,std::string,std::function<void(nlohmann::json)>)=0;virtual ~Transport()=default;};}
#endif
