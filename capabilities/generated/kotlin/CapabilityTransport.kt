package com.airdeck.client.core.capability.generated
import kotlinx.serialization.json.JsonElement
interface CapabilityTransport {suspend fun call(capability:String,method:String,payload:JsonElement):JsonElement;suspend fun subscribe(capability:String,topic:String,callback:(JsonElement)->Unit):()->Unit}
