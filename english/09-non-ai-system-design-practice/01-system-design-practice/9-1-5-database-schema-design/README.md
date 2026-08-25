# Database schema design

> **Learning Path:** Non-AI System Design Practice
> **Section:** 25.1.5 — System design practice

**Database schema design**

### 1. The problem
A schema is a long-lived contract. You are not just storing data, you are committing to how that data will be written, read, joined, indexed, migrated, and partitioned for years.

The problem appears when query patterns diverge from write patterns. A normalized model makes writes cheap and consistent, but reads require joins. A denormalized model makes reads fast, but writes become expensive and error-prone. Change the schema later and you pay migration cost, downtime, and application churn.

Schema design is therefore the decision about *what shape of data you can afford to maintain* under your constraints.

### 2. Mental model
Think of the schema as two layers:

* Logical schema: entities and relationships you want to enforce.
* Physical schema: how those entities are stored, indexed, partitioned to satisfy access patterns.

Good design starts with reads. Write the queries you must support, then derive the minimal data shape that satisfies them with acceptable consistency and cost.

### 3. How it works
The essential mechanism is trade-off between normalization and denormalization, guided by access patterns.

Normalization reduces redundancy and preserves integrity via FKs, 1NF-3NF. Good for transactional domains where writes dominate and correctness matters.

Denormalization duplicates data, pre-joins, materializes views. Good for read-heavy domains where latency and throughput matter more than write purity.

Physical design adds indexes, partition keys, and distribution. An index is a separate data structure with its own write cost. A partition key determines data locality and hot-spot risk.

```mermaid
flowchart LR
    App[Application Writes] -->|shape data| Schema[Logical Schema]
    Schema -->|maps to| Physical[Physical Layout: Tables/Indexes/Partitions]
    Physical -->|serves| Reads[Read Queries]
    Reads -->|feedback| App
```

### 4. Architectural reasoning
Design from constraints, not purity.

* **Workload**: OLTP vs OLAP. High write QPS favors narrow tables and minimal joins. High read QPS favors wide, pre-aggregated tables.
* **Consistency needs**: Financial transactions need strong consistency and normalized integrity. Product catalogs can tolerate eventual consistency and denormalization.
* **Scale**: Row size, cardinality, and growth rate drive partition strategy. Choose partition key for even distribution and locality of related reads.
* **Evolution**: Will you need to add fields, split entities, or change types? Design for additive change. Avoid monolithic tables that become migration bottlenecks.

Alternatives you are choosing between:
Normalized relational for correctness and flexible ad-hoc queries.
Denormalized relational/document for read performance and schema flexibility.
Separate read models via CQRS when read and write patterns are fundamentally different.

### 5. Trade-offs and failure modes
* **Normalization vs performance.** Joins cost latency and CPU. Denormalization saves reads but creates write amplification and consistency bugs.
* **Flexibility vs safety.** Schemaless stores allow fast iteration but push validation into application code, increasing bugs.
* **Partitioning.** Wrong partition key = hot partitions and cross-partition queries. Right partition key = good locality but can make some queries scatter.
* **Index bloat.** Every index speeds a read and slows a write. Over-indexing kills write throughput and increases storage cost.

Common failures:
Schema lock-in where a table becomes a "kitchen sink". Migration requires downtime.
Hot key on a single partition/row.
Implicit N+1 reads because the model was designed for writes only.
Changing a primary key or partition key later is essentially a rewrite.

### 6. Example
SaaS billing system.

Write path: create subscription, change plan, record invoice. Needs ACID, foreign keys to customers, plans, prices.

Read path: dashboard shows MRR, churn, invoices per customer, and real-time usage.

Decision: Keep transactional core normalized: `customers`, `subscriptions`, `invoices`, `line_items` with FKs.

Create separate read models: `customer_mrr_summary` materialized view updated asynchronously, and a denormalized `invoices_read` table with customer name and plan name pre-joined.

Partition `invoices` by `invoice_date` month. Index `subscriptions(customer_id, status)`. This gives correct writes and fast analytical reads without joining the whole transactional history.

### 7. Reasoning challenge
You have a social feed service. Writes are 10k/s of new posts. Reads are 100k/s of personalized feeds. The current normalized schema requires 3 joins per feed request and latency is spiking.

What do you change in the schema and why? What new failure mode do you introduce?

### 8. Key takeaway
* Schema design is query-first architecture, not normalization-first.
* Optimize for the dominant access pattern, not theoretical purity.
* Physical design decisions are distribution and index decisions, not just logical tables.
* Every denormalization buys read speed at the cost of write complexity and consistency risk.
* Design for evolution: additive changes, partition keys you can live with, and a clear boundary between transactional and analytical models.
