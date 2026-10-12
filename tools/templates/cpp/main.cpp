#include "decksdk.hpp"
#include <iostream>
#include <stdexcept>

static const char* plugin_id = __ID_JSON__;

class Plugin : public decksdk::DeckPlugin {
public:
    std::vector<decksdk::Button> catalog() override {
        decksdk::Button button;
        button.id = "hello.say";
        button.title = "Say hello";
        button.action = "hello";
        button.plugin_id = plugin_id;
        button.icon_key = "plugins";
        button.editor_tap = true;
        return {button};
    }

    void invoke(const std::string&, const std::string& action,
                const std::string&, const std::string&) override {
        if (action != "hello") { throw std::runtime_error("unknown action: " + action); }
        std::cerr << "Hello from AirDeck!" << std::endl;
    }
};

int main() { Plugin plugin; decksdk::run(plugin); }
