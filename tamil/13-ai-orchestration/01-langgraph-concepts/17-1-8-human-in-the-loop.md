# Human-in-the-loop

> **Learning Path:** AI Orchestration
> **Section:** 17.1.8 — LangGraph concepts

## 1. Problem

உங்களிடம் ஒரு AI agent இருக்கு. அது RAG மூலம் document படிச்சு, ஒரு contract-ஐ summarize பண்ணி, payment amount approve பண்ண சொல்லுது.

Agent சில நேரம் சரியா செய்யும். சில நேரம் hallucinate பண்ணும். ஒரு தவறான approve decision cost ஆகும்.

இப்போ நீங்கள் என்ன செய்வீர்கள்?

Agent-ஐ முழுக்க தனியா விட முடியாது. முழுக்க human-ஆக மாற்றினால் latency, cost, scalability பிரச்சனை.

இடைப்பட்ட தீர்வு தேவை: **Agent வேலையை பெரும்பாலும் தானாக செய்யட்டும், ஆனால் uncertainty அதிகமான இடத்தில் மட்டும் human-ஐ கொண்டு வந்து decide பண்ண வேண்டும்.**

அதுதான் Human-in-the-loop.

## 2. Mental Model

Human-in-the-loop என்பது ஒரு control valve.

Agent ஒரு workflow-ஐ ஓட விடும். ஒரு node-ல் confidence low ஆக இருந்தாலோ, risk high ஆக இருந்தாலோ, workflow தற்காலிகமாக pause ஆகி human reviewer-க்கு போகும். Human decision வந்ததும் workflow resume ஆகும்.

இது ஒரு synchronous wait அல்ல, asynchronous handoff.

LangGraph-ல் இதை நீங்கள் ஒரு node-ஆக மாதிரி வைக்கலாம். `interrupt()` மூலம் graph-ஐ pause பண்ணி, external input எதிர்பார்க்கலாம்.

## 3. How It Works

LangGraph conceptually ஒரு state machine.

`state` ஒரு graph node-ல் இருந்து இன்னொரு node-க்கு போகும். Human-in-the-loop என்பது ஒரு special node:

**Agent node → Decision node → [if uncertain] → Human review node → Resume node**

Implementation-ல்:

1. Agent ஒரு task செய்து output உருவாக்கும்.
2. Confidence score / risk flag calculate செய்யும்.
3. Threshold cross ஆனால் graph `interrupt` ஆகும்.
4. State checkpoint save ஆகும். Human UI / Slack / dashboard-ல் task pending ஆக தெரியும்.
5. Human approve / reject / edit செய்தால், அந்த decision state-க்கு திரும்ப append ஆகும்.
6. Graph அங்கிருந்து தொடரும்.

LangGraph-ல் `interrupt_before` மற்றும் `interrupt_after` பயன்படுத்தி, நீங்கள் எந்த node-க்கு முன்னால் அல்லது பின்னால் human checkpoint வைக்கலாம்.

## 4. Architectural Reasoning

இது எப்போது useful?

* High-stakes decision: payment approval, medical triage, legal clause extraction.
* Low-data / ambiguous context: agent-க்கு போதுமான context இல்லை.
* Compliance / audit trail தேவை: யார் approve பண்ணினார்கள் என்பதை log பண்ண வேண்டும்.
* Model limitations: reasoning தேவைப்படும் கேள்விகள்.

Alternatives:

* **Human-in-the-loop:** Human தேவைப்படும் இடத்தில் மட்டும் intervene.
* **Human-on-the-loop:** Agent முழுக்க தானாக run ஆகும், ஆனால் human முழு workflow-ஐ monitor செய்து override செய்யலாம். Oversight, not blocking.
* **Human-out-of-the-loop:** Full automation. Speed முக்கியம், risk குறைவு.

எதை தேர்ந்தெடுப்பது? Risk vs latency trade-off.

## 5. Trade-offs

**Latency:** Human wait time வந்துவிடும். SLA-க்கு பாதிப்பு.

**Scalability:** Human reviewer எண்ணிக்கை bottleneck ஆகும். 1000 requests per minute வந்தால் எல்லாவற்றையும் human பார்க்க முடியாது.

**Consistency:** Different humans different decisions எடுப்பார்கள். Inter-rater variance வரும்.

**Cost:** Human time விலை உயர்ந்தது. Automation cost-ஐ குறைக்கிறது, ஆனால் operational overhead அதிகரிக்கும்.

**Failure modes:** Human never responds → workflow stuck. Timeout handling தேவை. Resume state corrupt ஆகலாம். State checkpointing reliable-ஆக இருக்க வேண்டும்.

## 6. Practical Example

Enterprise support agent.

Workflow:

`Ingest Ticket → Classify Intent → Retrieve Knowledge → Draft Reply → Human Review → Send`

Classify Intent high confidence ஆனால் draft reply-க்கு confidence < 0.7 இருந்தால், graph interrupt ஆகி human reviewer queue-க்கு போகும்.

Reviewer UI-ல் ticket, agent draft, retrieved sources, confidence reason காட்டப்படும். Reviewer edit செய்து approve பண்ணும்.

அடுத்த முறை இதே type ticket வந்தால், ஏற்கனவே human edited example-ஐ training data ஆக பயன்படுத்தி agent improve ஆகும். இது active learning loop ஆகிறது.

LangGraph-ல் இதை ஒரு `interrupt` node-ஆக மாடல் செய்தால், state persistence, resume, audit trail எல்லாம் built-in ஆக handle ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு fraud detection agent இருக்கு. 95% transactions auto approve ஆகும். 5% suspicious என்று flag ஆகிறது. Human reviewer team உங்களிடம் 10 பேர் மட்டுமே இருக்கிறார்கள். Peak time-ல் 500 suspicious transactions per hour வருகிறது.

இங்கே Human-in-the-loop-ஐ எப்படி design செய்வீர்கள்? எல்லாவற்றையும் human-க்கு அனுப்புவதா? அல்லது மேலும் ஒரு routing layer வைத்து priority தருவதா? Workflow stuck ஆகாமல் இருக்க என்ன செய்வீர்கள்?

## 8. Key Takeaways

* Human-in-the-loop என்பது automation-ஐ முழுவதுமாக நிராகரிப்பது அல்ல, risk-ஐ கட்டுப்படுத்தும் valve.
* LangGraph-ல் இது ஒரு interruptible node, checkpointed state மூலம் asynchronous resume ஆகும்.
* முக்கிய trade-off latency vs safety, scalability vs control.
* Human decision-ஐ log செய்து, அதை model improvement loop-க்கு பயன்படுத்துவது தான் long-term value.
