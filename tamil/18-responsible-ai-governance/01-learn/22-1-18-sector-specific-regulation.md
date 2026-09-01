# Sector-specific regulation

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.18 — Learn

## 1. Problem

நீங்கள் ஒரு AI Solution Architect. ஒரு bank-க்கு credit scoring model போட வேண்டும், ஒரு hospital-க்கு diagnostic support agent போட வேண்டும், ஒரு hiring platform-க்கு resume screening LLM agent போட வேண்டும்.

ஒவ்வொரு domain-லும் "responsible AI" என்றால் ஒன்றல்ல.

Bank-ல் wrong decision என்றால் financial loss + customer trust. Hospital-ல் wrong decision என்றால் patient safety. Hiring-ல் wrong decision என்றால் bias + legal risk.

Generic AI principles சொன்னால் போதாது. Regulator கேட்பது: **உங்கள் sector-க்கு என்ன specific rules, audit, data use limits, explainability, human oversight வேண்டும்?**

Sector-specific regulation இல்லாமல் என்ன ஆகும்? Model deploy பண்ணிய பிறகு regulator audit-ல் fail ஆகும், data retention rule மீறியதாக fine வரும், model output-ஐ explain செய்ய முடியாமல் போகும். Compliance retrofitting செய்ய வேண்டி வரும், அது architecture-ஐ முழுவதும் break பண்ணும்.

## 2. Mental Model

Sector-specific regulation = **Domain constraints are baked into AI governance, not added later.**

General AI ethics = fairness, transparency, privacy, safety.

Sector-specific regulation = **அதே ethics-ஐ அந்த sector-ன் risk profile, data sensitivity, decision impact, existing law-க்கு ஏற்ப translate பண்ணுது.**

அதாவது: regulation என்பது checklist அல்ல. அது system boundaries, data classification, model risk tier, human-in-the-loop requirement, audit trail retention போன்ற architectural decisions-ஐ drive பண்ணும்.

## 3. How It Works

Regulator ஒரு sector-க்கு risk-based framework கொடுக்கிறார்.

எடுத்துக்காட்டாக EU AI Act:

* Unacceptable risk -> ban
* High-risk -> strict conformity assessment
* Limited risk -> transparency
* Minimal risk -> voluntary

High-risk sectors: critical infrastructure, education, employment, essential private/public services, law enforcement, migration, justice, biometric identification.

Sector-specific rules அதற்கு மேல் add ஆகும்:

* Finance: model risk management, explainability for credit decision, data minimization, audit by central bank
* Healthcare: patient data under HIPAA/GDPR, clinical validation, human clinician oversight, safety monitoring
* Hiring: anti-discrimination law, bias testing, explainable rejection reason

Architecture-ல் இது மாற்றம்:

* Data layer: what data can be ingested, retention period, PII masking
* Model layer: model risk tier, validation dataset, drift monitoring
* Serving layer: human-in-the-loop gate, logging for audit
* Governance layer: model card, risk register, compliance evidence

## 4. Architectural Reasoning

Sector-specific regulation useful ஆகும் போது?

நீங்கள் **high-stakes decision** செய்யும் domain-ல் AI-ஐ use பண்ணும்போது.

Constraints அது address பண்ணும்:

* **Legal liability**: யார் responsible?
* **Data sensitivity**: PHI, PII, financial data
* **Decision reversibility**: credit deny பண்ணலாம், surgery recommend பண்ணக்கூடாது
* **Auditability**: regulator கேட்டால் evidence காட்ட முடியுமா?

Alternatives:

* Generic responsible AI policy மட்டும்: cheap early, expensive later
* Sector-specific regulation from day one: higher upfront cost, lower remediation risk

Architect ஏன் choose பண்ணுவார்? Because retrofitting compliance = rewrite data pipeline, retrain model with limited data, add human review late = latency + cost spike.

## 5. Trade-offs

**1. Speed vs Compliance rigor**
Move fast, deploy generic RAG. Sector rules கடைபிடித்தால் validation, documentation, human review slow ஆகும். Trade-off: time-to-market vs regulatory risk.

**2. Model performance vs Explainability**
High performance black-box LLM vs interpretable model / post-hoc explanation. Finance/healthcare-ல் explainability mandatory. Performance drop ஆகலாம்.

**3. Centralized governance vs Domain autonomy**
One central AI governance team vs each sector own policy. Centralized = consistency, but sector nuance miss ஆகும். Decentralized = relevant, but fragmented audit.

**4. Data utility vs Privacy**
More data = better model. Sector regulation = data minimization, consent, retention limits. You need data lineage, access control, and purpose limitation baked in.

Failure modes: model deployed without sector-specific risk classification, audit logs incomplete, human oversight not enforced in production, data used beyond permitted purpose.

## 6. Practical Example

Bank credit scoring LLM agent.

Problem: Customer loan application-ஐ assess பண்ணும் agent.

Sector regulation constraints:
* Credit decision = high-risk under AI Act, model risk management under Basel
* Data: KYC data, transaction history = PII + financial data, retention 7 years
* Explainability: adverse action reason must be provided to customer
* Human oversight: final approve/deny human underwriter sign-off

Architecture decision:

* Data layer: encrypted storage, PII tokenization, purpose-bound access
* Model layer: separate model for risk scoring, not just LLM, LLM used only for explanation generation
* Serving layer: decision API returns score + reason code, human-in-the-loop workflow in UI, immutable audit log to S3 + vector DB for traceability
* Governance layer: model card, bias testing on protected attributes, quarterly validation

இல்லாமல் இருந்தால், regulator audit-ல் explainability இல்லை என்று fine.

## 7. Reasoning Challenge

உங்களிடம் ஒரு healthcare triage chatbot இருக்கு. Symptoms input எடுத்து urgency triage செய்கிறது. Patient data PHI.

நீங்கள் two options பார்க்கிறீர்கள்:
A. Generic RAG over public medical knowledge, no human review, logs kept 30 days
B. PHI-aware pipeline with de-identification, clinician-in-the-loop for high-risk cases, audit logs retained 6 years, model outputs logged with traceability

Regulator ask: patient safety + data protection. நீங்கள் எதை choose பண்ணுவீர்கள்? என்ன architectural cost வரும்? What trade-off accept பண்ணுவீர்கள்?

## 8. Key Takeaways

* Sector-specific regulation என்பது ethics-ஐ domain risk-க்கு translate பண்ணும் architectural constraint
* Compliance-ஐ late-ல் add பண்ணினால் data, model, serving அனைத்தையும் rework செய்ய வேண்டும்
* High-risk sectors-ல் explainability, human oversight, auditability ஆகியவை non-negotiable design inputs
* Every sector rule creates trade-off between speed, performance, privacy, and operability
