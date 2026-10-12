// Generated; do not edit.
package com.airdeck.client.core.capability.generated
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
object Pointer {
interface Transport : CapabilityTransport
@Serializable class Empty
@Serializable data class Motion(val dx:Double,val dy:Double,val sensitivity:Double)
@Serializable enum class ClickButton {@SerialName("left") LEFT,@SerialName("right") RIGHT}
@Serializable data class Click(val button:ClickButton,val double_click:Boolean)
class Client(private val transport:CapabilityTransport) {
suspend fun move(request:Motion):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.pointer","move",Json.encodeToJsonElement(Motion.serializer(),request)))
suspend fun scroll(request:Motion):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.pointer","scroll",Json.encodeToJsonElement(Motion.serializer(),request)))
suspend fun click(request:Click):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.pointer","click",Json.encodeToJsonElement(Click.serializer(),request)))
}
}
