// Generated; Gson supplies JSON encoding.
package com.airdeck.capabilities;
import com.google.gson.*;
import java.util.function.Consumer;
public final class Keyboard {
public interface Transport extends CapabilityTransport {}
private static final Gson JSON = new Gson();
public static final class Empty {  }
public static final class Key { public String key; }
public static final class Combo { public String combo; }
public interface Provider {
Empty press(Key request);
Empty hotkey(Combo request);
}
public static JsonObject dispatch(Provider p,String method,JsonObject payload){switch(method){
case "press": return JSON.toJsonTree(p.press(JSON.fromJson(payload,Key.class))).getAsJsonObject();
case "hotkey": return JSON.toJsonTree(p.hotkey(JSON.fromJson(payload,Combo.class))).getAsJsonObject();
default: throw new IllegalArgumentException("unknown method");}}
public static final class Client { private final CapabilityTransport t; public Client(CapabilityTransport t){this.t=t;}
public Empty press(Key p){return JSON.fromJson(t.call("core.keyboard","press",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty hotkey(Combo p){return JSON.fromJson(t.call("core.keyboard","hotkey",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
}
}
