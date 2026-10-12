package com.example.starter;

import com.airdeck.decksdk.Button;
import com.airdeck.decksdk.DeckPlugin;
import com.airdeck.decksdk.PluginHost;
import java.util.List;

public final class Plugin implements DeckPlugin {
    private static final String PLUGIN_ID = __ID_JSON__;

    @Override
    public List<Button> catalog() {
        Button button = new Button("hello.say", "Say hello", "hello", PLUGIN_ID);
        button.icon_key = "plugins";
        button.editor_tap = true;
        return List.of(button);
    }

    @Override
    public void invoke(String type, String action, String bodyJson, String payloadJson) {
        if (!"hello".equals(action)) {
            throw new IllegalArgumentException("unknown action: " + action);
        }
        System.err.println("Hello from AirDeck!");
    }

    public static void main(String[] args) throws Exception {
        PluginHost.run(new Plugin());
    }
}
