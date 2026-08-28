# Inference

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.9 — Understand

## Problem

Training முடிஞ்சுட்டு, நீங்க ஒரு LLM-ஐ production-ல விட்டா என்ன நடக்கும்?

User ஒரு prompt அனுப்புவார். அவருக்கு 1-2 வினாடிக்குள் பதில் வேண்டும். Model-ஐ அப்போது train பண்ண முடியாது. அது offline, expensive, slow.

இங்கே வரும் பெயின்: **ஒரு trained model-ஐ real-time, repeatable, cost-controlled முறையில் run பண்ணுவது எப்படி?**

Training-ல நீங்கள் weights-ஐ கற்றுக்கொள்கிறீர்கள். Inference-ல அந்த weights freeze ஆகி, input கொடுத்தால் output கிடைக்க வேண்டும். அதுவும் high concurrency-ல, consistent latency-ல, மற்றும் கட்டுப்படுத்தப்பட்ட cost-ல.

இதுதான் inference.

## Mental Model

Inference = forward pass only. Backprop இல்லை. Gradient இல்லை.

ஒரு trained neural network-ஐ ஒரு மிகப் பெரிய deterministic function போல நினைக்கவும். Input tokens உள்ளே போகும், ஒவ்வொரு layer-உம் calculation பண்ணும், output tokens வெளியே வரும்.

முக்கிய வித்தியாசம்: Training என்பது batch-oriented, offline, compute-heavy. Inference என்பது online, latency-sensitive, serving problem.

## How It Works

ஒரு typical LLM inference request இப்படி போகும்:

Prompt → Tokenizer → Input IDs → Embedding → Transformer layers → Logits → Sampling → Output tokens

LLM-கள் autoregressive. ஒரு token generate ஆனதும், அதை அடுத்த step-க்கு context-ஆ பயன்படுத்துவார்கள்.

இதனால் இரண்டு phase:

**Prefill:** User கொடுத்த whole prompt ஒரே முறையில் process ஆகும். Parallelizable.
**Decode:** ஒவ்வொரு token-ஆம் sequential-ஆ generate ஆகும். இங்கே latency தீர்மானிக்கப்படுகிறது.

KV cache இங்கே முக்கியம். ஏற்கனவே compute செய்த key-value pairs-ஐ memory-ல வைத்துக்கொள்வதால் மீண்டும் கணக்கிட தேவையில்லை. இதுதான் latency-ஐ குறைக்கிறது.

Batching: ஒரே GPU-ல பல requests-ஐ ஒன்றாக process பண்ணுவது throughput-ஐ அதிகரிக்கிறது. ஆனால் latency-க்கு trade-off உண்டு.

## Architectural Reasoning

Inference-ஐ design பண்ணும்போது கேட்க வேண்டிய கேள்விகள்:

*Latency vs Throughput?* Chatbot-க்கு p95 latency < 800ms வேண்டும். Batch size அதிகரித்தால் throughput போகும், ஆனால் first token latency அதிகரிக்கும்.

*Cost per token எவ்வளவு?* GPU memory பெரிய cost driver. Model size, quantization, மற்றும் hardware தேர்வு இதை தீர்மானிக்கும்.

*Quality vs Speed?* Larger model = better quality, அதிக latency & cost. Smaller distilled model அல்லது quantization 4-bit ஐ use செய்யலாம்.

*Self-host vs Managed?* vLLM, TGI போன்ற open source inference engines, அல்லது SageMaker, Bedrock போன்ற managed services. Team size, operability, மற்றும் control வேண்டுமா என்பதை பார்க்க வேண்டும்.

*Scalability எப்படி?* Request spikes வரும். Auto-scaling, request queue, timeout & retry policy தேவை. Load balancer முன், inference service-கள் stateless-ஆ இருக்க வேண்டும்.

## Trade-offs

**Latency vs Throughput:** Continuous batching செய்தால் GPU utilization உயரும். ஆனால் ஒரு request தனியாக வந்தால் கூட அது காத்திருக்கும். Low latency SLA-க்கு dynamic batching மற்றும் smaller max batch size தேவை.

**Memory vs Speed:** KV cache GPU memory-ல வைத்தால் decode வேகமாக இருக்கும். Long context prompt-களுக்கு memory போதாமல் OOM வரும். Offload to CPU செய்தால் cost குறையும், ஆனால் latency spike ஆகும்.

**Accuracy vs Cost:** FP16 vs INT4 quantization. Quality drop குறைவு என்றாலும், சில tasks-ல தெரியும். Production-ல A/B test செய்து தீர்மானிக்க வேண்டும்.

**Failure modes:** GPU node failure, long prompt → OOM, token generation loop, prompt injection. Timeout இல்லாமல் request hang ஆகும். Idempotent retry இல்லாத inference API duplicate charge ஆகும்.

## Practical Example

Enterprise RAG chatbot.

User query வரும் → retriever 5 documents எடுக்கும் → prompt assemble → LLM inference.

இங்கே constraints: p95 latency < 1.5s, cost per query < $0.01, peak 200 RPS.

Decision: 7B class model INT4 quantization, vLLM with continuous batching, KV cache enabled, max batch size 8, request queue with 500ms timeout. Fallback to smaller model if queue full.

மாற்றாக 70B model full
