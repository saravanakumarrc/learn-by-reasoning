# Naive RAG

> **Learning Path:** RAG Architecture
> **Section:** 8.2.1 — RAG architecture

## The problem

You have a capable LLM. It answers well, but it hallucinates, it doesn't know your data, and its knowledge cuts off. You can't fine-tune for every internal doc, product catalog, or policy update.

You need answers grounded in your own content, with low latency and without retraining. The constraint is: keep the LLM as-is, but give it the right context at query time.

That creates a need for retrieval, not learning.

## Mental model

Naive RAG is a librarian who fetches then answers.

User asks a question → system finds relevant passages from your corpus → system hands those passages to the LLM with the question → LLM generates an answer constrained to the fetched material.

No re-ranking, no multi-step reasoning, no query rewriting. Retrieve top-k, stuff into prompt, generate.

## How it works

The pipeline is intentionally minimal:

```mermaid
flowchart LR
    U[User Query] --> E[Embed Query]
    E --> V[Vector DB]
    V --> R[Top-K Chunks]
    R --> P[Prompt Builder: Context + Query]
    P --> L[LLM]
    L --> A[Answer with citations]
```

1. **Index offline:** Documents are chunked, embedded with a text embedding model, stored in a vector DB with metadata.
2. **Retrieve online:** Query is embedded, similarity search returns top-k chunks.
3. **Generate:** Chunks are concatenated into the prompt as context, LLM is instructed to answer using only that context.
4. Return answer, optionally with chunk references.

That's it. No feedback loop between generation and retrieval.

## Architectural reasoning

When it helps:
* You need grounding in a changing corpus you cannot fine-tune into the model.
* You need explainability via source citations.
* You need a cheap baseline before investing in complex retrieval.

What it solves: Hallucination on domain-specific facts, knowledge cutoff, and data freshness.

Alternatives:
* Fine-tuning / RAG fine-tune: bakes knowledge in, expensive and stale.
* No retrieval: pure LLM, fast but ungrounded.
* Advanced RAG: hybrid search, reranking, query expansion, iterative retrieval. More accurate, more complex and latency.

You choose Naive RAG when correctness matters more than perfect relevance, and you want to validate the retrieval value proposition fast.

## Trade-offs and failure modes

* **Retrieval quality = system quality.** If the top-k is irrelevant, the LLM will hallucinate within the context or refuse. Chunking strategy, embedding model, and corpus hygiene dominate results.
* **Context window pressure.** Stuffing many chunks burns tokens, increases latency and cost, and can dilute signal with noise. Naive RAG has no selection beyond top-k.
* **Single round retrieval.** No chance to refine query based on generation. Ambiguous queries get bad results and stay bad.
* **Staleness and drift.** Vector index must be kept in sync with source. No freshness checks by default.
* **Prompt injection via retrieved text.** Untrusted chunks can influence the model if instructions aren't isolated.

The most common failure is not retrieval recall, but bad chunking: too large = irrelevant noise, too small = loss of meaning.

## Example

Enterprise support bot for an internal knowledge base of 50k support articles.

Naive RAG implementation:
* Chunk articles at ~500 tokens with 100 token overlap, store embeddings in pgvector.
* User asks: "How to reset MFA for contractors?"
* Query embedding retrieves 5 chunks about MFA reset, contractor onboarding, and admin console.
* Prompt = system instruction + 5 chunks + user query.
* LLM returns step-by-step answer with links to the 3 most relevant chunks.

It works for 80% of queries. The remaining 20% fail because the query is paraphrased differently than the corpus, or the answer spans multiple articles that aren't retrieved together.

## Reasoning challenge

You have a financial compliance Q&A system. Regulations change monthly. Queries are high-stakes and must cite exact source paragraphs. Latency budget is 800ms.

Would you ship Naive RAG as-is? What is the first failure you would expect in production, and what minimal addition would you make before launch?

## Key takeaway

* Naive RAG = retrieve top-k chunks then generate. It's a baseline, not a best practice.
* Value comes from grounding, not from the LLM. Retrieval quality beats model size.
* The main risks are bad chunks, context overload, and single-pass retrieval.
* Ship it to prove retrieval adds value, then iterate to hybrid search, reranking, and query refinement when accuracy and latency constraints demand it.
