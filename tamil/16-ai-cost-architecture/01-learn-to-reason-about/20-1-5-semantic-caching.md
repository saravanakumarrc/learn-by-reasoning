# Semantic caching

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.5 — Learn to reason about

## 20.1.5 — Semantic caching

### 1. Problem

உங்கள் AI Cost Architecture-ல LLM call எல்லாம் expensive. Latency-ம் high.

ஒரு RAG agent-ல user ஒரே கேள்வியை வெவ்வேறு வார்த்தைகளில் கேட்கிறார்:

* "Q4 revenue எவ்வளவு?"
* "last quarter sales number என்ன?"
* "Q4-ல நாம் எவ்வளவு earn பண்ணோம்?"

Semantically same intent. ஆனால் string match ஆகாது. Every time நீங்கள் embedding → vector database → LLM inference → generation என full pipeline ஓடுகிறீர்கள்.

Pain points:
* Same meaning, different wording → repeat cost
* Peak traffic-ல latency spike
* LLM rate limit / cost blow up
* User-க்கு same answer கிடைக்க வேண்டும், fast

What goes wrong if we don't have this? You pay for reasoning you already paid for.

### 2. Mental Model

Semantic caching = meaning-based cache, not string-based cache.

Normal cache: `key = exact prompt string`. Hit only on exact match.

Semantic cache: `key = meaning of prompt`. Hit when intent similar.

Think of it as a cache layer between user query and LLM call. Query → embedding → nearest neighbor search in cache → if similarity > threshold, return cached response. Else call LLM, store result.

இது duplicate reasoning-ஐ தடுக்கிறது.

### 3. How It Works

Minimal flow:

1. User query வருகிறது.
2. Query-ஐ embedding model-ல் encode பண்ணு → vector.
3. Cache-ல உள்ள stored query vectors-க்கு cosine similarity தேடு.
4. Top match similarity > threshold, say 0.92 → cached response return.
5. Else LLM-க்கு call போ, response வந்ததும் query vector + response + metadata-ஐ cache-ல் store.

Cache store என்பது vector database / key-value store with vector index. Redis + vector, Qdrant, Pinecone, pgvector எதுவும் ஓடும்.

Important nuance: cache key is not the text, it's the vector. Eviction policy, TTL, invalidation தேவை.

### 4. Architectural Reasoning

When useful?

* High QPS, repetitive user intents. Customer support chatbot, internal knowledge assistant.
* Cost-sensitive workloads. LLM call per token cost.
* Low latency requirement for common questions.
* Queries have natural paraphrasing.

Constraint it addresses: **cost and latency** without sacrificing correctness for near-duplicate intents.

Alternatives:

* Exact prompt caching. LLM providers give this. Cheaper, but misses paraphrases.
* Prompt normalization / canonicalization. Rephrase to standard form before call. Fragile.
* No cache. Pay full price always.

Why choose semantic caching? Because real users don't ask same question same way. Meaning repeats, wording changes.

Decision factor: similarity threshold. High threshold = safe but low hit rate. Low threshold = high hit rate but risk of wrong answer.

### 5. Trade-offs

* **Correctness vs Hit Rate.** Semantic similarity ≠ semantic equivalence. "Revenue எவ்வளவு?" vs "Revenue எப்போது வரும்?" Similar vector but different intent. False positive ஆகும்.
* **Staleness.** Cached answer outdated ஆகும். Data changes, model drifts. TTL or invalidation strategy தேவை.
* **Cache poisoning / context leakage.** User-specific data cache-ல் mix ஆகக்கூடாது. Tenant isolation must.
* **Cost of embedding + search.** Every query-க்கு embedding compute + vector search. For very cheap models or rare queries, overhead > saving.

Failure modes:
* Similarity threshold too low → wrong response served.
* Cache not invalidated after data update → stale answer.
* No metadata filter → personal data leak across users.

### 6. Practical Example

Enterprise RAG for internal policy.

User asks: "VPN access எப்படி request பண்ணுறது?" and later "Remote access கேட்க எந்த form?"

Embedding similarity high. First query LLM + retrieval செய்து answer generate. Store vector + response with source docs list + timestamp.

Second query comes. Vector search hits first entry with similarity 0.94. Threshold 0.9 cross ஆனதால் cached response return. No LLM call. Latency 20ms vs 2s. Cost zero.

If user asks: "VPN access expire ஆனா என்ன பண்ணுறது?" Similarity lower, cache miss, fresh LLM call.

### 7. Reasoning Challenge

உங்களிடம் ஒரு finance assistant இருக்கிறது. User queries: "Q4 profit margin என்ன?" "last quarter-ல profit margin calculate பண்ணு" "Q4 margin?"

Daily close time-ல data refresh ஆகிறது. நீங்கள் semantic cache use பண்ண விரும்புகிறீர்கள்.

Threshold எவ்வளவு வைப்பீர்கள்? Cache-ஐ எப்போது invalidate செய்வீர்கள்? User-specific vs global cache என்று எப்படி பிரிப்பீர்கள்?

### 8. Key Takeaways

* Semantic caching saves LLM cost and latency for paraphrased, same-intent queries.
* It trades correctness for efficiency via similarity threshold.
* Cache invalidation and tenant isolation are architectural must-haves, not afterthoughts.
* Use it when query repetition by meaning is high, not for one-off creative generation.
