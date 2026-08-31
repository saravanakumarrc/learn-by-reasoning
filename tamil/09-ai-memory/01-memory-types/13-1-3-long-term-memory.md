# Long-term memory

> **Learning Path:** AI Memory
> **Section:** 13.1.3 — Memory types

## 1. Problem

ஒரு LLM agent-ஐ ஒரு user-உடன் 3 மாதம் பேச விட்டால் என்ன ஆகும்?

Session 1-ல user சொன்னார்: "நான் Chennai-ல இருக்கேன், fintech domain-ல வேலை பாக்குறேன்".
Session 2-ல user சொன்னார்: "எனக்கு payment reconciliation பிடிக்காது".
Session 47-ல user கேட்கிறார்: "எனக்கு என்ன பிடிக்காதுன்னு சொன்னேன்?".

Context window மட்டும் வைத்திருந்தால், session 1-ல சொன்னது எல்லாம் மறந்து போயிருக்கும். Agent ஒவ்வொரு முறையும் முதல் முதல் போல behave பண்ணும்.

இது பிரச்சனை ஆகிறது ஏனெனில்:
* User-க்கு personalization வேண்டும்
* Long conversations-ல continuity வேண்டும்
* Knowledge base-ல இருந்து facts-ஐ திரும்ப திரும்ப retrieve பண்ணக்கூடாது
* Agent ஒரு முறை கற்றதை அடுத்த session-லயும் use பண்ண வேண்டும்

What goes wrong if we don't have this? Agent stateless ஆக இருக்கும், costly re-computation, hallucination அதிகரிக்கும்.

## 2. Mental Model

Memory என்பது agent-க்கு long-term storage + retrieval system.

Simple ஆக சொன்னால்: short-term memory = context window, long-term memory = persistent store.

ஒரு human engineer-க்கு ஒப்பிட்டால்:
* Working memory = உடனடி chat history
* Long-term memory = notebook, wiki, database, vector store ல எழுதி வைத்தது

AI Memory-ல மூன்று layer உள்ளது:

1. **Short-term / Episodic memory**: Current session-ல உள்ள recent turns. Context window-ல வைத்திருக்கும்.
2. **Working memory**: Session cross-ல தற்காலிக state, e.g., multi-step task progress.
3. **Long-term memory**: Persistent, user-specific, domain-specific knowledge.

நாம் இப்போது long-term memory types-ஐ பார்க்கிறோம்.

## 3. How It Works

Long-term memory என்பது data + retrieval mechanism.

Data என்ன?
* User profile facts: name, role, preferences
* Conversation history summaries
* Agent experiences: past decisions, tool calls, outcomes
* Domain knowledge: documents, notes, embeddings

Retrieval எப்படி?
User query வரும்போது, agent அதை embed செய்து vector database-ல similarity search செய்யும். Relevant memories-ஐ fetch பண்ணி context window-ல inject பண்ணும்.

Core loop:
Query → Embed → Retrieve from long-term store → Rerank → Inject into prompt → Generate

Memory-ஐ write பண்ணும்போது, raw conversation-ஐ முழுவதும் சேமிக்காமல், extract → summarize → compress → store என்று செய்வார்கள். இல்லை என்றால் storage cost, noise எல்லாம் அதிகரிக்கும்.

## 4. Architectural Reasoning

Long-term memory ஏன் தேவை?

* Continuity: Session A-ல கற்றதை Session B-ல use பண்ண வேண்டும்
* Personalization: User specific facts-ஐ maintain பண்ண வேண்டும்
* Knowledge reuse: Repeated queries-க்கு recompute பண்ணாமல் retrieve பண்ண வேண்டும்

When to use?
* Agent multiple sessions-ல interact பண்ணும் போது
* User profile, preferences முக்கியம்
* Domain knowledge large and static
* Compliance/audit trail வேண்டும்

Alternatives:
* Context window மட்டும்: Simple, but limited to ~128k tokens, expensive, forgets
* Summarization per session: Cheaper but loses details
* Long-term memory with vector DB: Persistent, scalable, searchable

Architect ஏன் choose பண்ணுவார்? Cost vs personalization trade-off. Short-term மட்டும் போதும் என்றால் memory system சேர்க்காமல் போகலாம்.

## 5. Trade-offs

1. **Recall accuracy vs noise**
Better retrieval = better answer. ஆனால் irrelevant memories-ஐ fetch பண்ணினால் context pollution ஆகும், hallucination அதிகரிக்கும். Reranking, filtering தேவை.

2. **Freshness vs stability**
Memory எப்போது update பண்ணுவது? User preferences மாறும். Stale memory-ஐ திரும்ப திரும்ப use பண்ணினால் wrong personalization. TTL, versioning, overwrite policies தேவை.

3. **Privacy / security vs personalization**
User-specific long-term memory என்பது PII. Storage, access control, encryption, deletion on request என்பது compliance requirement. Multi-tenant isolation must.

4. **Write cost vs read quality**
Every turn-ஐ store பண்ணினால் cheap. ஆனால் summarization, extraction pipeline சேர்த்தால் quality better but latency & cost அதிகம்.

Failure modes:
* Memory leak: irrelevant facts accumulate
* Memory hallucination: agent wrongly assumes memory exists
* Retrieval failure: important memory miss due to bad embedding

## 6. Practical Example

Enterprise AI assistant for a bank.

User: Relationship Manager. Customer data, notes, past interactions உள்ளன.

Architecture:
* Conversation → Summarizer → Extract structured facts: customer_id, last meeting date, risk appetite, product interest
* Facts stored in relational DB for structured query + vector DB for free text notes
* Retrieval: User query வரும்போது, customer_id-ல fetch structured profile, vector search-ல relevant notes fetch
* Inject into prompt with clear delimiters: `MEMORY: ...`

Result: Agent சொல்லும்: "நீங்கள் last month Senthil-க்கு loan renewal பற்றி பேசினீர்கள், அவர் 7% rate வேண்டும் என்று கேட்டிருந்தார்".

Without long-term memory, agent ஒவ்வொரு முறையும் "நான் தெரியவில்லை" என்று சொல்லும்.

## 7. Reasoning Challenge

உங்கள் AI agent-க்கு 2 வகையான long-term memory வேண்டும்:

A. User personal preferences: "எனக்கு tables வேண்டாம்"
B. Domain knowledge: Company policy docs, 500 pages

இரண்டுக்கும் retrieval strategy வேறுபடுமா? எந்த memory-ஐ எப்படி store செய்வீர்கள், எப்படி retrieve செய்வீர்கள்? Consistency, freshness, access control-ல என்ன வித்தியாசம் வரும்?

## 8. Key Takeaways

* Long-term memory என்பது context window-ன் extension, persistent store + retrieval system
* Memory types-ஐ separate பண்ணுங்கள்: user profile vs domain knowledge vs agent experience
* Write path-ல summarization/extract பண்ணுங்கள், raw chat-ஐ முழுவதும் store பண்ணாதீர்கள்
* Retrieval quality = system quality. Bad recall > no memory
* Every memory decision என்பது privacy, cost, freshness trade-off
