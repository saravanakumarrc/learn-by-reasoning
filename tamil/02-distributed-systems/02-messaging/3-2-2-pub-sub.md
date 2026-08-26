# Pub/sub

> **Learning Path:** Distributed Systems
> **Section:** 3.2.2 — Messaging

### 1. Problem

ஒரு e-commerce system-ல Order service இருக்கு. Customer ஒரு order place பண்ணும்போது என்ன நடக்கணும்?

Inventory-க்கு stock reduce பண்ணணும். Shipping-க்கு label create பண்ணணும். Notification service-க்கு email/SMS அனுப்பணும். Analytics service-க்கு event log பண்ணணும். Fraud detection service-க்கு check பண்ணணும்.

இதை எல்லாம் Order service direct API call மூலம் synchronous-ஆ செய்தால் என்ன ஆகும்?

ஒரு service slow ஆனாலோ timeout ஆனாலோ, அது Order-ஐயே block பண்ணும். ஒரு service down ஆனால் முழு order flow-ம் fail ஆகும். New service add பண்ணணும்னா Order service-ஐ மாற்ற வேண்டும். Tight coupling.

இந்த pain தான் pub/sub-ஐ உருவாக்கியது. Producer எதை publish பண்ணணுமோ அதை மட்டும் பண்ண வேண்டும். Who consumes, when consumes, எத்தனை பேர் consume பண்ணுவாங்கன்னு producer-க்கு தெரிய வேண்டாம்.

### 2. Mental Model

Pub/sub என்பது newspaper subscription மாதிரி.

நீங்கள் ஒரு newspaper-ஐ subscribe பண்ணுவீர்கள். Publisher எத்தனை பேருக்கு போடுறாங்கன்னு தெரியாது. நீங்கள் வேண்டுமானால் எப்போது வேண்டுமானாலும் படிக்கலாம். Publisher நீங்கள் படித்தீர்களா இல்லையான்னு wait பண்ண மாட்டார்.

இது இரண்டு வகை decoupling கொடுக்கிறது:

* **Spatial decoupling:** Producer-க்கு consumer யார் என்று தெரியாது
* **Temporal decoupling:** Producer publish பண்ணும் நேரமும் consumer consume பண்ணும் நேரமும் வேறு வேறு

### 3. How It Works

மூன்று role மட்டும் போதும்.

**Producer** ஒரு event-ஐ ஒரு topic-க்கு publish பண்ணும். உதாரணம்: `orders.created`.

**Broker** அந்த event-ஐ store பண்ணி, அந்த topic-ஐ subscribe பண்ணியுள்ள எல்லா consumers-க்கும் fan-out பண்ணும்.

**Consumer** தனக்கு வேண்டிய topic-ஐ subscribe பண்ணி, event வரும்போது process பண்ணும்.

```
graph LR
A[Order Service - Producer] -->|publish orders.created| B[Pub/Sub Broker]
B --> C[Inventory Service]
B --> D[Shipping Service]
B --> E[Notification Service]
B --> F[Analytics Service]
```

Producer consumer-ஐ தெரிந்து வைத்திருக்க வேண்டாம். Broker தான் routing பார்க்கும்.

### 4. Architectural Reasoning

Pub/sub useful ஆகும் போது:

* One event, many interested parties. Fan-out தேவை.
* Producer block ஆகக்கூடாது. Fire-and-forget வேண்டும்.
* Consumers வெவ்வேறு speed-ல் process பண்ணும். Slow consumer fast consumer-ஐ பாதிக்கக்கூடாது.
* Replay தேவை. Past events-ஐ மீண்டும் process பண்ண வேண்டும்.

Alternatives என்ன?

* **Synchronous request-response:** Simple, strong consistency. ஆனால் coupling அதிகம், failure propagate ஆகும்.
* **Point-to-point queue:** One producer, one consumer. Work distribution-க்கு நல்லது. ஆனால் fan-out இல்லை.
* **Pub/sub:** Fan-out, decoupling. ஆனால் ordering, delivery guarantee complex.

Architect ஏன் pub/sub choose பண்ணுவார்? System boundary-ல் loose coupling வேண்டும், team autonomy வேண்டும். Order team தனியாக deploy பண்ண முடியும், Inventory team தனியாக deploy பண்ண முடியும்.

### 5. Trade-offs

**Ordering vs Scale:** Pub/sub-ல் global ordering கொடுப்பது கடினம். Partition per key பண்ணினால் order preserve ஆகும், ஆனால் throughput limit ஆகும்.

**Delivery guarantee:** At-least-once தான் எளிது. Exactly-once க்கு idempotent consumer + deduplication தேவை. Retry பண்ணும் போது duplicate event வரும்.

**Observability குறைவு:** Request-response-ல் trace easy. Pub/sub-ல் event போய் யார் consume பண்ணாங்க, fail ஆனாங்களான்னு track பண்ண கடினம். Dead letter queue, monitoring must.

**Cost:** Fan-out என்றால் same event பல முறை store/transfer ஆகும். Broker cost, storage cost grow ஆகும்.

Failure mode முக்கியம்: Consumer crash ஆனால் event நழுவக்கூடாது. Ack mechanism, offset management தேவை. Broker down ஆனால் whole system impact ஆகும்.

### 6. Practical Example

Order placed flow.

Order Service event publish பண்ணும்: `{orderId: 123, userId: 456, items: [...]}` to topic `orders.created`.

Inventory Service subscribe பண்ணி stock reserve பண்ணும். Shipping Service subscribe
