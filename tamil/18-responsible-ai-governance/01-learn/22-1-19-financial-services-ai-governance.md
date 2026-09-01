# Financial-services AI governance

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.19 — Learn

## 1. Problem

ஒரு bank-ல LLM-based chatbot customer-க்கு loan eligibility சொல்லுது. ஒரு நாள் அது தவறான rate கொடுத்துவிட்டது. அதுவும் audit trail இல்லாமல்.

அடுத்த வாரம் compliance கேட்கிறார்கள்: *"இந்த decision எந்த model version-ல் வந்தது? Training data என்ன? Prompt என்ன? Output ஏன் அப்படி வந்தது? Bias உண்டா?"*

உங்களால் பதில் சொல்ல முடியவில்லை.

Financial services-ல AI use பண்ணும்போது problem என்ன?

* Regulator கேட்கும்: fairness, explainability, auditability
* Business கேட்கும்: risk, brand reputation, liability
* Engineer கேட்கும்: model drift, data quality, prompt leakage

இதை மேனேஜ் பண்ணாமல் விட்டால் production-ல model deploy பண்ணவே முடியாது. அதனால் தான் AI governance வேண்டும்.

## 2. Mental Model

AI governance என்பது model-ஐ control பண்ணும் police அல்ல.

அது **decision lifecycle-ஐ observable, auditable, controllable ஆக்கும் framework**.

Think of it as: *who can use what model, on what data, for what decision, with what risk, and how we prove it later.*

Three pillars:

* **Policy**: என்ன allow, என்ன block
* **Control**: policy-ஐ technically enforce பண்ணும்
* **Evidence**: ஒவ்வொரு decision-க்கும் proof

## 3. How It Works

Production AI system-ல governance என்பது 4 layers:

**1. Model Registry & Versioning**
ஒவ்வொரு model version, prompt version, embedding model, fine-tune dataset ஆகியவை immutable artifact ஆக register ஆக வேண்டும். Model card இருக்க வேண்டும்.

**2. Data Governance & Lineage**
Training data, fine-tune data, RAG corpus எங்கிருந்து வந்தது, PII உள்ளதா, retention policy என்ன, என்பது traceable ஆக இருக்க வேண்டும்.

**3. Decision Logging**
ஒவ்வொரு inference request/response ஐயும் input, output, model_id, prompt_id, user_id, timestamp, latency, confidence score உடன் log பண்ணுங்கள். இது immutable audit log.

**4. Guardrails & Risk Controls**
Pre-call: input validation, PII redaction, prompt injection detection
Post-call: output classification, toxicity, hallucination check, policy violation check
Runtime: rate limit, cost limit, fallback to human

இவை எல்லாம் central policy engine மூலம் enforce ஆக வேண்டும். Service-க்கு service க்கு copy-paste guardrail இல்லை.

## 4. Architectural Reasoning

Financial services-ல AI governance ஏன் critical?

* **Regulatory constraint**: RBI, SEBI, IRDAI, GDPR, DPDP Act — explainability, fairness, data residency கேட்கும்
* **High stakes decision**: credit, fraud, KYC, insurance claim — தவறு = financial loss + legal liability
* **Non-deterministic system**: same input வெவ்வேறு output வரலாம். அதனால் reproducibility க்கு versioning முக்கியம்

எப்போது இதை தீவிரமாக செய்ய வேண்டும்?
எப்போது AI output direct customer impact செய்கிறதோ, அப்போது.

Chatbot FAQ = low risk. Credit scoring = high risk.

Alternatives:
* Ad-hoc manual review. Scale ஆகாது, inconsistent.
* No governance. Fast but audit fail ஆகும்.
* Centralized AI governance platform. Initial overhead அதிகம், ஆனால் long term operability நல்லது.

Architect choose பண்ணும்போது trade-off: speed to market vs auditability.

## 5. Trade-offs

**Centralized vs Decentralized controls**
Centralized policy engine ஒன்று maintain செய்வது consistent ஆக இருக்கும். ஆனால் latency add ஆகும், single point of failure ஆகும்.

**Full logging vs Privacy & Cost**
ஒவ்வொரு prompt/response-ஐயும் store பண்ணினால் audit சுலபம். ஆனால் PII retention risk, storage cost, vector DB size அதிகரிக்கும். Retention policy மற்றும் redaction முக்கியம்.

**Explainability vs Model performance**
Small interpretable model எளிதாக explain செய்யலாம். Large LLM performance better ஆனால் explainability குறைவு. Financial services-ல often you need both: LLM for generation + smaller classifier for policy check.

**Human-in-the-loop vs Full automation**
High risk decisions-ல human review வைத்தால் safe. ஆனால் latency, cost அதிகரிக்கும். Risk-based routing வேண்டும்.

Failure modes:
* Guardrail bypass via jailbreak → need continuous red teaming
* Model drift → performance degrade silently, need monitoring
* Log tampering → audit log must be append-only, ideally WORM storage

## 6. Practical Example

Bank-ல Loan pre-qualification chatbot.

Architecture:

User → API Gateway → Guardrail Service → LLM Service → Response

Guardrail Service input-ல PII detect செய்து mask பண்ணும், prompt injection check செய்யும்.

LLM Service model_id = `llm-v3.2`, prompt_id = `loan-prompt-v1.4` use பண்ணும்.

ஒவ்வொரு call-க்கும் event emit ஆகும் to `ai-audit-log` Kafka topic.

Consumer 1: real-time policy violation alert
Consumer 2: long term S3 + Parquet storage for audit
Consumer 3: model monitoring dashboard

If confidence < 0.7 or output contains rate info, route to human agent.

3 months later regulator audit வந்தால்: அந்த specific user request-க்கு exact model version, prompt, input, output, guardrail decision எல்லாம் retrieve செய்ய முடியும்.

## 7. Reasoning Challenge

உங்களிடம் fraud detection agent உள்ளது. அது real-time transaction-ஐ analyze செய்து block/allow முடிவு எடுக்கிறது.

Requirements:
* Decision latency < 200ms
* Full audit trail வேண்டும்
* Model weekly retrain ஆகிறது
* False positive க்கு business cost அதிகம்

நீங்கள் decision logging-ஐ synchronous-ஆக செய்வீர்களா அல்லது asynchronous-ஆக செய்வீர்களா? Guardrails-ஐ inline-ஆக வைப்பீர்களா அல்லது sidecar-ஆக வைப்பீர்களா? ஏன்?

## 8. Key Takeaways

* AI governance என்பது compliance checklist அல்ல, observable decision system
* Version everything: model, prompt, data, guardrail policy
* Log every decision immutably, redaction மற்றும் retention உடன்
* Risk-based controls: low risk automate, high risk human-in-the-loop
* Trade-off எப்போதும் உண்டு: speed vs auditability, performance vs explainability

இது தெரிந்தால் மட்டுமே financial services-ல AI-ஐ safely scale பண்ண முடியும்.
