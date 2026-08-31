# Where should memory live?

> **Learning Path:** AI Memory
> **Section:** 13.2.3 — Architecture

## 1. Problem

உங்களிடம் ஒரு AI agent இருக்கு. User-உடன் 10 message-க்கு மேல் பேசினால், முந்தைய context-ஐ மறந்துவிடுகிறது.

ஒரு customer support agent-க்கு முந்தைய ticket, user-ன் past purchases, preference எல்லாம் தேவை. ஒவ்வொரு request-லயும் முழு history-யை LLM context window-க்குள் அனுப்பினால் என்ன ஆகும்?

Latency போகும், cost பெருகும், context window overflow ஆகும். அதனால் memory-யை வெளியே வைக்க வேண்டியிருக்கு.

**அப்போ கேள்வி:** That memory எங்கே வைக்க வேண்டும்?

LLM-ன் உள்ளே? Application layer-ல்? External store-ல்? அல்லது அனைத்தும் சேர்ந்து?

## 2. Mental Model

Memory என்பது 3 layer-ல் வாழலாம்.

**Working memory** = LLM context window. Short term, expensive, ephemeral.
**Short-term memory** = Application session / in-process cache. Fast, limited lifetime.
**Long-term memory** = Persistent store. Durable, searchable, shared across sessions.

ஒரு architect-ஆக நீங்கள் decide பண்ணுவது: எந்த data எந்த layer-ல் இருக்க வேண்டும், எப்போது promote/demote செய்ய வேண்டும்.

## 3. How It Works

Simple flow ஒன்று:

User query → Retrieval step → Memory store-லிருந்து relevant facts தேடு → Context window-ல் inject செய் → LLM generate → Output + New facts → Store update

இங்கே memory live பண்ணும் இடம் retrieval-ன் speed, consistency, cost-ஐ decide செய்யும்.

Options:

* **In-context only:** எல்லாம் prompt-ல். Small chat bots-க்கு மட்டும் ok.
* **Application cache / Redis:** Session memory, recent facts, user state. Millisecond access.
* **Vector database:** Semantic memory, embeddings, similarity search. RAG memory-க்கு.
* **Relational / Document DB:** Structured memory, user profile, preferences, facts with schema.
* **Graph DB:** Relationship memory, connections between entities.
* **LLM internal weights:** Fine-tuning / RAG-less. Slow to update, expensive.

## 4. Architectural Reasoning

Memory-யை எங்கே வைக்கணும் என்பது constraints-ஆல் decide ஆகும்.

**Latency constraint:** Real-time agent-க்கு <500ms தேவை. அப்போ vector DB query + retrieval வேண்டுமானால் cache layer முன்னால் வேண்டும்.

**Consistency constraint:** Financial data, compliance audit trail. அப்போ relational DB + event log தேவை. Vector DB மட்டும் போதாது.

**Scale constraint:** Millions of users, each with conversation history. In-memory cache cost prohibitive. அப்போ tiered: hot data in Redis, warm in vector DB, cold in object storage.

**Personalization constraint:** Cross-session memory தேவை. அப்போ session scope-க்கு அப்பால் persistent store வேண்டும்.

Architectural decision tree:

1. Data ephemeral ஆ? → Session cache.
2. Data needs semantic search? → Vector DB.
3. Data needs structured queries & transactions? → Relational/Document DB.
4. Data needs relationships? → Graph DB.
5. Data needs long-term durability & audit? → Persistent store + event sourcing.

பெரும்பாலும் hybrid தான்.

## 5. Trade-offs

**Speed vs Durability**
In-process memory or Redis super fast, but data loss risk. Persistent DB durable but slower.

**Cost vs Recall**
Context window-ல் எல்லாம் வைப்பது accurate ஆனால் token cost அதிகம். External retrieval cheaper ஆனால் recall quality drop ஆகலாம்.

**Freshness vs Consistency**
Real-time updates வேண்டும் என்றால் cache invalidation complexity வரும். Eventual consistency accept பண்ணலாம்.

**Generality vs Precision**
Vector DB semantic similarity கொடுக்கும், ஆனால் exact fact lookup-க்கு பலவீனம். Relational DB exact ஆனால் semantic nuance miss ஆகும்.

Failure mode: Memory store down ஆனால் agent blind ஆகிவிடும். அதனால் fallback strategy வேண்டும்: last known profile from cache, graceful degradation.

## 6. Practical Example

Enterprise sales assistant agent.

Requirements:
* Conversation context for last 5 turns → working memory
* User preferences, industry → short-term memory in Redis, TTL 24h
* Past deals, CRM notes → relational DB, structured query
* Similar past conversations for suggestions → vector DB over embeddings
* Organization chart & relationships → graph DB

Flow:
User asks "Last quarter deal எப்படி போனது?"
Agent:
1. Redis-ல் user id → profile fetch
2. Relational DB-ல் deals query
3. Vector DB-ல் similar conversations retrieve
4. All facts 800 tokens-க்குள் compress பண்ணி context-ல் inject
5. LLM generate

Memory live location decide செய்தது latency <800ms, cost control, personalization.

## 7. Reasoning Challenge

உங்கள் RAG chatbot 1M users-க்கு serve பண்ணுகிறது. Each user-க்கு 50k tokens history உள்ளது. Daily active users 100k.

Options:
A) Every query-ல் full history-யை vector DB-ல் search பண்ணு
B) Recent 1k tokens-ஐ Redis-ல் வைத்து, older facts-ஐ vector DB-ல் archive பண்ணு
C) எல்லாவற்றையும் prompt-ல் அனுப்பு

Cost, latency, recall கணக்கில் எந்த architecture தேர்வு செய்வீர்கள்? Promotion/demotion policy என்ன வைப்பீர்கள்?

## 8. Key Takeaways

* Memory என்பது single place அல்ல, tiered architecture.
* Working memory = context window, short-term = cache, long-term = persistent store.
* Where memory lives decides latency, cost, consistency, and recall quality.
* Real systems use hybrid: Redis + Vector DB + Relational/Graph DB, with clear promotion rules.
* Every choice creates a new operational problem: cache invalidation, retrieval quality, consistency.
