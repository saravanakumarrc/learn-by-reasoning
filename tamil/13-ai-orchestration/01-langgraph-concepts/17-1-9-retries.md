# Retries

> **Learning Path:** AI Orchestration
> **Section:** 17.1.9 — LangGraph concepts

## 1. Problem

AI Orchestration-ல ஒரு agent ஒரு tool-ஐ call பண்ணுது. `web search`, `database query`, `LLM call`, `API call` — எல்லாமே network-அடிப்படையிலானது.

இப்போ ஒரு LLM node LangGraph flow-ல run ஆகுது. அது third-party API-க்கு call போடுது. Network blip வந்தது. Timeout ஆகுது. Response வரல.

என்ன ஆகும்?

Flow முழுக்க fail ஆகும். User-க்கு error காட்டும். Agent work half-done-ல நிக்கும்.

அதே call-ஐ கொஞ்சம் கழித்து மறுபடி try பண்ணினால் success ஆகலாம். அதுதான் retry.

**Problem painful enough:** Unreliable downstream services + non-deterministic failures = flaky orchestration.

## 2. Mental Model

Retry என்பது "immediate failure-ஐ தற்காலிகமாக ignore பண்ணி, கொஞ்சம் wait பண்ணி மறுபடி try பண்ணு".

இது network-க்கு ஒரு second chance கொடுக்கிறது. ஆனால் இது magic இல்லை. ஒவ்வொரு retry-ம் time, cost, side-effect-ஐ உருவாக்கும்.

LangGraph context-ல: ஒரு node fail ஆனால், அந்த node-ஐ மறுபடி run பண்ணலாம். அல்லது upstream-க்கு error propagate பண்ணலாம்.

## 3. How It Works

Basic retry loop:

1. Call பண்ணு
2. Fail ஆனால்? Error type பார்
3. Backoff wait பண்ணு
4. Max attempts வரை repeat

Important parts:

* **Retryable error**: Timeout, 5xx, connection reset, rate limit 429. இவை transient.
* **Non-retryable error**: 4xx client error, validation error, business logic error. இவற்றை retry பண்ணக்கூடாது.
* **Backoff**: Immediate retry = thundering herd. Exponential backoff + jitter use பண்ணு.
* **Idempotency**: Same request-ஐ மறுபடி அனுப்பினாலும் side-effect ஒன்றாக இருக்க வேண்டும். இல்லை என்றால் duplicate payment, duplicate email போன்ற பிரச்சனை.

LangGraph-ல இதை node wrapper-ல செய்யலாம். அல்லது `langgraph` built-in retry policies / `tenacity` போன்ற library உடன்.

## 4. Architectural Reasoning

Retry எப்போது useful?

* External API flaky, latency spikes உண்டு
* LLM provider temporary overload
* Network partition short-lived
* Agent tool call idempotent

எப்போது avoid பண்ண வேண்டும்?

* Request non-idempotent, e.g., create payment, create order
* Error deterministic ஆக தெரியும்
* User waiting for synchronous response, latency budget முடிந்துவிட்டது

Alternatives:

* **Circuit breaker**: Repeated failures வந்தால் fast-fail பண்ணு, downstream-ஐ protect பண்ணு
* **Fallback**: Alternative tool, cached result, degraded response
* **Queue + async retry**: Orchestration-ஐ block பண்ணாமல் background-ல retry

Architect decision: Retry என்பது reliability-க்கு first line defense. ஆனால் அதற்கு மேல் circuit breaker + fallback வேண்டும்.

## 5. Trade-offs

**Latency vs Reliability**
Retry வைத்தால் success rate அதிகரிக்கும், ஆனால் p95 latency கூடும். Agent flow synchronous-ஆக இருந்தால் user wait time அதிகரிக்கும்.

**Cost vs Success**
LLM call, API call எல்லாம் money. Retry = extra cost. 3 retries = 4x cost worst case. AI Orchestration-ல இது முக்கியம்.

**Duplicate side-effects**
Idempotency இல்லாத system-ல retry என்பது data corruption. Payment, booking, write to database. இதற்கு idempotency key வேண்டும்.

**Thundering herd**
System recover ஆகும் போது எல்லா clients ஒரே நேரத்தில் retry பண்ணினால் overload மீண்டும் வரும். Jitter தேவை.

## 6. Practical Example

Enterprise RAG agent: User query → LLM → web search tool → embedding → vector DB → answer.

Web search tool 10% time timeout ஆகுது. No retry.

Result: User-க்கு "search failed" என்று வரும். Agent incomplete.

Design:

* Search node-ஐ wrap பண்ணு with retry policy: max 3 attempts, exponential backoff 1s, 2s, 4s + jitter
* Retry only on timeout, 5xx, 429
* Don't retry on 400 bad query
* Search request idempotent ஆக இருக்கிறது, so safe

LangGraph flow-ல node fail ஆனாலும் state-ஐ preserve பண்ணி retry பண்ண முடியும். User experience improve ஆகும், cost சற்று அதிகம்.

இதே flow-ல payment tool இருந்தால் retry policy வேறு. Idempotency key இல்லாமல் retry பண்ணக்கூடாது.

## 7. Reasoning Challenge

உங்கள் LangGraph agent-ல ஒரு node external LLM API-க்கு call பண்ணுது. API 429 rate limit தருது. Network timeout-உம் வருது. Agent synchronous user chat-ல இயங்குது. Max wait 15 seconds.

நீங்கள் retry policy எப்படி design பண்வீர்கள்? Max attempts எவ்வளவு? Backoff எப்படி? எந்த errors-க்கு retry பண்ண மாட்டீர்கள்? Why?

## 8. Key Takeaways

* Retry என்பது transient failures-க்கு மட்டும். Deterministic errors-க்கு இல்லை.
* Idempotency இல்லாமல் retry பண்ணாதே.
* Exponential backoff + jitter கட்டாயம்.
* Retry = latency + cost + duplicate risk. Trade-off தெளிவாக தெரிய வேண்டும்.
* LangGraph orchestration-ல retry-ஐ node level-ல முடிவு செய், blind global retry வேண்டாம்.
