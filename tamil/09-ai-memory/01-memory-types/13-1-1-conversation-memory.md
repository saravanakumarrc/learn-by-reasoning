# Conversation memory

> **Learning Path:** AI Memory
> **Section:** 13.1.1 — Memory types

## 1. Problem

ஒரு AI agent-ஐ chat பண்ணும்போது முதல் 5 turns சூப்பரா இருக்கும். 6வது turn-ல இருந்து "நான் யார்? என்ன பண்ணிட்டு இருந்தேன்?" என்று கேட்க ஆரம்பிக்கிறது.

ஏன்? ஏனென்றால் model-க்கு context window மட்டுமே தெரியும். User session-க்குள்ளேயும் கூட, ஒவ்வொரு request-மும் கொஞ்சம் நினைவை மறந்துவிடுகிறது. Long-running conversation, multi-session follow-up, user preference retention எல்லாம் கைவிடப்படுகிறது.

**What goes wrong if we don't have this?**
- Repetition: user தன்னைப் பற்றி திரும்ப திரும்ப சொல்ல வேண்டும்
- Inconsistent answers
- Agent can't build relationship
- Cost ஏறும்: முழு history-யும் ஒவ்வொரு request-லும் அனுப்பினால் token cost அதிகம்

## 2. Mental Model

Conversation memory என்பது ஒரு agent-க்கு **நினைவாற்றல் layers** கொடுப்பது.

மனிதனை பாருங்கள்:
* Working memory = இப்போது பேசிக்கொண்டிருக்கும் sentence
* Short-term memory = இந்த session-ன் கடந்த சில நிமிடங்கள்
* Long-term memory = பழைய preferences, facts, உங்கள் பற்றிய தகவல்கள்

AI-க்கும் இதே மாதிரி 3 layer தேவை. இல்லையெனில் அது stateless chatbot மட்டுமே.

## 3. How It Works

**1. Conversation / Session Memory - Short-term**
இது current session-ன் recent turns-ஐ keep செய்கிறது. Usually context window-க்குள் fit ஆகும் window-வை slide செய்து manage பண்ணுகிறோம்.

Technique: conversation history buffer, summarization, sliding window. Redis / in-memory store. TTL based.

**2. Episodic Memory - Medium-term**
ஒரு session முடிந்த பிறகும் தொடர்புடைய interactions-ஐ retain செய்கிறது. "Last week நீங்கள் X பற்றி கேட்டீர்கள்" என்று link செய்ய.

Implementation: vector database + metadata. Each conversation turn / session-ஐ embedding பண்ணி store. Retrieval = similarity search on user query.

**3. Semantic / Long-term Memory**
User profile, preferences, facts that change rarely. "User is vegetarian", "uses USD", "works in fintech".

Implementation: structured profile store, key-value DB, or vector DB with strong metadata filtering. Update via explicit extraction + confirmation.

All three layers work together at inference time:
Query → Retrieve relevant episodic + semantic → Build augmented prompt → Generate

## 4. Architectural Reasoning

எப்போது இது useful?

* Multi-turn task: booking, research, coding help
* Personal assistant: preferences முக்கியம்
* Customer support: history இல்லாமல் agent useless
* RAG agents: conversation memory + knowledge base memory combine ஆக வேண்டும்

Alternatives:
* Full history in context: simple, but cost high, window limit
* Summarization only: cheap, but detail loss
* No memory: stateless, cheap, poor UX

Architect decision point: **Consistency vs Freshness vs Cost**

## 5. Trade-offs

**1. Freshness vs Relevance**
பழைய memory-ஐ எப்போது discard பண்ணுவது? User preferences மாறும். Stale memory = hallucination. Need versioning + timestamp + update policy.

**2. Privacy & Security**
Conversation data PII நிறைந்தது. Long-term storage = compliance risk. Need encryption at rest, access control, retention policy, right to be forgotten.

**3. Retrieval Quality vs Latency**
Vector search + filtering செய்ய latency add ஆகும். Too much retrieval = context overload, model confuse ஆகும். Need ranking, top-k limit, reranking.

**4. Cost**
Every memory read = embedding + vector search + tokens. At scale இது cost significant. Cache hot sessions, summarize long sessions.

Failure modes:
* Memory poisoning: wrong fact stored, then repeated
* Context bloat: irrelevant history model-ஐ confuse செய்யும்
* Cross-user leakage: isolation fail ஆனால் serious

## 6. Practical Example

Enterprise support agent.

User: "நேற்று நான் கேட்ட payment issue முன்னேற்றம் என்ன?"
Session memory இல்லாமல் agent கேட்கும்: "நீங்கள் எந்த payment பற்றி பேசுகிறீர்கள்?"

Architecture:
* Session Memory: last 10 turns in Redis with TTL 24h
* Episodic Memory: each resolved ticket as document in vector DB with user_id, ticket_id, timestamp
* Semantic Memory: user profile in Postgres - customer tier, preferred language, payment method

Flow:
1. Query வரும்போது user_id filter பண்ணி episodic memory-ல recent tickets retrieve
2. Semantic memory-ல் preference load
3. Both-ஐ prompt-ல inject
4. Response generate

Result: agent context-aware, no repetition, consistent.

## 7. Reasoning Challenge

உங்களிடம் ஒரு chatbot உள்ளது. 1M daily active users. ஒவ்வொரு user-க்கும் average 15 turns per session, session duration 30 mins. You want continuity across sessions for 90 days.

எந்த memory type எங்கே store பண்ணுவீர்கள்? Redis vs Postgres vs Vector DB? Retrieval எப்படி செய்வீர்கள் cost-ஐ control பண்ண? Privacy requirement உள்ளது.

சொல்லுங்கள்: data model, retention policy, மற்றும் எப்போது summarization use பண்ணுவீர்கள்?

## 8. Key Takeaways

* Memory is layered: session, episodic, semantic. ஒவ்வொன்றுக்கும் வெவ்வேறு storage & lifecycle
* Memory = architectural decision, not feature. Cost, privacy, freshness trade-offs இருக்கு
* Retrieve less but relevant. Context bloat மோசமானது
* Always design for update & deletion. User data changes, and must be forgettable
