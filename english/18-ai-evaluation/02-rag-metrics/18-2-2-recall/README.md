# Recall

> **Learning Path:** AI Evaluation
> **Section:** 14.2.2 — RAG metrics

**Recall in RAG**

### 1. The problem

A RAG system is only as good as what it feeds the LLM. The generator can be perfect, but if the retriever never surfaces the document that contains the answer, the answer will be wrong, incomplete, or hallucinated.

You get a question like *"What is our refund policy for digital goods bought in EU?"* The correct answer exists in 3 documents: policy_v2.md, eu_exceptions.md, and faq_refunds.md. If the retriever returns only policy_v2.md, the model can't answer correctly. If it returns 0 of them, it's guaranteed to fail.

The problem is not "how good is the LLM". It's "does retrieval cover the information needed to answer".

Constraints:
* Limited context window and token budget
* Latency SLA for retrieval + generation
* No way to know what is relevant without labels

### 2. Mental model

Think of recall as a fishing net, not a spear.

Precision asks: *of the docs you brought back, how many are useful?*
Recall asks: *of all the docs you needed, how many did you actually bring back?*

Recall@k = relevant docs in top k / total relevant docs for that query

High recall means you rarely miss a needed fact. Low recall means you systematically leave information out.

### 3. How it works

Evaluation requires ground truth. For a set of test queries you need a labeled set of relevant documents per query.

```
flowchart LR
Q[User Query] --> R[Retriever]
R --> TopK[Top-K Docs]
TopK --> G[LLM Generator]
G --> A[Answer]
TopK -- compare to --> GT[Ground Truth Relevant Set]
GT --> M[Recall@k]
```

In practice you measure:
* **Retrieval Recall@k**: does the retriever surface the gold documents?
* **Context Recall**: does the retrieved context contain all facts needed to answer the question? This is the RAGAS metric. It measures fact coverage, not just document overlap.

You cannot compute recall in production without labels, so you proxy it with human-reviewed samples, synthetic queries from your corpus, or downstream answer correctness.

### 4. Architectural reasoning

When does recall matter most?

* **High-stakes factual domains**: finance, medical, legal, compliance. Missing one exception clause is a failure.
* **Multi-hop questions**: need several documents to piece together an answer.
* **Low-tolerance for hallucination**: you prefer "I don't know" to a confident wrong answer.

When can you accept lower recall?

* Conversational summarization where some coverage is enough.
* Systems with a strong reranker and a generator that can ask clarifying follow-ups.

Architectural levers for recall:
* Increase k
* Hybrid retrieval: dense + sparse + BM25
* Query expansion and decomposition
* Reranker that is recall-oriented, not just precision-oriented

The decision is not "maximize recall". It's "what recall level is necessary for downstream correctness, and what is the cheapest way to get it".

### 5. Trade-offs and failure modes

* **Recall vs Precision vs Cost.** Raising k improves recall but adds noise. The LLM has to process more tokens, latency rises, cost rises, and precision drops. The generator can get distracted by irrelevant docs.
* **Recall vs Latency.** Hybrid search and larger k increase retrieval time. You may need async pre-fetching or caching.
* **Evaluation gap.** Recall measured on a static benchmark may not match real user queries. Distribution shift kills you.
* **False confidence.** High retrieval recall does not guarantee correct generation. The model can still misinterpret. Recall is necessary, not sufficient.

Common failure mode: optimizing retrieval recall alone. You get 20 documents, 3 relevant, 17 noisy. The model starts anchoring on irrelevant details and faithfulness drops.

### 6. Example

Enterprise support RAG with 2M tickets.

Initial setup: dense vector search, k=5. Recall@5 = 0.42. Answers are often partial.

Architectural change: hybrid retrieval + query expansion, k=12 then cross-encoder rerank to 6.

Result: Recall@12 = 0.81, effective Recall after rerank = 0.74. Latency +80ms, token cost +35%.

Decision kept k=12 for retrieval but reranked to 6 for generation. Recall improved enough to lift answer correctness from 61% to 84% in human eval, while keeping latency under SLA.

If they had just increased k to 20 without reranking, recall would be 0.88 but precision would collapse and faithfulness would drop.

### 7. Reasoning challenge

You have a customer support RAG with a 400ms p95 latency SLA. Current k=5 gives Recall@5 = 0.58 and p95 latency 310ms. Increasing k to 20 raises Recall@20 to 0.84 but adds 180ms retrieval time and doubles context tokens.

What do you change, and what do you measure to decide if the change is worth it?

### 8. Key takeaway

* Recall measures coverage of needed information, not quality of what you returned.
* In RAG, retrieval recall is the bottleneck for correctness. Fix it before tuning generation.
* Optimize recall first, then use reranking to restore precision and control cost/latency.
* You cannot monitor recall in production without labels; use sampled human review and synthetic query sets as proxies.
* High recall without precision creates noise that degrades faithfulness and increases cost.
