# Context recall

> **Learning Path:** AI Evaluation
> **Section:** 14.2.5 — RAG metrics

## The problem

A RAG system is two systems glued together: retrieve documents, then generate an answer conditioned on them. An LLM can hallucinate even with perfect context, and it can be perfect even with bad context. If you only measure final answer quality you cannot tell *why* it failed.

The architect's problem is attribution. Is the bad answer caused by retrieval missing the right information, retrieving irrelevant noise, or the generator failing to use what was retrieved? Without separation you cannot decide whether to improve embeddings, re-ranking, chunking, prompt, or model size.

Constraints are real: human evaluation is gold but too slow and expensive for CI/CD; automated metrics are cheap but can be gamed; latency and cost budgets limit how much retrieval you can do.

## Mental model

Think of RAG evaluation as instrumentation at three seams:

`Query -> Retrieval -> Context -> Generation -> Answer`

Metrics must answer three questions:
1. Did we find the right information?
2. Was the right information presented cleanly to the model?
3. Did the model use it correctly to satisfy the user?

Retrieval quality is independent of generation quality, but they interact. Bad retrieval can poison a good generator. Good retrieval cannot save a generator that ignores context.

## How it works

**Retrieval metrics** measure the first seam.
* Recall@K / Hit Rate: is the gold document in top K?
* MRR / NDCG: how high is it ranked?
These tell you embedding, chunking, and index health.

**Context quality metrics** measure what the generator actually sees.
* Context Precision / Context Recall: of the retrieved chunks, how many are relevant and how much of the relevant information is covered?
* Context Relevance: noise ratio. Too much noise dilutes attention.
These bridge retrieval and generation.

**Generation groundedness metrics** measure faithfulness to context.
* Faithfulness / Groundedness: does each claim in the answer have support in retrieved context?
* Answer Relevancy: does the answer address the query, independent of context?
* Correctness / Factuality vs ground truth when available.

**End-to-end system metrics** measure user outcome.
* Latency P95, tokens per query, cost per query
* User acceptance, task completion, escalation rate

Offline evaluation uses synthetic or labeled query sets. Online evaluation uses production logs with human rating sampling.

```mermaid
flowchart LR
    Q[User Query] --> R[Retriever]
    R --> C[Context]
    C --> G[Generator]
    G --> A[Answer]
    R -.-> M1[Recall@K, MRR]
    C -.-> M2[Context Precision/Recall]
    A -.-> M3[Faithfulness, Relevancy]
    A -.-> M4[Latency, Cost, User Signal]
```

## Architectural reasoning

When it helps: any RAG system that ships to users and must be improved iteratively. Metrics let you A/B test retriever changes without waiting for human review.

What problem it solves: attribution and prioritization. If Context Recall is high but Faithfulness is low, invest in prompting / grounding, not retrieval. If Recall@K is low but Context Precision is high, invest in embeddings / hybrid search / chunking.

Alternatives: pure LLM eval with BLEU/ROUGE. These measure surface similarity, not groundedness, and fail for RAG where phrasing varies. Pure human eval is accurate but non-repeatable.

Decision: instrument a minimal set that covers the seams, not all metrics. Most teams need Recall@K, Context Precision, Faithfulness, Answer Relevancy, and latency/cost. Add human eval for a sampled holdout.

## Trade-offs and failure modes

* Automated vs human: automated metrics are fast and cheap but drift from user intent. Faithfulness models can be fooled by paraphrasing. Always calibrate automated scores with human judgments.
* Metric gaming: optimizing for Recall@K can increase noise. Optimizing for Faithfulness can make answers overly conservative and refuse to answer.
* Offline vs online: offline sets are static and lose distribution shift. Online signals are real but noisy and delayed.
* Retrieval vs generation blame: without context-level metrics you will over-tune the LLM and under-invest in retrieval, the cheaper win.

Common failure: measuring only final answer similarity to a reference. That hides retrieval misses and rewards memorization from the LLM's pre-training.

## Example

Enterprise support RAG over internal docs.

Initial launch shows low CSAT. Metrics show Recall@10 = 0.78, Context Precision = 0.42, Faithfulness = 0.91. The retriever finds relevant docs but returns 3x noise. Generator is faithful, so answers are safe but incomplete and verbose.

Architectural decision: add re-ranker and reduce top-k from 10 to 5, add context compression. After change: Recall@5 drops to 0.71, Context Precision rises to 0.78, Faithfulness stays 0.90, latency drops 18%. CSAT improves. The metric split made the trade-off explicit.

## Reasoning challenge

You ship a RAG chatbot for legal contracts. After a model upgrade, Answer Relevancy rises 12% but Faithfulness drops 8% and user escalations rise. Context Precision is unchanged. Where do you intervene and what metric would you watch to confirm the fix?

## Key takeaway

* RAG metrics exist to attribute failure to retrieval, context, or generation, not to score the LLM in isolation.
* Separate retrieval quality from grounded generation; optimize the seam with the biggest gap.
* Instrument a small, stable set of automated metrics and calibrate with sampled human judgments.
* Trade latency/cost against retrieval depth; measure both system performance and user outcome.
