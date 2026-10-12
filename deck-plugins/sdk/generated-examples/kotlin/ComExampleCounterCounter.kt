// Generated; do not edit.
package com.airdeck.client.core.capability.generated
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
object ComExampleCounterCounter {
interface Transport : CapabilityTransport
@Serializable class Empty
@Serializable data class Count(val value:Long)
class Client(private val transport:CapabilityTransport) {
suspend fun getCount(request:Empty):Count = Json.decodeFromJsonElement(Count.serializer(),transport.call("com.example.counter.counter","getCount",Json.encodeToJsonElement(Empty.serializer(),request)))
suspend fun subscribeCount(callback:(Count)->Unit):()->Unit = transport.subscribe("com.example.counter.counter","count") { callback(Json.decodeFromJsonElement(Count.serializer(),it)) }
}
}
