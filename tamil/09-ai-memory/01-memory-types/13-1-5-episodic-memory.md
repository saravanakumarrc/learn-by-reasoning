# Episodic memory

> **Learning Path:** AI Memory
> **Section:** 13.1.5 — Memory types

## 1. Problem

ஒரு agent-க்கு முன்பு நடந்த conversation-ஐ மட்டும் தெரியுமா? இல்லை. Agent-க்கு "நான் கடந்த வாரம் உங்களுடன் பேசினபோது..." என்று நினைவு வைத்துக்கொள்ள வேண்டும்.

RAG + vector database இருந்தாலும், ஒரு customer என்ன சொன்னார், எப்போது சொன்னார், எந்த context-ல் சொன்னார் என்பது தெரியாமல் போகிறது.

> What goes wrong if we don't have this? Agent stateless ஆக இருக்கும். ஒவ்வொரு interaction-ம் முதல் முறையாகத் தெரியும். Personalization, continuity, trust எல்லாம் போய்விடும்.

இந்த தேவையிலிருந்துதான் Episodic memory வருகிறது.

## 2. Mental Model

Episodic memory = **எப்போது, எங்கே, யாருடன், என்ன நடந்தது** என்ற நினைவு.

Human brain-ல் நாம் personal experiences-ஐ time + context உடன் சேமிப்பது போல.

AI system-ல் இது: timestamped events, interactions, user actions, conversation turns, session data, என்ன context-ல் நடந்தது என்ற metadata உடன் சேமிக்கப்படும் memory.

Semantic memory-ல் "facts" இருக்கும். Episodic memory-ல் "stories" இருக்கும்.

## 3. How It Works

ஒரு episode = structured record

* `who`: user_id, agent_id
* `when`: timestamp, session_id
* `what`: conversation transcript, action taken, decision made
* `where`: channel, product, task context
* `why`: intent, outcome

இந்த episodes-ஐ store செய்ய வேண்டும். பின்னர் retrieve செய்யும்போது:

1. **Index by time + user + context**
2. **Query for relevant past episodes** - "இதே user கடந்த 30 நாளில் என்ன கேட்டார்?"
3. **Summarize & reason** - past episodes-ஐ current query-க்கு connect செய்ய LLM பயன்படுத்தும்.

Vector DB மட்டும் போதாது. Episodic memory-க்கு relational + time-series store தேவை. அதனால் hybrid store பயன்படுத்தப்படுகிறது: PostgreSQL / TiDB for structured episodes + vector embeddings for semantic search.

## 4. Architectural Reasoning

**When useful?**

* Multi-turn conversations
* Personal assistants, customer support agents
* Long-running workflows where continuity matters
* Audit & compliance - "ஏன் இந்த decision எடுக்கப்பட்டது?"

**What constraint it addresses?**

Stateless LLM-ன் context window limit + no persistent personal history.

**Alternatives**

* Short-term context window only: cheap, but forgets quickly
* Semantic memory only: facts remember, but story forget
* Full conversation log dump: works for small scale, retrieval பயங்கரம்

**Why choose episodic?**

Because architect-க்கு தெரிய வேண்டும்: user-க்கு consistent experience வேண்டும், மற்றும் system-க்கு explainability வேண்டும்.

## 5. Trade-offs

* **Storage vs Recall quality**: எல்லா interaction-ம் save செய்தால் storage cost அதிகம், noise அதிகம். Filter, summarize, compress செய்ய வேண்டும்.
* **Privacy & compliance**: Episodic memory = personal data. GDPR delete request வந்தால் அந்த user-ன் episodes-ஐ முழுவதும் purge செய்ய வேண்டும். Retention policy தேவை.
* **Retrieval latency**: Past episodes-ஐ தேடுவது expensive. Indexing, TTL, summarization layer தேவை.
* **Freshness vs Relevance**: பழைய episode-ஐ எப்போது forget செய்ய வேண்டும்? Forgetting policy இல்லை என்றால் stale context வரும்.

Failure mode: Wrong episode retrieve ஆனால் hallucination போல தவறான personalization. Hence source attribution முக்கியம்.

## 6. Practical Example

Enterprise support agent.

User: "நான் கடந்த மாதம் புகார் கொடுத்தேன், அது என்ன ஆச்சு?"

System:

1. Episodic memory store-ல் user_id + last 90 days episodes query
2. Episode: 2025-07-12, ticket #4821, issue: billing error, agent resolved with refund
3. Current query-க்கு connect செய்து answer: "உங்கள் refund 2025-07-15 process ஆகி..."

இங்கே semantic search மட்டும் "billing error" என்ற fact கொடுக்கும். Episodic memory "நீங்கள்", "கடந்த மாதம்", "ticket #4821" என்ற story கொடுக்கும்.

Architecture:

`API Gateway -> Agent Service -> Memory Service`
Memory Service -> `Postgres` for episodes table, `Vector DB` for semantic linkage, `Cache` for recent episodes.

Write path: every session end-ல் episode summarize செய்து store.

Read path: current user query + recent episodes retrieve -> LLM context-ல் inject.

## 7. Reasoning Challenge

உங்களிடம் banking assistant உள்ளது. Customer-கள் தினமும் 1000 interactions செய்கிறார்கள். Episodes-ஐ 7 years வைத்திருக்க வேண்டும் compliance-க்கு. ஆனால் agent-க்கு கடந்த 3 மாத episodes மட்டுமே relevant.

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Hot vs cold storage எப்படி பிரிப்பீர்கள்? Privacy delete request வந்தால் எப்படி handle செய்வீர்கள்?

## 8. Key Takeaways

* Episodic memory = time-bound personal experiences, not just facts
* இது continuity, personalization, trust-க்கு தேவை
* Semantic + Episodic memory-ஐ hybrid store-ல் combine செய்ய வேண்டும்
* Storage cost, privacy, retrieval latency முக்கிய trade-offs
* Every architectural solution creates forgetting & compliance problem
