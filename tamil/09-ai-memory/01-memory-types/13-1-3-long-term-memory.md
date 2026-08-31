# Long-term memory

> **Learning Path:** AI Memory
> **Section:** 13.1.3 — Memory types

## 13.1.3 — Memory types: Long-term memory

### 1. Problem

ஒரு AI agent-ஐ நீங்கள் build பண்ணும்போது, session முடிந்ததும் எல்லாம் மறந்துவிடுகிறது. அதே user மறுபடி வந்தால், "நான் யார்? என் பிராஜெக்ட் என்ன?" என்று கேட்க வேண்டியிருக்கிறது.

Short-term memory, அதாவது conversation context window, சில ஆயிரம் tokens மட்டுமே வைத்திருக்கும். User-ன் preferences, past decisions, documents, past interactions — இவை எல்லாம் அடுத்த session-க்கு கொண்டு போக வேண்டும்.

**What goes wrong if we don't have this?** Every session starts from zero. User experience broken ஆகும், agent repetitive questions கேட்கும், personalization இருக்காது, முக்கியமான facts repeat ஆகும்.

அதனால் தேவை: session-க்கு அப்பால் survive பண்ணும் memory.

### 2. Mental Model

Long-term memory என்பது agent-ன் external brain.

Short-term = RAM. Fast, volatile, limited.

Long-term = Disk. Slowish, persistent, huge.

Agent ஒரு thought பண்ணும்போது, அது தேவையானதை மட்டும் long-term இலிருந்து retrieve பண்ணி, short-term context-ல் வைத்து reason பண்ணும்.

Mental model: **Store once, retrieve on demand, update over time.**

### 3. How It Works

Long-term memory வழக்கமாக மூன்று layer-களாக வேலை செய்கிறது:

**Capture → Store → Retrieve**

**Capture:** Conversation, user action, document upload, tool output ஆகியவற்றிலிருந்து relevant facts-ஐ extract பண்ண வேண்டும். Raw conversation-ஐ முழுவதும் store பண்ணுவது waste. Summarization, entity extraction, embedding generation பண்ணி structured form-ல் save பண்ணுவது.

**Store:** இரண்டு வகை storage.

* Structured: PostgreSQL / MongoDB-ல் user profile, preferences, facts table-ல் key-value அல்லது relational ஆக.
* Unstructured / Semantic: Vector database-ல் embeddings ஆக. "இதே போன்ற அர்த்தம்" என்று search செய்ய வேண்டும்போது.

Long-term memory என்பது vector store மட்டும் அல்ல. Vector store semantic recall-க்கு, relational store explicit facts & relationships-க்கு.

**Retrieve:** New query வந்தால், user ID + query context-ன் அடிப்படையில் relevant memories-ஐ fetch பண்ணி context window-ல் inject பண்ணுவது. Retrieval = hybrid search: keyword + vector similarity + metadata filter.

### 4. Architectural Reasoning

Long-term memory useful ஆகும்போது:

* User returning across sessions
* Personalization தேவை
* Knowledge base தேவை: documents, tickets, codebase
* Agent continuity தேவை

Constraint it addresses: context window limit and volatility.

Alternatives:

* Bigger context window: Cost அதிகம், linear growth, irrelevant noise. முழு history-யும் load பண்ண முடியாது.
* RAG only on external docs: user-specific learning இல்லை.
* No memory: Stateless agent.

ஏன் long-term memory தேர்வு? Because you need persistent, evolving user model. Trade-off ஏற்படும்: complexity & cost.

### 5. Trade-offs

**Recall accuracy vs storage cost.** Everything store பண்ணினால் vector DB cost & noise அதிகம். Too little store பண்ணினால் important facts miss ஆகும். Need summarization policy.

**Freshness vs stability.** User preference மாறும். Old memory stale ஆகும். Versioning, TTL, confidence score வேண்டும். இல்லை என்றால் agent hallucinate பண்ணும் with outdated info.

**Privacy & security.** Long-term memory = PII storage. Compliance, encryption, deletion on request, access control தேவை. Stateless agent-க்கு இந்த liability இல்லை.

**Retrieval latency.** Real-time agent-க்கு memory fetch 200ms-க்குள் வர வேண்டும். Heavy hybrid search, re-ranking குறிப்பாக cost ஆகும்.

Failure modes: Wrong memories retrieved → context poisoning. Too many memories retrieved → context window overflow. No deduplication → same fact repeated.

### 6. Practical Example

Enterprise support agent.

User first session: "நான் Acme bank-ல் SRE. நாங்கள் Kubernetes 1.29 use பண்றோம். On-call rotation என்னுடையது."

Agent captures entities: user_id, role=SRE, company=Acme bank, k8s_version=1.29, on_call=true. Structured DB-ல் store.

Later session: "production-ல் pod crash ஆகுது, எப்படி debug பண்ணுறது?"

Agent retrieves long-term memory: user is SRE, k8s 1.29, on-call. So response Kubernetes specific, kubectl commands, not generic. It also retrieves past incidents user faced, stored as embeddings in vector DB.

If user uploads runbook PDF, அதை chunk பண்ணி embeddings ஆக store. அடுத்த முறை "எங்கள் runbook-ல என்ன சொல்லியிருக்கு?" என்றால் semantic search-ல் relevant chunk retrieve ஆகும்.

Implementation: capture with LLM extractor, store in Postgres for structured facts + Pinecone/Qdrant for semantic, retrieve via hybrid search with user_id filter.

### 7. Reasoning Challenge

உங்களிடம் 10,000 active users இருக்கிறார்கள். ஒரு user-க்கு சராசரி 500 conversations per month. ஒவ்வொரு conversation-லும் 50 facts extract ஆகிறது.

இங்கே என்ன store பண்ணுவீர்கள்? எல்லா raw messages-ஐயும் store பண்ணுவீர்களா? அல்லது summarized facts மட்டுமா? Vector DB-ல் எதை put பண்ணுவீர்கள்? Retrieval time-ஐ எப்படி கட்டுப்படுத்துவீர்கள்?

Think about cost, noise, privacy.

### 8. Key Takeaways

* Long-term memory = persistence across sessions, not bigger context window.
* Structured store for explicit facts, vector store for semantic recall. Both தேவை.
* Capture smart, store less but relevant, retrieve filtered.
* Every memory system needs update policy, TTL, privacy controls. இல்லை என்றால் stale & toxic ஆகும்.
* Architecturally, memory is a separate bounded context with its own consistency, retrieval SLA, and cost model.
