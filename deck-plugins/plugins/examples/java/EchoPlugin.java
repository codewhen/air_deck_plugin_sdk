package com.example.echo;

import com.airdeck.decksdk.Button;
import com.airdeck.decksdk.DeckPlugin;
import com.airdeck.decksdk.PluginHost;
import java.io.IOException;
import java.util.List;

/** Echo Beep — Java example plugin using the decksdk. */
public final class EchoPlugin implements DeckPlugin {
  private static final String PLUGIN_ID = "com.example.echo";

  public static void main(String[] args) throws Exception {
    PluginHost.run(new EchoPlugin());
  }

  @Override
  public List<Button> catalog() {
    Button b = new Button("echo.beep", "Echo Beep", "beep", PLUGIN_ID);
    b.icon_key = "plugins";
    b.editor_tap = true;
    b.editor_toggle = true;
    return List.of(b);
  }

  @Override
  public void invoke(String type, String action, String bodyJson, String payloadJson) {
    if (action != null && !action.isEmpty() && !"beep".equals(action)) {
      throw new IllegalArgumentException("unknown action: " + action);
    }
    String os = System.getProperty("os.name", "").toLowerCase();
    ProcessBuilder sound = os.contains("mac")
        ? new ProcessBuilder("afplay", "/System/Library/Sounds/Tink.aiff")
        : os.contains("win")
            ? new ProcessBuilder("powershell", "-NoProfile", "-Command", "[console]::beep(880,180)")
            : new ProcessBuilder("paplay", "/usr/share/sounds/freedesktop/stereo/message.oga");
    try {
      sound.redirectOutput(ProcessBuilder.Redirect.DISCARD)
          .redirectError(ProcessBuilder.Redirect.INHERIT).start().waitFor();
    } catch (IOException error) {
      System.err.println("[echo] sound unavailable: " + error.getMessage());
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
    }
  }
}
