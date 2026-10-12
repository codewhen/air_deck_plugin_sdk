// Generated; do not edit.
package com.airdeck.client.core.capability.generated
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
object Keyboard {
interface Transport : CapabilityTransport
@Serializable class Empty
@Serializable data class Key(val key:String)
@Serializable data class Combo(val combo:String)
class Client(private val transport:CapabilityTransport) {
suspend fun press(request:Key):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.keyboard","press",Json.encodeToJsonElement(Key.serializer(),request)))
suspend fun hotkey(request:Combo):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.keyboard","hotkey",Json.encodeToJsonElement(Combo.serializer(),request)))
}
}
