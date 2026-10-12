// Generated; do not edit.
package com.airdeck.client.core.capability.generated
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
object Apps {
interface Transport : CapabilityTransport
@Serializable class Empty
@Serializable data class Launch(val target:String)
@Serializable data class Application(val id:String,val name:String,val target:String)
@Serializable data class Applications(val apps:List<Application>)
class Client(private val transport:CapabilityTransport) {
suspend fun launch(request:Launch):Empty = Json.decodeFromJsonElement(Empty.serializer(),transport.call("core.apps","launch",Json.encodeToJsonElement(Launch.serializer(),request)))
suspend fun list(request:Empty):Applications = Json.decodeFromJsonElement(Applications.serializer(),transport.call("core.apps","list",Json.encodeToJsonElement(Empty.serializer(),request)))
}
}
