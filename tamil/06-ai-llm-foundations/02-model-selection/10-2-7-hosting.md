# Hosting

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.7 — Model selection

## 1. Problem

நீங்கள் ஒரு LLM feature build பண்ண வேண்டும். RAG chatbot, agent, summarizer என எதுவாக இருந்தாலும் முதல் கேள்வி இதுதான்: **எந்த model-ஐ host பண்ணுறது?**

Own GPU-ல run பண்ணலாமா? OpenAI API-க்கு call பண்ணலாமா? Self-hosted open model போட்டுக்கலாமா?

Small model வைத்தால் cost குறைவு, ஆனால் quality குறையும். Large model வைத்தால் quality நல்லா இருக்கும், ஆனால் latency, cost, infra complexity எகிறும்.

இந்த decision தப்பாக போனால், production-ல போய் bill shock வரும், latency spike வரும், அல்லது user experience தரமில்லாமல் போகும்.

## 2. Mental Model

Model selection என்பது spec sheet compare பண்ணுவது அல்ல. இது **constraints-ஐ satisfy பண்ணும் trade-off**.

ஒரு service-க்கு தேவையானது: latency, throughput, cost per request, context length, reasoning quality, privacy, control.

Model என்பது ஒரு engine. Hosting decision என்பது அந்த engine-ஐ எங்கே, எப்படி run பண்ணுறது என்பது.

## 3. How It Works

மூன்று broad hosting options இருக்கு:

**1. Managed API - OpenAI, Anthropic, Gemini**
நீங்கள் API call பண்ணுறீங்க. Infra உங்களுடையது இல்லை. Scaling, uptime, optimization provider பார்த்துக்கொள்வார்.

**2. Self-hosted open weights - Llama, Mistral, Qwen, DeepSeek**
Model weights உங்கள் infra-ல இருக்கும். vLLM, TGI, Ollama மாதிரி serving stack மூலம் serve பண்ணுவீர்கள். GPU/accelerator உங்களுக்கு தேவை.

**3. Hybrid / Fine-tuned**
Base model managed API-ல இருக்கும், ஆனால் RAG, routing, guardrails, fine-tune உங்கள் கட்டுப்பாட்டில்.

Selection என்பது model capability மட்டும் அல்ல. Hosting cost + operational complexity + data privacy + latency budget எல்லாம் சேர்ந்தது.

## 4. Architectural Reasoning

Model selection எப்போது முக்கியமாகும்?

* **Latency sensitive**: Chat UI-ல user typing, 500ms-க்குள் first token வேண்டும். Small model on-prem GPU-ல தான் முடியும்.
* **Throughput high**: 10k requests per minute. Managed API cost அதிகமாகும். Self-hosted batching + caching மூலம் cost control பண்ணலாம்.
* **Data privacy / compliance**: Financial, healthcare data. Data third-party API-க்கு போகக்கூடாது. Self-hosted mandatory.
* **Cost predictable**: Startup-க்கு முதலில் API, scale ஆகும்போது self-hosted.
* **Reasoning heavy**: Agent, tool calling தேவைப்படும் போது larger model தேவை.

Decision flow பொதுவாக:

Problem → Latency & cost constraints → Data sensitivity → Model size → Hosting option.

## 5. Trade-offs

**Managed API vs Self-hosted**

* Cost: API per token, predictable ஆனால் scale-ல விலை ஏறும். Self-hosted upfront CapEx + ops cost, long term cheaper.
* Control: Self-hosted-ல version pin, fine-tune, logging முழு கட்டுப்பாடு. API-ல provider change பண்ணினால் prompt behavior மாறும்.
* Ops complexity: Self-hosted என்றால் GPU provisioning, model serving, autoscaling, monitoring, security patching உங்கள் பொறுப்பு.
* Latency: On-prem low network latency. API-ல internet roundtrip உண்டு.

**Model size trade-off**

Small 7B-8B model: fast, cheap, local GPU-ல run ஆகும். ஆனால் reasoning weak, long context handle பண்ண முடியாது.

Large 70B+ model: quality நல்லா இருக்கும், ஆனால் multi GPU தேவை, latency அதிகம், cost அதிகம்.

**Open weights vs Closed**

Open weights: inspect, fine-tune, host anywhere. Community support. Closed model: best quality, zero ops, ஆனால் vendor lock-in.

Failure mode: Self-hosted-ல GPU OOM, serving crash, version mismatch. Managed API-ல rate limit, downtime, price change.

## 6. Practical Example

Enterprise support chatbot, internal documents-ல RAG பண்ண வேண்டும்.

Constraint: PII data, so data cannot leave VPC. Latency budget 2 sec per response. 500 requests per day initially, scale to 5000.

Decision: Start with Llama 3.1 8B instruct, self-hosted on 1x A10G via Kubernetes + vLLM. RAG pipeline separate.

Why? Data privacy satisfy ஆகும். 8B model 2 sec-க்குள் respond பண்ணும். Cost fixed. Later traffic increase ஆனால் autoscaling or model upgrade to 70B possible.

அதே feature consumer app-க்கு external facing, non-sensitive data என்றால், initially GPT-4o mini API use பண்ணி launch பண்ணி, usage pattern பார்த்த பிறகு self-hosted-க்கு migrate பண்ணலாம்.

## 7. Reasoning Challenge

உங்களுக்கு 20k requests per day இருக்கு. Average prompt 4k tokens, output 500 tokens. Latency requirement < 800ms p95. Data PII அல்ல. Team-க்கு ML ops experience குறைவு.

Managed API பயன்படுத்தலாமா? Self-hosted small model பயன்படுத்தலாமா? எந்த model class தேர்வு செய்வீர்கள்? Cost, latency, ops complexity எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Model selection என்பது capability மட்டும் அல்ல, hosting constraints-ஐயும் சேர்த்து பார்க்க வேண்டும்.
* Data privacy + latency requirement இருந்தால் self-hosted தான் வழி.
* Start simple with managed API, scale-ல ops maturity வந்த பிறகு self-hosted-க்கு மாறுவது பொதுவான pattern.
* Every model choice creates a new trade-off: quality vs cost vs latency vs control.
