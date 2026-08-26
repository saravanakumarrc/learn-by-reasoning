# Distributed communication

> **Learning Path:** Distributed Systems
> **Section:** 3.1.5 — Core concepts

## 1. Problem

நீங்க ஒரு monolith-ல இருந்து microservices-க்கு போறீங்க. ஒரு service இன்னொரு service-ஐ call பண்ணணும். Local function call மாதிரி இல்ல. Network-ல போகுது.

இங்க தான் வலி ஆரம்பிக்குது. Network failure வரும். Packet loss ஆகும். Service down ஆகும். Network partition ஆகும். Latency spike ஆகும்.

ஒரு request போனது, response வரல. Client retry பண்ணுது. Server side-ல request ஏற்கனவே process ஆகிடுச்சா இல்லையா தெரியாது. இதுவே duplicate payment, duplicate order வர காரணம்.

Distributed communication-ன் core problem இது தான்: **network is unreliable, and partial failure is normal**.

## 2. Mental Model

Local call-ல "இது success ஆச்சா இல்லையா"ன்னு உடனே தெரியும். Distributed call-ல அது guaranteed இல்ல.

Communication-ஐ இரண்டு வழியில் நினைக்கலாம்.

1. **Synchronous request-response**: நீங்க call பண்ணி, பதில் வரும்வரை காத்திருக்கீங்க. Like a phone call.
2. **Asynchronous message passing**: நீங்க message-ஐ அனுப்பி விட்டுட்டு போறீங்க. Receiver எப்போ வேணும்னாலும் process பண்ணும். Like a post.

இந்த இரண்டுக்கும் வேற வேற failure modes, latency, coupling இருக்கு.

## 3. How It Works

ஒரு distributed call-ல என்ன நடக்குது:

Service A → serialization → transport TCP/HTTP/gRPC → network → Service B → deserialization → process → response path back.

இங்க ஒவ்வொரு step-லயும் failure வரலாம்.

அதனால எல்லா distributed communication-லயும் இதை கையாளணும்:
* **Timeout**: எவ்வளவு நேரம் காத்திருப்பது?
* **Retry**: fail ஆனா மறுபடி try பண்ணுமா?
* **Idempotency**: same request twice வந்தா duplicate effect இல்லாம பார்ப்பது எப்படி?
* **Delivery guarantee**: at-most-once, at-least-once, exactly-once என்ன வேணும்?

Sync RPC-ல REST, gRPC போன்றவை request-response pattern. Async-ல message queue like Kafka, RabbitMQ, event bus போன்றவை producer-consumer pattern.

## 4. Architectural Reasoning

**When sync?**
உடனே decision வேணும். Example: User login ஆனதும் user details fetch பண்ணணும். Order create பண்ணும்போது payment success confirmation வேணும். Low latency, strong coupling ஏற்படும்.

**When async?**
Decoupling வேணும். Producer slowdown ஆக கூடாது. Event replay வேணும். Example: Order placed ஆனதும் inventory update, payment, notification, analytics எல்லாம் தனித்தனியா போகலாம். Order service-க்கு inventory எவ்வளவு நேரம் எடுக்குதுன்னு கவலை இல்ல.

ஒரு architect இப்படி தேர்வு பண்ணுவார்:
* Latency requirement என்ன?
* Consumer count எவ்வளவு? Speed vary ஆகுமா?
* Replay தேவையா?
* Failure-ல data loss accept பண்ண முடியுமா?

## 5. Trade-offs

**Sync vs Async**
Sync simple, immediate consistency தெரியும். ஆனால் caller caller block ஆகும், cascading failure வரும். One service slow ஆனா அதை call பண்ணும் எல்லாம் slow ஆகும்.

Async resilient, decoupled, scalable. ஆனால் ordering guarantee கஷ்டம், eventual consistency வரும், debugging கடினம்.

**Reliability vs Latency**
Retry பண்ணினா reliability கூடும், ஆனால் latency அதிகரிக்கும். Timeout குறைச்சா fast fail ஆகும், ஆனால் false positive அதிகம்.

**Coupling**
Sync call-ல caller receiver-ன் schema, availability-ஐ தெரிஞ்சு இருக்கணும். Async-ல contract மட்டும் போதும், schema evolution easier.

Important failure mode: **thundering herd on retry**. Service down ஆன உடனே எல்லா client-உம் retry பண்ணி overload பண்ணிடும். Exponential backoff, jitter தேவை.

##
