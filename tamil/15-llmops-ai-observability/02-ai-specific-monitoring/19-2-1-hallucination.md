# Hallucination

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.1 — AI-specific monitoring

## 1. Problem

உங்க production-ல ஒரு RAG agent இருக்கு. User கேட்கிறார்: "கடந்த quarter-ல எங்க Chennai branch-க்கு விற்பனை எவ்வளவு?" 

Agent திருப்பி தருது: "₹ 4.2 Cr". Confidence high. ஆனா உண்மையில் vector database-ல அந்த data இல்ல. Model தன் training knowledge-ல இருந்து ஒரு plausible number-ஐ உருவாக்கி கொடுத்துவிட்டது.

இது hallucination. 

Traditional monitoring-ல CPU, latency, error rate எல்லாம் green. API 200 OK திரும்புது. ஆனால் business-க்கு தவறான முடிவு போய்விட்டது. 

இதுதான் AI-specific monitoring தேவைப்படும் இடம். Correctness, not just availability.

## 2. Mental Model

Hallucination = Model-க்கு தெரியாததை தெரிந்த மாதிரி சொல்லுவது.

ஒரு distributed system-ல service தெரியாத input வந்தால் 404/500 தரும். LLM தெரியாததை 500 தராது. அது ஒரு கதையை generate பண்ணும்.

மனதில் வைக்க வேண்டியது: **LLM ஒரு probability distribution machine. அது truth-ஐ predict பண்ணுவது இல்ல, next token-ஐ predict பண்ணுது.**

RAG இருந்தாலும் hallucination வரும்: retrieval failed, context truncated, conflicting docs, prompt ambiguous.

## 3. How It Works

Hallucination எப்படி உருவாகும்?

**1. No grounding:** Retrieval step-ல relevant document கிடைக்காமல் போகும். Model context window-ல empty இருக்கும். Model தன் internal knowledge-க்கு fallback ஆகும்.

**2. Bad retrieval:** Wrong document கிடைக்கும். Model அதை trust பண்ணி hallucinate பண்ணும்.

**3. Over-trust in prompt:** System prompt-ல strictness இல்லை. "I don't know" என்று சொல்லும் option இல்லாமல் போகும்.

**4. Ambiguity:** User query vague. Model fill-in-the-gap பண்ணும்.

Observability angle-ல நாம் பார்க்க வேண்டிய signals:
* Retrieval quality: top-k score, context relevance
* Generation confidence: token probability, perplexity
* Grounding: answer இல் உள்ள facts context-ல உள்ளதா?
* User feedback: thumbs down, correction

## 4. Architectural Reasoning

Hallucination-ஐ முழுவதுமாக தடுக்க முடியாது. Manage பண்ண வேண்டும்.

எப்போது இது critical?
* Financial advice, medical, legal, internal data lookup
* Agent autonomous actions எடுக்கும் system

Options:
* **Guardrails + validation:** LLM output-ஐ structured schema-க்கு validate பண்ணு. Pydantic output parser, regex checks.
* **Retrieval verification:** RAG-ல context citation compulsory ஆக்கு. "Source ID" return பண்ண சொல்லு. Post-hoc grounding check: answer-ல உள்ள claims-ஐ embedding similarity மூலம் context-ல verify பண்ணு.
* **Confidence thresholding:** Token logprob குறைவாக இருந்தால் "I don't know" என்று fallback.
* **Human-in-the-loop:** High risk queries-க்கு human review queue.

ஏன் architect இதை தேர்வு பண்ணுவார்? Because business risk > latency cost. Observability without grounding check என்பது blind.

## 5. Trade-offs

* **Strictness vs Helpfulness:** Model-ஐ "I don't know" சொல்ல வைத்தால் user experience drop ஆகும். ஆனால் hallucination risk குறையும்.
* **Latency vs Safety:** Retrieval verification, LLM-as-judge, citation check எல்லாம் extra hops. p95 latency increase ஆகும்.
* **Cost vs Coverage:** Hallucination detection models, embedding similarity checks cost add ஆகும். எல்லா query-க்கும் பண்ண முடியாது. Sampling / risk-based gating தேவை.
* **False positives:** Grounding checker strict ஆக இருந்தால் correct answers-ஐயும் reject பண்ணும். Tuning தேவை.

Failure mode: Monitor-ல hallucination rate track பண்ணினாலும், அதை label பண்ண யார்? Automated judge-லும் bias இருக்கும்.

## 6. Practical Example

Enterprise support agent.

Flow:
User query -> Retriever -> Context -> LLM -> Answer + citations

Observability pipeline:
* Log: query, retrieved doc IDs, retrieval scores, prompt, response, citations
* Real-time check: citation present? Retrieval score < 0.7? Response contains numeric claim without source?
* Async job: Embedding-based grounding check: answer sentences vs context similarity < threshold => flag hallucination
* Dashboard: hallucination rate per model version, per query type, per data source

ஒரு நாள் hallucination rate 2% -> 8% jump ஆனது. Investigation-ல தெரிந்தது vector DB reindex பண்ணப்போது chunk size மாறி retrieval quality drop ஆனது. Traditional monitoring-ல இது தெரியாது.

## 7. Reasoning Challenge

உங்களிடம் customer-facing RAG chatbot இருக்கு. 10k queries/day. Hallucination detection model add பண்ணினால் latency 300ms increase ஆகும், cost 20% increase ஆகும்.

நீங்கள் எந்த queries-க்கு மட்டும் detection enable பண்ணுவீர்கள்? எந்த signal-ஐ use பண்ணி gate பண்ணுவீர்கள்? 

Why?

## 8. Key Takeaways

* Hallucination என்பது error code அல்ல, correctness problem. Traditional monitoring போதாது.
* Retrieval quality + generation confidence + grounding verification ஆகியவை AI-specific signals.
* Hallucination-ஐ zero ஆக்க முடியாது, detect, measure, and contain பண்ண வேண்டும்.
* Architectural decision: risk level-க்கு ஏற்ப guardrails, citations, human-in-the-loop mix பண்ணு.
