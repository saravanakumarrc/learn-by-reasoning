# Indexing

> **Learning Path:** Data Architecture
> **Section:** 3.1.5 — Databases

### 1. The problem

A database that stores data in pages on disk cannot find a row by scanning the whole table forever.

With 10 rows, a full scan is fine. With 10 million rows, a full scan costs I/O, CPU, and latency for every query. The constraint is not the storage capacity, it's the cost of *finding*.

The problem gets worse with:
* ad-hoc filters on non-key columns
* range queries and ordering
* high read concurrency where many queries compete for the same scan

You need a way to answer "where is this data?" without reading everything.

### 2. Mental model

An index is a separate data structure that trades space and write work for faster reads.

Think of a book index: the text is the data, the index maps a term to page numbers. You don't read the whole book, you look up the term first.

In a database, an index maps a column value to the physical location of the row, typically the primary key pointer. The database first resolves the query through the index, then fetches only the needed data pages.

```mermaid
flowchart LR
    Q[Query: WHERE user_id = 42] --> I[Index Lookup O(log n)]
    I --> P[Row Pointer]
    P --> D[Data Page Fetch]
    Q -.-> FS[Full Scan O(n)]
```

### 3. How it works

The essential mechanism is ordering + pointer.

Most OLTP systems use a B-Tree or B+Tree: a balanced tree where leaf nodes are sorted by the indexed key and point to data rows. Lookup is O(log n) page reads instead of O(n) row reads.

A secondary index does not contain the whole row, just key → primary key. A covering index contains enough columns to satisfy the query without touching the table.

For non-relational needs the structure changes but the idea is the same:
* Inverted index for text: term → list of documents
* Vector index for embeddings: approximate nearest neighbor structure like HNSW/IVF to find similar vectors fast

The index is maintained by the storage engine on every write.

### 4. Architectural reasoning

Index helps when read selectivity is low and read volume is high.

Use it when:
* Queries filter, sort, or join on a column frequently
* Latency matters more than write throughput
* You need to enforce uniqueness

Don't use it when:
* The table is tiny or always scanned
* Writes dominate and reads are rare or sequential
* You can push filtering upstream, e.g. partition pruning

Alternatives to consider:
* Full scan + in-memory filter: acceptable for small, hot tables
* Partitioning / sharding: reduces scan size by narrowing the data set first
* Materialized view / pre-aggregation: trades freshness for read speed
* Denormalization / covering index: eliminates the join entirely

Decision is driven by access pattern, not by "make everything fast".

### 5. Trade-offs and failure modes

**Write amplification.** Every insert/update/delete must update all indexes. A table with 5 secondary indexes can be 5x more expensive to write.

**Storage and cache pressure.** Indexes consume disk and RAM. A hot index that doesn't fit in buffer pool creates more I/O.

**Choice sensitivity.** A composite index (a,b) helps WHERE a=? AND b=? but not WHERE b=? alone. Wrong column order creates unused indexes.

**Hotspots.** Range indexes on monotonically increasing keys, e.g. timestamp or UUID, cause write hotspots in distributed stores.

**Bloat and stale statistics.** After deletes/updates, B-Trees fragment. Optimizer picks bad plans if statistics are stale.

Failure mode to watch: adding indexes to "fix" slow queries in production without measuring write impact, leading to write latency spikes and lock contention.

### 6. Example

E-commerce order service. Table `orders` with 500M rows.

Common queries:
* `WHERE user_id = ? AND created_at >= ?` for user order history
* `WHERE status = 'paid' AND created_at < now() - 30 days` for retention job

Architecture:
* Primary key: `order_id`
* Composite secondary index: `(user_id, created_at DESC)` for user history. The index is also covering for user_id, created_at, total.
* Separate index on `status, created_at` for the retention job, or better, partition by `created_at` monthly and keep a partial index for `status='paid'`.

Result: user history goes from seconds of scan to a few index page reads. Retention job scans only recent partitions.

If writes were 100k TPS and reads were 5k TPS, you would limit secondary indexes and rely more on partitioning. If reads were 200k TPS, the extra indexes pay off.

### 7. Reasoning challenge

You are designing a real-time recommendation feed. Writes are 10k embeddings/sec, reads are 50k vector similarity queries/sec. Each query needs the top 10 nearest neighbors from a 200M vector collection.

Would you build a precise B-Tree index on the vector, an approximate HNSW index, or rely on brute force scan with GPU? What degrades first if traffic doubles: latency, recall, or write throughput? What would you monitor?

### 8. Key takeaway

* Indexing exists to avoid full scans by trading write cost and storage for read speed.
* The right index is defined by query pattern: selectivity, order, and columns needed.
* Every index has a cost: write amplification, storage, and operational complexity.
* Choose structure to the access pattern: B-Tree for exact lookups/ranges, inverted for text, approximate graph for high-dimensional similarity.
