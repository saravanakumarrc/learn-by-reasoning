# AI governance

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.1 — Learn

## 1. Problem

உங்க team ஒரு LLM-powered agent build பண்ணியிருக்கு. Customer support chatbot, credit approval assist, hiring screening tool — எதுவாக இருந்தாலும் சரி.

ஒரு நாள் இது நடக்குது:
* Model ஒரு customer-க்கு தவறான தகவல் கொடுத்து விட்டது.
* Hiring agent ஒரு candidate-ஐ bias-ஆக filter பண்ணி விட்டது.
* Production-ல புது model version deploy பண்ணினதும் latency spike ஆகி, cost 3x ஆகி விட்டது.

Engineering-க்கு பிரச்சனை என்ன? Model work ஆகுது, code work ஆகுது. ஆனால் **யார் decide பண்ணினார்? எந்த data use ஆச்சு? ஏன் இந்த output வந்தது? compliance எப்படி prove பண்ணுவது?**

AI governance இல்லாமல், system வளர வளர, risk, cost, legal liability எல்லாம் invisible ஆக grow ஆகும். Architect-க்கு தேவை ஒரு framework, system-ஐ control, audit, மற்றும் responsible ஆக scale பண்ண.

## 2. Mental Model

AI governance என்பது model-ஐ police பண்ணுவது அல்ல. 

இது **decision-making system-க்கான guardrails**.

Think of it as:
* **Policy as code** — என்ன allow பண்ணலாம், என்ன block பண்ணணும்
* **Observability as evidence** — என்ன input வந்தது, model என்ன செய்தது, ஏன்
* **Lifecycle control** — data → training/fine-tune → deployment → monitoring → retirement

ஒரு distributed system-ல service mesh, rate limiting, tracing இருப்பது போல, AI system-ல governance = risk control + auditability + cost control.

## 3. How It Works

Practically governance 4 layers-ல work ஆகும்:

**1. Data Governance**
Training, fine-tuning, RAG retrieval data எங்கிருந்து வருது? PII உள்ளதா? Data lineage track பண்ண முடியுமா? Consent உள்ளதா?

**2. Model Governance**
Model versioning, evaluation benchmarks, risk classification. High-risk use case-க்கு stronger review. Model card, prompt template registry maintain பண்ணுவது.

**3. Runtime Governance**
Production-ல request filtering, PII redaction, toxicity check, allowlist/blocklist, cost & latency guardrails. Real-time policy enforcement.

**4. Audit & Compliance**
Logging: prompt, output, retrieved documents, model version, user id. Immutable audit trail. For EU AI Act, GDPR, etc., prove பண்ண வேண்டும்.

இது ஒரு central policy service + sidecar enforcement + observability pipeline ஆக implement ஆகும்.

## 4. Architectural Reasoning

When does governance become necessary?
* Model output user-facing ஆகும் போது
* Regulatory scope உள்ளது — finance, healthcare, hiring, lending
* Multiple teams same model/prompt reuse பண்ணும் போது
* Cost unpredictable ஆகும் போது

Alternatives:
* **Ad-hoc review**: Manual check before deploy. Works for 1 model, fails at scale.
* **Platform governance**: Centralized policy engine, model registry, evaluation harness. Operable at org scale.
* **Vendor-only**: Rely on OpenAI/Anthropic safety filters. Good baseline, not sufficient for business risk.

Architect choose பண்ணுவது ஏன்? Because governance shifts left. Policy failure-ஐ production incident ஆக மாறுவதற்கு முன் catch பண்ண வேண்டும்.

## 5. Trade-offs

**Safety vs Latency**
Runtime filtering, classification models add 100-500ms. Real-time agent-க்கு trade-off.

**Control vs Developer Velocity**
Strict approval gates slow down experimentation. Too loose = risk. Need risk tiering.

**Observability vs Cost & Privacy**
Full prompt logging helps audit, but stores PII. Need retention policy, redaction, encryption. Logging cost itself grows.

**Centralization vs Autonomy**
Central policy ensures consistency. Team-specific needs may require local override. Balance via policy inheritance.

Failure modes:
* Policy drift — policy update ஆனாலும் old model continue run ஆகும்
* Incomplete logging — audit time-ல evidence இல்லை
* False positive blocking — legitimate use case block ஆகி user experience degrade

## 6. Practical Example

Enterprise RAG for internal knowledge.

Architecture:
Client → API Gateway → Policy Enforcer → Retrieval Service → LLM Service → Response

Policy Enforcer checks:
* User has access to requested data domain? 
* Query contains disallowed topic? 
* Retrieved docs contain PII? Redact.
* Cost budget exceeded for tenant?

Observability pipeline writes to audit log: user_id, query hash, retrieved doc ids, model version, policy decision, latency, tokens.

Monthly review: eval harness runs on golden dataset, bias & hallucination metrics track ஆகும். Threshold breach ஆனால் model auto rollback.

இப்படி, business risk, compliance, cost எல்லாம் measurable ஆகும்.

## 7. Reasoning Challenge

உங்களுக்கு 3 products இருக்கு: internal code assistant, customer support chatbot, credit scoring assist.

Same LLM platform use பண்ணுறாங்க. ஒவ்வொன்றுக்கும் risk level வேறுபடும்.

நீங்கள் ஒரே governance system design பண்ண வேண்டும்.

எப்படி tiering பண்ணுவீர்கள்? Policy enforcement எங்கே வைப்பீர்கள் — per request, per service, அல்லது central? Logging granularity என்ன இருக்க வேண்டும்?

## 8. Key Takeaways

* AI governance என்பது trust, auditability, cost control-க்கான architecture, not just ethics checklist.
* Policy as code + observability + lifecycle control = core mental model.
* Risk tiering பண்ணி, safety, latency, velocity trade-off-ஐ manage பண்ணுங்கள்.
* Every model change creates liability. Governance makes that liability visible and controllable.
