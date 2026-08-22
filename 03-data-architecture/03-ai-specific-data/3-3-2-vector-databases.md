# Vector databases

> **Learning Path:** Data Architecture
> **Section:** 3.3.2 — AI-specific data

## The problem

You can store documents in Postgres and search them with keywords. You can store vectors in Postgres too, but you can't ask it to find *meaningfully similar* items fast at scale.

When you build RAG, semantic search, or recommendation you stop caring about exact matches and start caring about *nearest neighbors* in embedding space. An embedding turns text, image, audio into a high-dimensional vector. Similarity becomes distance: cosine or L2.

The constraints that appear:
* **Scale:** Millions of vectors, each 768-4096 dims. Brute force scan = O(N*d) per query. Unusable.
* **Latency:** RAG needs <100ms retrieval to keep LLM response time acceptable.
* **Recall:** You need the top-k most similar, not perfect neighbors, but bad recall kills answer quality.
* **Hybrid needs:** You want semantic similarity *and* metadata filters: tenant_id, date, access control, price range.

That is the problem vector databases solve: fast approximate nearest neighbor search over embeddings with metadata filtering.

## Mental model

A vector database is an ANN index with a key-value store attached.

Think of it as a spatial index for meaning. Relational DBs index equality and ranges. A vector DB indexes *closeness*. You insert an ID + vector + metadata. You query with a vector and get the k closest IDs.

The core mental model is recall vs latency vs write cost. You are trading exactness for speed.

## How it works

1. Embeddings in: Text/image -> embedding model -> dense vector.
2. Indexing: Vectors are inserted into an approximate nearest neighbor structure. HNSW builds a layered graph for fast graph traversal. IVF partitions space into centroids and searches only promising partitions.
3. Query: Query vector goes through same index, graph walk returns candidate neighbors, exact distance re-ranked on top-k.
4. Metadata: Most systems store a row of metadata alongside the vector and apply a filter *before* or *after* ANN search. Filter-first reduces search space but can hurt recall.

That's it. No magic. The value is in tuned ANN, persistence, replication, and filtering.

```mermaid
flowchart LR
User[User Query] --> Embed[Embedding Model]
Embed --> Search[Vector DB ANN Search + Metadata Filter]
Search --> Retrieve[Top-k Chunks]
Retrieve --> LLM[LLM with Context]
LLM --> Answer
```

## Architectural reasoning

When it helps:
* RAG retrieval where semantic relevance beats keyword
* Recommendation: find similar users/items
* Anomaly detection on feature vectors

Alternatives and why you might not choose a vector DB:
* **Brute force FAISS in memory**: Great for batch offline, bad for multi-tenant, persistent, filtered serving.
* **Elasticsearch/OpenSearch with dense_vector field**: Works for hybrid keyword+vector up to ~few million vectors. Simpler ops if you already run ES. Degrades on high dim and strict filtering.
* **pgvector**: Fine for <1M vectors, single node, strong transactional needs. You pay Postgres latency and lack of purpose-built ANN scaling.
* **No vector store**: If you only need keyword search or exact lookup.

Decision rule: Choose a dedicated vector DB when you need high QPS ANN search with metadata filtering, horizontal scale, and managed persistence. Choose pgvector/ES when scale is modest and you value operational simplicity.

## Trade-offs and failure modes

* **Recall vs latency.** HNSW with higher ef_search gives better recall but more CPU/latency. Architects tune this per workload.
* **Write amplification.** Inserting vectors updates the graph/index. High ingest rates need sharding and backpressure. Vector DBs are read-optimized.
* **Stale embeddings.** Model drift or document updates require re-embedding and re-indexing. Without a pipeline, retrieval quality silently degrades.
* **Metadata filtering hurts ANN.** Filter-after search wastes work. Filter-before can prune too aggressively. The best systems push filters into the graph traversal.
* **Chunking matters more than index.** Bad chunk size/overlap = bad recall regardless of HNSW parameters. This is an upstream data problem, not a DB problem.
* **Cost.** ANN indexes are memory heavy. Expect RAM proportional to vector count * dim * 4 bytes. Sharding adds network hop latency.

## Example

Enterprise support RAG.

10M support articles chunked to 512 tokens, embedded with 1536-dim model. Queries need tenant-scoped results and recency bias.

Architecture: Ingest pipeline embeds chunks, writes to vector DB with metadata {tenant_id, article_id, chunk_id, created_at, language}. Query path: embed user question -> vector DB search with filter tenant_id = X AND created_at > 2023-01-01, top 20 -> re-rank with cross-encoder -> pass to LLM.

Vector DB chosen over Elasticsearch because recall on paraphrased questions was poor with BM25, and over pgvector because QPS target was 2k with 10ms p95. Sharding by tenant_id kept blast radius limited.

## Reasoning challenge

You have a 10M product catalog. Requirements: semantic search by description, filter by category, brand, price range, in-stock flag, and personalization by user purchase history. QPS 500, p95 <50ms.

Do you deploy a dedicated vector DB, use Elasticsearch with dense_vector, or a hybrid of both? What is your primary architectural risk and how would you mitigate it?

## Key takeaway

* Vector databases exist to make *similarity* a first-class query primitive at scale, not exact match.
* They are ANN indexes with metadata, not magic. Quality comes from embeddings, chunking, and filtering strategy as much as index choice.
* Choose them when you need fast, filtered ANN at scale with managed persistence. Otherwise prefer simpler stacks.
* Operate them around recall/latency tuning, embedding freshness, and sharding by tenant/workload to avoid hot partitions.
