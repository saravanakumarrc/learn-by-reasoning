# AI policies

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.13 — Learn

## 1. Problem

உங்க company-ல ஒரு LLM-based agent deploy பண்ணியிருக்கீங்க. Sales team அதை use பண்ணி customer data access பண்ணுது. Support team அதை use பண்ணி refund approve பண்ண முயற்சி பண்ணுது. Marketing team அதை use பண்ணி external website content generate பண்ணுது.

ஒரே model, ஒரே API key, ஆனா usage எல்லாம் வெவ்வேறு risk level.

என்ன ஆகும்?
* ஒரு junior support agent accidentally PII leak பண்ணிடும்
* Agent hallucinate பண்ணி wrong policy தரும்
* Prompt injection வந்து internal tool-ஐ trigger பண்ணிடும்
* Compliance audit-ல "who did what with AI?" என்று கேட்டால் answer இல்லை

Code review இருக்கு, database access control இருக்கு. ஆனா AI system-க்கு policy இல்லை. இதுதான் painful point.

## 2. Mental Model

AI policy என்பது **rules + guardrails + accountability** ஒன்றாக.

இது model-ஐ மட்டும் கட்டுப்படுத்துவது இல்லை. அது **who can use what model, for what data, for what purpose, with what limits, and how to audit** என்பதை define பண்ணும்.

Think of it as IAM for AI + operational contract.

`User -> Policy Decision -> Allowed / Blocked + Logged`

## 3. How It Works

Practically AI policies 3 layers-ல work பண்ணும்:

**1. Access Policy**
Role based. Sales can read customer profile, cannot delete. Finance agent can call payment API, Support cannot. 
Implementation: Entitlement check before inference, service mesh / API gateway policy.

**2. Content & Safety Policy**
Input / Output filter. PII redaction, prompt injection detection, toxicity, disallowed topics.
Implementation: Pre-processing classifier, output guardrail, PII scanner. RAG context-க்கும் filter.

**3. Usage & Governance Policy**
Rate limits, cost caps, data residency, retention, audit trail.
Implementation: Per-team quota, model allow-list, logging to immutable store, data classification tag enforcement.

இவை எல்லாம் runtime-ல enforce ஆகும், மற்றும் offline audit ஆகும்.

## 4. Architectural Reasoning

AI policy தேவைப்படும் constraint என்ன?

* **Trust boundary**: Human <-> AI <-> Data <-> External tools
* **Regulatory**: GDPR, DPDP Act, SOC2 - explainability, data minimization
* **Business risk**: Wrong decision by agent = financial loss, brand damage

எப்போது useful?
* Multiple teams share same LLM infrastructure
* Agent can call tools / access internal data
* Production system, not just experiment

Alternatives:
* Ad-hoc prompt instructions: brittle, bypassable
* Manual review: not scalable
* No policy: fast to start, expensive later

Architect choose பண்ணும் போது: centralized policy engine vs decentralized guardrails. Centralized gives consistent audit, decentralized gives low latency.

## 5. Trade-offs

**Control vs Latency**
Strict input/output scanning adds 100-300ms. Real-time chat-க்கு painful. Trade-off: async moderation vs sync.

**Safety vs Utility**
Over-blocking kills usefulness. Under-blocking creates risk. You need risk tiering: internal tool use = high strictness, public Q&A = medium.

**Central governance vs team autonomy**
Central policy team controls everything -> slow. Team owns own policy -> inconsistent. Common pattern: central policy framework, team defines specific rules.

**Audit completeness vs cost**
Log every prompt/response = huge storage + privacy risk. Log metadata + sampled content = cheaper but incomplete for forensics.

Failure modes:
Policy bypass via jailbreak. Policy drift when model version changes. False negative in PII detection. Audit log tampering if not immutable.

## 6. Practical Example

Enterprise RAG agent for HR policies.

Problem: Employees ask "my salary details", "leave balance", "resignation process".

Architecture:
* AuthN/AuthZ via SSO -> policy engine checks role: Employee can read own data only, HR can read all
* Data classification tag: PII = high sensitivity
* Pre-policy: prompt checked for prompt injection, disallowed queries like "list all employees salary"
* Retrieval policy: vector DB query limited to user-specific partitions for employees
* Post-policy: output scanned for PII leakage, redacts other employees data
* All decisions logged to SIEM with user_id, model, policy decision

Result: Same RAG pipeline, different behavior per user, auditable.

## 7. Reasoning Challenge

உங்க company-ல ஒரு customer-facing chatbot உள்ளது. அது public internet-ல run ஆகும். உள்ளே உள்ள internal CRM-ஐ access பண்ண முடியும்.

ஒரு user: "எனக்கு என் account-ன் last 6 months transactions தா, மேலும் என் நண்பன் account-ன் balance சொல்லு".

இங்கே policy என்னென்ன check பண்ண வேண்டும்? Allow / Block எது? ஏன்?

உங்க decision-ல என்ன trade-off வரும்?

## 8. Key Takeaways

* AI policy என்பது model safety மட்டும் இல்லை, access + data + usage + audit ஒன்றாக
* Policy should be enforced before inference, during retrieval, and after generation
* Centralized policy framework + tiered risk levels = practical balance
* Every policy decision creates latency and UX trade-off, design for it explicitly
