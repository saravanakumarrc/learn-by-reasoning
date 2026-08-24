# Precision

> **Learning Path:** AI Evaluation
> **Section:** 14.2.1 — RAG metrics

### The problem

In RAG you retrieve first, then generate. The generator can only be as good as the context you give it.

The problem appears when you increase top-k to improve coverage. You get more recall, but you also inject noise: irrelevant chunks, off-topic passages, contradictions. That noise increases token cost, latency, and hallucination risk. The model starts attending to wrong information.

You need a way to know: of the documents I actually fed the LLM, how many were useful? That's precision.

### Mental model

Precision is a retrieval quality filter.

Precision@k = relevant retrieved / total retrieved in top k

Think of it as signal purity of the context window you hand to the model. High precision means almost every chunk you pass is on point. Low precision means you are paying for and forcing the model to read junk.

It is not about whether you found *all* relevant docs. That's recall. Precision is about *waste*.

### How it works

You need a relevance judgment for each retrieved doc. In practice:

1. Ground truth relevance is defined per query. For evaluation you use human labels, LLM-as-judge, or a gold set.
2. For each query, retrieve top k docs.
3. Count True Positives = retrieved docs that are relevant. False Positives = retrieved docs that are irrelevant.
4. Precision@k = TP / (TP + FP)

Common variants:
* **Precision@1:** Is the first retrieved doc relevant? Critical for single-pass RAG where you only use one chunk.
* **Precision@k:** Purity of the whole context set.
* **Mean Precision:** average across queries.

In RAG pipelines precision is measured at the retriever stage, before generation. You can also measure precision of the reranker output.

```mermaid
flowchart LR
    Q[User Query] --> R[Retriever top-k]
    R --> J[Relevance Judge]
    J --> P[Precision@k = Relevant / k]
    P --> D[Decision: k, rerank, filter]
```

### Architectural reasoning

Precision helps you decide how to trade context quality for coverage.

When it helps:
* **High cost per token / strict latency.** You want a small, clean context window. High precision@3-5 beats low precision@20.
* **Sensitive domains.** Finance, legal, medical. One irrelevant chunk can cause a bad citation. You want purity over completeness.
* **Reranker gating.** You retrieve 100, rerank to 10, then filter to 3-5. Precision tells you if the reranker is actually cleaning signal.

What problem it solves: It quantifies noise injection into generation. It gives you a measurable target for retriever tuning.

Alternatives and why you might choose them:
* **Recall@k:** Use when missing a relevant doc is catastrophic, e.g., compliance search where you must surface all sources. You will accept noise.
* **nDCG / MAP:** Use when relevance is graded, not binary. Better for ranking quality overall.
* **Generation metrics like faithfulness:** Use when you care about final answer correctness, not just retrieval.

Decision pattern: Start with precision@5 as a guardrail for context purity, then tune recall@k for coverage. Most production RAG systems optimize for high precision in the final context set, and high recall in the candidate pool before reranking.

### Trade-offs and failure modes

* **Precision vs Recall.** Increasing k raises recall but drops precision. A reranker improves precision at the cost of latency and compute.
* **Precision vs Cost.** High precision means smaller k, lower token cost and lower latency. Low precision forces you to pay for irrelevant context.
* **Annotation definition.** Precision is only as good as relevance labels. If relevance is defined too narrowly, you penalize useful but partial matches. If defined too loosely, precision looks artificially high.
* **Position bias.** Precision@k treats all k equally. In practice, doc 1 matters more than doc k. Use Precision@1 for first-hit critical flows.
* **Evaluation drift.** LLM-as-judge for relevance can be inconsistent. Human labels are gold but expensive. Your precision number can shift with judge.

Failure mode: Optimizing precision@k alone leads to over-filtering. You get a clean but empty context window and the model hallucinates because it has no signal. You need both precision and recall in the pipeline: recall in the candidate pool, precision in the final context.

### Example

Enterprise support RAG for internal KB.

Query: "How do I refund a partial order in EU?"

Retriever top-20 returns 8 relevant docs, 12 irrelevant.
Reranker top-5 returns 4 relevant, 1 irrelevant.

Precision@20 = 0.40. Precision@5 = 0.80.

Architectural decision: Use retriever with high recall, then a cross-encoder reranker, then a precision gate: only pass top 3 docs with reranker score > 0.7 to LLM. This keeps precision@3 ~0.9, token cost low, and citation accuracy high. Recall is preserved in the 20 candidate pool for debugging.

If precision@3 drops below 0.7 in A/B test, you increase reranker threshold or add query expansion, accepting higher latency.

### Reasoning challenge

You have a customer-facing RAG chatbot. Current config: retriever top-50, reranker to 10, LLM uses all 10. Precision@10 = 0.5, Recall@10 = 0.85. Latency is 1.2s, token cost is high, and users complain about irrelevant citations.

Do you decrease k to 5, increase reranker threshold, or add a post-retrieval filter? What metric do you watch to avoid hurting coverage?

### Key takeaway

* Precision measures purity of the context you actually give the LLM, not how much you found.
* High precision reduces noise, hallucination, token cost and latency; it is the primary lever for safe generation.
* Architect for recall in the candidate pool and precision in the final context window via k, reranking, and score gating.
* Never optimize precision alone. Pair it with recall and generation quality to avoid over-filtering.
