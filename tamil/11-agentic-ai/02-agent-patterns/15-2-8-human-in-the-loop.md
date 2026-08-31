# Human-in-the-loop

> **Learning Path:** Agentic AI
> **Section:** 15.2.8 — Agent patterns

## 1. Problem

உங்க agent ஒரு financial document-ஐ read பண்ணி, customer-க்கு refund approve பண்ணணும். Agent rule-ஐ follow பண்ணி decision எடுக்குது. ஆனா request-ல சில edge cases இருக்கு: amount unusually high, policy exception, fraud signals.

Agent full autonomy-ல இருந்தா என்ன ஆகும்?
* Wrong approve பண்ணி money loss
* Wrong reject பண்ணி customer churn
* Model hallucination-ஆல policy-வை தவறாக interpret பண்ணலாம்

Pure automation-க்கு confidence இல்லாதபோது, ஒரு human-ஐ loop-ல கொண்டு வராம இருந்தா risk அதிகம். ஆனா human-ஐ எல்லா decision-க்கும் கொண்டு வந்தா latency, cost, throughput எல்லாம் கெட்டுவிடும்.

**Problem painful enough:** Agent 80% cases-ல சரியா handle பண்ணும். 20% uncertain, high-risk, or policy-critical cases-ல human judgment தேவை. அந்த 20%-ஐ எப்படி detect பண்ணி, எப்படி human-க்கு pass பண்ணி, மீண்டும் agent-க்கு திருப்பி கொடுக்கறது?

இதுதான் Human-in-the-loop.

## 2. Mental Model

Human-in-the-loop என்பது agent-ஐ fully autonomous ஆக்காம, **decision boundary**-ல human-ஐ gatekeeper-ஆக வைக்கிறது.

அது ஒரு feedback loop:
`Agent → Confidence / Risk check → Human review → Correction / Approval → Agent learns / continues`

Human என்பது oracle அல்ல, bottleneck. அதனால் loop-ஐ design பண்ணும்போது முக்கியம்: **எந்த decision-க்கு human தேவை, எப்போ interrupt பண்ண வேண்டும், மீண்டும் எப்போ hand back பண்ண வேண்டும்.**

## 3. How It Works

Architecture-ல மூன்று patterns வரும்:

**a. Pre-approval:** Agent action-ஐ execute பண்ணுவதற்கு முன் human approve பண்ண வேண்டும். 
Example: refund > $1000, agent draft பண்ணும், human approve/reject.

**b. Post-action review:** Agent action பண்ணிடும், பிறகு human audit பண்ணும்.
Example: support agent ticket close பண்ணும், human daily sample review பண்ணி quality check.

**c. Escalation on uncertainty:** Agent self confidence score or risk signal பார்த்து, threshold கீழே போனால் human-க்கு escalate பண்ணும்.
Example: intent classification confidence < 0.7, or policy conflict detected.

Implementation-ல நீங்கள் தேவை:
* **Decision point:** where to inject human
* **Handoff interface:** human-க்கு context, reasoning trace, suggested action
* **State management:** task paused, waiting for human
* **Timeout / fallback:** human response வராமல் இருந்தால் என்ன செய்ய?
* **Telemetry:** which cases escalated, why, human took how long, override rate

## 4. Architectural Reasoning

Human-in-the-loop useful ஆகும் போது:

* **High cost of error:** finance, healthcare, legal, compliance
* **Low data for automation:** rare edge cases, long tail
* **Regulatory need:** audit trail, explainability, non-repudiation
* **Model uncertainty:** ambiguous input, conflicting instructions

Alternatives:
* **Full automation:** fast, cheap, scalable. ஆனால் risk high.
* **Human-in-the-loop vs Human-on-the-loop:** On-the-loop என்பது human supervises multiple agents, override பண்ண முடியும் ஆனால் per-decision review இல்லை.
* **Guardrails + rules:** deterministic checks for known bad cases. Human தேவையில்லை. ஆனால் unknown cases-ல fail.

Architect choose பண்ணும்போது கேள்வி:
1. Error cost > Human cost ஆ?
2. Escalation volume sustainable ஆ? Team size?
3. Latency SLA break ஆகுமா? Human wait time acceptable ஆ?

## 5. Trade-offs

* **Quality vs Latency:** Human review தரத்தை உயர்த்தும், ஆனால் response time seconds-ல இருந்து minutes/hours ஆகும்.
* **Cost vs Risk:** Human reviewers செலவு. அதிக escalation = அதிக cost. குறைவான escalation = அதிக risk.
* **Operability:** Human queue management, SLA, shift coverage தேவை. Agent-க்கு புதிய failure mode: human never responds.
* **Learning loop:** Human corrections-ஐ agent-க்கு திருப்பி feed பண்ணினால் system improve ஆகும். இல்லைன்னா human வெறும் cost center ஆகிவிடும்.

Failure modes:
* Human fatigue, inconsistent decisions
* Context overload: human-க்கு too much info கொடுத்தால் slow, too little ஆனால் wrong decision
* Loop never closes: task stuck in waiting state

## 6. Practical Example

Enterprise RAG agent for internal policy Q&A.

Flow:
1. User asks: "Client-க்கு 30 days return வேண்டும், product opened?"
2. Agent retrieves policy, generates answer with confidence 0.82
3. Rule: If confidence < 0.9 AND topic = returns/refunds → escalate
4. Task goes to human reviewer queue in tool. UI shows: question, retrieved docs, agent reasoning trace, suggested answer.
5. Human edits answer, marks reason for correction: "policy changed in Jan 2025"
6. Agent continues with approved answer, correction logged to feedback store for fine-tuning / retrieval update.

Here human is not doing all work, only uncertain high-impact cases.

## 7. Reasoning Challenge

உங்க customer support agent-க்கு 10,000 requests/day வருகிறது. 95% cases-ல agent சரியாக solve பண்ணுகிறது. Refund > $500 ஆனால் மட்டும் error cost அதிகம். Human team 5 people, ஒரு decision-க்கு average 8 minutes எடுக்கும்.

நீங்கள் எந்த pattern தேர்வு செய்வீர்கள்: pre-approval, post-review, or escalation on uncertainty? Threshold எப்படி set பண்ணுவீர்கள்? Human queue pile up ஆனால் என்ன fallback?

## 8. Key Takeaways

* Human-in-the-loop என்பது automation-ஐ replace பண்ணுவது அல்ல, risk boundary-ஐ define பண்ணுவது.
* Escalation criteria clear-ஆக இருக்கணும்: confidence, risk, policy sensitivity.
* Human handoff-ல context + reasoning trace கொடுத்தால் review time குறையும்.
* Every loop creates cost, latency, and operational complexity. அதனால் loop-ஐ measure பண்ணுங்கள்: escalation rate, override rate, human response time.
* Good design-ல human corrections agent-க்கு திரும்பி வரும், system gradually less human dependent ஆகும்.
