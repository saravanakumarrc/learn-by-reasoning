# Exactly-once vs at-least-once

> **Learning Path:** Distributed Systems
> **Section:** 3.1.26 — Core concepts

## Problem

ஒரு e-commerce order API இருக்கு. Customer order place பண்ணும்போது `OrderService` payment service-ஐ call பண்ணி, success ஆனா order confirm பண்ணும்.

Network glitch வந்து response வரல. Client-க்கு timeout ஆகும். Client என்ன பண்ணும்? **Retry பண்ணும்.**

இப்போ முதல் request உண்மையில் server-ல process ஆகி payment charge ஆகிடுச்சு, ஆனா response போகல. Retry வந்தா இன்னொரு முறை charge ஆகுமா? 

இதே பிரச்சனை message queue-லயும் வரும். Producer ஒரு event publish பண்ணும். Broker crash ஆகி ack வரல. Producer retry பண்ணி அதே event-ஐ இன்னொரு முறை அனுப்பும். Consumer அதை இரண்டு முறை பார்த்துடும்.

இங்கே கேள்வி என்னன்னா: **ஒரு operation-ஐ எத்தனை முறை execute பண்ண வேண்டும்?**

## Mental Model

Delivery semantics-ன்னு இதைப் பார்க்கலாம்.

* **At-least-once:** Message கண்டிப்பாக ஒரு முறையாவது கிடைக்கும். Duplicate வரலாம்.
* **Exactly-once:** Message ஒரு முறை மட்டுமே process ஆகும். Duplicate இருக்காது.

நிஜத்துல network unreliable. Timeout, crash, retry எல்லாம் normal. அதனால at-least-once தான் default ஆக எளிது.

Exactly-once என்பது **illusion** மாதிரி. நிஜமாக கிட்டத்தட்ட எல்லா system-லயும் at-least-once + idempotency மூலம் simulate பண்ணுவாங்க.

## How It Works

**At-least-once என்ன பண்ணும்?**

Producer send செய்யும். Ack வரலன்னா retry. Broker persist பண்ணி consumer-க்கு deliver பண்ணும். Consumer crash ஆனா broker மீண்டும் deliver பண்ணும். Consumer ack தரும் வரை deliver ஆகிக்கொண்டே இருக்கும்.

Result: message lost ஆகாது, ஆனால் duplicate வரும்.

**Exactly-once பெற என்ன தேவை?**

1. **Idempotency:** Same operation-ஐ எத்தனை முறை call பண்ணினாலும் effect ஒன்றாக இருக்கணும்.
2. **Deduplication:** Producer / broker / consumer ல message id-ஐ track பண்ணி, ஏற்கனவே process ஆனதை skip பண்ணணும்.
3. **Transactional boundary:** Produce + DB write ஒன்றாக commit ஆகணும். இல்லன்னா lost or duplicate வரும்.

Simple flow:
```mermaid
graph LR
Client -->|request with idempotency-key| API
API -->|write DB in same tx| Outbox Table
Outbox -->|relay| Message Queue
Queue -->|deliver| Consumer
Consumer -->|check dedup store| Process
Consumer -->|mark processed| Dedup Store
```

## Architectural Reasoning

எப்போ at-least-once போதும்?
* Inventory decrement, notification send, analytics event count போன்றவை duplicate-க்கு tolerant ஆன system-ல.
* Retry logic simple, latency குறைவு, operational cost குறைவு.

எப்போ exactly-once மாதிரி behavior வேண்டும்?
* Money transfer, payment capture, stock allocation, loyalty points credit போன்ற financial / business critical operations.
* Constraint: duplicate process ஆனால் business loss.

அதனால architect என்ன பண்ணுவார்? Exactly-once-ஐ system level-ல guarantee பண்ண முயற்சி செய்யாமல், **application level-ல idempotent design** பண்ணுவார். At-least-once delivery-ஐ accept பண்ணி, duplicate-ஐ application handle பண்ணும்.

## Trade-offs

* **Complexity vs Correctness:** At-least-once cheap and simple. Exactly-once க்கு dedup store, idempotency key, transactional outbox, exactly-once processing semantics எல்லாம் வேண்டும். Latency, cost, operational complexity எல்லாம் ஏறும்.
* **Throughput:** Dedup check DB lookup சேர்க்கும். High throughput system-ல bottleneck ஆகும்.
* **Failure modes:** At-least-once-ல duplicate common. Exactly-once simulation-ல dedup store itself failure ஆனால் false negative வரும்.
* **Scope:** Exactly-once end-to-end guarantee கடினம். Usually message delivery + processing ஒன்றாக பார்க்கணும்.

## Practical Example

Bank-ல debit transfer. Client POST `/transfer` with `idempotency-key: uuid`.

1. API request வரும். DB-ல `idempotency_keys` table-ல key exist ஆ? இருந்தா stored response-ஐ திருப்பி அனுப்பு.
2. இல்லன்னா transfer-ஐ DB transaction-ல execute பண்ணி, key + result-ஐ save பண்ணு. Commit ஆன பிறகு தான் response return.
3. Timeout ஆனாலும் client retry பண்ணினாலும் same key-க்கு same result.

இங்கே message queue use பண்ணினா, outbox pattern use பண்ணி DB write + event publish ஒரே transaction-ல
