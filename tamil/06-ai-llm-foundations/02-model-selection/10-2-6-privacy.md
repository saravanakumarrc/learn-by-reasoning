# Privacy

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.6 — Model selection

## 1. Problem

உங்க company ஒரு LLM பயன்படுத்தி customer support chatbot பண்ணுது. Users தங்க personal data, PII, credit card number, medical history போன்றவற்றை தட்டச்சு செய்கிறார்கள்.

அந்த data எங்கே போகிறது?
* Prompt முழுவதும் model provider-க்கு அனுப்பப்படுகிறது.
* Provider அதை logging பண்ணலாம், training-க்கு பயன்படுத்தலாம், அல்லது அவர்களின் internal systems-ல் store பண்ணலாம்.

இப்போது privacy compliance என்ன சொல்கிறது? GDPR, HIPAA, India DPDP Act — user data-வை third party-க்கு அனுப்புவது, retain பண்ணுவது தெளிவான consent இல்லாமல் சட்டவிரோதம்.

**Problem ஆனது:** Model selection செய்யும்போது performance மட்டும் பார்த்தால் போதாது. Data எங்கே செல்கிறது, யார் பார்க்கிறார்கள், எவ்வளவு நேரம் retain ஆகிறது என்பது architectural decision ஆகிறது.

## 2. Mental Model

Privacy என்பது data flow-ன் boundary control.

ஒரு model-ஐ தேர்வு செய்வது என்பது:
* **Data residency:** Data எந்த region-ல் process ஆகிறது
* **Data retention:** Provider data-வை எவ்வளவு நேரம் வைத்திருக்கிறார்
* **Training usage:** உங்க prompt provider-ன் model training-க்கு பயன்படுமா?
* **Access control:** யார் உங்க prompts-ஐ பார்க்க முடியும்?

இது model accuracy-க்கு எதிரான trade-off அல்ல. இது architecture constraint.

## 3. How It Works

LLM model selection-ல் privacy-க்கு மூன்று main options உள்ளன:

**1. Public API hosted models**
OpenAI, Anthropic, Gemini போன்றவை. Model உங்களுடைய infrastructure-ல் இல்லை. Prompt network மூலம் அனுப்பப்படுகிறது. Provider-ன் privacy policy-க்கு உட்பட்டது. பெரும்பாலும் data 30 நாள் வரை logging-க்கு retain ஆகும்.

**2. Private / Dedicated deployment**
Model-ஐ உங்கள் VPC-ல், on-prem அல்லது private cloud-ல் deploy செய்வது. Azure OpenAI Service private endpoint, AWS Bedrock with VPC, self-hosted open source models.

Data provider network-க்கு வெளியே இருக்காது. Logging நீங்கள் control செய்கிறீர்கள்.

**3. On-device / Local inference**
Edge device-ல் small model run செய்வது. Data device-ஐ விட்டு வெளியே போகாது. Privacy maximum, performance limited.

Model selection-ன் core question: **"இந்த prompt-ல் உள்ள data-வை எவ்வளவு trust செய்ய முடியும்?"**

## 4. Architectural Reasoning

Privacy constraint வரும்போது model selection எப்படி மாறுகிறது?

* **PII அல்லது regulated data இருந்தால்:** Public API direct use ஆபத்து. Data minimization பண்ண வேண்டும். PII-ஐ redact செய்து tokenize செய்ய வேண்டும். அல்லது dedicated deployment தேர்வு.
* **Low sensitivity data, high throughput, cost sensitive:** Public API சரியானது. Latency குறைவு, operational overhead இல்லை.
* **Audit requirement உள்ள enterprise:** Data residency guarantee வேண்டும். EU customer data EU region-ல் process ஆக வேண்டும். Provider-ன் data processing agreement தேவை.

அதனால் architect-கள் முதலில் data classification பண்ணுவார்கள்:
* Public
* Internal
* Confidential
* Restricted

ஒவ்வொன்றுக்கும் வெவ்வேறு model deployment tier.

## 5. Trade-offs

**Privacy vs Cost & Operability**
Private deployment-க்கு GPU infra, MLOps team, monitoring வேண்டும். Cost 5-10x அதிகம். Public API-க்கு pay-per-token, zero ops.

**Privacy vs Model Quality**
Latest frontier model பெரும்பாலும் public API-ல் மட்டுமே கிடைக்கும். Self-hosted open source models quality குறைவு. அப்படி எனில் privacy-க்காக performance குறைக்க தயாரா?

**Privacy vs Latency**
On-prem model network hop இல்லை. ஆனால் smaller model-ஐ தான் run செய்ய முடியும். Public API-ல் larger model கிடைக்கும்.

**Failure mode:** Privacy misconfiguration. நீங்கள் "training data off" option-ஐ enable பண்ணவில்லை என்றால், உங்க customer data அடுத்த model version-ல் leak ஆகும்.

## 6. Practical Example

Bank-க்கு loan application chatbot.

User தன் PAN, income, bank statement details upload செய்கிறார். இது Restricted data.

Architect reasoning:
* Public API-க்கு raw data அனுப்ப முடியாது.
* Option A: Data redaction pipeline. PII-ஐ mask செய்து, `<PERSON_ID>` placeholder வைத்து model-க்கு அனுப்பு. Model output-ஐ பிறகு rehydrate செய்.
* Option B: Private deployment. Azure OpenAI with customer managed keys, private link. Data never leaves bank VPC. DPA signed.

Bank Option B தேர்ந்தெடுக்கிறது. Trade-off: Cost அதிகம், model update slow. ஆனால் compliance breach penalty கோடிகளில் இருக்கும்.

இதே chatbot marketing FAQ-க்கு மட்டும் என்றால் public API போதும்.

## 7. Reasoning Challenge

உங்களிடம் healthcare RAG system உள்ளது. Patient records vector database-ல் உள்ளன. Doctor query-க்கு LLM answer generate செய்ய வேண்டும். Data HIPAA regulated.

Option 1: OpenAI API with data retention off.
Option 2: Self-hosted Llama 3 on private Kubernetes with encryption at rest.

Processing latency requirement < 2s. Team size 3 engineers.

நீங்கள் எதை தேர்வு செய்வீர்கள்? ஏன்? என்ன trade-off ஏற்படும்?

## 8. Key Takeaways

* Model selection என்பது performance மட்டுமல்ல, data boundary decision.
* Privacy constraints model deployment topology-ஐ dictate செய்கிறது: public API vs private vs on-device.
* PII/regulated data-க்கு data minimization, redaction, அல்லது dedicated deployment தேவை.
* Every privacy gain comes with cost, ops complexity, அல்லது model quality trade-off.
