# Conversation memory

> **Learning Path:** AI Memory
> **Section:** 13.1.1 — Memory types

### 1. Problem

ஒரு chatbot-ஐ பேச வைக்கிறோம். User: "என் பெயர் Arjun". அடுத்த turn-ல: "எனக்கு ஒரு itinerary ப்ளான் பண்ணு". 

Agent-க்கு Arjun யார் என்று தெரியவில்லை. ஒவ்வொரு turn-ம் isolated ஆக இருந்தால் context இழந்துவிடும்.

இன்னும் மோசம்: User 10 நாட்களுக்கு முன் சொன்ன preference, budget, travel style எல்லாம் இப்போது தேவை. அதை எப்படி கொண்டு வருவது?

Conversation memory இல்லாமல், ஒவ்வொரு request-ம் முதல் முறையாகத் தெரிகிறது. User frustrated ஆகிறார். Repeating information ஆகிறது.

இந்த pain தான் memory types-ஐ உருவாக்கியது.

### 2. Mental Model

Conversation memory-ஐ 3 layer stack ஆக பார்.

**Short-term = Working memory**
இந்த session-க்குள் நடந்தது. Last few turns. LLM-ன் context window-க்குள் இருக்கிறது.

**Medium-term = Conversation memory / Session memory**
Session முடிந்த பிறகும் தக்க வைக்க வேண்டியது. User profile, preferences, past decisions.

**Long-term = Persistent memory / Knowledge memory**
User-க்கு மட்டுமல்ல, product-க்கும் தேவையான long lived facts. "Arjun likes vegetarian food, budget < 2L, hates flights before 9am". இது weeks/months வரை இருக்க வேண்டும்.

ஒரு conversation என்பது stream. Memory என்பது அந்த stream-ஐ எவ்வளவு தூரம் திரும்ப பார்க்க முடியும் என்பது.

### 3. How It Works

Practically, மூன்று வழிகள்:

**Context window.** LLM-க்கு உள்ளேயே last N tokens. Simple, fast, but limited and expensive. Long conversation-ல் cost ஏறும், மறந்துவிடும்.

**Conversation store.** Session ID-க்கு ஒரு table. Messages-ஐ append பண்ணி வைத்துக்கொள்வது. Retrieval-ன் போது recent messages + relevant summary-ஐ prompt-ல் சேர்ப்பது.

**External memory store.** Vector database / graph / relational DB. User profile, facts, embeddings. Query time-ல் retrieve செய்து context-ல் inject செய்வது.

Workflow: User input → retrieve relevant memory → build augmented prompt → generate → write back important facts to memory.

அதனால் memory = retrieve + write policy.

### 4. Architectural Reasoning

எப்போது தேவை?

* Multi-turn task completion. Booking, support, planning.
* Personalization. User-க்கு தனிப்பட்ட experience வேண்டும்.
* Agent continuity. Different tools, different steps.

Constraints-ஐ பார்:

* **Latency.** Retrieve செய்வது extra round trip.
* **Cost.** Bigger context = more tokens.
* **Privacy.** User data retain செய்வது compliance issue.
* **Correctness.** Stale memory toxic ஆகும்.

Alternatives:

* Stateless per turn. Cheapest, zero retention. Good for simple Q&A.
* Full history in context. Easy but scales badly.
* Summarization. Compress history to key facts.
* Hybrid: short-term in context + long-term in vector DB.

Architect choose பண்ணும்போது question: "எவ்வளவு தூரம் நினைவில் வைக்க வேண்டும்? எவ்வளவு செலவு ஏற்றுக்கொள்ளலாம்?"

### 5. Trade-offs

**Recency vs Relevance.** Recent messages எப்போதும் முக்கியமா? சில சமயம் 10 turns முன் சொன்ன budget தான் முக்கியம். Retrieval ranking தேவை.

**Fidelity vs Compression.** Full transcript வைத்தால் accurate ஆனால் noisy. Summary வைத்தால் concise ஆனால் loss of detail. Summarization drift ஆகும்.

**Freshness vs Stability.** User preference மாறும். Old fact-ஐ overwrite எப்படி செய்வது? Versioning மற்றும் timestamp தேவை.

**Privacy vs Personalization.** More memory = better UX. More retention = higher risk. GDPR delete, anonymize policy தேவை.

Failure modes: Memory poisoning - hallucinated fact store ஆகி போவது. Context overflow - irrelevant history prompt-ஐ மூழ்கடிப்பது. Stale preference - user now wants non-veg, system still serves veg.

### 6. Practical Example

Enterprise support agent.

User first conversation: "என் account ID 44521, நான் Chennai-ல இருக்கேன், preferred language Tamil".

System: Short-term memory-ல் இதை வைத்து respond செய்யும். Session முடிந்ததும், key facts extract: account_id, location, language. Write to conversation store + user profile DB.

2 weeks later user returns: "மீண்டும் என் bill பார்க்கணும்".

System: Session memory-ல் retrieve பண்ணி account_id தெரிந்து, language Tamil-ல் respond. No re-ask.

3 months later user says: "இனி English-ல பேசு".

System should update preference, old Tamil preference-ஐ invalidate செய்ய வேண்டும்.

Architecture: Messages table per session, user profile in Postgres, important facts embeddings in vector DB for semantic search. Write policy: extract structured facts with LLM, validate, then store.

### 7. Reasoning Challenge

உங்களிடம் 10M users இருக்கிறார்கள். ஒவ்வொரு user-க்கும் average 50 conversations per month. ஒவ்வொரு conversation-லும் ~200 messages.

உங்கள் agent-க்கு last 5 conversations-ல் இருந்து personalization தேவை, ஆனால் full history-ஐ context-ல் வைக்க முடியாது. Latency < 600ms வேண்டும். Cost control முக்கியம்.

நீங்கள் memory types-ஐ எப்படி design செய்வீர்கள்? Short-term, medium-term, long-term-க்கு எந்த storage, எந்த retrieval strategy use பண்ணுவீர்கள்? ஏன்?

### 8. Key Takeaways

* Conversation memory என்பது session continuation அல்ல, personalization மற்றும் continuity க்கான system.
* Short-term = context window, Medium-term = session store, Long-term = persistent profile + vector store.
* Memory decisions = retrieve policy + write policy + retention policy.
* Every memory solution adds latency, cost, privacy risk. Choose based on how far back you really need to remember.
