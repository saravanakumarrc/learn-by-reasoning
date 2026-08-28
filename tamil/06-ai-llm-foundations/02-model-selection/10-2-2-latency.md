# Latency

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.2 — Model selection

### 1. Problem

ஒரு LLM service-ஐ production-ல விட்டுட்டோம். User prompt அனுப்புகிறார், response வர 8-12 seconds ஆகிறது.

Product team சொல்கிறது: "இது chat அல்ல, user walk away ஆகிறார்."

Engineering team சொல்கிறது: "Model பெரியது, accurate. அதனால் slow."

இங்கே problem என்ன? **Latency** என்பது user perception-ஐ நேரடியாக கட்டுப்படுத்துகிறது.

LLM-ல latency என்பது token generate ஆகும் வரை ஆகும் நேரம். முதல் token வரும் வரை **Time To First Token - TTFT**, மற்றும் முழு response முடியும் வரை **Time To Last Token**.

Model selection செய்யும்போது accuracy மட்டும் பார்த்தால் போதாது. Latency, throughput, cost மூன்றும் ஒன்றாக முடிவு செய்ய வேண்டும்.

### 2. Mental Model

Latency = distance + processing + queue.

ஒரு request வரும்போது:

1. **Network latency** - client to API gateway
2. **Queue latency** - request wait பண்ணும், autoscaling நடக்கும்
3. **Prefill latency** - input prompt-ஐ process பண்ணி KV cache build பண்ணும்
4. **Decode latency** - token by token generate பண்ணும், autoregressive

ஒரு distributed system-ல service call பண்ணும்போது network failure வரலாம் என்று புரிந்திருக்கும். LLM-லும் அதே தான், ஆனால் processing itself தான் dominant factor.

### 3. How It Works

Model size ↑ → parameters அதிகம் → compute அதிகம் → latency ↑.

Context length ↑ → prefill time ↑ linearly.

Batch size ↑ → throughput ↑ ஆனால் per-request latency ↑.

Quantization, smaller model, speculative decoding, caching ஆகியவை latency-ஐ குறைக்கும் technique.

Latency-ஐ அளவிடும் போது p50, p95, p99 பார்க்க வேண்டும். Average மட்டும் பார்த்தால் மோசமான user experience மறைந்து விடும்.

### 4. Architectural Reasoning

Model selection என்பது "சிறந்த model" தேர்வு அல்ல. **Use case-க்கு ஏற்ற latency budget** தேர்வு.

**When latency matters most:**
* Chatbot, real-time assistant - user typing while waiting. TTFT < 600ms வேண்டும்
* Agent tool calling loop - ஒவ்வொரு step-க்கும் model call. Latency compound ஆகும்
* RAG pipeline - embedding + retrieval + LLM. End-to-end latency அதிகரிக்கும்

**Constraint அடிப்படையில் தேர்வு:**
* Latency sensitive → small, distilled model, e.g., 7B-14B class, quantized
* Quality sensitive → larger model, maybe 70B+, accept higher latency
* Cost sensitive → batching, smaller model, caching

உதாரணமாக, internal code completion-க்கு 2B model 150ms-ல response கொடுக்கும். அதே task-ஐ 70B model 3 sec-ல செய்தால் developer flow break ஆகும்.

### 5. Trade-offs

**Latency vs Quality**
பெரிய model சிறந்த accuracy கொடுக்கும். ஆனால் latency அதிகம். Distilled smaller model 80% quality-ஐ 30% latency-ல கொடுக்கும். அது போதுமானதா? என்பது product decision.

**Latency vs Throughput**
Batching பண்ணினால் GPU utilization அதிகரிக்கும், cost/token குறையும். ஆனால் first request wait பண்ணும். Real-time use case-ல batching குறைவாக வேண்டும்.

**Latency vs Cost**
Low latency வேண்டுமென்றால் over-provision GPU, keep model warm, use larger instance type. Cost அதிகரிக்கும். Autoscaling latency spike கொடுக்கும்.

**Failure mode:** Latency SLA breach ஆனால் timeout ஆகும். Client retry பண்ணும். Retry காரணமாக traffic spike, cascade failure. Idempotency இல்லாமல் duplicate generation ஆகும்.

### 6. Practical Example

Enterprise support chatbot.

Requirements: TTFT < 800ms, p95 < 3s, cost per conversation < $0.02.

Options:
A. GPT-4 class model direct. TTFT ~1.5s, cost high.
B. 7B distilled model self-hosted on GPU. TTFT ~400ms, quality acceptable for FAQ.
C. Hybrid: first 7B model-ல quick draft, if confidence low → fallback to larger model.

Architectural decision: Route simple queries to small model, complex queries to larger model. Add prompt caching for repeated context. Use streaming to show first token fast.

Result: Average latency குறைந்தது, cost 60% குறைந்தது, user satisfaction உயர்ந்தது.

### 7. Reasoning Challenge

உங்களிடம் இரண்டு model உள்ளது:

* Model A: 8B, TTFT 300ms, output quality 7/10, $0.0002 / 1K tokens
* Model B: 70B, TTFT 1.8s, output quality 9/10, $0.0015 / 1K tokens

உங்கள் agent system ஒரு user request-க்கு சராசரியாக 4 LLM calls செய்கிறது. Latency budget மொத்தம் 5 seconds.

நீங்கள் எந்த model-ஐ primary-ஆக தேர்வு செய்வீர்கள்? எப்போது Model B-க்கு route செய்வீர்கள்? Trade-off என்ன?

### 8. Key Takeaways

* Latency என்பது model size, context length, batching, infrastructure ஆகியவற்றால் தீர்மானிக்கப்படுகிறது
* Model selection = latency budget + quality need + cost constraint ஆகியவற்றின் trade-off
* TTFT user perception-க்கு முக்கியம், end-to-end latency business metric-க்கு முக்கியம்
* Every latency optimization creates a new trade-off: quality, cost, or operational complexity
