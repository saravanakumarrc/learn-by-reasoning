# Model gateway

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.2 — Enterprise patterns

## 1. Problem

உங்களுக்கு ஒரு enterprise AI system வளர்ந்து வருகிறது.

ஒரு service summarization க்கு LLM use பண்ணுது. இன்னொரு service code generation க்கு வேற model use பண்ணுது. Customer support chatbot ஒரு model, internal RAG agent இன்னொரு model. 

ஒவ்வொரு team-ம் நேரடியாக OpenAI, Anthropic, local LLM, vector DB connect பண்ணி code எழுத ஆரம்பிக்கிறாங்க.

இப்போ என்ன problem வரும்?

* ஒரு model price மாறினா, அல்லது API down ஆனா, எல்லா service-லயும் code மாற்றணும்.
* Rate limit, retry, timeout logic எல்லா இடத்துலயும் duplicate ஆகுது.
* Prompt format ஒவ்வொரு provider-க்கும் வேற. Context window, token limits வேற.
* Cost எவ்வளவு ஆகுது, எந்த team எந்த model use பண்ணுது என்பது தெரியாது.
* Security, PII filtering, prompt injection guardrails எல்லாம் app layer-ல scattered ஆகுது.

இதை தொடர்ந்து விட்டால், AI usage ஒரு spaghetti ஆகும். Operability இல்லாமல் போகும்.

> **What problem became painful?** Too many apps talking directly to too many models, with no central control on routing, cost, policy, observability.

அதுக்குத்தான் Model Gateway தேவை.

## 2. Mental Model

Model Gateway என்பது உங்கள் LLM models-க்கு ஒரு **single entry point / API façade**.

உங்கள் app -> Gateway -> Model Provider.

Gateway ஒரு smart router போல வேலை செய்யும். Request வரும்போது யார் கேட்டார்கள், என்ன use case, latency requirement என்ன, cost budget என்ன என்பதை பார்த்து, எந்த model-க்கு route பண்ண வேண்டும் என்று முடிவு செய்யும்.

இது traffic cop + policy enforcer + observability hub.

## 3. How It Works

ஒரு typical request flow:

`App -> AuthN/Z -> Gateway -> Policy / Routing -> Provider Adapter -> LLM`

* **Normalization**: Gateway OpenAI-style chat completion format-ஐ accept பண்ணி, அதை target provider-க்கு translate பண்ணும். Anthropic, Azure OpenAI, local vLLM எல்லாத்துக்கும் adapter இருக்கும்.
* **Routing**: Rule based or intelligent. ex: `summarization` -> cheap model, `code review` -> larger model, `latency < 500ms` -> specific deployment.
* **Resilience**: Retry with exponential backoff, timeout, circuit breaker, failover to another model/provider.
* **Governance**: Prompt sanitization, PII redaction, content filter, rate limit per tenant/team.
* **Observability**: Token usage, cost per request, latency, error rate, prompt/response logging.

Gateway stateless ஆக இருக்கலாம், அல்லது routing decisions க்கு small state store use பண்ணலாம்.

## 4. Architectural Reasoning

Model Gateway useful ஆகும் போது:

* **Multiple providers/models**: OpenAI, Anthropic, Gemini, on-prem Llama. App code-ல provider lock-in வேண்டாம்.
* **Multi-team platform**: Different teams different SLAs, cost budgets.
* **Central policy**: Security, compliance, audit log எல்லாம் ஒரே இடத்தில்.
* **Cost control**: Route low priority jobs to cheaper model, peak traffic-ல fallback.

Alternatives:

* **Direct client call**: Simple start-ல ok. Scale ஆகும்போது கட்டுப்படுத்த முடியாது.
* **Per-service wrapper**: DRY violate ஆகும். Update propagation கஷ்டம்.
* **Service mesh sidecar**: Low-level, model-specific logic handle பண்ண கஷ்டம்.

Gateway தேர்வு செய்யும்போது நீங்கள் ஒரு control plane உருவாக்குகிறீர்கள். App team-க்கு model என்பது just an API, internal complexity hide ஆகும்.

## 5. Trade-offs

* **Latency overhead**: Gateway extra hop add ஆகும், ~10-50ms. Caching/streaming மூலம் குறைக்கலாம்.
* **Single point of failure**: Gateway down ஆனால் எல்லா AI call-ம் down. High availability, multi-region, autoscaling முக்கியம்.
* **Complexity shift**: App-லிருந்து gateway-க்கு move ஆகும். Routing logic தவறாக இருந்தால் wrong model-க்கு cost spike ஆகும்.
* **Observability vs privacy**: Logging prompts for debugging useful, ஆனால் PII leak risk. Data retention policy தேவை.

Failure mode: Gateway routing config bug -> production traffic expensive model-க்கு போகும். அதனால் canary rollout + cost alerts must.

## 6. Practical Example

Enterprise bank.

3 products: Fraud detection agent, Loan document summarizer, Customer chatbot.

All need LLM.

Architecture:

`Apps -> Model Gateway -> Routing`

* `fraud` -> high accuracy model, on-prem private deployment, strict latency SLA
* `summarizer` -> cost optimized model, batch allowed
* `chatbot` -> balanced model, with guardrails + PII redaction

Gateway-ல் tenant isolation: per product rate limit, monthly spend cap.

Provider OpenAI-லிருந்து Azure OpenAI-க்கு மாற வேண்டும் என்றால், Gateway config மாற்றினால் போதும். App code touch வேண்டாம்.

Cost dashboard: எந்த team எவ்வளவு token use பண்ணுது, எந்த prompt expensive என தெரியும்.

## 7. Reasoning Challenge

உங்களிடம் 3 models இருக்கு: `fast-cheap`, `accurate-expensive`, `on-prem-private`.

Production-ல chat traffic 10k RPM. 70% simple FAQ, 20% complex reasoning, 10% sensitive PII containing.

Latency budget 800ms. Cost budget strict.

Gateway-ல routing எப்படி design பண்ணுவீங்க? Failover என்ன செய்வீங்க? Sensitive traffic எப்படி handle பண்ணுவீங்க?

## 8. Key Takeaways

* Model Gateway என்பது model access-க்கு centralized control plane. Lock-in குறைக்கும்.
* Route by use case, latency, cost, compliance, not just "best model".
* Resilience, observability, governance ஆகியவை gateway-ன் core value.
* Gateway ஒரு architectural trade-off: central control vs extra hop and SPOF.

இதை வச்சு நீங்கள் model choice-ஐ business constraint-களோடு align பண்ண முடியும், code change இல்லாமல்.
