# Scaling strategies

> **Learning Path:** Non-AI System Design Practice
> **Section:** 25.1.6 — System design practice

**Scaling strategies**

### 1. The problem

Traffic doesn't grow linearly. It grows in spikes, by region, by feature. A system that works at 1k RPS fails at 10k RPS not because the code is bad, but because a single resource becomes the bottleneck.

The constraint is: **You must increase capacity without increasing failure probability or cost disproportionately.**

### 2. Mental model

Scaling is about moving work away from a single point of contention.

Think of a restaurant. One chef can only make so many dishes. You can:
* Give the chef a bigger kitchen and better knives = scale up
* Hire more chefs and split orders = scale out
* Pre-make popular dishes and keep them hot = cache
* Take orders first, cook later = async

The decision is which bottleneck you are hitting, and what kind of state you have.

### 3. How it works

Core strategies map to bottlenecks:

**Scale Up vs Scale Out**
* Scale Up: bigger instance, more CPU/RAM. Simple, no code change.
* Scale Out: more identical instances behind a load balancer. Requires statelessness.

**Partitioning / Sharding**
Split data by key so no single node holds all load. `user_id % N` → shard. Write scales with N, reads can be localized.

**Replication**
Read replicas for read-heavy workloads. Primary for writes. Eventually consistent reads are cheaper.

**Caching**
Move read load out of the system of record. Cache at edge, app, or database. Hit rate determines savings.

**Async / Queue**
Decouple producer and consumer. Absorbs bursts and lets slow consumers scale independently.

```mermaid
flowchart TD
    LoadIncrease --> CanVertical? -->|Yes, cheap & short term| ScaleUp
    CanVertical? -->|No| ScaleOut
    ScaleOut --> Stateless? -->|Yes| AddInstances LB
    Stateless? -->|No| PartitionOrShard
    PartitionOrShard --> Hotspot? -->|Yes| RebalanceKeys
    PartitionOrShard -->|No| ReplicateReads
```

### 4. Architectural reasoning

When it helps:
* Scale up helps when you are CPU/memory bound and need immediate relief, and you have no state.
* Scale out helps when you can make services stateless and want linear cost.
* Partitioning helps when data size or write throughput exceeds single node limits.
* Replication helps when read:write ratio is high.
* Caching helps when reads are repetitive and tolerates staleness.
* Async helps when latency is not critical end-to-end and you need backpressure.

Alternatives to consider: Optimize first. A 10x query improvement is cheaper than 10x nodes. Then scale.

Decision flow: Identify bottleneck → Is it compute, storage, or coordination? → Is state tied to instance? → Can you tolerate latency/consistency loss?

### 5. Trade-offs and failure modes

* **Scale Up:** Ceiling exists. Hardware maxes out. Single point of failure. Downtime for upgrade.
* **Scale Out:** Network and coordination overhead. Session affinity breaks. Cost of idle capacity.
* **Sharding:** Hot partitions kill scaling. Rebalancing is painful. Cross-shard transactions are expensive.
* **Replication:** Write amplification. Replication lag causes stale reads. Split-brain risk.
* **Caching:** Cache invalidation and thundering herd on miss. Extra consistency complexity.
* **Async:** Increases end-to-end latency. Adds operational complexity of queues and dead-letter handling.

Most real failures: scaling one layer while another remains a bottleneck. You scale app servers but DB connection pool saturates. You shard but forget the single primary.

### 6. Example

E-commerce checkout during flash sale.

Initial design: Monolith + single Postgres. At 5k concurrent users, DB CPU saturates, writes queue.

Reasoning: Writes are not partitionable by user? They are. Reads are product catalog, mostly read-only. Payment is latency sensitive, inventory is not.

Architecture:
* Stateless API tier scaled out behind LB with autoscaling on CPU.
* Product catalog read from Redis cache with 60s TTL, fallback to read replica.
* Orders sharded by `user_id % 16` across Postgres shards. Writes go to primary shard.
* Inventory decrement and email sent via Kafka. Checkout returns fast, eventual consistency acceptable for inventory.
* Rate limiter at edge to protect DB.

Result: Write capacity grows with shards, read capacity grows with cache+replicas, bursts absorbed by queue.

### 7. Reasoning challenge

You have a real-time chat service. 10M users, messages per second growing 20% month over month. Each message must be delivered to all participants in a room, and room membership changes frequently. Current single Redis holds room state and fan-out. Latency SLA is <100ms.

Where is the bottleneck likely to appear first, and which scaling strategy do you reach for? What new failure mode does it introduce?

### 8. Key takeaway

* Scale to the bottleneck, not to the hype. Measure first.
* Stateless = scalable. State = you must partition or replicate it.
* Horizontal scaling buys elasticity but costs coordination complexity.
* Caching and async are scaling strategies, not just optimizations.
* Every scaling decision trades consistency, latency, cost, and operability.
