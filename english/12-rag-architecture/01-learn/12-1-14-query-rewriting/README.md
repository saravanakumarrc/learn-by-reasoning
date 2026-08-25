# Query rewriting

> **Learning Path:** RAG Architecture
> **Section:** 8.1.14 — Learn

### 1. The problem

In RAG, retrieval quality is bounded by the quality of the query you send to the vector store. User queries are rarely retrieval-optimal.

They are conversational: *"It was expensive"*, *"What about the other one?"*
They are underspecified: *"best practice for deployment"*
They are multi-intent: *"Compare X and Y, and tell me which is cheaper for small teams"*
They use synonyms or domain jargon that doesn't match your chunked corpus.

A raw user query sent directly to a retriever will miss relevant docs and retrieve noise. You can make the retriever smarter, but you can't fix an ambiguous input with better embeddings alone.

Query rewriting exists to bridge the gap between how users ask and how retrieval works.

### 2. Mental model

Think of the rewriter as a translator sitting between the user and the retriever.

User language -> Canonical, self-contained, retrieval-friendly query.

It does not answer the question. It makes the question answerable by retrieval.

### 3. How it works

The essential mechanism is a small LLM pass before retrieval:

```mermaid
flowchart LR
    U[User Query + Conversation History] --> R[Rewriter LLM]
    R --> Q[Standalone Canonical Query]
    Q --> Ret[Retriever]
    Ret --> Docs[Top-k Chunks]
    Docs --> Gen[Generator LLM]
    Gen --> A[Answer]
```

Core patterns:

* **History-aware rewriting.** Make pronouns and references explicit. *"It was expensive"* + history -> *"Was the AWS RDS provisioned IOPS storage expensive compared to GP3?"*
* **Decomposition.** Break complex queries into sub-queries that can be retrieved independently, then merged. *"Compare X and Y"* -> `["pros of X", "pros of Y", "cost of X vs Y"]`
* **Expansion / paraphrasing.** Generate semantically equivalent variants to increase recall. Sometimes done as multiple rewrites and merged results.
* **Clarification.** When the query is too vague, the rewriter can request disambiguation instead of guessing.

The rewriter runs with a tight prompt, no retrieval context, and outputs only the rewritten query or queries.

### 4. Architectural reasoning

When it helps:
* Conversational RAG with multi-turn context
* Queries with implicit dependencies on prior turns
* Complex, multi-hop questions where decomposition improves recall
* Domain-specific user phrasing that mismatches corpus vocabulary

What it solves: higher recall and precision at retrieval time, fewer hallucinations from the generator because it gets better context.

Alternatives:
* **Better chunking / embeddings.** Helps but doesn't fix ambiguity.
* **HyDE - Hypothetical Document Embedding.** Generate a hypothetical answer first, then retrieve with it. Powerful but more expensive and can drift.
* **Ask the user to clarify.** Safe, but bad UX.

Why choose rewriting: It is cheap, composable, and sits in the pre-retrieval stage. You can A/B test it without changing your index.

### 5. Trade-offs and failure modes

* **Latency and cost.** An extra LLM call per turn. Can be mitigated with caching, small models, or only rewriting when confidence is low.
* **Rewrite drift.** The rewriter hallucinates facts not in the conversation and bakes them into the query, poisoning retrieval. Prompt it to only rephrase, not add knowledge.
* **Over-specification.** Turning a broad exploratory query into a narrow one reduces serendipity. Useful for follow-ups, harmful for discovery.
* **Error propagation.** A bad rewrite is worse than the original query. You need guardrails: max length, no external knowledge, output schema validation.
* **Security.** Rewriter sees full conversation history. Ensure PII handling and prompt injection filtering before rewriting.

### 6. Example

Enterprise support RAG for an internal SaaS platform.

User turn 1: *"How do I set up SSO?"*
Rewritten: *"How to set up SAML SSO for Acme SaaS platform"*
Retrieved: docs on SSO setup.

User turn 2: *"Can I use Okta?"*
Naive retrieval fails. History-aware rewrite: *"Can I use Okta as IdP for SAML SSO for Acme SaaS platform?"*
Retrieved: Okta-specific integration steps.

Without rewriting, the second turn would retrieve generic Okta docs.

### 7. Reasoning challenge

You are building a RAG assistant for financial analysts. Queries are often multi-intent and domain-specific, e.g., *"Show me Q2 revenue trends for the top 3 products and flag anything unusual vs guidance."*

Do you use single history-aware rewriting, query decomposition into multiple retrieval calls, or both? What failure mode worries you most in this domain, and how would you mitigate it?

### 8. Key takeaway

* Query rewriting fixes the input to retrieval, not the retriever itself.
* The core value is making conversational, ambiguous queries self-contained and retrieval-friendly.
* Use history-aware rewriting for multi-turn, decomposition for multi-intent, and keep the rewriter constrained to paraphrase only.
* The main trade-offs are latency/cost vs recall, and the risk of rewrite drift introducing hallucinated constraints.
