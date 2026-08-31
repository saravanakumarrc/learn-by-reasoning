# What should be remembered?

> **Learning Path:** AI Memory
> **Section:** 13.2.1 — Architecture

## 1. Problem

உங்க agent ஒன்று user-கிட்ட 3 மணி நேரம் chat பண்ணுது. 50-turn conversation. பின்னர் user திரும்ப வந்து "நேத்து நான் சொன்ன budget limit என்ன?"ன்னு கேக்குறார்.

Agent-க்கு என்ன இருக்கு? Last 10 messages மட்டும் context window-ல இருக்கு. முந்தைய decisions, preferences, project details எல்லாம் போயாச்சு.

அப்புறம் user சொல்றார்: "இதே மாதிரி ஒரு request முன்னாடியே கொடுத்தேன், அதே response கொடு."

இங்கே என்ன வலி? Agent stateless. LLM-க்கு long-term memory இல்ல. Every request fresh.

நீங்கள் என்ன build பண்ணுவீங்க? Everything-ஐ context window-ல வைக்க முடியாது. Token limit, latency, cost எல்லாம் பிரச்சனை.

**What problem became painful?** Short-term context மட்டும் போதாது. User identity, preferences, past decisions, conversation history, knowledge base எல்லாம் remember பண்ணணும். ஆனால் எல்லாத்தையும் remember பண்ணினால் noise, cost, hallucination.

## 2. Mental Model

AI Memory என்பது ஒரு **filter + store + retrieve** system.

Agent ஒரு நாளைக்கு ஆயிரக்கணக்கான facts பார்க்கும். அதில் முக்கியமானது மட்டும் தேர்ந்தெடுத்து store பண்ணணும். தேவைப்படும்போது மட்டும் retrieve பண்ணணும்.

Mental model: Human memory போல.

* Working memory = context window, short-term
* Episodic memory = conversation history, sessions
* Semantic memory = facts, knowledge, user profile
* Procedural memory = learned patterns, tools usage

Architecture-ல நாம் இதை explicit-ஆ separate பண்ணி manage பண்ணுவோம்.

## 3. How It Works

Basic flow:

**Ingest → Extract → Decide Store/Forget → Store → Index → Retrieve → Rank → Inject**

1. **Ingest**: Conversation turn, tool output, document.
2. **Extract**: LLM அல்லது extractor இருந்து entities, facts, preferences, decisions-ஐ extract பண்ணு. Summarization, entity linking.
3. **Decide**: இது important-ஆ? User-specific-ஆ? Duplicate-ஆ? Privacy sensitive-ஆ? இங்கே policy engine decide பண்ணும்.
4. **Store**: Different stores for different need.
   * Vector DB for semantic search
   * Relational / KV for structured profile
   * Graph DB for relationships
5. **Retrieve**: Query time-ல user intent-ஐ புரிஞ்சு relevant memories retrieve. Hybrid search: vector + keyword + metadata filter.
6. **Rank**: Relevance + recency + importance score.
7. **Inject**: Top K memories-ஐ context window-ல inject. மொத்தம் dump பண்ணக்கூடாது.

## 4. Architectural Reasoning

When this becomes useful?

* Multi-session continuity வேண்டும்
* Personalization வேண்டும்
* Agent long-running tasks பண்ணணும்
* Knowledge base growing

Constraints address:

* **Token limit**: முக்கியமானது மட்டும் எடு
* **Latency**: Pre-computed embeddings, caching
* **Consistency**: User profile update எல்லா session-ல reflect ஆகணும்
* **Cost**: Retrieve selective, not full history

Alternatives:

* **Full history in context**: Simple, but scales poorly, cost high, noisy
* **Summarization only**: Cheap, but lossy, fine details போகும்
* **Memory architecture**: More complex, but controllable, scalable

Architect choose memory when user lifetime value > memory infra cost, and continuity is core product promise.

## 5. Trade-offs

**Remember everything vs Remember wisely**

* Recall vs Precision: அதிக retrieve பண்ணினால் noise வரும், hallucination increase ஆகும். குறைவாக retrieve பண்ணினால் relevant info miss ஆகும்.

**Freshness vs Stability**

* Real-time update செய்தால் consistency tough. Batch update செய்தால் lag.

**Granularity**

* Fine-grained facts = accurate but storage & search cost high.
* Coarse summaries = cheap but lose nuance.

**Privacy & Security**

* Memory persistent ஆகும். PII store பண்ணலாமா? Retention policy? User delete request-க்கு எப்படி purge?

**Failure modes**

* Stale memory: Old preference இன்னும் active-ஆ இருக்கு.
* Memory pollution: Wrong extraction.
* Retrieval bias: Similar but irrelevant memories dominate.

## 6. Practical Example

Enterprise sales agent.

User: "Acme Corp-க்கு நான் எப்போ proposal அனுப்பினேன்? அவங்க budget என்ன சொன்னாங்க?"

System:

* Conversation history from CRM + Slack + email ingest ஆகி memory store-ல இருக்கு.
* Extraction: `company=Acme Corp, proposal_date=2024-11-02, budget=250k, decision_maker=Priya`
* Store in Postgres as structured fact + vector embedding for free-form notes.
* Retrieve time: Query filter `user_id + company`. Hybrid search returns top 3 memories.
* Rank by recency + importance. Inject into prompt.

Without memory, agent context window-ல 3 மணி நேர conversation fit ஆகாது. With memory, agent correct answer கொடுக்கும்.

Architecture: Event bus → Extractor service → Memory store [Postgres + Qdrant] → Retrieval service → Ranker → Prompt builder.

## 7. Reasoning Challenge

உங்க product-ல 1M users இருக்காங்க. ஒவ்வொருத்தருக்கும் average 500 conversations per month. Each conversation 20 turns.

இப்போ உங்களுக்கு requirement: user preferences across sessions remember பண்ணணும், ஆனால் cost control பண்ணணும்.

இங்கே என்ன memory architecture தேர்வு செய்வீங்க? Store everything raw? Summarize per session? Summarize per user? Embeddings for everything?

ஏன் அந்த choice? என்ன trade-off accept பண்ணுறீங்க?

## 8. Key Takeaways

* Memory என்பது recall மட்டும் இல்ல, **filter + store + retrieve + forget** system.
* Context window என்பது working memory. Persistent memory என்பது architecture decision.
* What to remember is more important than how to remember. Importance scoring + retention policy தான் core.
* Every memory adds cost, latency, and risk. Remember wisely, not maximally.

இது புரிஞ்சா, AI Memory-ஐ build பண்ணும்போது நீங்கள் technology-ஐ first-ஆ பார்க்க மாட்டீங்க. Problem-ஐ first-ஆ பார்ப்பீங்க.
