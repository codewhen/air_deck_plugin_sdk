#include "decksdk.hpp"
#include "com_example_counter_counter.hpp"
struct P: airdeck::com_example_counter_counter::Provider {
 airdeck::com_example_counter_counter::Count getCount(airdeck::com_example_counter_counter::Empty) override {return {42};}
};
int main(){decksdk::Host host;P provider;host.provide("com.example.counter.counter",[&](auto method,auto value){return airdeck::com_example_counter_counter::dispatch(provider,method,value);});airdeck::com_example_counter_counter::Client client{host};}
