# Compliance

> **Learning Path:** Security Architecture
> **Section:** 6.2.8 — Enterprise security

## Problem

நீங்கள் ஒரு fintech product build பண்ணிட்டீங்க. Payments, KYC, user PII எல்லாம் handle பண்ணுது. Product வேலை செய்யுது, revenue வருது.

அப்புறம் இரண்டு விஷயம் நடக்கும்:

1. Enterprise customer கேட்கிறார்: "SOC2 Type II report கொடுங்கள். எங்கள் auditor உங்களை approve பண்ணணும்."
2. Legal team கூப்பிட்டு சொல்கிறார்: "EU customer data handle பண்ணுறோம். GDPR apply ஆகும். India-ல DPDP Act வந்திருக்கு."

இப்போது code வேலை செய்வது மட்டும் போதாது. நீங்கள் **prove பண்ணணும்** - data எப்படி protect பண்ணுறீங்க, யார் access பண்ணினார்கள், எப்போது delete பண்ணீங்க என்பதை provable-ஆக காட்டணும்.

Compliance இல்லாமல் என்ன ஆகும்? Fines, business ban, payment processor disconnect, customer churn. Architect-ஆக இது ஒரு external constraint.

## Mental Model

Compliance என்பது checklist அல்ல. 

இது **external requirement -> technical control -> evidence -> audit** என்ற chain.

Regulation சொல்வது: "PII-ஐ protect பண்ணு". அதற்கு உங்களுக்கு தேவை: encryption at rest, encryption in transit, access control, audit logging, data retention policy.

அந்த controls இருப்பதை நீங்கள் evidence-ஆக காட்ட முடியணும். அதை auditor verify பண்ணுவார்.

> Mental model: Compliance = architecture decisions + observable evidence.

## How It Works

Regulation -> Requirement -> Control -> Evidence

```
Regulation --> Requirement --> Control --> Evidence --> Audit
GDPR Art 32 --> Encrypt PII --> KMS + TLS --> Key rotation logs, access logs --> Auditor review
```

Practical-ஆக இதற்கு தேவை:

* **Data classification**: PII, PHI, PCI, public. Classification இல்லாமல் control apply பண்ண முடியாது.
* **Access control**: IAM, RBAC, least privilege. Who can read what, from where.
* **Encryption**: Data at rest with KMS, in transit with TLS. Key management auditable ஆக இருக்கணும்.
* **Audit logging**: Immutable logs. Who accessed what data, when, from which service. Log tampering கூடாது.
* **Retention & Deletion**: Legal hold எவ்வளவு நாள், எப்போது delete பண்ணணும். Right to erasure-க்கு technical delete path வேண்டும்.
* **Change management & Vulnerability management**: Production deploy-க்கு approval, patching SLA.

இதை manual-ஆக spreadsheet-ல manage பண்ண முடியாது. Policy as code, automated evidence collection தான் scale ஆகும்.

## Architectural Reasoning

Compliance useful ஆகும் போது:

* Regulated domain: finance, health, payments, telecom
* Enterprise sales: SOC2, ISO27001 கேட்கும்
* Cross-border data: GDPR, DPDP Act

Architect-ஆக நீங்கள் முடிவு பண்ண வேண்டியது:

**Build in or bolt on?** 
Retrofit செய்வது மிகவும் cost-ஆகும். Audit log இப்போது இல்லை என்றால் பின்னால் database-ஐ மாற்றுவது painful.

**Centralize vs decentralize controls**
Centralized policy engine, centralized audit log, centralized secret management எளிதாக audit ஆகும். ஆனால் latency, blast radius trade-off உண்டு.

**Scope boundary**
எந்த data regulated scope-ல் வரும்? PCI DSS scope-ஐ குறைப்பதற்காக card data-ஐ தனி service-ல் isolate பண்ணுவது common pattern. Less scope = less audit cost.

## Trade-offs

1. **Speed vs Evidence**: Fast shipping vs provable controls. Compliance adds friction - approval gates, logging, review.
2. **Privacy vs Usability**: Data minimization, masking, retention நல்லது. ஆனால் analytics, feature development-க்கு data தேவை.
3. **Cost vs Coverage**: Full audit logging, immutable storage, KMS, SIEM எல்லாம் cost. Small startup-க்கு over-engineering ஆகும். ஆனால் enterprise customer இல்லாமல் revenue இல்லை.
4. **Complexity vs Operability**: More controls = more things break. Key rotation, log retention, access review automation இல்லாமல் team burnout.

Failure mode: Logs எழுதப்படவில்லை, அல
