// Generated; Gson supplies JSON encoding.
package com.airdeck.capabilities;
import com.google.gson.*;
import java.util.function.Consumer;
public final class Pointer {
public interface Transport extends CapabilityTransport {}
private static final Gson JSON = new Gson();
public static final class Empty {  }
public static final class Motion { public double dx; public double dy; public double sensitivity; }
public enum ClickButton {@com.google.gson.annotations.SerializedName("left") LEFT,@com.google.gson.annotations.SerializedName("right") RIGHT}
public static final class Click { public ClickButton button; public boolean double_click; }
public interface Provider {
Empty move(Motion request);
Empty scroll(Motion request);
Empty click(Click request);
}
public static JsonObject dispatch(Provider p,String method,JsonObject payload){switch(method){
case "move": return JSON.toJsonTree(p.move(JSON.fromJson(payload,Motion.class))).getAsJsonObject();
case "scroll": return JSON.toJsonTree(p.scroll(JSON.fromJson(payload,Motion.class))).getAsJsonObject();
case "click": return JSON.toJsonTree(p.click(JSON.fromJson(payload,Click.class))).getAsJsonObject();
default: throw new IllegalArgumentException("unknown method");}}
public static final class Client { private final CapabilityTransport t; public Client(CapabilityTransport t){this.t=t;}
public Empty move(Motion p){return JSON.fromJson(t.call("core.pointer","move",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty scroll(Motion p){return JSON.fromJson(t.call("core.pointer","scroll",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty click(Click p){return JSON.fromJson(t.call("core.pointer","click",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
}
}
