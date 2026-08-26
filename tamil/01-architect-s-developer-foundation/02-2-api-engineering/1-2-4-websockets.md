# WebSockets

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.4 — 2. API engineering

### 1. Problem

நீங்கள் ஒரு chat app அல்லது live order tracking build பண்றீங்க. User A message அனுப்பினால் User B க்கு உடனே தெரியணும். Dashboard-ல price ticker real-time update ஆகணும்.

HTTP request-response மாடலில் இது எப்படி work ஆகும்? Client தான் request அனுப்பணும். Server பதில் சொல்லும். Server-initiated push இல்லை.

Options என்ன? Short polling: client 2 sec க்கு ஒரு முறை GET /messages கேட்கும். Server-க்கு எதுவும் இல்லைனாலும் response அனுப்பும். 10k users இருந்தா 5 req/sec per user = 50k req/sec waste. Battery drain, latency.

Long polling: client request பண்ணி server close ஆகும் வரை திறந்து வைக்கும். Better ஆனாலும் ஒவ்வொரு message-க்கும் new HTTP connection. Header overhead, TCP handshake மறுபடியும்.

இங்கே பிரச்சனை என்ன? **Server க்கு client-க்கு தகவல் அனுப்ப வேண்டிய தேவை இருக்கு, ஆனால் HTTP ஒரு one-way pull மாதிரி இருக்கு.**

### 2. Mental Model

WebSocket ஒரு persistent, full-duplex channel.

HTTP ஒரு postcard system: நீங்கள் கேள்வி அனுப்புங்க, server பதில் அனுப்பும், connection முடியும்.

WebSocket ஒரு phone call: handshake முடிந்ததும் connection திறந்திருக்கும். Client-ம் server-ம் எப்போ வேண்டுமானாலும் பேசலாம். Low latency, low overhead.

### 3. How It Works

Start with normal HTTP.

```mermaid
sequenceDiagram
Client->>Server: GET /ws Upgrade: websocket, Sec-WebSocket-Key
Server-->>Client: 101 Switching Protocols
Client<->>Server: frames bidirectional
```

Client HTTP request அனுப்பும், header-ல `Upgrade: websocket` கொடுக்கும். Server accept பண்ணி 101 Switching Protocols திருப்பி அனுப்பினால் connection WebSocket-க்கு மாறும்.

அதுக்கு அப்புறம் HTTP framing இல்லாமல் lightweight frames மூலம் data போகும். Text அல்லது binary. Connection close ஆகும் வரை open இருக்கும்.

Implementation-ல heartbeats, ping/pong, automatic reconnect தேவை. Network failure வந்தால் client மீண்டும் connect பண்ணணும்.

### 4. Architectural Reasoning

WebSocket useful ஆகும் போது:

* Server push தேவைப்படும்: chat, notifications, live sports score, trading ticker
* Low latency தேவை, மில்லி seconds முக்கியம்
* Frequent small messages: polling overhead அதிகம்
* Bidirectional interaction: multiplayer game, collaborative editor

எப்போது use பண்ணக்கூடாது?

* One-way stream மட்டும் வேண்டுமானால் Server-Sent Events போதும். SSE HTTP-based, auto-reconnect, simpler.
* Request-response API மட்டும் இருந்தால் REST போதும்.
* Stateless scale முக்கியம், connection state manage பண்ண விருப்பம் இல்லை என்றால்.

Constraint பார்க்கணும்: connection stateful ஆகும். ஒரு user எந்த server instance-ல் இருக்கான் என்பது முக்கியம். Horizontal scaling-க்கு sticky session அல்லது central pub/sub தேவை.

### 5. Trade-offs

**Stateful connections vs stateless.** HTTP request ஒவ்வொன்றும் independent. WebSocket ஒரு connection maintain பண்ணணும். Server memory, file descriptor limit வரும். 1M concurrent connections என்பது non-trivial.

**Scaling complexity.** New server வந்தால் existing connections move ஆகாது. Message broadcast-க்கு Redis Pub/Sub, Kafka, NATS போன்ற message bus தேவைப்படும். Service A message அனுப்பினால் அது எந்த instance-ல் இருக்கும் client-க்கும் route ஆகணும்.

**Operational failure modes.** Connection drop ஆனால் client-க்கு தெரியாது. Reconnect logic, exponential backoff, message loss, duplicate delivery handle பண்ணணும். Idle connection-ஐ proxy/firewall close பண்ணும். Heartbeat வேண்டும்.

**Cost.** Idle connection-க்கும் resources. 10k idle WebSocket connections ≈ few hundred MB memory. Polling-க்கு CPU spike, WebSocket-க்கு memory footprint.

### 6. Practical Example

E-commerce live order tracking.

Customer order confirm ஆனதும், rider pick up, en route, delivered என்ற status update real-time வேண்டும்.

Architecture:

Client browser
