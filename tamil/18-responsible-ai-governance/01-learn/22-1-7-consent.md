# Consent

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.7 — Learn

## 1. Problem

ஒரு AI product-ல user data எடுத்து model training, personalization, analytics எல்லாம் பண்ணும்போது ஒரு கேள்வி வரும்: **இந்த data-வை நாம் உபயோகிக்க consent இருக்கா?**

Engineer ஆக நீங்கள் ஒரு feature build பண்ணுகிறீர்கள். App-ல user chat history-ஐ எடுத்து RAG pipeline-ல பயன்படுத்தலாம், அல்லது அதே data-வை model fine-tuning-க்கு அனுப்பலாம்.

இங்கே என்ன போகிறது wrong?

User சொல்லாமல் data எடுத்தால் trust போகும். GDPR, DPDP Act போன்ற regulation-ல fine வரும். முக்கியமாக, AI system output biased அல்லது harmful ஆகும் போது, "நாங்கள் எந்த data-வை உபயோகித்தோம் என்பது தெரியாது" என்று சொல்ல முடியாது.

Consent இல்லாமல் data use பண்ணினால் நீங்கள் கட்டுப்பாடு இல்லாத data pipeline-ஐ உருவாக்குகிறீர்கள். அதன் consequence audit, legal, reputation எல்லாம்.

## 2. Mental Model

Consent என்பது **permission with context** அல்ல, simple checkbox அல்ல.

Mental model: ஒரு data என்பது ஒரு key. அந்த key-ஐ எந்த door-க்கு திறக்க உபயோகிக்கலாம் என்பதை user decide பண்ண வேண்டும்.

Consent = **who can use what data for what purpose, for how long, and user can withdraw**.

அதனால் consent என்பது boolean flag அல்ல. இது purpose-bound, time-bound, revocable permission.

## 3. How It Works

ஒரு responsible AI system-ல consent flow இப்படி இருக்க வேண்டும்:

1. **Informed**: User-க்கு clear ஆக சொல்ல வேண்டும் - என்ன data எடுக்கிறோம், எதற்கு, எப்படி process பண்ணுவோம், third party-க்கு share பண்ணுவோமா.
2. **Specific**: "நாங்கள் உங்கள் data-வை எதற்கும் உபயோகிப்போம்" என்பது valid consent அல்ல. Training vs analytics vs personalization என தனித்தனியாக ask பண்ண வேண்டும்.
3. **Freely given**: Consent-ஐ கட்டாயமாக்கக்கூடாது. Service-ஐ access செய்ய consent தரவேண்டும் என்பது coercive.
4. **Revocable**: User எப்போது வேண்டுமானாலும் withdraw பண்ண முடிய வேண்டும். Withdraw பண்ணியதும் data usage stop ஆக வேண்டும், pipeline-ல இருந்து remove பண்ண வேண்டும்.

Technically, இது consent record-ஐ store பண்ணும். consent_id, user_id, purpose, granted_at, expires_at, version, channel. இந்த record audit-க்கு immutable log ஆக வேண்டும்.

## 4. Architectural Reasoning

Consent எப்போது useful?

* User-generated content, chat logs, biometric data, health data போன்ற sensitive data-ஐ AI model training / RAG / agent action-க்கு பயன்படுத்தும் போது.
* Cross-border data transfer இருக்கும் போது.
* Personalization engine, recommendation system, profiling.

Constraint it addresses: Legal compliance + trust + data governance.

Alternatives:
* **Opt-out**: Default allow, user later opt-out. இது regulation-ல பெரும்பாலும் valid அல்ல.
* **Implicit consent**: User action-ஐ consent ஆக assume பண்ணுவது. AI use case-ல risky.
* **No consent, anonymize**: Data-வை anonymize பண்ணி use பண்ணலாம். ஆனால் AI training-ல true anonymization கடினம். Re-identification risk உண்டு.

Architect choose explicit, purpose-specific consent when risk high, data sensitive, model decisions impact user.

## 5. Trade-offs

**Granularity vs UX friction**: Purpose-wise granular consent தர முடியும், ஆனால் user-க்கு 10 checkboxes காட்டினால் drop-off ஏறும். Balance பண்ண வேண்டும்.

**Consent storage vs system complexity**: Consent-ஐ enforce பண்ண data pipeline, feature flag, access control எல்லாவற்றிலும் check செய்ய வேண்டும். இது latency, complexity சேர்க்கும்.

**Revocation vs data immutability**: Model already trained on user data. User withdraw consent செய்தால் அந்த data-வை model-ல இருந்து முழுவதுமாக remove பண்ண முடியாது. இதற்கு data retention policy, unlearning, or training data versioning தேவை.

**Auditability vs cost**: Consent log immutable, verifiable ஆக வைத்திருக்க வேண்டும். இது storage, compliance overhead.

Failure mode: Consent UI update ஆனால் backend enforcement update ஆகவில்லை. User unchecked "training use" ஆனாலும் data training pipeline-க்கு போகிறது. இது silent violation.

## 6. Practical Example

Enterprise RAG product: Customer support chat history-ஐ knowledge base ஆக்குகிறோம்.

Architecture:

User signs up -> Onboarding-ல clear consent screen:
- "உங்கள் chat-ஐ நாங்கள் உங்கள் account-க்கு மட்டும் personalization-க்கு உபயோகிப்போம்" -> allow
- "உங்கள் anonymized chat-ஐ model improvement-க்கு training-க்கு உபயோகிப்போம்" -> separate toggle
- "Third party analytics vendor-க்கு share செய்வோம்" -> separate toggle

Consent store ஆகிறது Postgres + immutable audit log in object storage.

API gateway-ல middleware: request வரும்போது user_id -> consent service query -> purpose allowed? No, then block data access.

Feature flag system consent purpose-ஐ check செய்கிறது. Training pipeline ingestion job consent = false ஆன user data-ஐ filter பண்ணுகிறது.

User withdraw செய்தால், consent record update, data deletion workflow trigger ஆகி RAG index-ல இருந்து document remove, future training batch-ல exclude.

## 7. Reasoning Challenge

உங்களிடம் ஒரு generative AI assistant இருக்கிறது. User upload செய்த PDF-களை RAG-க்கு பயன்படுத்துகிறீர்கள். இப்போது product team கேட்கிறது: "இந்த uploaded documents-ஐ aggregate பண்ணி foundation model fine-tuning-க்கு உபயோகிக்கலாமா?"

உங்கள் data-ல 30% users explicit consent தந்துள்ளனர் "model improvement". மற்றவர்கள் தரவில்லை. Upload flow-ல consent checkbox இல்லை.

இங்கே என்ன architecture decision எடுப்பீர்கள்? Consent-ஐ எப்படி retrofit பண்ணுவீர்கள்? Withdrawal எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

* Consent என்பது checkbox அல்ல, purpose-bound permission with audit trail.
* AI system design-ல consent enforcement-ஐ data access layer-ல இருந்து pipeline வரை bake பண்ண வேண்டும்.
* Granularity முக்கியம்: training, personalization, sharing எல்லாம் தனித்தனி consent.
* Revocation என்பது technical problem: model unlearning, data deletion, pipeline filtering எல்லாம் design-ல இருக்க வேண்டும்.
