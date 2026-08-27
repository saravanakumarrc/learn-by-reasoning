# Secrets management

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.1.12 — Cloud fundamentals

## 1. Problem

ஒரு microservices app-ல 15 services இருக்கு. ஒவ்வொன்றுக்கும் database password, third-party API key, JWT signing key வேண்டும்.

முதல்ல என்ன பண்ணுவீங்க? 
* config file-ல எழுதி code-க்கு பக்கத்தில் வைப்பீங்க
* environment variable-ல போடுவீங்க
* அல்லது repo-வில் `.env` file-ஆ commit பண்ணிடுவீங்க

இப்போ என்ன பிரச்சனை வரும்?

Git history-ல secret leak ஆகும். Developer laptop-ல copy ஆகும். Log-ல print ஆகும். Production-ல password மாற்ற வேண்டுமென்றால் 15 services-ல எல்லாம் deploy பண்ண வேண்டும். யார் secret பார்த்தார்கள், யார் மாற்றினார்கள் என்ற audit இல்லை. 

Secret ஒன்று compromise ஆனால் அதை தெரியாமல் months வரை இருக்கும்.

**இது config management பிரச்சனை அல்ல. Access, lifecycle, audit பிரச்சனை.**

## 2. Mental Model

Secret என்பது value அல்ல, **sensitive data with lifecycle**.

Config: `DB_HOST`, `PORT` - பார்த்தால் பிரச்சனை இல்லை.
Secret: `DB_PASSWORD`, `API_KEY`, `PRIVATE_KEY` - பார்க்கப்படக்கூடாது, மாற்றப்பட வேண்டும், யார் பயன்படுத்தினார்கள் என்று தெரிய வேண்டும்.

Mental model: **Central vault + strict access control + short-lived access**.

Service secret-ஐ தன்னிடம் store பண்ணக்கூடாது. தேவைப்படும் போது மட்டும் fetch பண்ணி memory-ல வைத்துக்கொள்ள வேண்டும்.

## 3. How It Works

ஒரு proper secrets management அமைப்பு 4 விஷயங்களை தருகிறது:

**1. Central store with encryption at rest.** 
Secrets manager-ல எல்லாம் ஒரே இடத்தில் இருக்கும். Rest-ல KMS-ஆல் encrypt ஆகி இருக்கும். 

**2. Identity based access, not shared files.**
Service A-க்கு மட்டும் DB_PASSWORD read permission. Developer-க்கு production secret read permission இல்லை. IAM role / service identity-ஆல் access control நடக்கும்.

**3. Audit and rotation.**
யார் எப்போது secret access பண்ணினார்கள் என்று log இருக்கும். Rotation policy வைத்து automatic-ஆக secret மாற்றலாம். Old version still works for graceful rollout.

**4. Dynamic secrets.**
Database password-க்கு பதில், service request பண்ணும் போது தற்காலிக credential generate பண்ணி கொடுக்கலாம். 1 hour-க்கு பிறகு auto expire.

Flow:
`service -> IAM auth -> Secrets Manager -> KMS decrypt -> secret return -> service uses in memory`

Kubernetes-ல இது `External Secrets Operator + Vault` அல்லது cloud managed `AWS Secrets Manager / Azure Key Vault / GCP Secret Manager` மூலம் நடக்கும்.

## 4. Architectural Reasoning

Secrets management தேவைப்படுவது எப்போது?

* Multiple services / multiple environments. Secret sprawl ஆரம்பிக்கும்
* Team size > 3. Secrets manually share பண்ணுவது risky
* Compliance requirement. PCI, SOC2-ல audit trail கேட்பார்கள்
* Zero trust architecture. Service-க்கு தேவையான minimum secret மட்டும்

Alternative என்ன?
* Environment variables: Simple, but process env-ல dump ஆகும், container image-ல bake ஆகும்
* Config map / Vault file mount: Better, but rotation கடினம்
* Hardcoded in code: Disaster

Architect-ஆக நீங்கள் தேர்வு செய்யும் போது கேட்க வேண்டிய கேள்வி:
Secret compromise ஆனால் impact என்ன? அதை detect பண்ண முடியுமா? அதை rotate பண்ண எவ்வளவு நேரம் ஆகும்?

## 5. Trade-offs

**Security vs Availability.** Secrets manager down ஆனால் service start ஆகாது. அதனால் caching, local fallback, high availability region setup தேவை.

**Latency.** Service start time-ல secret fetch செய்வது extra network call. அதனால் startup latency வரும். Cache + background refresh பண்ண வேண்டும்.

**Complexity vs Operability.** Vault setup, policy as code, rotation automation - initial complexity அதிகம். ஆனால் long term-ல blast radius குறையும்.

**Static vs Dynamic secrets.** Static secret simple ஆனால் long lived risk அதிகம். Dynamic secret secure ஆனால் database / service support வேண்டும்.

Failure mode முக்கியம்: Secret rotation போது new secret deploy ஆகும் முன்பு service crash ஆனால்? Versioning + dual read support வேண்டும்.

## 6. Practical Example

E-commerce platform. `payment-service` Stripe secret key வைத்திருக்கிறது. `order-service` Postgres-க்கு connect ஆக வேண்டும்.

Old way: Stripe key `.env` file-ல இருக்கு. Developer laptop-ல உள்ளது. Key leak ஆனால் தெரியாது.

New way:
* Secrets Manager-ல `prod/stripe/sk_live_
