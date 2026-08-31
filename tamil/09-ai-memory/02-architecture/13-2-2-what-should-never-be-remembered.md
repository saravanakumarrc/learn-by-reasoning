# What should never be remembered?

> **Learning Path:** AI Memory
> **Section:** 13.2.2 — Architecture

### 1. Problem

உங்கள் AI agent ஒரு enterprise customer support system-ல run ஆகுது. User chat history-யை memory-ல வச்சு context maintain பண்ணுறீங்க. ஒரு நாள் support agent accidentally user-ன் credit card number, Aadhaar number, password reset link எல்லாம் memory-ல save ஆகிடுது.

இப்போ அந்த memory vector database-ல permanent ஆக இருக்கு. RAG pipeline அதை retrieve பண்ணி, இன்னொரு user-க்கு leak பண்ணிடுது. Compliance audit fail ஆகுது. GDPR, PCI-DSS breach ஆகுது.

இங்கே கேள்வி இல்லை "memory எப்படி வேலை செய்யும்" என்பது. கேள்வி இது: **எதை நாம் memory-ல வைக்கவே கூடாது?**

Memory என்பது convenience tool. அது security, privacy, correctness ஆகியவற்றை compromise பண்ணக்கூடாது.

### 2. Mental Model

Memory-ல இரண்டு வகை data இருக்கு:

1. **Knowledge** - Stable, generalizable, safe to retain. Ex: user prefers Tamil, user is on plan Gold, company policy for refund.
2. **Toxic context** - Sensitive, ephemeral, identifiable, or incorrect. Ex: PII, secrets, one-time tokens, raw conversation transcript, hallucinated facts.

Architecturally, memory is not a dump. Memory is a **curated store with retention policy**. நாம் remember பண்ணுறது என்ன, forget பண்ணுறது என்ன என்பதை consciously decide பண்ணணும்.

### 3. How It Works

ஒரு production AI memory system-ல நீங்கள் இதை enforce பண்ணுவீங்க:

* **Ingestion filter**: Memory write-க்கு முன் PII redaction, secret detection, classification.
* **Retention policy**: TTL, scope, user consent boundary.
* **Access control**: Who can read/write this memory? User-specific vs shared.
* **Non-persistence by default**: Ephemeral session context should stay in short-term memory, not long-term vector DB.

உதாரணமா, ஒரு banking chatbot-ல user சொன்ன "My PAN is ABCDE1234F" என்பது embedding ஆகி vector store-ல போகக்கூடாது. அதை நீங்கள் either drop பண்ணனும் அல்லது tokenized reference ஆக மாற்றனும்.

### 4. Architectural Reasoning

Memory useful ஆகும் போது:

* User preferences, long-term intent, cross-session continuity தேவைப்படும் போது.
* Agent needs to reason over past decisions.

Memory harmful ஆகும் போது:

* Data sensitive ஆக இருந்தால்.
* Data ephemeral ஆக இருந்தால், e.g., one-time OTP, temporary link.
* Data incorrect or user-provided unverified fact ஆக இருந்தால், அது hallucination-ஐ reinforce பண்ணும்.

அதனால் architect-ஆக நீங்கள் முடிவு பண்ணுவது:

* What is the **memory boundary**? Session vs user vs organization.
* What is the **retention window**? 24 hours vs 90 days vs forever.
* What is the **classification tier**? Public, internal, confidential, restricted.

இதை policy as code ஆக define பண்ணுவது தான் real architecture.

### 5. Trade-offs

* **Utility vs Privacy**: அதிகம் remember பண்ணினால் personalization improve ஆகும், ஆனால் risk அதிகரிக்கும்.
* **Accuracy vs Completeness**: Raw transcript எல்லாம் save பண்ணினால் context rich ஆக இருக்கும், ஆனால் noise, hallucination, PII mix ஆகும். Summarized, cleaned memory சேர்த்தால் safe ஆனால் information loss இருக்கும்.
* **Cost vs Compliance**: Long-term memory storage cheap. ஆனால் data deletion, audit, encryption, access logging expensive. What you never store, you never have to delete.

Failure mode: Memory poisoning. User தவறான info கொடுத்தால் அது memory-ல settle ஆகி, agent அதை fact ஆக நம்ப ஆரம்பிக்கும். அதனால் source attribution மற்றும் confidence scoring தேவை.

### 6. Practical Example

Enterprise RAG agent for HR.

User asks: "I want to apply for parental leave. My employee ID is 45219 and I have a medical certificate attached."

What should never be remembered?

* Employee ID + medical certificate content = PII + health data. Should never go to long-term vector DB.
* Raw chat transcript with personal reason.

What should be remembered?

* User has queried parental leave policy before.
* User prefers documents in Tamil.
* General preference: notify via email.

Architecture:

Ingestion pipeline-ல classifier run ஆகும். PII detected -> redact and route to ephemeral session memory only. Policy summary மட்டும் persistent memory-க்கு போகும்.

Memory store இரண்டு tier: 
- Short-term Redis with TTL 24h for raw session.
- Long-term vector DB for sanitized, aggregated preferences.

### 7. Reasoning Challenge

உங்களிடம் multi-agent system இருக்கு. Agent A customer support chat பண்ணுது. Agent B அதே user-ன் historical tickets-ஐ analyze பண்ணி upsell recommendation கொடுக்குது.

User chat-ல அவர் password reset link, bank details mention பண்ணியிருக்கார். இந்த data-வை Agent B க்கு share பண்ணலாமா? Memory layer-ல என்ன policy வைப்பீங்க? ஏன்?

நினைவில் வைக்கவே கூடாத data-வை share பண்ணினால் என்ன consequence வரும்?

### 8. Key Takeaways

* Memory is a design decision, not a default store. Remember by intent, not by accident.
* PII, secrets, tokens, health/financial data, ephemeral context - இவற்றை long-term memory-ல வைக்கவே கூடாது.
* Classify, redact, and apply TTL before write. Forget is a feature.
* Every memory write should answer: Who can read this? For how long? What if it leaks?

இது புரிஞ்சா தான் AI memory system secure ஆகவும் useful ஆகவும் இருக்கும்.
