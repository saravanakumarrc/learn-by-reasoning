# Read replicas

> **Learning Path:** Data Architecture
> **Section:** 3.2.7 — Data architecture

**Read replicas**

### 1. The problem

A single database primary can handle a limited amount of work. Writes are serializable and must go through one node. Reads also compete for the same CPU, I/O and network as writes.

When read traffic dominates, or when analytical/reporting queries run against the same instance that serves live transactions, you get:
* Read latency spikes from write contention
* Primary becomes the bottleneck for scale
* Long-running reads block or starve writes

You need more read capacity without adding write complexity.

### 2. Mental model

A read replica is a read-only copy of the primary that lags slightly behind.

Think of it as a newspaper printing press. One editor writes the master copy. Multiple presses print copies for distribution. Readers get the printed copies, not the editor's desk. The copies are eventually up to date, but not instantaneously.

Primary = source of truth for writes. Replicas = eventually consistent mirrors for reads.

### 3. How it works

The primary records every change as a write-ahead log. Replicas stream that log asynchronously and replay it locally.

```
flowchart LR
    Client[App] -->|writes| Primary[(Primary DB)]
    Client -->|reads| Replica1[(Read Replica 1)]
    Client -->|reads| Replica2[(Read Replica 2)]
    Primary -->|replication log / WAL| Replica1
    Primary -->|replication log / WAL| Replica2
```

The replica applies changes in order. Most systems offer physical or logical replication. The application routes reads to replicas and writes to primary. Routing can be done in the app, proxy, or driver.

### 4. Architectural reasoning

**When it helps**
* Read-heavy workloads: 80/20 or 90/10 read/write ratios
* Isolating analytical/reporting queries from OLTP
* Reducing read latency via geographic placement
* Offloading backups and long scans

**What it solves**
* Horizontal read scale without sharding writes
* Cheaper read capacity than scaling primary vertically
* Better availability for read traffic during primary load spikes

**Alternatives and why not always**
* Caching: great for hot data, but invalidation is hard and it doesn't help full scans
* Vertical scale: hits price and ceiling
* Sharding: solves writes too but adds complexity for transactions
* CQRS with separate read model: stronger separation but more engineering

Read replicas are the simplest way to get more read capacity with minimal code change.

### 5. Trade-offs and failure modes

* **Eventual consistency and lag.** A write to primary is not immediately visible on replicas. Typical lag is milliseconds to seconds. If a user writes then immediately reads, they may see stale data.
* **Read your own writes.** You must route the session's reads back to primary for a short window, or accept staleness.
* **Replica failure modes.** A replica can fall behind, fail to apply, or promote incorrectly. Promotion during failover can cause data loss if the primary diverged.
* **Write amplification.** Every write is sent to N replicas, increasing network and storage cost.
* **No write scale.** Replicas do not help write throughput. Write bottleneck remains on primary.
* **Operational complexity.** You now have to monitor lag, replication health, and decide which reads go where.

### 6. Example

E-commerce catalog and orders.

Writes: create order, update inventory, process payment -> primary only.
Reads: product listing, product detail, search suggestions, order history -> replicas.

The product catalog is read 100x more than written. Replicas in US-East and EU-West serve local users with lower latency. Reporting jobs run on a dedicated replica to avoid impacting checkout.

If a user just placed an order, the app reads order status from primary for 1-2 seconds to guarantee read-your-writes, then falls back to replica.

### 7. Reasoning challenge

You are architecting a fintech ledger. Balances must be accurate to the cent and users expect to see their deposit immediately after it lands. You have high read volume for balance checks and statements.

Would you serve balance reads from read replicas? If yes, how would you handle the read-your-writes requirement? If no, what is the cost?

### 8. Key takeaway

* Read replicas scale reads, not writes. They trade strong consistency for read capacity.
* Use them when read load dominates and slight staleness is acceptable.
* Design for lag: route recent writes to primary, tolerate eventual consistency, or use session pinning.
* Monitor replication lag as a first-class SLO; it is your consistency window.
* Replicas simplify read scale, they do not eliminate the need to think about consistency, failover, and cost.
