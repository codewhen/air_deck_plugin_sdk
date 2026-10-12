// Generated; Gson supplies JSON encoding.
package com.airdeck.capabilities;
import com.google.gson.*;
import java.util.function.Consumer;
public final class Apps {
public interface Transport extends CapabilityTransport {}
private static final Gson JSON = new Gson();
public static final class Empty {  }
public static final class Launch { public String target; }
public static final class Application { public String id; public String name; public String target; }
public static final class Applications { public Application[] apps; }
public interface Provider {
Empty launch(Launch request);
Applications list(Empty request);
}
public static JsonObject dispatch(Provider p,String method,JsonObject payload){switch(method){
case "launch": return JSON.toJsonTree(p.launch(JSON.fromJson(payload,Launch.class))).getAsJsonObject();
case "list": return JSON.toJsonTree(p.list(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
default: throw new IllegalArgumentException("unknown method");}}
public static final class Client { private final CapabilityTransport t; public Client(CapabilityTransport t){this.t=t;}
public Empty launch(Launch p){return JSON.fromJson(t.call("core.apps","launch",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Applications list(Empty p){return JSON.fromJson(t.call("core.apps","list",JSON.toJsonTree(p).getAsJsonObject()),Applications.class);}
}
}
