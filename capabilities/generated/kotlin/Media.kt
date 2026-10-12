// Generated; do not edit.
package com.airdeck.client.core.capability.generated
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
object Media {
interface Transport : CapabilityTransport
@Serializable class Empty
@Serializable enum class PlaybackStatus {@SerialName("playing") PLAYING,@SerialName("paused") PAUSED,@SerialName("stopped") STOPPED,@SerialName("unknown") UNKNOWN}
@Serializable data class Playback(val status:PlaybackStatus,val available:Boolean)
@Serializable data class Track(val title:String,val artist:String,val album:String,val app:String,val available:Boolean)
@Serializable data class Volume(val level:Double,val muted:Boolean,val available:Boolean)
@Serializable data class SetVolume(val level:Double)
@Serializable data class AdjustVolume(val delta:Double)
@Serializable data class Mute(val muted:Boolean)
class Client(private val transport:CapabilityTransport) {
suspend fun getPlayback(request:Empty):Playback = Json.decodeFromJsonElement(Playback.serializer(),transport.call("core.media","getPlayback",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun getTrack(request:Empty):Track = Json.decodeFromJsonElement(Track.serializer(),transport.call("core.media","getTrack",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun getVolume(request:Empty):Volume = Json.decodeFromJsonElement(Volume.serializer(),transport.call("core.media","getVolume",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun togglePlayback(request:Empty):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","togglePlayback",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun play(request:Empty):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","play",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun pause(request:Empty):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","pause",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun next(request:Empty):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","next",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun previous(request:Empty):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","previous",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun setVolume(request:SetVolume):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","setVolume",Json.encodeToJsonElement(SetVolume.serializer(),request)))
suspend fun adjustVolume(request:AdjustVolume):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","adjustVolume",Json.encodeToJsonElement(AdjustVolume.serializer(),request)))
suspend fun setMute(request:Mute):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.media","setMute",Json.encodeToJsonElement(Mute.serializer(),request)))
suspend fun subscribePlayback(callback:(Playback)->Unit):()->Unit = transport.subscribe("core.media","playback") { callback(Json.decodeFromJsonElement(Playback.serializer(),it)) }
suspend fun subscribeTrack(callback:(Track)->Unit):()->Unit = transport.subscribe("core.media","track") { callback(Json.decodeFromJsonElement(Track.serializer(),it)) }
suspend fun subscribeVolume(callback:(Volume)->Unit):()->Unit = transport.subscribe("core.media","volume") { callback(Json.decodeFromJsonElement(Volume.serializer(),it)) }
}
}
