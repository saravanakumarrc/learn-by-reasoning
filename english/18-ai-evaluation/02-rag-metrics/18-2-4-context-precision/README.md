# Context precision

> **Learning Path:** AI Evaluation
> **Section:** 14.2.4 — RAG metrics

**Context precision**

### 1. The problem

RAG only works if the LLM sees the right information, not just more information.

In production you will see two failure modes from retrieval:
* **Under-retrieval:** The correct chunk is missing. The model hallucinates or refuses.
* **Over-retrieval:** You retrieve 10 chunks, 3 are relevant, 7 are noise. The model gets distracted, cost goes up, latency increases, and precision drops.

You need a way to know if your retriever is bringing *relevant* context, not just *similar* context. Recall tells you if you found the needles. Precision tells you if you also brought a lot of hay.

That is the architectural problem context precision solves: controlling noise entering the prompt.

### 2. Mental model

Think of retrieval as a filter before the LLM.

Precision@k = relevant retrieved / total retrieved

* High precision = most of what you put in the prompt helps answer the query.
* Low precision = you are paying tokens and attention for garbage.

Recall@k = relevant retrieved / all relevant in corpus

Precision and recall trade off. A permissive retriever raises recall but kills precision. An aggressive reranker raises precision but can kill recall.

You want enough recall to have an answer, then you want precision to keep the prompt clean.

### 3. How it works

Evaluation needs a ground truth of relevance for a set of queries.

```
flowchart LR
    Q[Query] --> R[Retriever]
    R --> C[Top-k Chunks]
    C --> J[Relevance Judge]
    J --> P[Precision@k]
```

The judge is human annotation or an LLM-as-judge with a clear rubric: Is this chunk necessary and sufficient to answer the query?

Precision@k = |{retrieved chunks that are relevant}| / k

Common variants:
* **Precision@5 / Precision@10:** How clean is your first retrieval window?
* **Context precision:** Often reported as precision averaged over queries.

This is not about answer quality. It is about input quality. A perfect answer can still be produced from noisy context, but you cannot trust it at scale.

### 4. Architectural reasoning

When it helps:
* Token budget is tight and cost matters. Every irrelevant chunk is wasted.
* The domain is noisy. Customer support, legal, medical docs contain many near-duplicates.
* You use a small context window or a model sensitive to distraction.

What it solves:
* Prevents prompt pollution. Fewer irrelevant chunks = less hallucination from conflicting facts.
* Makes reranking investments measurable. You can A/B test a cross-encoder vs. a BM25 boost.

Alternatives:
* **Increase k blindly.** Improves recall, destroys precision and cost.
* **Rerank aggressively.** Improves precision, risks losing recall.
* **Query expansion / hybrid retrieval.** Can improve both if done carefully.

Decision rule: Optimize precision first for high-stakes, high-cost queries. Optimize recall first for exploratory search, then filter.

### 5. Trade-offs and failure modes

* **Precision vs Recall.** You cannot maximize both. Raising the similarity threshold improves precision but misses paraphrased relevant chunks.
* **Judge quality.** LLM judges are cheap but can be biased toward surface similarity. Human judges are expensive but stable. Inconsistent judging makes precision numbers meaningless.
* **Chunking strategy interacts.** Small chunks increase precision potential but hurt recall for multi-hop queries. Large chunks raise recall but lower precision.
* **False precision.** A chunk can be topically related but not answer-bearing. Precision metrics that only check topic overlap overestimate real usefulness.
* **Distribution shift.** Precision measured on synthetic queries does not transfer to real user phrasing. You need live query logs.

### 6. Example

Enterprise support RAG with 2M help articles.

Retriever returns top-10 chunks per query. Baseline precision@10 = 0.3. Three of ten chunks are useful.

Cost: 10 chunks * ~500 tokens = 5k tokens per query, ~$0.02. With 1M queries/month that's $20k/month, 70% wasted.

You add a cross-encoder reranker, keep top-5. Precision@5 goes to 0.8. Recall@5 stays at 0.85 vs recall@10 of 0.92.

Architectural decision: Accept a 7% recall loss for 2.6x precision gain and 50% token reduction. Monitor answer correctness, not just precision.

### 7. Reasoning challenge

Your finance RAG has precision@10 = 0.6 and recall@10 = 0.95. Users complain about wrong numbers in answers. Latency SLA is 800ms. Reranking adds 120ms.

Do you increase k to 15, add a stricter reranker, or shrink chunks? What metric do you watch to know it worked?

### 8. Key takeaway

* Context precision measures noise entering the prompt, not answer quality.
* High precision reduces cost, latency, and distraction; high recall ensures coverage. You need both, tuned to the use case.
* Measure precision@k with a consistent relevance judge and track it alongside recall and downstream task metrics.
* Architectural wins come from reranking, better chunking, and query reformulation, not from retrieving more.
