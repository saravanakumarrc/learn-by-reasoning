# NoSQL

> **Learning Path:** Data Architecture
> **Section:** 3.1.9 — Databases

**NoSQL**

### 1. The problem

Relational databases are excellent for transactional integrity. They break down when the constraints change:

* **Scale out, not up.** Write throughput and storage grow faster than a single node can handle, and you cannot just add disks forever.
* **Availability over strict consistency.** A global app needs to stay up during network partitions; waiting for a quorum is a downtime event.
* **Schema rigidity.** Product features ship weekly. Adding columns to a billion-row table is expensive and blocks deploys.
* **Access pattern mismatch.** You often need to fetch an entire user profile by ID, not join 5 tables.

The problem is not SQL. The problem is a single data model, single-node scaling, and strong consistency as defaults.

### 2. Mental model

NoSQL = *Not only SQL*. It is a family of data models optimized for specific access patterns, with horizontal scale and partition tolerance as first-class concerns.

Think of it as choosing the container for the data first, then the query language.

`flowchart LR
    Workload --> AccessPattern
    AccessPattern --> DataModel
    DataModel --> ConsistencyChoice
    ConsistencyChoice --> System[Key-Value | Document | Wide-Column | Graph]
```

Relational = row-oriented, schema-first, ACID-first.
NoSQL = model-first, scale-first, availability-first, consistency tunable.

### 3. How it works

The core mechanism is changing the trade-off surface:

* **Partitioned storage.** Data is sharded by key and spread across nodes. Reads/writes go to one shard, no cross-node joins.
* **Model specialization.**
  * Key-Value: get by key, fastest write path.
  * Document: JSON-like blob with nested fields, schema flexible.
  * Wide-Column: sparse tables, great for time series and large scans.
  * Graph: edges as first-class, traversal fast.
* **Eventual consistency.** Under partition, most NoSQL systems favor Availability + Partition tolerance from CAP, relaxing immediate consistency. Strong consistency is possible but costs latency and throughput.

The application owns more data modeling: denormalization, pre-aggregation, and access path design happen at write time.

### 4. Architectural reasoning

When it helps:
* High write volume and simple read patterns: session store, telemetry, counters.
* Heterogeneous or evolving schemas: user profiles, product catalogs, content.
* Global low-latency reads: you need local replicas.
* You can tolerate eventual consistency for reads.

Alternatives:
* Scale up relational with read replicas and sharding. Works until operational complexity explodes.
* NewSQL for strong consistency with horizontal scale. Good for financial ledgers.
* Object storage + search index for immutable blobs.

Decision rule: **Model the data to the query, not the query to the model.** If your primary access is `get(user_id) -> full profile`, a document store beats a normalized relational schema.

### 5. Trade-offs and failure modes

* **Consistency.** Eventual consistency means stale reads after writes. Architect with idempotency, version vectors, and conflict resolution. Failure mode: lost updates on concurrent writes to the same document.
* **Query flexibility.** No ad-hoc joins. You must pre-shape data for each access pattern. Failure mode: late-stage requirement for cross-entity analytics forces expensive scans or a separate warehouse.
* **Operational complexity.** You manage sharding keys, hot partitions, replication lag, and repair. A bad partition key creates a hot node. Failure mode: uneven data distribution under load.
* **Data integrity moves to app.** No foreign keys. You enforce invariants in code and pipelines. Failure mode: orphaned data and silent corruption.

### 6. Example

Global SaaS user profile service.

Requirement: 50k writes/sec of preferences, feature flags, and device metadata. 10M daily active users across regions. Schema changes weekly.

Choice: Document store sharded by `user_id`, with local replicas in 3 regions. Reads are `get(user_id)`. Writes are append-only with last-write-wins + version.

Relational would need cross-region replication, schema migrations, and join-heavy reads. NoSQL gives horizontal write scale, schema flexibility, and regional availability. Analytics are exported nightly to a warehouse.

### 7. Reasoning challenge

Your team wants MongoDB for a payments ledger because "we need fast writes and horizontal scale."

What is the architectural flaw, and what would you ask before deciding?

### 8. Key takeaway

* NoSQL solves scale, availability, and schema flexibility problems, not SQL problems.
* Choose the data model by access pattern; denormalize for reads.
* CAP forces a choice: most NoSQL picks AP; relational typically picks CP.
* You trade ad-hoc query power and strong consistency for write throughput, elasticity, and operational availability.
* Model correctness is now an application responsibility.
