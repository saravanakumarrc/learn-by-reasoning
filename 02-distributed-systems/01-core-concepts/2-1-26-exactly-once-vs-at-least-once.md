# Exactly-once vs at-least-once

> **Learning Path:** Distributed Systems
> **Section:** 2.1.26 — Core concepts

**Exactly-once vs at-least-once**

### 1. The problem

In distributed systems a message can be lost, duplicated, or processed twice because of retries and failures.

Network blips, broker crashes, consumer timeouts, and process restarts are normal. If you retry a send to be safe, you may deliver the same event twice. If you don’t retry, you may lose it.

The question is not “can we avoid failures” — we can’t. It’s “what guarantees do we want about processing despite failures”.

### 2. Mental model

Think of a bank transfer notification.

* At-least-once: The bank will try until it knows you got it. You may receive the same notification twice. You must handle duplicates.
* Exactly-once: You receive it one time, no more, no less. The system guarantees it.

Exactly-once is a business guarantee about *effect*, not just delivery. It means the side effect happens once.

### 3. How it works

Delivery semantics are defined by producer → broker → consumer.

* **At-most-once**: Send once, no retry. Fast, lossy.
* **At-least-once**: Retry on failure. Guarantees delivery, not uniqueness.
* **Exactly-once**: Guarantees one processing with idempotent effect.

At-least-once is cheap: producer retries, consumer acks. If ack is lost, broker redelivers.

Exactly-once needs three things together:
1. **Deduplication** — track what has been seen
2. **Idempotence** — processing same input twice yields same state
3. **Atomic coordination** — record of processing and side effects commit together

```mermaid
flowchart LR
Producer -->|send msg| Broker
Broker -->|deliver| Consumer
Consumer -->|process + write state| DB
Consumer -->|ack| Broker

subgraph At-least-once
Broker -.timeout / crash.->|redeliver| Consumer
end

subgraph Exactly-once
Consumer -->|write state + dedupe id in same tx| DB
DB -.commit only if new-> Broker
end
```

In practice “exactly-once” is usually implemented as at-least-once + idempotent consumer + transactional outbox / write-ahead log. The broker gives at-least-once, your application makes it effectively exactly-once.

### 4. Architectural reasoning

Choose at-least-once when:
* Duplicates are tolerable if handled
* You need low latency and high throughput
* You can make processing idempotent

Choose exactly-once semantics when:
* Business invariants are violated by duplicates: double charge, double shipment, double credit
* You cannot tolerate replays in downstream systems
* Cost of deduplication is lower than cost of error

Most real systems pick at-least-once delivery with an idempotent consumer. True exactly-once across services is rarely worth it.

### 5. Trade-offs and failure modes

* **Complexity vs safety.** Exactly-once requires coordinated state, durable dedupe store, and often distributed transactions. It adds latency and coupling.
* **At-least-once duplicates.** Without idempotence you get double writes, double emails, double payments.
* **At-most-once loss.** Without retries you lose messages silently. Rarely acceptable.
* **Deduplication window.** You must retain dedupe IDs long enough for late retries. Too short = duplicates, too long = storage cost.
* **Clock and ordering.** Exactly-once does not guarantee exactly-once *order* across partitions. You still need ordering guarantees if required.

Failure mode to remember: a consumer crashes after processing but before ack. Broker redelivers. If processing is not idempotent, you have duplicate side effects.

### 6. Example

Payment capture pipeline.

Producer emits `PaymentAuthorized` event. Consumer charges the card and creates an invoice.

With at-least-once, a crash after charge but before ack causes redelivery → second charge.

Fix: make consumer idempotent by storing `event_id` with the charge in the same DB transaction as the invoice. On redelivery, the dedupe check skips the charge.

This is effectively exactly-once for the business effect, even though the broker delivered twice.

Kafka, RabbitMQ, and most queues provide at-least-once. Systems like transactional outbox, Kafka Streams with exactly-once semantics, and databases with idempotent writes provide the application layer needed to approach exactly-once.

### 7. Reasoning challenge

You are designing an inventory reservation service for flash sales. One event `ReserveItem(user, item, qty)` must decrement stock once. Network is unreliable and retries are required.

Do you demand exactly-once delivery from the message bus, or at-least-once delivery with an idempotent consumer? What state do you need to store and for how long?

### 8. Key takeaway

* Delivery guarantees are about failure handling, not perfection.
* At-least-once is the practical default; exactly-once is an application-level property built on idempotence + deduplication.
* Prefer idempotent consumers over stronger broker guarantees.
* Decide based on cost of duplicate vs cost of lost message for your domain.
* Document your dedupe window and failure mode explicitly; it is part of the architecture.
