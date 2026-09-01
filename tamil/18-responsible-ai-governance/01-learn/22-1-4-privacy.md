# Privacy

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.4 — Learn

## 1. Problem

உங்கள் company-க்கு user data இருக்கு. Name, phone, email, transaction history, location, chat logs. இதை model training-க்கு use பண்ணலாம். App performance improve பண்ணலாம். Personalization கொடுக்கலாம்.

ஆனால் ஒரு user கேட்கிறார்: "என் data எங்கே போகிறது? நீங்கள் என் data-வை delete செய்யுங்கள்." அல்லது regulator கேட்கிறார்: "இந்த data எப்படி collect பண்ணீங்கள்? Consent எங்கே?"

இப்போது problem வருகிறது. Data-வை collect பண்ணும்போது நீங்கள் நினைக்கவில்லை. ஆனால் இப்போது அது liability ஆகிறது. Data leak ஆனால் fine வரும். Trust போகும்.

**Privacy என்பது feature அல்ல, இது architectural constraint.**

## 2. Mental Model

Privacy என்பது "hide everything" அல்ல. இது **control**.

User-க்கு control இருக்க வேண்டும்:
* என்ன data collect பண்ணுகிறீர்கள்?
* ஏன் collect பண்ணுகிறீர்கள்?
* யாருடன் share பண்ணுகிறீர்கள்?
* எப்போது delete பண்ணுவீர்கள்?

ஒரு distributed system-ல் ஒரு service இன்னொரு service-ஐ call பண்ணும்போது data பரவுகிறது. அதை track பண்ண முடியாமல் போகிறது. அதுதான் real problem.

## 3. How It Works

Privacy என்பது மூன்று layer-ல் implement ஆகிறது.

**Collection layer:** Consent, data minimization. உங்களுக்கு தேவையான data மட்டும் கேளுங்கள். `email` தேவைப்படும்போது மட்டும் கேளுங்கள், profile photo தேவையில்லை என்றால் கேட்காதீர்கள்.

**Processing layer:** Purpose limitation. Collect பண்ணிய data-வை அதற்கு தவிர வேறு purpose-க்கு use பண்ணக்கூடாது. Training data-வை marketing-க்கு use பண்ணுவது violation.

**Storage & Access layer:** Minimization + retention + access control. Data எவ்வளவு நேரம் வைத்திருக்கிறீர்கள்? Who can access? Audit log இருக்கிறதா? Right to erasure-க்கு delete எப்படி செய்வீர்கள்?

Technical tools: encryption at rest and in transit, tokenization, pseudonymization, access control, audit logging, data lineage.

## 4. Architectural Reasoning

Privacy எப்போது painful ஆகிறது?

* AI/LLM training data-வில் PII இருந்தால் model அதை memorize பண்ணும். RAG pipeline-ல் user query direct vector database-க்கு போனால் leakage risk.
* Event-driven architecture-ல் message queue-ல் raw PII போகிறது. 10 downstream services அதை consume பண்ணுகிறது. Delete request வந்தால் எங்கெல்லாம் தேட வேண்டும்?
* Multi-tenant SaaS-ல் tenant A data tenant B-க்கு leak ஆகும் risk.

அதனால் architect-கள் என்ன செய்கிறார்கள்?

Data classification பண்ணுகிறார்கள்: Public, Internal, Confidential, Restricted. Privacy controls tier-wise apply பண்ணுகிறார்கள்.

Privacy by design: System design-ன் ஆரம்பத்திலேயே privacy requirement-ஐ constraint ஆக வைத்துக்கொள்வது. பிறகு bolt-on பண்ண முடியாது.

Alternatives: Centralized PII store vs distributed. Centralized-ல் control எளிது, ஆனால் latency அதிகம். Distributed-ல் performance நல்லது, ஆனால் compliance கடினம்.

## 5. Trade-offs

**Privacy vs Utility.** அதிக anonymization செய்தால் data value குறையும். Model training quality drop ஆகும். Minimal data collect பண்ணினால் personalization மோசமாகும்.

**Privacy vs Cost.** Encryption, tokenization, audit logging, data lineage tracking எல்லாம் infrastructure cost அதிகப்படுத்தும். Team-க்கு operational complexity அதிகம்.

**Privacy vs Latency.** Every request-க்கு consent check, policy enforcement பண்ணினால் latency increase ஆகும். Real-time system-ல் இது problem.

**Compliance vs Speed.** GDPR, DPDP Act க்கு Right to Access, Right to Erasure support பண்ண வேண்டும். இது engineering effort அதிகம். "Just ship fast" மனநிலைக்கு எதிரானது.

Failure mode: You think you deleted user data from primary database. ஆனால் backup, logs, vector embeddings, third-party analytics tools-ல் அது இருக்கிறது. Regulator audit-ல் catch ஆகும்.

## 6. Practical Example

ஒரு fintech app. User chat support-க்கு LLM agent உள்ளது. User message-ல் account number, PAN இருக்கிறது.

Bad architecture: Raw message direct RAG pipeline-க்கு போகிறது. Vector database-ல் store ஆகிறது. Model fine-tuning-க்கு logs use ஆகிறது.

Good architecture:
* Ingestion-ல் PII detection service run பண்ணி tokenize / mask பண்ணு. `PAN: XXXX-XXXX-1234` → `PAN: [REDACTED]`
* Consent check: User opted in for training? If no, message-ஐ training pipeline-ல் தடு.
* Data retention policy: Chat logs 90 days மட்டும். Auto purge.
* Access control: Support agent-க்கு masked view மட்டும். Raw data-க்கு separate access.

இப்போது privacy breach risk குறையும், compliance maintain ஆகும்.

## 7. Reasoning Challenge

உங்கள் AI product-ல் user-களின் chat history-ஐ model improvement-க்கு use பண்ண வேண்டும். 5 million users இருக்கிறார்கள். Data global-ல் distributed ஆகிறது. DPDP Act-க்கு compliance வேண்டும்.

நீங்கள் என்ன architectural decision எடுப்பீர்கள்? Data-வை எப்படி store பண்ணுவீர்கள்? Consent, deletion, audit எப்படி handle பண்ணுவீர்கள்? Privacy vs model quality trade-off-ஐ எப்படி manage பண்ணுவீர்கள்?

## 8. Key Takeaways

* Privacy என்பது trust-ன் architecture. Feature-க்கு பிறகு add பண்ண முடியாது.
* Collect less, retain less, share less. Data minimization என்பது default design principle.
* PII spread ஆன பிறகு control பண்ண முடியாது. Boundaries மற்றும் lineage-ஐ முதலில் வடிவமைக்கவும்.
* Every privacy control has cost in latency, complexity, and utility. Choose consciously.

**"இது ஏன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியும்னு reason பண்ண முடியும்னு தெரியும்."**
