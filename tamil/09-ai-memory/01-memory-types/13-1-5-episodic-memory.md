# Episodic memory

> **Learning Path:** AI Memory
> **Section:** 13.1.5 — Memory types

## 1. Problem

உங்களிடம் ஒரு AI agent இருக்கு. அது customer support chat-ல work பண்ணுது.

Customer இன்னைக்கு கேட்டது: "என் last order எங்க இருக்கு?"
நாளைக்கு அதே customer கேக்குது: "நீ கடந்த தடவை சொன்னது என்ன?"

Agent-க்கு என்ன தேவை?
இப்போதைக்கு context மட்டும் போதாது. Agent அந்த customer-உடன் நடந்த **நிகழ்வு** ஞாபகம் வைத்திருக்க வேண்டும்.

எந்த product, எந்த date-ல order பண்ணினார், என்ன complaint பண்ணினார், நீங்கள் என்ன promise பண்ணினீர்கள் — இது எல்லாம் time-stamped experience.

இதை வைத்திருக்காமல், agent எப்போதும் generic ஆக பதில் தரும். Personalization இல்லை, continuity இல்லை. User trust போய்விடும்.

**What problem became painful?** Same user, multiple interactions over time. System-க்கு அந்த interaction-ஐ ஒரு story ஆக நினைவில் வைக்க தெரியவில்லை.

## 2. Mental Model

Episodic memory = **when, where, who, what happened**.

Semantic memory என்பது facts: "iPhone 16 price is 79,000". Static knowledge.

Episodic memory என்பது experience: "2025-08-12 அன்று 11:23 AM-க்கு user Arjun உடன் chat ஆரம்பித்து, order #48291 delay பற்றி புகார் செய்தான். நான் refund approve செய்ததாக சொன்னேன்."

இது ஒரு memory with context and timestamp. Human brain-ல நாம் personal episodes ஆக நினைவு வைக்கிறோம். AI-க்கு அதை simulate பண்ண வேண்டும்.

## 3. How It Works

Episodic memory system basically 3 பகுதிகள்:

**1. Capture:** Conversation, action, event நடக்கும் போது அதை capture பண்ணி structure செய்ய வேண்டும்.
Input = raw interaction. Output = episode object.

Example episode:
```
{
  timestamp: 2025-08-12T11:23:00Z,
  user_id: u_4821,
  session_id: s_991,
  event_type: "support_chat",
  summary: "Order delay complaint",
  entities: {order_id: 48291, product: "iPhone 16"},
  outcome: "refund promised"
}
```

**2. Store:** Episodes store ஆகும். Vector database + relational store combo பொதுவாக use பண்ணுவார்கள்.
Vector embedding for semantic search: "என் last order" என்ற query-க்கு relevant episodes கண்டுபிடிக்க.
Relational metadata for filtering: user_id, date range, event_type.

**3. Retrieve:** New query வரும்போது, current context + relevant past episodes retrieve பண்ணி LLM-க்கு provide பண்ணுவது.
RAG pipeline-ல இது memory retrieval step.

இது working memory அல்ல. Long-term, persistent.

## 4. Architectural Reasoning

Episodic memory useful ஆகும் போது?

* Agent needs continuity across sessions
* Personalization requires history of past interactions
* Audit / compliance க்கு "என்ன சொன்னோம்" proof வேண்டும்
* Multi-turn planning: past attempt fail ஆனது, அதை திரும்ப try பண்ணக்கூடாது

Constraint it addresses: LLM stateless. Model-க்கு past session தெரியாது. System-க்கு memory layer வேண்டும்.

Alternatives:
* **Full conversation history replay:** Simple but expensive, context window overflow, noise அதிகம்.
* **Summarized session memory:** Semantic memory. Useful but loses specific details like timestamp, exact promise.
* **Episodic memory:** Structured episodes with metadata, searchable, replayable.

Architect choose episodic memory when fidelity + retrieval control முக்கியம்.

## 5. Trade-offs

**Storage cost vs usefulness:** Every interaction-ஐ episode ஆக்கி store பண்ணினால் data volume வேகமாக வளரும். Summarize பண்ணி prune பண்ண வேண்டும்.

**Precision vs recall:** Too specific episodes -> miss similar intent. Too generic -> wrong episode retrieve ஆகும். Embedding quality and summarization strategy matter.

**Privacy & security:** Episodes contain PII. User-specific memory isolation வேண்டும். GDPR right to be forgotten -> specific user's episodes delete செய்ய வேண்டும். Vector DB-ல hard delete சிக்கல்.

**Freshness vs hallucination:** Retrieval system outdated episode கொடுத்தால் agent wrong info சொல்லும். Timestamp filter, recency weighting must.

**Operational complexity:** Capture pipeline, embedding pipeline, retrieval pipeline, retention policy எல்லாம் maintain பண்ண வேண்டும். Team size small என்றால் over-engineering ஆகும்.

## 6. Practical Example

Enterprise customer support agent.

Architecture:
`Chat API -> Conversation Capture Service -> Episode Builder -> Vector DB [episodes] + Postgres [metadata]`
`Retriever -> RAG -> LLM`

User returns after 3 days: "நீ கடந்த தடவை சொன்ன refund எப்போ வரும்?"
Retriever query: user_id + semantic similarity on "refund". Top 2 episodes from last 7 days retrieve.
LLM receives current chat + episodes: summary, timestamp, outcome.
Agent can answer: "நீங்கள் 12-08-க்கு order #48291 delay குறித்து பேசினீர்கள். Refund 5 working days-ல process ஆகும் என்று சொன்னேன். நிலை இப்படி இருக்கு..."

Without episodic memory, agent would ask repeat questions. With it, continuity உண்டு.

## 7. Reasoning Challenge

உங்களிடம் banking assistant agent இருக்கு. User ஒரு loan application பற்றி 3 வாரங்களாக பேசுகிறார். 8 sessions நடந்துள்ளது. Agent ஒவ்வொரு session-லயும் அதே document request செய்கிறது.

என்ன problem? எப்படி episodic memory design பண்ணி இதை தீர்ப்பீர்கள்? What metadata store பண்ணுவீர்கள், என்ன prune strategy use பண்ணுவீர்கள்?

## 8. Key Takeaways

* Episodic memory = timestamped experiences, not just facts.
* It solves continuity and personalization across sessions.
* Capture -> Store -> Retrieve pipeline வேண்டும். Vector + relational combo works well.
* Trade-off: fidelity vs cost, privacy vs personalization, freshness vs hallucination.
* Use it when agent needs to remember *what happened with whom and when*, not just *what is true*.
