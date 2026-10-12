package com.airdeck.capabilities;
import com.google.gson.JsonObject;
import java.util.function.Consumer;
public interface CapabilityTransport {JsonObject call(String capability,String method,JsonObject payload);Runnable subscribe(String capability,String topic,Consumer<JsonObject> callback); }
