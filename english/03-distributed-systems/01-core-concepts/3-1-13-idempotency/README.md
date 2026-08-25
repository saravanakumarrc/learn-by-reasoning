# Idempotency

> **Learning Path:** Distributed Systems
> **Section:** 2.1.13 — Core concepts

### The problem

You build a distributed API. Networks drop, services time out, load balancers retry.

A client sends `POST /payments`. The request reaches your service, the payment is created, but the response is lost. The client retries. Now you have two payments for one intent.

The root cause is not bad code. It is the mismatch between **at-least-once delivery** in distributed systems and **non-idempotent business operations**. Retries are a feature, not a bug. You need operations to survive being executed multiple times.

### Mental model

Idempotency means: applying the same operation N times has the same effect as applying it once.

Think `SET volume = 10` vs `INCREMENT volume`. Setting to 10 is idempotent. Incrementing is not. Run it twice and you get 12, not 10.

In distributed systems this is about *intent*, not *request*. The client’s intent is “create this payment once”. The system must make repeated requests for that intent collapse to a single effect.

### How it works

There are two ways to get idempotency.

**Natural idempotency.** Some operations are inherently idempotent. `GET`, `PUT /resource/id` with full replacement, `DELETE /resource/id`. Replaying them is safe.

**Artificial idempotency.** For non-idempotent operations like `POST /payments`, you make the intent addressable.

1. Client generates a stable idempotency key for the intent.
2. Service checks a deduplication store: *have I already processed this key?*
3. If yes, return the cached response. If no, process, store result + key, then return.

```mermaid
flowchart LR
    C[Client] -->|POST /payments {idempotencyKey: abc123}| A[API]
    A --> D[(Idempotency Store)]
    D -->|hit| A
    D -->|miss| A
    A -->|process once| P[Payment Service]
    A -->|store result| D
    A --> C
```

The key is the anchor. The first execution wins, retries are replayed.

Implementation is simple state: `key -> {status, response, created_at}`. Keys must be unique per intent, scoped to client + operation type. TTL prevents unbounded growth.

### Architectural reasoning

When does it help?
* Any API exposed to retries, timeouts, or at-least-once messaging.
* Write operations in payment, order creation, provisioning, money movement.
* Saga steps and outbox processors where messages can be redelivered.

Alternatives:
* **At-most-once**: drop retries. Loses reliability.
* **Exactly-once**: requires distributed transactions and global coordination. Impractical at scale.
* **Client-side deduplication**: fragile, doesn’t survive client crash.

Idempotency gives you *effectively once* without coordination. You keep retries for reliability, and you get safety from duplicates.

Decision rule: If the operation has side effects you cannot reverse cheaply, make it idempotent at the API boundary.

### Trade-offs and failure modes

* **Storage cost and lifetime.** You must store keys long enough for retries to stop, but not forever. Typical TTL 24h-7d. Lost store = lost dedupe.
* **Key design.** Key too broad = false collisions. Key too narrow = duplicates slip through. Scope by `client_id + operation + business key`.
* **Partial failure.** Process succeeds but store write fails. You may process twice. Make the check-store-process sequence atomic where possible, or accept a small window and make the business operation itself idempotent.
* **Non-idempotent reads.** Caching GET is safe, but using GET for mutation is not.
* **Distributed state.** The dedupe store must be strongly consistent for the same key. Use a single primary or a consistent hash. Cross-region replication adds latency.

The biggest failure mode is assuming idempotency is free. It shifts complexity from the network to state management.

### Example

Payment creation.

Client wants to charge $50. It sends:
```
POST /payments
Idempotency-Key: usr_42_order_991
{ amount: 50, ... }
```

First call: miss in store, create payment id `pay_123`, store `usr_42_order_991 -> pay_123`, return 201.

Timeout, client retries with same key. Service hits store, returns cached `pay_123` with 200. No double charge.

If the client generates a new key each retry, you will double charge. Idempotency is a contract between client and server.

### Reasoning challenge

You have `POST /orders` which creates an order and decrements inventory. Retries happen. You add an idempotency key. A request times out after the order is created but before inventory is decremented. The retry hits the dedupe store, returns the cached order, but inventory is still not decremented.

Is the operation idempotent? What would you change?

### Key takeaway

* Idempotency exists to make retries safe in unreliable networks.
* It is about *intent identity*, not request identity. Use stable keys.
* Prefer naturally idempotent designs; add artificial idempotency at the boundary for non-idempotent writes.
* The cost is state: you must store and expire idempotency keys correctly, and reason about partial failures.
* You are not guaranteeing exactly-once; you are guaranteeing at-most-once effect per intent.
