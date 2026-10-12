// Generated; Gson supplies JSON encoding.
package com.airdeck.capabilities;
import com.google.gson.*;
import java.util.function.Consumer;
public final class Media {
public interface Transport extends CapabilityTransport {}
private static final Gson JSON = new Gson();
public static final class Empty {  }
public enum PlaybackStatus {@com.google.gson.annotations.SerializedName("playing") PLAYING,@com.google.gson.annotations.SerializedName("paused") PAUSED,@com.google.gson.annotations.SerializedName("stopped") STOPPED,@com.google.gson.annotations.SerializedName("unknown") UNKNOWN}
public static final class Playback { public PlaybackStatus status; public boolean available; }
public static final class Track { public String title; public String artist; public String album; public String app; public boolean available; }
public static final class Volume { public double level; public boolean muted; public boolean available; }
public static final class SetVolume { public double level; }
public static final class AdjustVolume { public double delta; }
public static final class Mute { public boolean muted; }
public interface Provider {
Playback getPlayback(Empty request);
Track getTrack(Empty request);
Volume getVolume(Empty request);
Empty togglePlayback(Empty request);
Empty play(Empty request);
Empty pause(Empty request);
Empty next(Empty request);
Empty previous(Empty request);
Empty setVolume(SetVolume request);
Empty adjustVolume(AdjustVolume request);
Empty setMute(Mute request);
}
public static JsonObject dispatch(Provider p,String method,JsonObject payload){switch(method){
case "getPlayback": return JSON.toJsonTree(p.getPlayback(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "getTrack": return JSON.toJsonTree(p.getTrack(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "getVolume": return JSON.toJsonTree(p.getVolume(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "togglePlayback": return JSON.toJsonTree(p.togglePlayback(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "play": return JSON.toJsonTree(p.play(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "pause": return JSON.toJsonTree(p.pause(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "next": return JSON.toJsonTree(p.next(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "previous": return JSON.toJsonTree(p.previous(JSON.fromJson(payload,Empty.class))).getAsJsonObject();
case "setVolume": return JSON.toJsonTree(p.setVolume(JSON.fromJson(payload,SetVolume.class))).getAsJsonObject();
case "adjustVolume": return JSON.toJsonTree(p.adjustVolume(JSON.fromJson(payload,AdjustVolume.class))).getAsJsonObject();
case "setMute": return JSON.toJsonTree(p.setMute(JSON.fromJson(payload,Mute.class))).getAsJsonObject();
default: throw new IllegalArgumentException("unknown method");}}
public static final class Client { private final CapabilityTransport t; public Client(CapabilityTransport t){this.t=t;}
public Playback getPlayback(Empty p){return JSON.fromJson(t.call("core.media","getPlayback",JSON.toJsonTree(p).getAsJsonObject()),Playback.class);}
public Track getTrack(Empty p){return JSON.fromJson(t.call("core.media","getTrack",JSON.toJsonTree(p).getAsJsonObject()),Track.class);}
public Volume getVolume(Empty p){return JSON.fromJson(t.call("core.media","getVolume",JSON.toJsonTree(p).getAsJsonObject()),Volume.class);}
public Empty togglePlayback(Empty p){return JSON.fromJson(t.call("core.media","togglePlayback",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty play(Empty p){return JSON.fromJson(t.call("core.media","play",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty pause(Empty p){return JSON.fromJson(t.call("core.media","pause",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty next(Empty p){return JSON.fromJson(t.call("core.media","next",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty previous(Empty p){return JSON.fromJson(t.call("core.media","previous",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty setVolume(SetVolume p){return JSON.fromJson(t.call("core.media","setVolume",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty adjustVolume(AdjustVolume p){return JSON.fromJson(t.call("core.media","adjustVolume",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Empty setMute(Mute p){return JSON.fromJson(t.call("core.media","setMute",JSON.toJsonTree(p).getAsJsonObject()),Empty.class);}
public Runnable subscribePlayback(Consumer<Playback> fn){return t.subscribe("core.media","playback",raw->fn.accept(JSON.fromJson(raw,Playback.class)));}
public Runnable subscribeTrack(Consumer<Track> fn){return t.subscribe("core.media","track",raw->fn.accept(JSON.fromJson(raw,Track.class)));}
public Runnable subscribeVolume(Consumer<Volume> fn){return t.subscribe("core.media","volume",raw->fn.accept(JSON.fromJson(raw,Volume.class)));}
}
}
