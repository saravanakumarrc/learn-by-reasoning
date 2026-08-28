# PARTIAL — Latency

> Generation was not accepted as complete.
> Reason: Ollama reported done_reason=length

## Problem

உங்க team ஒரு customer support chatbot பண்ணுது. User ஒரு கேள்வி கேட்டவுடன் response வர 8-10 seconds ஆகுது. User typing-ஐ நிறுத்திட்டு wait பண்ணறார். சிலருக்கு timeout ஆகுது. Conversion drop ஆகுது.

இன்னொரு பக்கம் code generation tool உள்ளது. Developer-க்கு suggestion வேணும். அங்கே 8-10 seconds ஓகே தான்.

எதுலயும் "model slow" என்று சொல்லலாம். ஆனால் **எந்த latency தான் பிரச்சனை?** Model selection பண்ணும்போது நீங்கள் வெறும் accuracy மட்டும் பார்க்கலாம். Production-ல் latency தான் UX-ஐ முடிவு செய்யும்.

இதை தெளிவாக பார்க்க latency என்பது ஒரு single number இல்லை.

## Mental Model

Latency-ஐ இரண்டு பகுதியாக பிரித்து பாருங்கள்:

* **Time to First Token - TTFB**: user request போனது முதல் முதல் token வரை எவ்வளவு நேரம். இது perceived responsiveness-ஐ தீர்மானிக்கும்.
* **Time to Last Token**: முழு response generate ஆக எவ்வளவு நேரம். இது throughput மற்றும் cost-ஐ தொடர்புடையது.

ஒரு LLM-க்கு latency பெரும்பாலும் inference compute-ல் இருந்து வரும்: prefill phase + decode phase. Prefill என்பது prompt-ஐ process பண்ணும் phase. Decode என்பது token-by-token generate பண்ணும் phase.

ஒரு distributed system-ல் network, queue, serialization, tokenization, embedding lookup, RAG retrieval எல்லாம் சேர்ந்து latency budget-ஐ தின்னும்.

## Architectural Reasoning

Model selection-ல் latency ஒரு first class constraint.

**Constraints என்ன?**
* User experience budget: Chat-க்கு TTFB < 800ms, p95 < 2s வேணும். Internal batch job-க்கு 30s ஓகே.
* Traffic & throughput: 1000 RPS வரும். ஒரு request-க்கு 10s ஆனால் GPU-கள் எத்தனை வேணும்?
* Cost: Bigger model = better quality ஆனால் higher latency + higher cost per token.
* Consistency: p99 latency spike வந்தால் user abandon பண்ணுவார்.

**Options உள்ளன:**
1. **Model size trade-off**: 7B vs 70B vs 405B. Smaller model = lower latency, lower quality.
2. **Optimization**: Quantization INT4/INT8, distillation, speculative decoding, continuous batching.
3. **Architecture**: Streaming response, caching frequent prompts, RAG pre-fetch, router model - small model for easy queries, big model for hard queries.
4. **Infrastructure**: GPU vs vCPU, KV cache management, max batch size.

Architect ஆக நீங்கள் கேட்க வேண்டியது: *இந்த use case-க்கு quality-ஐ எவ்வளவு குறைத்தாலும் ஓகே?* அப்புறம் latency budget-க்கு எந்த model fit ஆகும்?

## Trade-offs

1. **Latency vs Quality**: Bigger model generally better reasoning, better hallucination control. ஆனால் latency அதிகம். 70B model 7B model-ஐ விட 3-5x slow ஆகும். உண்மையான trade-off user perception vs correctness.

2. **Latency vs Cost**: Fast latency வேணும்னா smaller model அல்லது more replicas வேணும். Both cost. ஒரு 70B model-ஐ low latency-ல் serve பண்ண நிறைய GPU வேணும். அதே cost-ல் 7B model-ஐ scale பண்ணி better p99 கொடுக்கலாம்.

3. **TTFB vs Full response time**: Streaming ஆரம்பிக்கலாம். User-க்கு முதல் token விரைவாக வந்தால் பொறுமை வரும். ஆனால் total generation time மாறாது.

4. **Batching vs Latency**: Throughput அதிகரிக்க batching செய்யலாம். Latency அதிகரிக்கும். Real-time chat-க்கு continuous batching தேவை, offline job-க்கு large batch ஓகே.

Failure mode: p99 latency spike. ஏன்? Long context prompt, cache miss, GPU contention, cold start. Model selection பண்ணும்போது worst case-ஐ design பண்ணுங்கள், average case அல்ல.

## Practical Example

Enterprise RAG chatbot for sales support.

Request flow: User query -> intent classification -> embedding -> vector database search -> context build -> LLM generate.

Latency breakdown: Retrieval 120ms, tokenization 30ms, prefill 400ms, decode 1.2s. TTFB ~ 550ms.

Decision: 70B model TTFB 1.2s ஆகுது. UX team says >800ms unacceptable. Option A: 70B + speculative decoding + smaller context. Option B: 7B distilled model + router - simple queries 7B, complex queries 70B.

அவர்கள் hybrid router தேர்ந்தெடுத்தார்கள். 80% queries 7B-ல் handle ஆகுது. p95 TTFB 650ms. Cost 40% குறைந்தது. Quality drop for simple queries கிடையாது.

இங்கே model selection என்பது ஒரு single model pick அல்ல. Latency budget-க்கு ஏற்ற architecture.

##
