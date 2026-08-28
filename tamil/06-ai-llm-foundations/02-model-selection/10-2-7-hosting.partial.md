# PARTIAL — Hosting

> Reason: Ollama reached num_predict
> num_predict: 32768

## 1. Problem

Prototype-ல OpenAI API கூப்பிட்டு LLM feature வேலை செய்தது. நல்லா இருந்தது.

Production-க்கு வந்ததும் என்ன ஆகுது?

* Traffic spike-ல cost திடீரென்று 3x ஆகுது
* Latency P95 2 sec-க்கு மேல் போகுது, user drop ஆகிறார்கள்
* Customer data PII வெளியே போகக் கூடாது என்ற compliance இருக்கு
* Prompt திருத்தினால் உடனே test பண்ணணும், model version lock வேண்டும்

இப்போது கேள்வி வருது: **Model-ஐ எங்கே run பண்ணுவது?** இதுதான் hosting decision.

## 2. Mental Model

Hosting என்பது infra மட்டும் இல்லை. இது ஒரு contract:

* **Where** weights run → latency, data residency
* **Who** manages GPU, scaling, uptime → ops burden
* **How** you pay → per token vs fixed infra cost

Model selection-ஐ தனியாக பார்க்க முடியாது. Hosting constraint தான் viable models-ஐ filter பண்ணும்.

## 3. How It Works

மூன்று realistic patterns இருக்கு.

**Managed API hosting**  
OpenAI, Anthropic, Gemini போன்றவை. நீங்கள் API call பண்ணுவீர்கள். They handle GPU, scaling, patching.

**Self-hosted open weights**  
Llama, Mistral, Qwen போன்ற open models-ஐ உங்கள் infra-ல் run பண்ணுவது. Kubernetes + GPU nodes, vLLM/TensorRT-LLM போன்ற serving stack.

**Hybrid / Routing**  
Sensitive traffic → self-hosted. Bulk, non-sensitive → managed API. Cost/Latency based routing.

Data flow simple-ஆக:

```mermaid
graph LR
    Client-->API Gateway
    API Gateway-->Router
    Router-->ManagedLLM
    Router-->SelfHostedLLM
    SelfHostedLLM-->VectorDB
```

Router தான் policy decide பண்ணும்: data class, latency budget, cost cap.

## 4. Architectural Reasoning

எப்போது என்ன தேர்வு?

**Managed API** useful when:
* Team-க்கு ML ops இல்லை
* Traffic unpredictable, bursty
* Time-to-market முக்கியம்
* Data non-sensitive, public

**Self-hosted** useful when:
* Data privacy / data residency hard requirement
* Predictable high volume, cost per token அதிகம் ஆகுது
* Latency SLA < 500ms, network hop தேவையில்லை
* Model customization, fine-tuning, prompt caching control வேண்டும்

Constraint → Option mapping:
* Compliance → Self-hosted
* Latency → Self-hosted + same region
* Cost at scale → Self-hosted
* Team size small → Managed

## 5. Trade-offs

* **Control vs Ops burden**: Self-hosted-ல் model version, quantization, batching முழு control உண்டு. ஆனால் GPU driver, node failure, scaling, monitoring உங்கள் பொறுப்பு. On-call ஆகும்.
* **Cost predictability**: Managed API ஆரம்பத்தில் cheap. Scale-ல் per token cost கூடி, bill unpredictable ஆகும். Self-hosted upfront capex + fixed infra, ஆனால் marginal cost குறைவு.
* **Latency & availability**: Managed API network latency + provider outage உங்கள் கையில் இல்லை. Self-hosted-ல் region control உண்டு, ஆனால் உங்கள் infra down ஆனால் நீங்கள் தான் fix பண்ண வேண்டும்.
* **Vendor lock-in & model switching**: API-ல் provider change செய்வது painful. Self-hosted-ல் weights swap பண்ணி 10 நிமிடத்தில் மாறலாம்.

Failure mode: Managed API rate limit hit ஆனால் retry with exponential backoff மட்டுமே option. Self-hosted-ல் GPU OOM, request queue buildup ஆனால் autoscaling slow, request timeout ஆகும்.

## 6. Practical Example

Enterprise RAG chatbot for HR policy.

Constraints: employee PII, latency <800ms, 5k queries/day, cost sensitive.

Decision: Hybrid.

* Public policy Q&A → Managed API with small model, cheap
* PII containing queries → Self-hosted Llama 3.1 8B quantized on 1x A10G in same VPC, with private vector DB
* Router checks if query contains employee ID → route to self-hosted

Result: Compliance satisfied, cost 60% குறைந்தது, latency P95 620ms.

## 7. Reasoning Challenge

உங்களிடம் AI coding assistant feature உள்ளது. Daily 50k requests, average prompt 4k tokens. Data mostly public code snippets, ஆனால் 10% requests internal repo code. Team-ல்
