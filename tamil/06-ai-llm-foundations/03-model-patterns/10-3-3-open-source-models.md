# Open-source models

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.3 — Model patterns

## 1. Problem

நீங்கள் ஒரு AI feature build பண்ணறீங்க. LLM தேவை. Options என்ன?

1. Closed API-க்கு call பண்ணு - OpenAI, Anthropic மாதிரி
2. Own infrastructure-ல open-source model run பண்ணு

Closed API எளிது. ஆனால் painful ஆகும் போது?

* Cost unpredictable ஆகும். Token usage scale ஆகும் போது bill கணிசமாக உயரும்.
* Latency உங்க control-ல இல்லை. Network hop, rate limit வரும்.
* Data privacy. Customer PII, proprietary data external API-க்கு போகுது.
* Prompt / output control முழுமையாக இல்லை. Model version change ஆனால் behavior மாறும்.
* Offline / air-gapped requirement வரும்.

இந்த constraints painful ஆகும்போது engineers open-source models பார்க்கிறார்கள். இது free license-ல release ஆன model weights, ஆனால் அது முழு solution இல்லை.

## 2. Mental Model

Open-source model = model weights + license + community.

Model weights மட்டும் போதாது. உங்களுக்கு தேவை:

* Inference infrastructure: GPU, serving system
* Fine-tuning / evaluation pipeline
* Observability, safety guardrails

அதனால் open-source என்பது **control and cost ownership** வாங்குவது. Vendor lock-in குறைக்கிறது, ஆனால் operational complexity உங்களுக்கு மாறுகிறது.

## 3. How It Works

Open-source model release ஆன பிறகு flow இப்படி:

Developer downloads weights → quantize / optimize பண்ணி → serve via vLLM, TGI, Ollama, or TensorRT-LLM → API wrapper மூலம் உங்கள் service call பண்ணும்.

பெரும்பாலும் உண்மையான production-ல நீங்கள் raw model-ஐ direct use பண்ண மாட்டீங்க. RAG pipeline, tool calling, routing logic சேர்க்கிறீங்க.

Key difference: closed API-ல model is a black box service. Open-source-ல model is a component you host. நீங்கள் version pin பண்ணலாம், fine-tune பண்ணலாம், data local-ல keep பண்ணலாம்.

## 4. Architectural Reasoning

Open-source model use பண்ணும் போது எப்போ useful?

* **Cost predictability தேவை**: High volume internal use cases. Chatbot for support, code generation for engineers. Per token cost உங்க infrastructure cost-க்கு மாறும்.
* **Latency / availability SLA**: On-prem deployment, no external network dependency.
* **Data sovereignty**: Finance, healthcare, legal data external போகக் கூடாது.
* **Customization**: Domain specific fine-tuning, custom tokenizer, instruction tuning with internal data.
* **Experimentation control**: Model version, temperature, system prompt full control.

Alternatives:

* Closed API: fastest to start, zero ops
* Hybrid: Small open model on-prem for PII, large closed model for quality
* Model distillation: Open model-ஐ closed model-ஆல் train பண்ணி smaller model கிடைக்கும்

Architect decision point: Traffic pattern + data sensitivity + team ops capability.

## 5. Trade-offs

**Control vs Ops burden**
Open-source தரும் control-க்கு விலை GPU cost, MLOps team. Serving, scaling, monitoring எல்லாம் உங்கள் problem.

**Quality vs Cost**
Top open models Llama 3.1 405B, Mistral Large class-ல closed models-ஐ approach பண்ணும். ஆனால் smaller open models 7B-70B range-ல quality gap இருக்கு. உங்கள் use case quality sensitive ஆனால் open-source தேர்வு tricky.

**Innovation speed vs Stability**
Open community fast release. ஆனால் breaking changes வரும். Version pin பண்ணி test செய்யணும்.

**Security surface**
Model weights open. Adversarial prompt, data leakage risks. உங்களுக்கு safety layer, output filtering தேவை. Closed provider அதை handle பண்ணும்.

**Failure modes**
GPU OOM, request queue build-up, model cold start latency. Closed API-ல auto scale உள்ளது. Open-source-ல நீங்கள் autoscaling, batching, caching plan பண்ணணும்.

## 6. Practical Example

Enterprise bank internal document Q&A system.

Constraint: Customer loan documents, NDA data. External API allowed இல்லை.

Decision: Llama 3 70B open weights-ஐ on-prem GPU cluster-ல deploy. RAG pipeline with private vector database.

Architecture: API Gateway → Auth service → Router. Router simple queries-க்கு 7B model, complex reasoning-க்கு 70B model. Embedding model open-source. All traffic stays inside VPC.

Trade-off accepted: Initial GPU investment $200k, 2 engineers for serving. Gain: zero data egress, predictable cost per query, compliance pass.

## 7. Reasoning Challenge

உங்களிடம் இரண்டு use cases உள்ளது:

A. Customer-facing chatbot, 10M requests/month, non-sensitive content, quality critical
B. Internal code review assistant, 50 engineers, proprietary codebase, latency sensitive

ஒரே infrastructure-ல இரண்டையும் handle பண்ண வேண்டும். Open-source model use பண்ணுவீர்களா? எந்த model size / deployment pattern தேர்வு செய்வீர்கள்? ஏன்? Cost, latency, data privacy எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Open-source model என்பது model weights மட்டும் இல்லை, control and operational ownership.
* தேர்வு driver data privacy, cost predictability, latency SLA, customization need.
* Every open-source gain comes with ops burden: serving, scaling, safety, monitoring.
* Hybrid architecture பெரும்பாலும் practical: sensitive path open-source on-prem, public path closed API.
