# Parent-child retrieval

> **Learning Path:** RAG Architecture
> **Section:** 8.1.18 — Learn

**Parent-child retrieval**

### 1. The problem

RAG needs two conflicting things at once:
* **Retrieval needs granularity.** A query like "What is the refund window for premium subscriptions?" is best matched against a small 200-500 token chunk, not a 10k token support article.
* **Generation needs context.** Answering correctly requires the full section, definitions, caveats, and the original wording. A single chunk is often truncated and incoherent.

If you embed the whole document, you get poor recall. If you embed tiny chunks, you get good recall but bad answers because the LLM has no surrounding context.

Parent-child retrieval decouples *what to find* from *what to read*.

### 2. Mental model

Think of a book with an index.

Children = index cards with a short excerpt and an embedding.
Parent = the actual page/section of the book they came from.

You search the index cards for relevance, then you pull the full pages for those cards to give the LLM complete context.

### 3. How it works

Ingestion:
Document -> split into overlapping chunks -> each chunk is a child node with its own embedding
Store: child.embedding, child.text, child.parent_id -> parent.document_id, parent.full_text

Retrieval:
Query -> embed query -> ANN search over children -> top k children
Aggregate unique parent_ids from those children -> fetch parent documents
Optionally re-rank children within each parent, then return full parent text to LLM

```mermaid
flowchart LR
    DOC[Source Document] --> CHUNK[Chunk into children]
    CHUNK --> EMB[Embed children]
    EMB --> VDB[(Vector DB)]
    DOC --> PARENT[Parent record with parent_id]
    PARENT --> DOCSTORE[(Doc Store]

    QUERY[User Query] --> QEMB[Embed Query]
    QEMB --> VDB
    VDB --> CHILD[Top K Children]
    CHILD --> PARENTIDS[Unique parent_ids]
    PARENTIDS --> DOCSTORE
    DOCSTORE --> PARENTS[Full Parent Docs]
    PARENTS --> LLM[LLM Generation]
```

### 4. Architectural reasoning

When it helps:
* Long documents where queries target small parts but answers need surrounding context: policies, contracts, support KBs, research papers.
* You need high recall on specific facts without sacrificing coherence.

What it solves:
* Small chunks improve embedding discrimination and recall.
* Parent fetch preserves document-level context, structure, and citations.

Alternatives:
* **Whole doc retrieval.** Simple, but recall drops for long docs and vector DB token limits are hit.
* **Chunk-only retrieval.** Good recall, bad generation quality and hallucinated stitching.
* **Hybrid with metadata filtering.** Helps but doesn't solve context loss.
* **Summarization + retrieval.** Creates a separate summary layer; adds latency and drift.

Choose parent-child when you have a clear parent-child relationship in the data and the cost of storing and joining is acceptable.

### 5. Trade-offs and failure modes

* **Latency.** Two-step retrieval: vector search + parent fetch. Mitigate with pre-join cache or fetching parents in parallel.
* **Storage and indexing cost.** You store embeddings for many children plus the parent documents. ~2-5x storage vs whole doc.
* **Parent explosion.** If you aggregate parents naively, 10 children from the same doc can return the same 10k token parent 10 times. Deduplicate by parent_id and cap tokens.
* **Chunking sensitivity.** Bad chunk boundaries create children that are meaningless on their own and misleading for retrieval. Overlap and semantic chunking matter.
* **Stale links.** On document update you must re-chunk and re-link all children. Versioning and orphan cleanup are operational concerns.
* **Re-ranking complexity.** Child score != parent score. You typically re-rank parents by max/mean child score.

### 6. Example

Enterprise support RAG.

Parent = full KB article "Premium Subscription Refund Policy v3", ~4k tokens.
Children = 12 chunks: eligibility, time window, exceptions, process steps, etc.

User asks: "Can I get a refund after 30 days if I upgraded?"

Vector search finds child #7 "exceptions for upgrades" with high similarity. Parent fetch returns the whole article. LLM can cite the relevant paragraph and also see the definition of "upgrade" from the intro and the process steps.

Without parent-child, either the whole article is retrieved with low relevance, or only the 250 token exception chunk is retrieved with no definition of upgrade.

### 7. Reasoning challenge

You have a 2M document corpus of legal contracts averaging 15k tokens each. Queries are highly specific clause lookups, but answers must include the full clause plus the surrounding definitions section for legal correctness.

Would you use parent-child retrieval, and if so, how would you define parent and child boundaries? What is your biggest operational risk?

*Think about chunk size for retrieval, token budget for generation, and update frequency.*

### 8. Key takeaway

* Retrieval granularity and generation context are separate problems. Parent-child retrieval lets you optimize each independently.
* Embed small children for recall, return large parents for coherence.
* The pattern trades storage and latency for better relevance and answer quality on long documents.
* Success depends on good chunking, parent deduplication, and a clear update strategy for the parent-child link.
