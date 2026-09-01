# Human oversight

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.11 — Learn

## 1. Problem

உங்கள் AI system production-ல் ஓடுகிறது. Model ஒரு decision எடுக்கிறது — loan approve/reject, medical triage priority, content moderation block/allow.

இப்போது ஒரு bad decision நடந்தது. Customer complaint வந்தது. Regulator கேட்கிறார்: "யார் இந்த decision-க்கு பொறுப்பு? ஏன் இப்படி முடிவு செய்யப்பட்டது?"

அப்போது தெரிகிறது: model தானாக decide பண்ணுகிறது, log-கள் இல்லை, human எதையும் review பண்ணவில்லை, override செய்யும் வழி இல்லை.

இதுதான் painful point. Automation speed கிடைத்தது, ஆனால் accountability, safety, compliance இழந்தோம்.

Human oversight என்பது இந்த gap-ஐ close பண்ணுவதற்காக வந்தது.

## 2. Mental Model

Human oversight என்பது AI ஒரு black box ஆக இயங்காமல், **human in the loop** அல்லது **human on the loop** இருப்பதை உறுதி செய்வது.

Model சொல்வதை blind trust பண்ணாமல், ஒரு human ஆட்சேபிக்க, திருத்த, stop பண்ண முடியும்.

முக்கியமானது: human always final decision maker இல்லை. சில சமயம் human monitors, audits, overrides.

## 3. How It Works

Architecturally, இது 3 layers ஆக வரும்:

**1. Human-in-the-loop:** Model output வருவதற்கு முன் human approve பண்ண வேண்டும். High-risk decision-களுக்கு.
Flow: Input → Model → Human Review UI → Approve/Reject → Output

**2. Human-on-the-loop:** Model தானாக act பண்ணும், ஆனால் human monitor dashboard பார்த்து intervene செய்யலாம். Real-time alert, kill switch.
Flow: Input → Model → Output → Telemetry + Alert → Human can override

**3. Human-in-command:** Policy level oversight. Human sets guardrails, thresholds, escalation rules. Model within those bounds ஓடும்.

Supporting mechanisms: audit log, explainability view, confidence score, disagreement tracking, override reasons capture.

## 4. Architectural Reasoning

Human oversight எப்போது தேவை?

* **High stakes:** Financial loss, safety, legal liability, reputational risk
* **Low data quality / distributional shift:** Model uncertain ஆக இருக்கும்
* **Regulatory requirement:** EU AI Act, finance, healthcare க்கு mandatory
* **Novel scenario:** Model training data-வில் இல்லாத input வரும்போது

Alternatives?

* Full automation: fast, cheap, scalable. ஆனால் no accountability.
* Post-hoc audit only: cheap ஆனால் damage ஆன பிறகு தான் தெரியும்.

Architect ஏன் choose பண்ணுவார்? Because **risk > speed**. System failure cost human oversight cost-ஐ விட அதிகம் என்றால், oversight வேண்டும்.

## 5. Trade-offs

**Latency vs Safety:** Human review add செய்தால் latency increase ஆகும். Real-time chatbot-க்கு இது problem. ஆனால் loan approval-க்கு acceptable.

**Cost vs Coverage:** Human reviewer team, tooling, training வேண்டும். Scale ஆகும்போது cost explode ஆகும். அதனால் sampling, risk-based routing பண்ண வேண்டும்.

**Automation bias:** Human reviewer model-ஐ over trust பண்ணி, critical review பண்ணாமல் approve பண்ணுவது. இது oversight illusion create பண்ணும்.

**Operational complexity:** Override path, escalation, audit trail எல்லாம் system-ல் build பண்ண வேண்டும். Failure mode: human override stuck ஆனால் system halt ஆகும்.

## 6. Practical Example

Enterprise RAG agent, HR policy Q&A.

Model employee-க்கு policy summary கொடுக்கிறது. சில questions sensitive: termination, harassment complaint.

Architecture:
1. Query → RAG retrieve → LLM generate → Confidence score + risk classifier
2. If risk = low & confidence > 0.9 → auto respond
3. If risk = medium → response queue to human reviewer pool. Reviewer UI-ல் context, source docs, model reasoning காட்டு. Approve/Edit/Reject
4. If risk = high → auto refuse, escalate to HR lead via ticket

Audit log-ல்: query, model output, reviewer decision, latency, override reason store ஆகும்.

இங்கே human oversight cost-ஐ குறைக்க risk-based routing use பண்ணோம். Full manual review பண்ணினால் 100% coverage கிடைக்கும், ஆனால் team வேண்டும்.

## 7. Reasoning Challenge

உங்களிடம் fraud detection model இருக்கிறது. Model real-time transaction-ஐ block/allow பண்ணுகிறது. False positive cost: customer can't pay. False negative cost: company loss.

Regulator கேட்கிறார்: every block decision traceable இருக்க வேண்டும், human review possible.

நீங்கள் human oversight எப்படி design பண்ணுவீர்கள்? Human-in-the-loop செய்தால் latency problem வரும். Human-on-the-loop செய்தால் எப்போது intervene பண்ணுவீர்கள்? Threshold எது?

## 8. Key Takeaways

* Human oversight என்பது trust பிரச்சனைக்கு solution, not just UI.
* Speed, cost, safety trade-off-ஐ explicit ஆக decide பண்ண வேண்டும்.
* Oversight without audit trail, override path, alerting என்பது theater மட்டுமே.
* Model confidence + risk signal use பண்ணி human effort-ஐ focus பண்ணுவது scale-க்கு முக்கியம்.
