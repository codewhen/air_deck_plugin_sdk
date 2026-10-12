// Generated; Gson supplies JSON encoding.
package com.airdeck.capabilities;
import com.google.gson.*;
import java.util.function.Consumer;
public final class ComExampleCounterCounter {
public interface Transport extends CapabilityTransport {}
private static final Gson JSON = new Gson();
public static final class Empty {  }
public static final class Count { public long value; }
public interface Provider {
Count getCount(Empty request);
}
public static JsonObject dispatch(Provider p,String method,JsonObject payload){switch(method){
case "getCount": return JSON.toJsonTree(p.getCount(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
default: throw new IllegalArgumentException("unknown method");}}
public static final class Client { private final CapabilityTransport t; public Client(CapabilityTransport t){this.t=t;}
public Count getCount(Empty p){return JSON.fromJson(t.call("com.example.counter.counter","getCount",JSON.toJsonTree(p).getAsJsonObject()),Count.class);}
public Runnable subscribeCount(Consumer<Count> fn){return t.subscribe("com.example.counter.counter","count",raw->fn.accept(JSON.fromJson(raw,Count.class)));}
}
}
