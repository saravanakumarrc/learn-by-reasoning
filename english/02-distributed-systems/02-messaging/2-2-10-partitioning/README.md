# Partitioning

> **Learning Path:** Distributed Systems
> **Section:** 2.2.10 — Messaging

**The problem**

A single logical message stream hits a wall. One queue can only be read by one consumer at a time, or with competing consumers it serializes work. Throughput plateaus, latency grows, and a slow consumer drags everyone.

You also want ordering. If events for the same entity must be processed in order — e.g., `OrderCreated -> OrderPaid -> OrderShipped` — you cannot just hand them to any worker arbitrarily.

You need both parallelism *and* per-entity ordering.

**Mental model**

Think of a post office sorting room. One central conveyor is a bottleneck. Add multiple lanes, each lane preserves order of letters inside it, and you can have multiple workers process lanes in parallel.

A partition is a lane. Messages go to a lane via a deterministic rule, and a consumer group assigns workers to lanes. Ordering is guaranteed *within* a lane, not across lanes.

**How it works**

A topic is a set of ordered, immutable partitions. Producers write to a partition chosen by a partitioner, typically `hash(key) % num_partitions`.

```mermaid
flowchart LR
    P[Producer] --> R[Partitioner hash(key)]
    R --> A[(Partition 0)]
    R --> B[(Partition 1)]
    R --> C[(Partition 2)]
    A --> G[Consumer Group]
    B --> G
    C --> G
```

Each partition has a head and a tail, an offset log. Consumers in a group cooperatively own partitions. One consumer per partition at a time. Scale consumers -> scale partitions -> more parallelism.

The key design choice is the partition key. Messages with the same key always land on the same partition, preserving order for that entity.

**Architectural reasoning**

Partitioning solves throughput and decoupling while keeping ordering where it matters.

Use it when:
* You have high publish/subscribe volume that exceeds one broker thread
* Consumers process at different speeds and you need independent scaling
* You need replayability and durability per partition
* You need ordering per business entity, not globally

Alternatives:
* Single queue with more powerful consumer: hits single-threaded limit, no parallelism
* Sharding by service instance: pushes partitioning logic to clients, hard to rebalance
* No partitioning, just unordered parallel processing: loses per-entity ordering guarantees

Partitioning lets you trade global ordering for scalable per-key ordering.

**Trade-offs and failure modes**

* Ordering scope. Guaranteed within partition only. If you need global ordering you lose partitioning benefits.
* Hot partitions. A bad key distribution creates skew. One partition becomes a bottleneck while others are idle. UserId=1 generating 50% of traffic is a classic failure.
* Rebalancing cost. Adding partitions or consumers causes group rebalance, temporary pause in processing and offset commit storms.
* Consumer lag divergence. Partitions process unevenly, making end-to-end latency hard to reason about.
* Key choice is sticky. Changing partition key requires backfill or dual write.

Operational pain points: uneven load, partition leader failure in replicated systems, and the temptation to increase partition count late, which is expensive.

**Example**

E-commerce order events. Topic `orders` with 12 partitions, key = `order_id`.

Producers emit `OrderCreated`, `OrderPaid`, `OrderShipped`. All events for order `12345` hash to partition 7, so they are consumed in order by one consumer instance. A consumer group with 12 instances processes all orders in parallel, ~12x throughput of a single queue.

If you later need 24 instances, you scale partitions to 24 and expand the group. You don't redesign the pipeline.

**Reasoning challenge**

You are designing a user activity feed service. Events: `PageView`, `Like`, `Comment`. Requirements:
1. Process events for a given user in order to build correct feed state
2. Support 10x traffic spikes for a viral user
3. Keep overall latency low

Would you partition by `user_id`, by `event_type`, or by `user_id + event_type`? What happens to a viral user under each choice, and what is the ordering guarantee you actually need?

**Key takeaway**

* Partitioning exists to get parallelism without losing per-entity ordering.
* Order is per partition, not global. Choose partition key to define the ordering boundary.
* Scale throughput by adding partitions and consumers, not by making a single queue faster.
* The main risks are hot keys, rebalancing churn, and the cost of changing partition count/key later.
