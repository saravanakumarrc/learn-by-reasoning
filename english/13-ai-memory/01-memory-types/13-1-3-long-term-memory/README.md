# Long-term memory

> **Learning Path:** AI Memory
> **Section:** 9.1.3 — Memory types

**Long-term memory**

### 1. The problem

A language model is stateless and has a bounded context window. Within a single session it can use working memory - the messages you give it now. Once the session ends, that memory is gone.

In production this creates three architectural constraints:
* **Context limit:** You cannot keep a user's entire history in the prompt.
* **Statelessness:** No session remembers the user from last week.
* **Knowledge decay:** The model does not learn from interactions; it only retrieves.

Without a persistent store, every conversation starts from zero. You pay re-prompting cost, lose personalization, and cannot build cumulative understanding.

### 2. Mental model

Think of it like human memory.

Working memory = RAM + current conversation. Fast, small, volatile.
Long-term memory = persistent storage. Slower to access, large, durable.

The LLM is the processor. Long-term memory is the disk where facts, preferences, and past interactions are kept so they can be loaded into working memory when relevant.

### 3. How it works

Long-term memory is not a single tech. It is a retrieval path from persistent store into context.

```
flowchart LR
    User[User Input] --> WM[Working Memory / Context Window]
    WM --> LLM[LLM]
    LLM --> Decision[Action / Response]
    LLM -->|write| LT[Long-Term Memory Store]
    LT -->|retrieve| WM
    LT --> VectorDB[(Vector DB)]
    LT --> RelDB[(Relational / KV)]
    LT --> KG[(Knowledge Graph)]
```

Essentially:
* **Capture:** Summarize, extract entities, and write interactions to a durable store.
* **Index:** Embeddings for semantic search, plus structured fields for filtering.
* **Retrieve:** Given current query + user identity, fetch relevant memories, re-rank, and inject into context.
* **Consolidation:** Periodically compress old sessions into summaries to avoid unbounded growth.

Implementation choices are consequences, not the concept. Vectors for similarity, SQL for precise facts, graphs for relationships.

### 4. Architectural reasoning

Use long-term memory when you need continuity across sessions and cumulative knowledge.

* **Personalization:** Remember preferences, past decisions, tone.
* **Knowledge base:** Store domain facts the model should not re-learn per request.
* **Auditability:** Need to explain why the model acted, with provenance.

Alternatives and when to skip:
* **Bigger context window:** Works for short, expensive sessions. Fails at scale and cost.
* **Fine-tuning:** Good for stable world knowledge. Bad for rapidly changing per-user data.
* **Prompt caching:** Saves cost, not persistence.

Decision rule: If the information must survive session end, be queried by similarity, and be updated over time, you need long-term memory.

### 5. Trade-offs and failure modes

* **Freshness vs cost.** Write every turn is expensive and noisy. Write only summaries loses detail. You must decide a write policy.
* **Retrieval precision vs recall.** More results increase context bloat and hallucination risk. Too few misses critical context.
* **Staleness.** Long-term memory drifts. Without invalidation and versioning, the model acts on outdated preferences.
* **Contamination.** Poor filtering retrieves irrelevant memories, leading to confabulation.
* **Embedding drift.** As the embedding model or domain evolves, old vectors degrade. You need re-indexing strategy.

Common failure: treating long-term memory as a dump. Unstructured retrieval without filtering by user, time, and relevance produces noisy context and worse answers.

### 6. Example

Enterprise support agent.

Working memory holds the current ticket and last 3 turns. Long-term memory holds:
* Customer profile in SQL: plan, industry, SLA.
* Past tickets in vector DB with embeddings of issue + resolution.
* Product knowledge graph: features, dependencies.

Flow: New ticket arrives → retrieve last 5 similar tickets for this customer + relevant KB nodes → inject into prompt → generate response → write summary back with tags.

Result: agent resolves faster, references history, and learns from prior fixes without fine-tuning.

### 7. Reasoning challenge

You are building a sales coach agent. It should remember each rep's past calls, objections, and successful rebuttals.

Option A: Store full transcripts in a vector DB and retrieve top-k chunks per call.
Option B: Summarize each call into structured JSON - objection type, outcome, rebuttal used - stored in relational DB, retrieve via filters.

Which do you choose, and what do you lose with the other?

### 8. Key takeaway

* Long-term memory exists to make LLM systems stateful across sessions without blowing up context.
* It is a write → index → retrieve → inject pipeline, not just a vector database.
* Design decisions are about what to store, how to summarize, and how to filter at retrieval time.
* The main risks are stale data, noisy retrieval, and unbounded growth; solve them with consolidation, versioning, and strong filters.
