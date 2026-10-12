package com.example.echo;

import com.airdeck.decksdk.Button;
import com.airdeck.decksdk.DeckPlugin;
import com.airdeck.decksdk.PluginHost;
import java.awt.Toolkit;
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
    Toolkit.getDefaultToolkit().beep();
    try {
      Thread.sleep(120);
    } catch (InterruptedException ignored) {
      Thread.currentThread().interrupt();
    }
  }
}
