# When should memory be retrieved?

> **Learning Path:** AI Memory
> **Section:** 13.2.4 — Architecture

## 1. Problem

உங்க AI agent ஒரு user-க்கு conversation continue பண்ணுது. User சொல்றாரு: "நேத்து நான் சொன்ன budget limit-ஐ மறந்துட்டியா?"

Agent-க்கு இரண்டு option இருக்கு.

1. எல்லா previous conversation-ஐயும் context window-ல dump பண்ணிட்டு LLM-க்கு கொடுக்கிறது.
2. தேவைப்படும்போது மட்டும் relevant memory-ஐ retrieve பண்ணி கொடுக்கிறது.

முதல் approach-ல என்ன ஆகும்? Context window நிரம்பும், cost அதிகரிக்கும், latency போகும், irrelevant info noise ஆகும். LLM hallucinate பண்ணும் chance அதிகம்.

இரண்டாவது approach-ல தேவையான memory மட்டும் தரலாம். ஆனா எப்போ retrieve பண்ணனும்? எல்லா turn-லயும் retrieve பண்ணினா over-retrieval. Retrieve பண்ணாம விட்டா stale அல்லது incomplete answer.

> **Core pain:** Retrieval is expensive and noisy. Do it too much, you pay cost and latency. Do it too little, you lose personalization and continuity.

## 2. Mental Model

Memory retrieval என்பது database query மாதிரி இல்ல. இது **decision gate**.

User input வந்ததும் agent ஒரு கேள்வி கேட்டுக்கணும்:
> இந்த turn-க்கு past memory தேவையா? எந்த level-ல தேவை?

அதற்கு மூன்று levels இருக்கு:

* **No retrieval** — current user message மட்டும் போதும்
* **Short-term / session memory** — இந்த conversation-க்குள்ள recent facts
* **Long-term / persistent memory** — user profile, preferences, past interactions, knowledge base

Retrieval என்பது always-on filter அல்ல. இது **conditional and selective**.

## 3. How It Works

Typical flow:

1. User query வரும்
2. **Retrieval policy** evaluate ஆகும் — query signals, conversation state, task type
3. தேவைப்பட்டால் embedding generate பண்ணி vector database / memory store-ல search
4. Relevant chunks retrieve பண்ணி rerank பண்ணி
5. LLM-க்கு context-ல கொடுக்கிறது
6. Generate response

முக்கியமானது step 2. அதுதான் architecture decision.

## 4. Architectural Reasoning

**When should memory be retrieved?**

### A. Task type அடிப்படையில்

* **Transactional / one-off queries:** "5*7 என்ன?" — memory தேவையில்லை.
* **Continuity dependent:** "நேற்று சொன்ன design-ஐ மாற்று" — session memory தேவை.
* **Personalization dependent:** "எனக்கு பிடித்த budget range-ல சொல்லு" — long-term user memory தேவை.
* **Knowledge augmented:** "எங்க company policy என்ன?" — RAG retrieval தேவை.

### B. Conversation state அடிப்படையில்

Conversation start-ல ஒரு quick lightweight retrieval போதும். Multi-turn deep dive-ல incremental retrieval தேவை. User explicit reference செய்யும்போது — "அதை", "அந்த report" — definite retrieval trigger.

### C. Cost / Latency constraints அடிப்படையில்

High QPS chatbot-ல every turn retrieval செய்ய முடியாது. அப்போ heuristic gate போடணும். Eg: query contains pronoun, entity reference, task continuation signal என்றால் மட்டும் retrieve.

**Alternatives:**

* **Always retrieve:** Simple to build, expensive, noisy.
* **Never retrieve:** Cheap, but stateless, bad UX.
* **Selective retrieval with policy:** Best balance. Policy can be rule-based, LLM-based classifier, or hybrid.

## 5. Trade-offs

* **Recall vs Precision:** Wider retrieval = more recall but noise increases. Narrow retrieval = clean but miss relevant facts.
* **Latency vs Freshness:** Real-time retrieval தரும் freshness ஆனால் latency add ஆகும். Cache பண்ணினால் fast ஆனால் stale ஆகும்.
* **Cost vs Quality:** Vector search + rerank cost per turn. Retrieval frequency அதிகரித்தால் token cost அதிகரிக்கும்.
* **Privacy / Security:** User memory retrieve பண்ணும்போது access control தேவை. எல்லா data-யும் எல்லா agent-க்கும் தெரியக்கூடாது.

Failure mode: **Retrieval cascade**. ஒரு bad retrieval தவறான context கொடுத்து LLM-ஐ mislead பண்ணும். அதனால retrieval quality-க்கு guardrails தேவை.

## 6. Practical Example

Enterprise support agent.

User: "My order is delayed"

First turn: Session memory retrieve பண்ணாம போகலாம். Agent user ID-ஐ identify பண்ணி, order lookup பண்ணி கேள்வி கேட்கும்.

Next turn: "நேற்று சொன்ன order-ஐ பார்த்தியா?"

இங்கே pronoun "நேற்று", "order" என்ற reference இருக்கு. Retrieval trigger ஆகும். Short-term session memory-ல recent order mention retrieve பண்ணி.

Later: "இதே மாதிரி முன்னாடி எனக்கு ஆனது போல ஒரு refund வேணும்"

இங்கே long-term user memory தேவை. Past refund history retrieve பண்ணி pattern புரிஞ்சிக்க.

Architecture: Rule-based classifier first checks for explicit reference signals. If hit, do session retrieval. If not, LLM-based intent classifier decides if personalization needed. Then vector search.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு... Wait different.

Scenario: ஒரு AI coding assistant. User பல files மாற்றி மாற்றி கேள்வி கேட்கிறார். Every turn-ல full repo context retrieve பண்ணினால் latency 2 sec ஆகும். ஆனால் file-level context இல்லாமல் code suggest பண்ண முடியாது.

நீங்கள் retrieval எப்போ trigger செய்வீர்கள்? எந்த granularity-ல retrieve செய்வீர்கள்? ஏன்?

## 8. Key Takeaways

* Memory retrieval என்பது always-on அல்ல, conditional decision.
* Task type, conversation state, and explicit reference signals தான் retrieval trigger ஆக இருக்க வேண்டும்.
* Session memory vs long-term memory vs RAG knowledge என்று level பிரித்து retrieve பண்ணினால் cost, latency, noise குறையும்.
* Every retrieval adds cost and risk of noise. Retrieve only when the problem justifies it.
