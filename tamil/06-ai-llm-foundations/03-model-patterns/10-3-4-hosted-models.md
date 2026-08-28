# Hosted models

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.4 — Model patterns

## 1. Problem

உங்க team-க்கு ஒரு LLM feature வேண்டும். ஆனால் உங்களிடம்:

- GPU infra இல்லை
- ML ops team இல்லை
- Model training அல்லது fine-tuning தெரியாது
- Latency, uptime, scaling எல்லாம் உங்கள் கவலை அல்ல

இப்போது நீங்கள் என்ன செய்வீர்கள்? சொந்தமாக model host பண்ணி கஷ்டப்படுவீர்களா?

அல்லது ஏற்கனவே ரன்னிங் ஆகிற model-ஐ ஒரு API மூலம் use பண்ணுவீர்களா?

இதுதான் hosted models-ன் பிரச்சனை. Build vs Buy-ன் LLM version.

## 2. Mental Model

Hosted model என்பது நீங்கள் model-ஐ own பண்ணாமல், மற்றொரு provider-ன் infrastructure-ல் run ஆகும் model-ஐ API call மூலம் use பண்ணுவது.

நீங்கள் கவலைப்படுவது: prompt, context window, output parsing, cost per token.
Provider கவலைப்படுவது: GPU, autoscaling, model serving, patching, availability.

இது cloud-ல் database பயன்படுத்துவது போல. RDS வாங்கும் போது நீங்கள் disk management பண்ணுவதில்லை. அதே மாதிரி.

## 3. How It Works

நீங்கள் ஒரு hosted endpoint-க்கு HTTP request அனுப்புகிறீர்கள்:

`POST /v1/chat/completions` with model name, messages, temperature.

Provider:
- request-ஐ queue பண்ணி
- running model instance-க்கு route பண்ணி
- inference செய்து
- response திருப்பி அனுப்புகிறது

நீங்கள் control பண்ணுவது: model selection, parameters, rate limits, access keys.
நீங்கள் control பண்ண முடியாதது: model weights, version upgrade timing, underlying hardware.

முக்கியம்: நீங்கள் model-ஐ self-host பண்ணினால், உங்கள் VPC-ல் model containers run ஆகும். Hosted-ல், model provider-ன் network-ல் run ஆகும். Data leaves your boundary.

## 4. Architectural Reasoning

Hosted model எப்போது useful?

**Speed to market.** 2 வாரத்தில் RAG chatbot launch வேண்டும். Model training இல்லாமல், hosted API வைத்து prototype பண்ணலாம்.

**Variable load.** Day-ல் 10 requests, night-ல் 10k requests. Self-host-க்கு 24/7 GPU வேண்டும். Hosted-ல் pay-per-token.

**Ops complexity.** Model serving-க்கு vLLM, TensorRT, quantization, GPU memory management தேவை. Team-க்கு அந்த expertise இல்லை என்றால் hosted தேர்வு.

**Multiple models.** A/B test பண்ண வேண்டும்: GPT-4o vs Claude 3.5 vs open source model. Hosted providers model switching-ஐ config level-ல் செய்ய விடுகிறார்கள்.

Alternatives:
- **Self-hosted open source:** Mistral, Llama, Qwen. Full control, data stays in-house, but ops cost high.
- **On-prem hosted:** Provider-ன் hardware உங்கள் data center-ல். Compliance க்கு useful, cost high.
- **Managed hosting:** SageMaker, Vertex AI. Middle ground.

## 5. Trade-offs

**1. Control vs Convenience**
Hosted-ல் model version provider decide பண்ணுவார். நேற்று வேலை செய்த prompt இன்று behavior மாறலாம். Self-host-ல் pin பண்ணலாம்.

**2. Data privacy vs Compliance**
Prompts provider-க்கு போகிறது. PII, internal documents leak ஆகும் risk. Data residency, audit trail கட்டுப்படுத்த முடியாது. Financial/health domains-ல் இது blocker ஆகும்.

**3. Cost predictability**
Pay-per-token simple ஆக தெரியும். ஆனால் traffic spike வந்தால் bill spike. Self-host-ல் fixed cost. Long term, high volume-ல் self-host cheaper ஆகலாம்.

**4. Latency & reliability**
Provider network உங்கள் user-க்கு தொலைவில் இருந்தால் latency அதிகம். Retry, timeout, circuit breaker வேண்டும். Provider downtime = உங்கள் feature down.

Failure mode: Rate limit hit. உங்கள் service suddenly 429 errors தரும். அதனால் client-side retry with backoff, and fallback model தேவை.

## 6. Practical Example

Enterprise support chatbot.

Requirement: 3 languages support, 500 concurrent users, sensitive customer data.

Architecture:
API Gateway -> Auth Service -> Hosted LLM provider with private endpoint
RAG pipeline: Vector DB உங்கள் VPC-ல், embeddings hosted model மூலம் generate.

ஏன் hosted? Team-ல் 2 backend engineers மட்டுமே. GPU ops learn பண்ண நேரமில்லை. 2 வாரத்தில் MVP வேண்டும்.

Trade-off accept பண்ணினார்கள்: customer ticket summaries hosted model-க்கு போகும். Data classification filter வைத்து PII மாஸ்க் செய்தார்கள். Cost per 1M tokens monitor பண்ணி budget alert வைத்தார்கள்.

## 7. Reasoning Challenge

உங்களிடம் fintech app உள்ளது. Fraud detection notes-ஐ LLM generate பண்ண வேண்டும். Data extremely sensitive, cannot leave VPC. Volume predictable ~ 1M tokens/day. Team-ல் ML engineer இருக்கிறார்.

Hosted model use பண்ணுவீர்களா? Self-host பண்ணுவீர்களா? ஏன்? Cost, latency, compliance மூன்றையும் balance பண்ணி முடிவு சொல்லுங்கள்.

## 8. Key Takeaways

- Hosted models = inference infrastructure-ஐ outsource பண்ணுவது. Speed and ops simplicity க்கு பதிலாக control கொடுக்கிறீர்கள்.
- Model pattern தேர்வு data sensitivity, team size, load pattern, cost model மூலம் decide ஆகும்.
- எப்போதும் retry, timeout, rate limit handling, cost monitoring, and PII filtering வேண்டும்.
- Hosted தொடங்குங்கள், volume & compliance need வந்தால் self-host-க்கு migrate பண்ண plan வையுங்கள்.
