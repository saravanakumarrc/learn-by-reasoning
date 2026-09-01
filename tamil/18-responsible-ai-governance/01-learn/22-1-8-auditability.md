# Auditability

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.8 — Learn

## 1. Problem

ஒரு AI system ஒரு decision எடுக்குது. உதாரணமா, loan approve / reject, fraud flag, job resume screen.

ஒரு வாரம் கழித்து customer கேட்கிறார்: "ஏன் என் loan reject ஆச்சு?"

அல்லது regulator கேட்கிறார்: "இந்த model எப்படி train ஆச்சு? எந்த data use பண்ணீங்க? நேற்று ஏன் இந்த output வந்தது?"

இப்போது உங்களிடம் என்ன இருக்கு?

எந்த log இல்லை, model version தெரியாது, input என்ன என்று தெரியாது, யார் approve பண்ணார் என்று தெரியாது.

இது business risk, legal risk, trust risk.

Auditability இல்லாமல், நீங்கள் **prove செய்ய முடியாது** - என்ன நடந்தது, ஏன் நடந்தது, யார் பொறுப்பு.

## 2. Mental Model

Auditability = ஒரு decision-க்கு **complete story** இருக்க வேண்டும்.

> Who did what, with what data, using which model version, when, and why.

இது CCTV camera மாதிரி அல்ல. இது tamper-evident ledger மாதிரி.

நீங்கள் பின்னால் வந்து, ஒரு specific event-ஐ reconstruct பண்ண முடியும்.

## 3. How It Works

Auditability என்பது மூன்று layer-கள்:

**1. Data Provenance:** Input data எங்கிருந்து வந்தது, எப்போது ingest ஆச்சு, எந்த transformation நடந்தது.

**2. Decision Provenance:** Request time-ல் எந்த model version / agent / policy run ஆச்சு, parameters என்ன, prompt என்ன, tools எதை call பண்ணியது.

**3. Action Provenance:** Decision-ன் அடிப்படையில் என்ன action எடுக்கப்பட்டது, யார் review பண்ணார், approval யார் கொடுத்தார்.

பொதுவாக இது audit log-கள் மூலம் implement ஆகும்.

* Immutable append-only store
* Structured event schema: timestamp, actor, action, resource, context, model_version, data_version
* Correlation ID across services
* Non-repudiation: cryptographic signature / hash chain

RAG system-ல்: query, retrieved documents IDs with scores, embedding model version, LLM version, temperature, final answer.

Agent system-ல்: plan steps, tool calls with inputs/outputs, final decision.

## 4. Architectural Reasoning

Auditability எப்போது must-have?

* Regulated domain: finance, healthcare, hiring
* High-stakes AI decisions: credit, fraud, medical triage
* Multi-team production system where blame தெளிவாக இருக்க வேண்டும்
* Model evolves frequently - reproducibility தேவை

Architect என்ன constraint-ஐ solve பண்ணுறார்?

Reproducibility + Accountability.

Options:

* **Inline logging:** Every service emit audit event to central log. Simple, but log loss ஆனால் gap.
* **Outbox pattern + Event bus:** Audit event-களை transactional outbox-ல் write செய்து, async publish. Durable.
* **Separate audit service:** Decision-ஐ make செய்யும் service, audit service-க்கு call பண்ணும். Coupling அதிகம்.

Decision driver: performance vs completeness.

Audit log-ஐ hot path-ல் synchronous write பண்ணினால் latency அதிகரிக்கும். Async பண்ணினால் loss risk.

## 5. Trade-offs

**Completeness vs Performance:** Detailed logging = more latency, storage cost. Production-ல் sampling பண்ணலாம், ஆனால் audit-க்கு sampling work ஆகாது.

**Immutability vs Cost:** Append-only, WORM storage, signed logs. Cost அதிகம், மாற்ற முடியாது. Operational complexity அதிகரிக்கும்.

**Granularity vs Usability:** Too much data = needle in haystack. Too little = audit fail. Schema design முக்கியம்.

**Privacy vs Auditability:** PII log பண்ணினால் audit easy ஆகும், ஆனால் GDPR/CCPA risk. Need masking, retention policy, access control.

Failure mode: Log tampering, clock skew, missing correlation ID, model version not captured. Audit trail broken ஆனால் auditability zero.

## 6. Practical Example

Enterprise loan approval RAG agent.

Request வரும் → API gateway assigns `request_id`.

Service flow:

1. User profile fetch from database
2. RAG retrieve from policy knowledge base → document IDs logged
3. LLM call with model `llm-v3.2`, temperature 0.2, prompt template `v1.4`
4. Agent calls credit score tool, fraud check tool
5. Decision: Approve with limit

Audit log entry:

```
request_id: req_abc123
timestamp: 2026-01-10T10:15:32Z
user_id: u_987
model_version: llm-v3.2
prompt_version: v1.4
retrieved_docs: [doc_45, doc_102]
tools: [credit_score, fraud_check]
decision: APPROVE
approver: agent_auto
reviewer: null
```

6 மாதம் கழித்து regulator கேட்கும்போது, நீங்கள் இந்த request_id-ஐ use பண்ணி, exact input, model version, retrieved context, tool outputs எல்லாம் reconstruct பண்ண முடியும்.

இல்லை என்றால், "system says approve" என்று சொல்லி முடிந்துவிடும்.

## 7. Reasoning Challenge

உங்கள் AI agent production-ல் 10k requests/day handle பண்ணுகிறது. Audit log-கள் 1 year retain செய்ய வேண்டும். Synchronous logging-ல் p95 latency 120ms-ல் இருந்து 210ms ஆகிறது.

இங்கே auditability-க்காக என்ன architectural choice செய்வீர்கள்? Synchronous vs async? Log storage எங்கே? Retention எப்படி manage பண்ணுவீர்கள்? Privacy concern இருந்தால் என்ன செய்வீர்கள்?

## 8. Key Takeaways

* Auditability என்பது feature அல்ல, architectural property. Design-லேயே build செய்ய வேண்டும்.
* Decision reconstruct செய்ய முடியும் என்றால் மட்டுமே auditability உள்ளது. Model version, data version, context எல்லாம் log செய்ய வேண்டும்.
* Immutability, correlation ID, non-repudiation மூன்றும் core.
* Every audit solution creates trade-off: latency, cost, privacy. அதை consciously choose செய்யுங்கள்.
