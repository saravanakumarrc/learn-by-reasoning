# Semantic memory

> **Learning Path:** AI Memory
> **Section:** 13.1.4 — Memory types

## 1. Problem

உங்க AI agent க்கு conversation context மட்டும் கொடுத்தால் போதுமா?

User கேட்கிறார்: "என்னோட கடந்த மாத revenue எவ்வளவு?"
Agent கடந்த 10 messages-ல் அது இல்லை. அது மறந்துவிடும்.

அடுத்து user கேட்கிறார்: "நாம எப்போதும் சொன்னதை போல செய்".
அது என்ன? எந்த தடவை? எந்த user?

ஒரு agent-க்கு தேவை:
- **Episodic memory**: என்ன நடந்தது, எப்போது நடந்தது
- **Semantic memory**: என்ன உண்மை, என்ன நிரந்தரமான knowledge

Semantic memory இல்லாமல், agent ஒவ்வொரு முறையும் முதல் முதல் கற்க வேண்டும். அதே facts-ஐ repeatedly retrieve பண்ண வேண்டும். Cost அதிகம், latency அதிகம், hallucination அதிகம்.

**What problem became painful?** Context window limited, long-term facts decay, agent can't build consistent world model.

## 2. Mental Model

Semantic memory = agent-ன் **knowledge base**.

Episodic memory என்பது diary போன்றது: "2025-11-01, user X asked about revenue".
Semantic memory என்பது encyclopedia + company wiki போன்றது: "Company X revenue is calculated from Stripe + Shopify, fiscal year starts April, user X is finance lead".

Episodic என்பது *when it happened*. Semantic என்பது *what is true*.

ஒரு human போல நினைக்கவும்: நீங்கள் ஒரு குறிப்பிட்ட உரையாடலை மறந்தாலும், "பூமி வட்டமானது", "என் பெயர்..." போன்ற உண்மைகள் நிலைத்திருக்கும்.

Agent-க்கு semantic memory இல்லாமல், அது ஒரு goldfish மாதிரி.

## 3. How It Works

Semantic memory-ஐ build பண்ண, agent தன்னுடைய experience-ஐ extract பண்ணி, generalize பண்ணி, store பண்ணும்.

Typical flow:

1. **Ingest**: Conversation, documents, tool outputs.
2. **Extract**: Entities, relations, facts, preferences, constraints.
3. **Consolidate**: Duplicate-ஐ merge பண்ணு, contradictions-ஐ resolve பண்ணு.
4. **Store**: Structured knowledge graph or vector store with metadata.
5. **Retrieve**: Query time-ல் relevant semantic facts-ஐ context-ல் inject பண்ணு.

Implementation options:
- **Vector DB + embedding**: semantic search-க்கு நல்லது. "revenue calculation" போன்ற fuzzy queries-க்கு.
- **Knowledge graph / graph DB**: relations explicit ஆக வேண்டும் என்றால். "User X owns project Y" போன்றது.
- **Relational DB + structured schema**: well-defined facts-க்கு. User profile, preferences.

பெரும்பாலும் hybrid: vector for recall, graph/relational for precise facts.

Retrieval என்பது RAG போல தான், ஆனால் source என்பது agent-ன் own past experience, external docs அல்ல.

## 4. Architectural Reasoning

Semantic memory எப்போது useful?

- Agent needs persistent world model across sessions.
- Facts repeat across conversations. e.g., company policies, user preferences, product catalog.
- Need consistency: ஒரே user-க்கு ஒரே answer.
- Need reasoning over long-term knowledge, not just last 10 messages.

Alternatives:
- **Long context window only**: Simple, but cost scales linearly, forgets old facts, no generalization.
- **Episodic memory only**: Conversation history store பண்ணி retrieve பண்ணலாம். ஆனால் raw history-ல் signal noise அதிகம்.
- **Semantic memory**: Extract and compress. Less noise, faster retrieval.

Architectural decision: Extract at write time vs read time?

Write-time extraction: background job ஓடி facts-ஐ consolidate பண்ணும். Read latency குறைவு, but stale ஆகலாம்.
Read-time extraction: on-demand summarization. Fresh, but latency அதிகம்.

பெரும்பாலும் write-time + periodic consolidation.

## 5. Trade-offs

**Storage vs Accuracy**: More aggressive summarization = smaller store, ஆனால் nuance இழக்கும்.

**Freshness vs Stability**: Fact update ஆனால் old version-ஐ எப்படி invalidate பண்ணுவது? Versioning தேவை.

**Generalization vs Hallucination**: Extraction model தவறாக infer பண்ணினால், wrong semantic fact store ஆகி, அது permanent bias ஆகும்.

**Retrieval precision**: Vector search approximate. Exact facts-க்கு hybrid retrieval தேவை: vector + keyword + structured filter.

Failure modes:
- Contradictory facts merge ஆகாமல்.
- User preference drift: user மாறினார், old preference இன்னும் active.
- Privacy & compliance: semantic memory-ல் PII store ஆனால் GDPR deletion எப்படி?

## 6. Practical Example

Enterprise support agent.

User: "நான் Chennai office-ல இருக்கேன், எனக்கு laptop issue".
Agent semantic memory-ல்: User X = Chennai office, role = Design Lead, device = MacBook Pro M3, prefers remote support.

இது episodic அல்ல. இது semantic fact.

அடுத்த session-ல் user: "My laptop is slow".
Agent context window-ல் previous chat இல்லை. ஆனால் semantic memory retrieve பண்ணி: device model தெரியும், location தெரியும், support SLA தெரியும். அதனால் தான் appropriate troubleshooting steps suggest பண்ண முடியும்.

Architecture:
- Conversation → LLM extraction → `facts` table: `{subject, predicate, object, confidence, source, timestamp}`
- Vector store for fuzzy facts: preferences, notes.
- Retrieval: query "laptop slow" → semantic search → facts about device, user, past issues.

Cost reduce ஆகும், because full history retrieve பண்ண தேவை இல்லை.

## 7. Reasoning Challenge

உங்களுக்கு 10,000 users இருக்கும் customer success agent. ஒவ்வொரு user-க்கும் preferences, contract terms, past incidents தேவை.

நீங்கள் semantic memory-ஐ design பண்ண வேண்டும்.

கேள்வி:
- Vector DB மட்டும் போதுமா? அல்லது structured DB + vector hybrid வேண்டுமா?
- Fact update ஆனால், எப்படி old version-ஐ invalidate பண்ணுவீர்கள்?
- Confidence score எப்படி use பண்ணுவீர்கள் retrieval-ல்?

இதற்கு எந்த trade-off-ஐ accept பண்ணுவீர்கள்: consistency vs freshness?

## 8. Key Takeaways

- Semantic memory = persistent, generalized knowledge. Episodic = specific events.
- Context window-ஐ replace பண்ணாது, complement பண்ணும்.
- Extract-consolidate-store-retrieve pipeline தேவை. Quality of extraction = quality of memory.
- Hybrid storage வேண்டும்: vector for recall, structured/graph for precise facts.
- Every write creates a maintenance problem: updates, contradictions, privacy deletion.

**Mental model to leave with:** Semantic memory is the agent's long-term understanding of *what is true*, not just *what happened*.
