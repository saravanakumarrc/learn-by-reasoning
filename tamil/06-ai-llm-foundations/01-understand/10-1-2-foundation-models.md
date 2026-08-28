# Foundation models

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.2 — Understand

## 1. Problem

ஒரு enterprise-க்கு sentiment analysis வேண்டும், அடுத்து summarization வேண்டும், அடுத்து code generation வேண்டும், அடுத்து customer support chatbot வேண்டும்.

ஒவ்வொரு task-க்கும் தனியா dataset கொண்டு வந்து, label போட்டு, model train பண்ணுறது என்ன ஆகும்? 

Data collection cost, labeling cost, training compute cost, time to market எல்லாம் அதிகம். ஒரு model-ஐ production-க்கு கொண்டு வர 3-6 மாதம் ஆகும். Team size பெருசு.

இப்படி ஒவ்வொரு use case-க்கும் from scratch பண்ண முடியாது. Pain point clear: **reuse இல்லாமல் general language understanding-ஐ எப்படி scale பண்ணுவது?**

## 2. Mental Model

Foundation model என்பது **முதலில் பொதுவான language understanding-ஐ கற்றுக்கொண்ட பெரிய pre-trained model**.

அது specific task-க்கு train பண்ணப்படவில்லை. அது internet-scale text, code, images போன்ற massive unlabeled data மீது self-supervised objective-ல் train ஆகி இருக்கும்.

நினைத்துப்பார்: ஒரு senior engineer-ஐ வேலைக்கு எடுத்து, 10 வருட அனுபவம் கொடுத்தது போல. அவனுக்கு ஒரு புது domain கொடுத்தால் சீக்கிரம் adapt ஆகிறான். அதே concept தான்.

## 3. How It Works

Core idea: **pre-training → adaptation**.

Pre-training:
Transformer architecture + next-token prediction போன்ற objective. Model billions of parameters-ஐ பார்த்து grammar, world knowledge, reasoning patterns, code syntax எல்லாவற்றையும் internal representation-ஆக கற்றுக்கொள்கிறது.

Adaptation:
இதை குறைந்த data-யில் task-க்கு ஏற்றவாறு tune பண்ணலாம். Options இருக்கு:
* Prompting + in-context learning: zero-shot / few-shot
* Fine-tuning: LoRA / QLoRA போன்ற parameter efficient methods
* RAG: external knowledge-ஐ retrieval பண்ணி context-ஆக கொடுப்பது

Model எப்போதும் from scratch train ஆகவில்லை. பொதுவான backbone மீது build பண்ணுகிறோம்.

## 4. Architectural Reasoning

இது எப்போது useful?

* நீங்கள் பல downstream tasks வைத்திருக்கிறீர்கள். ஒரே backbone-ஐ reuse பண்ணலாம்.
* Domain data குறைவு. Massive pre-training knowledge transfer ஆகும்.
* Time to market முக்கியம். Fine-tune செய்வது months அல்ல, weeks/days.

Constraint it addresses: **data and compute scarcity**.

Alternatives:
* Train small task-specific model from scratch: control அதிகம், cost அதிகம்.
* Use off-the-shelf API: fast, but latency, privacy, cost per token.
* Distill to smaller model: on-device use case-க்கு.

Architect-ஆக நீங்கள் முடிவு பண்ண வேண்டியது: pre-trained backbone-ஐ internal-ஆக host பண்ணுவதா, managed API-யை use பண்ணுவதா? Data sensitivity, latency SLA, cost per request இதை decide பண்ணும்.

## 5. Trade-offs

* **General vs Specific.** Foundation model எல்லாம் பார்த்திருக்கும். ஆனால் உங்கள் internal jargon, product policy சரியாக தெரியாது. Hallucination வரும்.
* **Compute & Latency.** Large model = high inference cost, high latency. Production-ல் throughput முக்கியம். Quantization, distillation, caching தேவை.
* **Control & Privacy.** Third-party API use பண்ணினால் data leaves your perimeter. On-prem host பண்ணினால் ops complexity அதிகம்.
* **Adaptation cost.** Fine-tune பண்ணினால் model drift, versioning, evaluation overhead வரும். Prompt engineering + RAG போதுமானதா என்பதை reason பண்ண வேண்டும்.

Failure mode: Foundation model-ஐ blind trust பண்ணி validation இல்லாமல் போடுவது. It confidently hallucinates.

## 6. Practical Example

Bank-க்கு 3 needs இருக்கு: KYC document QA, fraud transaction explanation, customer support chatbot.

Foundation model approach:
ஒரே LLM backbone-ஐ எடுக்கிறோம். 
* Document QA-க்கு RAG pipeline: internal policy docs, transaction logs-ஐ vector database-ல் index பண்ணி retrieval.
* Fraud explanation-க்கு structured data + few-shot prompting.
* Support chatbot-க்கு fine-tune with brand tone data using LoRA.

மூன்று separate models train பண்ண தேவையில்லை. Backbone reuse. New use case வந்தால் prompt/RAG மாற்றினால் போதும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு healthcare app இருக்கு. Patient data sensitive, latency < 500ms வேண்டும், compliance கண்டிப்பாக தேவை.

Foundation model-ஐ எப்படி use பண்ணுவீர்கள்? Public API-யை direct-ஆக use பண்ணலாமா? On-prem smaller distilled model-ஐ fine-tune பண்ணலாமா? RAG-ஐ எங்கே வைப்பீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

* Foundation model என்பது **general pre-training + cheap adaptation** என்ற architecture pattern.
* இது data/compute scarcity பிரச்சினையை தீர்க்கிறது, ஆனால் control, cost, hallucination என்ற புது trade-off-
