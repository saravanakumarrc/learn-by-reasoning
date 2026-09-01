# Audit layer

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.15 — Enterprise patterns

## 1. Problem

உங்கள் Enterprise AI system ஒரு decision எடுக்குது. உதாரணமா ஒரு RAG agent customer refund approve பண்ணுது. அல்லது credit limit increase பண்ணுது.

மூன்று மாதம் கழித்து compliance team கேட்கிறார்கள்:
> "இந்த decision எப்படி வந்தது? எந்த data பயன்படுத்தப்பட்டது? எந்த model version? எந்த user prompt? யார் approve பண்ணினார்கள்?"

இப்போது உங்களிடம் இல்லை. Logs scattered ஆக இருக்கு. API gateway log-ல request இருக்கு, application log-ல வேறு, vector DB query trace இல்லை, LLM prompt மறைந்து போச்சு.

Audit இல்லாமல் என்ன நடக்கும்?
* Regulatory fine, SOX / GDPR / RBI compliance fail
* Incident-ல root cause கண்டுபிடிக்க முடியாது
* Model drift அல்லது bias பற்றி prove பண்ண முடியாது
* Legal dispute-ல உங்கள் system-ஐ defend முடியாது

Problem painful ஆகும் போது தான் Audit layer தேவைப்படுகிறது.

## 2. Mental Model

Audit layer என்பது system-ன் **black box recorder** மற்றும் **decision ledger** ஆகும்.

ஒவ்வொரு முக்கியமான action / decision / data access-க்கும் ஒரு immutable, time-ordered record உருவாக்குவது. இது business logic-ஐ மாற்றாமல், அதை observe பண்ணி capture பண்ணுகிறது.

Analogy: விமானத்தில் flight data recorder இருப்பது போல. Flight ஓடும் போது interfere பண்ணாது. Accident ஆன பிறகு என்ன நடந்தது என்பதை reconstruct பண்ண உதவும்.

## 3. How It Works

Audit layer பொதுவாக மூன்று விஷயங்களை capture பண்ணும்:

**What happened?** - Event type: `refund_approved`, `llm_tool_call`, `data_access`
**Who / What context?** - user_id, service_name, request_id, session_id, model_version, prompt_id
**Why?** - Input data snapshot, decision inputs, output, policy rule triggered

Implementation pattern:
* Application code அல்லது middleware ல `audit.emit(event)` call செய்யப்படும்
* Event async ஆக audit pipeline-க்கு அனுப்பப்படும் - message queue / event bus
* Audit service event-ஐ normalize பண்ணி, tamper-evident store-ல write பண்ணும் - append-only log, object storage with WORM, அல்லது immutable ledger
* Query API மூலம் reconstruct செய்ய முடியும்

AI system-க்கு specific ஆக:
`user_prompt -> retrieved_chunks [doc_id, score] -> system_prompt -> model_version -> tool_calls -> final_answer` என்ற chain முழுவதும் capture ஆக வேண்டும்.

## 4. Architectural Reasoning

Audit layer useful ஆகும் போது:
* Decision has financial / legal / safety impact
* Non-repudiation தேவை
* Model behavior explainability தேவை
* Cross-service correlation தேவை

Constraint இது address பண்ணும்: **Observability vs Accountability**. Logs debugging-க்கு. Audit compliance மற்றும் trust-க்கு.

Alternatives:
* Application logs மட்டும்: searchable ஆனால் mutable, incomplete, retention குறைவு
* Database transaction history: business data இருக்கும், decision rationale இருக்காது
* Third-party SIEM மட்டும்: security events கவர் பண்ணும், AI decision lineage கவர் பண்ணாது

Architect ஏன் audit layer தேர்வு செய்வார்?
Business logic-ஐ pollute பண்ணாமல் centralized, tamper-resistant trail வேண்டும். மேலும் audit requirements எப்போதும் மாறும். Separate layer வைத்தால் change isolated ஆக இருக்கும்.

## 5. Trade-offs

**Performance vs Completeness.** Full payload capture latency-ஐ அதிகரிக்கும். Sampling அல்லது async write தேவை. ஆனால் sampling audit integrity-ஐ குறைக்கும்.

**Storage cost vs Retention.** Immutable audit data grow ஆகும். 7 years retention வேண்டும் என்றால் storage + indexing cost முக்கியம். Cold storage + tiering தேவை.

**Privacy vs Auditability.** PII, PHI data capture செய்யும் போது GDPR right to erasure conflict ஆகும். Solution: pseudonymization, selective redaction, access control.

**Tight coupling vs Missed events.** Audit emit-ஐ business code-ல போட்டால் developer forget பண்ணுவார். Middleware / sidecar / OpenTelemetry processor பயன்படுத்தி enforcement பண்ண வேண்டும்.

Failure mode: Audit write fail ஆனால் business operation continue ஆகுமா? Usually audit must not block critical path. ஆனால் audit loss ஆனால் compliance breach. எனவே best effort async + dead letter queue + alerting.

## 6. Practical Example

Enterprise RAG Agent for loan approval.

Request flow:
User -> API Gateway -> Agent Service -> Retriever -> Vector DB -> LLM -> Policy Engine -> Decision

Audit layer captures:
```
{
  request_id: r_123,
  timestamp: 2026-01-10T10:12:00Z,
  user_id: u_456,
  model_version: llm/gpt-4o-2025-11,
  retrieved_docs: [{doc_id: policy_88, score: 0.92}, ...],
  prompt: "...",
  tool_calls: [{tool: credit_check, input: {...}}],
  decision: {action: approve, amount: 50000, reason: "policy_rule_12 matched"},
  actor: system
}
```

Compliance audit-ல: ஏன் approve ஆனது என்பதை doc + model + policy chain-உடன் prove பண்ண முடியும். Incident-ல மாடல் hallucination ஆனால் எந்த retrieved chunk காரணம் என்பதை trace பண்ண முடியும்.

## 7. Reasoning Challenge

உங்கள் AI agent ஒரு நாளைக்கு 10M requests handle பண்ணுகிறது. Full prompt + response capture செய்தால் storage cost அதிகம். Compliance கேட்பது: ஒவ்வொரு financial decision-க்கும் complete lineage வேண்டும். மற்ற requests-க்கு summary மட்டும் போதும்.

இங்கே audit layer-ஐ எப்படி design பண்ணுவீர்கள்? என்ன capture செய்வீர்கள், என்ன skip செய்வீர்கள், எப்படி enforce செய்வீர்கள்?

## 8. Key Takeaways

* Audit என்பது debugging அல்ல, accountability மற்றும் non-repudiation-க்கான immutable trail.
* AI systems-ல audit என்பது prompt, retrieval, model version, tool calls, decision ஆகிய chain முழுவதும் capture பண்ண வேண்டும்.
* Audit layer-ஐ business logic-ல இருந்து separate பண்ணுவது operability மற்றும் compliance change-ஐ எளிதாக்கும்.
* Every architectural decision creates trade-off: completeness vs cost vs latency vs privacy.
