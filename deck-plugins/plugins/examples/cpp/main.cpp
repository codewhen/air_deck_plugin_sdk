// Echo Beep — C++ example plugin using decksdk.hpp
//
// Build:
//   c++ -std=c++17 -O2 -I../../../sdk/cpp -o echo-plugin main.cpp

#include "decksdk.hpp"

#include <cstdlib>
#include <stdexcept>
#include <string>
#include <vector>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

static const char* kPluginId = "com.example.echo";

class EchoPlugin : public decksdk::DeckPlugin {
 public:
  std::vector<decksdk::Button> catalog() override {
    decksdk::Button b;
    b.id = "echo.beep";
    b.title = "Echo Beep";
    b.icon_key = "plugins";
    b.columns = 1;
    b.rows = 1;
    b.action = "beep";
    b.plugin_id = kPluginId;
    b.editor_tap = true;
    b.editor_toggle = true;
    return {b};
  }

  void invoke(const std::string& /*type*/, const std::string& action,
              const std::string& /*body*/, const std::string& /*payload*/) override {
    if (!action.empty() && action != "beep") {
      throw std::runtime_error("unknown action: " + action);
    }
#if defined(__APPLE__)
    if (std::system("afplay /System/Library/Sounds/Tink.aiff >/dev/null 2>&1") != 0) {
      std::system("osascript -e 'beep' >/dev/null 2>&1");
    }
#elif defined(_WIN32)
    Beep(880, 180);
#else
    std::system(
        "paplay /usr/share/sounds/freedesktop/stereo/message.oga >/dev/null 2>&1");
#endif
  }
};

int main() {
  EchoPlugin plugin;
  decksdk::run(plugin);
  return 0;
}
