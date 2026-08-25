# Retrieval evaluation

> **Learning Path:** AI Evaluation
> **Section:** 14.1.8 — Evaluation

### 1. The problem

In RAG and agent systems the generator is only as good as what it receives. A great LLM will confidently hallucinate if the retriever returns irrelevant or incomplete context. End-to-end evaluation hides this: a bad answer can be caused by bad retrieval *or* bad generation, and a good answer can mask a brittle retriever.

You need to isolate the retriever and ask: does it surface the right documents for a given query, in the right order, under realistic query distribution? Without that, you cannot improve the system safely.

### 2. Mental model

Retrieval evaluation is the gatekeeper test for RAG.

Think of it as a precision/recall audit for the first hop in your pipeline. The retriever has two jobs: find relevant chunks and rank them so the top-k are useful. Evaluation measures how well it does that independent of the LLM.

### 3. How it works

You need three things: queries, a corpus, and relevance judgments.

**Offline evaluation**
* Build a test set of queries representative of production. Use real logs or synthetic queries generated from documents.
* For each query, define ground truth: which documents are relevant. This is `qrels`. Human annotated is gold. Synthetic with LLM-as-judge is cheaper but biased.
* Run the retriever, get top-k results, compare to qrels.

Core metrics:

* **Hit Rate / Recall@k**: Is at least one relevant doc in top-k? Does the retriever find *all* relevant docs in top-k? Measures coverage.
* **Precision@k**: Of the top-k returned, how many are relevant? Measures noise.
* **MRR / Reciprocal Rank**: How far down is the first relevant doc. Matters when you only use one doc.
* **nDCG@k**: Rewards relevant docs higher up and accounts for graded relevance. Best for ranking quality.

```mermaid
flowchart LR
    Q[Query Set] --> R[Retriever]
    R --> TopK[Top-K Docs]
    TopK --> Compare[Compare to Qrels]
    Corpus --> R
    Qrels --> Compare
    Compare --> Metrics[Recall@k, Precision@k, nDCG@k, HitRate]
```

**Online evaluation**
Log production queries, sample retrievals, and get human or implicit signals: click-through, citation usage, follow-up query reformulation. Offline metrics correlate but do not equal user satisfaction.

### 4. Architectural reasoning

When it helps:
* Before changing embedding model, chunking strategy, or hybrid weighting.
* When you need a regression test for the retrieval layer.
* When you want to decide k, reranker threshold, or hybrid alpha.

What it solves: It gives you a fast, cheap signal to iterate on retrieval without running expensive LLM generation and human review for every change.

Alternatives:
* End-to-end eval only: cheaper to build, but you cannot attribute failure.
* Human review of final answers only: high fidelity, low coverage, slow.

Decision rule: Evaluate retrieval offline continuously, and evaluate end-to-end with real users periodically. The retriever metrics are leading indicators; end-to-end is lagging.

### 5. Trade-offs and failure modes

* **Human qrels vs synthetic**: Human is accurate and expensive, slow to scale. Synthetic LLM judges are cheap but can share biases with your generator and overfit to the judge model.
* **Relevance definition**: Binary relevant/not relevant is easy but misses nuance. Graded relevance is better but harder to annotate consistently.
* **Metric mismatch**: High Recall@10 does not guarantee the LLM can use the docs. Long, noisy chunks can hurt generation even if they are technically relevant.
* **Distribution shift**: Test queries from last quarter may not match current user intent. Retrieval performance degrades silently as corpus grows.
* **Chunking coupling**: Changing chunk size changes both retrieval and relevance judgments. You must freeze chunking when evaluating embedding changes, or re-annotate.

Common failure: Optimizing for nDCG@10 in isolation while k you actually feed to LLM is 3. Rank quality beyond the used k is wasted compute.

### 6. Example

Enterprise support RAG with 2M KB articles, hybrid BM25 + embeddings, reranker, k=5 fed to LLM.

You suspect the new embedding model improves semantic match. You freeze chunking and hybrid weights.

You create a test set of 500 real support tickets with human-annotated relevant articles. Offline run shows Recall@5 improves from 0.61 to 0.73 and nDCG@5 from 0.54 to 0.68. You ship.

Two weeks later, online logs show higher citation usage and 12% fewer follow-up clarifications. Retrieval evaluation predicted the lift. If you had only measured end-to-end answer quality, the LLM's stochasticity would have obscured the gain for weeks.

### 7. Reasoning challenge

You have a RAG system with tight latency budget. You can either increase k from 3 to 8 to improve Recall, or keep k=3 and add a cross-encoder reranker.

Your offline test set shows Recall@3 = 0.55, Recall@8 = 0.78. With reranker, Recall@3 improves to 0.71 at +40ms latency.

Which change do you test first, and what retrieval metric would you monitor to know if it is actually helping the LLM? What risk are you accepting?

### 8. Key takeaway

* Retrieval quality is a prerequisite for generation quality. Evaluate it separately.
* Offline metrics with qrels give fast iteration; online signals give truth.
* Optimize for the k you actually consume, not for leaderboard k.
* Relevance judgments are the bottleneck. Invest in a maintainable, sampled human annotation process and treat synthetic judges as approximations.
* Monitor retrieval metrics continuously as a regression suite for embeddings, chunking, and hybrid weights.
