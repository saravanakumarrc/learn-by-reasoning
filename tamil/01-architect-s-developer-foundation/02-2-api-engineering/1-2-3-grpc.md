# gRPC

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.3 — 2. API engineering

### 1. Problem

உங்ககிட்ட 50+ microservices இருக்கு. `Order Service` `Payment Service`-ஐ call பண்ணும், அது `Fraud Service`-ஐ call பண்ணும். எல்லாம் REST + JSON over HTTP/1.1.

இங்கே என்ன வலிக்கிறது?

* **Chattiness:** ஒரு business operation-க்கு 5-7 hop ஆகும். ஒவ்வொரு hop-லும் TCP handshake, headers, JSON parse. Latency கூடிக்கிட்டே போகும்.
* **Payload size:** JSON text heavy. `latency` முக்கியமான internal call-ல இது waste.
* **No streaming:** Server side event stream வேணும்னா REST-ல long polling / chunked hack பண்ணணும்.
* **Versioning chaos:** REST-ல field add/remove பண்ணினால் client break ஆகுமோ என்ற பயம். Contract தெளிவாக இல்லை.

இந்த வலி internal service-to-service communication-ல தான் அதிகம். Public API-க்கு REST நல்லா வேலை செய்யும். Inside data center / service mesh-ல efficiency வேணும்.

### 2. Mental Model

gRPC என்பது **contract-first RPC over HTTP/2**.

நீங்கள் முதலில் `.proto` file-ல service contract-ஐ define பண்ணுறீங்க. அதே contract-ல இருந்து client & server stubs auto-generate ஆகும். Communication binary ஆக, HTTP/2 multiplexing-ல நடக்கும்.

REST = resource + HTTP verbs + text JSON.
gRPC = procedure call + HTTP/2 + binary protobuf.

### 3. How It Works

`.proto` schema:
```proto
service Payment {
  rpc Charge(ChargeRequest) returns (ChargeResponse);
  rpc StreamStatus(stream StatusRequest) returns (stream StatusResponse);
}
```

Codegen Go/Java/Python/C# etc க்கு client/server stubs உருவாக்கும்.

HTTP/2 கொடுக்கிறது:
* **Multiplexing:** ஒரே TCP connection-ல பல requests parallel.
* **Header compression:** HPACK.
* **Bi-directional streaming:** unary, server-streaming, client-streaming, bidirectional.

protobuf கொடுக்கிறது:
* Binary serialization, ~3-5x smaller than JSON, parse fast.
* Backward/forward compatible schema evolution.

Flow:
```mermaid
graph LR
Client App -->|generated stub| gRPC Client
gRPC Client -->|HTTP/2 frames| gRPC Server
gRPC Server -->|generated stub| Service Impl
```

### 4. Architectural Reasoning

gRPC உபயோகிக்கும் போது என்ன constraint solve பண்ணுறோம்?

* **Low latency, high throughput internal calls.** Service mesh-ல 10k+ RPS.
* **Polyglot teams.** ஒரே `.proto` தான் source of truth. Go service, Java service எல்லாம் same contract.
* **Streaming use cases.** Live price feed, real-time notifications, bidirectional chat.
* **Strong typing.** Compile time contract check.

REST-ஐ விட்டு gRPC-க்கு போகிறோம் என்றால் system boundary internal தான். Public internet API, browser client என்றால் REST/JSON or gRPC-Web தான்.

### 5. Trade-offs

* **Observability vs efficiency.** Binary protobuf debug பண்ண கஷ்டம். REST-ல curl பண்ணி பார்க்கலாம். gRPC-க்கு grpcurl, interceptors வேணும்.
* **HTTP/2 operational complexity.** Proxies, load balancers, firewalls எல்லாம் HTTP/2 well support பண்ணணும். HTTP/1.1 fallbacks மெதுவாகும்.
* **Browser support.** Native browser gRPC இல்லை. Public API-க்கு translation layer வேணும்.
* **Schema evolution discipline.** Field number remove பண்ணக்கூடாது. Good practice வேணும் இல்லைனா breaking change.

Every architectural solution creates another trade-off. Efficiency கிடைக்கும், operational simplicity கொஞ்சம் குறையும்.

### 6. Practical Example

Enterprise order flow.

`Order Service` -> `Payment Service` -> `Inventory Service` -> `Notification Service`.

Order create பண்ணும் போது Payment-க்கு `Charge` RPC call. Response 20ms குறைவாக வேணும். Payload 2KB JSON இருந்தது, protobuf-ல 400 bytes ஆகிறது.

Notification-க்கு `StreamOrderEvents` bidirectional streaming use பண்ணி, order state change real-time client-க்கு push பண்ணுறோம்.

Team A Go-ல, Team B Java-ல எழுதினாலும் `.proto` ஒன்றே. CI-ல proto change ஆனால் breaking change detect பண்ணி block பண்ணுவோம்.

### 7. Reasoning Challenge

உங்களிடம் mobile app public API உள்ளது. 2M DAU. அதே service-ஐ internal recommendation engine-ம் use பண்ணுது, 50k RPS internal.

இந்த scenario-ல external API-க்கு REST வைத்து, internal calls-க்கு gRPC வைப்பீர்களா? அப்படி split பண்ண
