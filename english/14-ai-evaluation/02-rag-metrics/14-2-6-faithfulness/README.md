# Faithfulness

> **Learning Path:** AI Evaluation
> **Section:** 14.2.6 — RAG metrics

**Faithfulness**

### The problem

RAG gives the LLM context to ground its answer. Retrieval is not enough.

With retrieval you get a new failure mode: the model reads the right documents and still invents. It adds plausible details not in the source, connects facts that were never connected, or paraphrases into something unsupported.

You can retrieve perfectly relevant docs and still ship a hallucination. Relevance metrics tell you *did we fetch the right stuff*. Faithfulness tells you *did the model stay inside the stuff we fetched*.

This matters for an architect because hallucination risk is not solved by better retrieval alone. It is a generation discipline problem, and you need a measurable signal to control it in production.

### Mental model

Faithfulness = alignment between the answer and the retrieved context.

Think of it as a citation check, not a truth check. A faithful answer is fully entailed by the context, even if the context itself is wrong or incomplete.

Faithfulness ≠ Correctness/Factuality. An answer can be faithful to a bad source. Factuality asks if the answer is true in the world. Faithfulness asks if the answer is true *to the source*.

### How it works

The core mechanism is claim decomposition + entailment.

```mermaid
flowchart LR
    Q[User Query] --> R[Retriever]
    R --> C[Context Chunks]
    C --> G[Generator LLM]
    G --> A[Answer]
    A --> E[Claim Extractor]
    C --> E
    E --> N[NLI Entailment]
    N --> F[Faithfulness Score]
```

1. Extract atomic claims from the answer.
2. For each claim, check if the retrieved context entails it.
3. Aggregate to a score, typically % of claims supported.

In practice this is done with an NLI model or a second LLM as a judge: "Is this claim supported by this context? Yes/No/Partial". RAGAS faithfulness is the canonical implementation.

It does not require gold answers. Only query, context, and generated answer.

### Architectural reasoning

When it helps: any RAG system where you cannot tolerate ungrounded statements. Compliance, support, medical, legal, finance.

What problem it solves: gives you a production signal for hallucination risk separate from retrieval quality. You can monitor drift, compare prompts, and gate outputs.

Alternatives:
* **Human review** - accurate, expensive, not scalable.
* **Self-consistency / majority voting** - reduces randomness, does not guarantee grounding.
* **Citation enforcement** - force model to cite chunks. Helps traceability but does not prove the cited chunk actually supports the claim.
* **Faithfulness scoring** - automated, cheap, continuous.

Why choose it: you need a non-human-in-the-loop guardrail that runs per request and feeds metrics, alerts, and reranking.

Decision pattern: use faithfulness as a quality gate in the RAG pipeline, not as a retrieval metric.

### Trade-offs and failure modes

Faithfulness is conservative by design. High faithfulness often means short, bland answers that stay close to the source.

Key trade-offs:
* **Faithfulness vs Completeness.** A model that sticks strictly to context will under-answer when context is fragmented. You need good chunking and query decomposition to avoid false negatives.
* **Faithfulness vs Relevance.** You can have faithful answers to irrelevant context. Use both metrics together.
* **Granularity.** Claim-level scoring is more useful than document-level, but extraction errors create noise. Splitting claims incorrectly penalizes good answers.
* **Context limits.** If the retriever returns too much noisy context, the model can find a sentence to justify an unsupported claim. Faithfulness rewards retrieval quality indirectly.

Failure modes to watch:
* **Paraphrase overreach.** Model rephrases two facts into a new causal link not present in source. NLI often misses this.
* **Implicit world knowledge leakage.** Model injects common sense not in context. Faithfulness score stays high if judge is lenient.
* **Chunk boundary cuts.** A claim needs two chunks to be supported. Single-chunk check fails.

### Example

Enterprise support RAG for internal product docs.

Query: "How do I refund a partial order in the new billing system?"

Retriever returns 3 chunks about refunds, partial credits, and API limits.

A faithful answer restates only what those chunks contain: steps, required permissions, and the 30-day limit. It does not add "you can refund after 30 days with manager approval" even if that is true in the old system.

You run faithfulness scoring on every answer. P95 score drops from 0.92 to 0.71 after a prompt change that encourages "more helpful" tone. You roll back. The metric caught hallucination creep before tickets increased.

### Reasoning challenge

You launch a RAG chatbot for financial reporting. Faithfulness scores are 0.95+, but users complain answers are incomplete and they have to ask follow-ups. Retrieval recall is good.

What is the likely architectural cause, and what do you change first: retriever, chunking strategy, generation prompt, or faithfulness threshold?

### Key takeaway

* Faithfulness measures grounding in retrieved context, not truth in the world. Use it to detect hallucinations, not factual errors.
* It is a generation quality signal that complements retrieval relevance. You need both.
* High faithfulness can coexist with low usefulness. Optimize for the right balance via context quality and prompt constraints.
* Deploy it as a continuous metric and guardrail, not a one-off evaluation.
