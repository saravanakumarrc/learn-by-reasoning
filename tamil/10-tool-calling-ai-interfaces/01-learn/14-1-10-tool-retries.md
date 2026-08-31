# Tool retries

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.10 — Learn

## 1. Problem

நீங்கள் ஒரு LLM agent-ஐ build பண்ணுகிறீர்கள். Agent ஒரு tool-ஐ call பண்ணும். உதாரணமாக `get_stock_price` அல்லது `create_invoice`.

Network glitch வந்தது. API timeout ஆனது. LLM-க்கு response வரவில்லை.

Agent என்ன செய்யும்? இதே request-ஐ மீண்டும் அனுப்பும். அல்லது user-க்கு "failed" என்று சொல்லிவிடும்.

இங்கே இரண்டு painful outcomes உள்ளது:

* Retry இல்லாமல், transient failure-க்கு agent முழுவதுமாக fail ஆகிறது. User experience மோசம்.
* Blind retry இருந்தால், ஒரு non-idempotent tool-ஐ இரண்டு முறை call பண்ணி double charge, double order போன்ற பிரச்சனை வரும்.

Tool retries என்பது இந்த இடையில் வரும் architectural problem.

## 2. Mental Model

Tool call என்பது distributed system call தான்.

LLM → Tool Service. Network, latency, rate limit, timeout எல்லாம் உண்டு.

Retry என்பது **temporary failure-ஐ மறைக்கும் resilience pattern**. ஆனால் அது **side effects-ஐ பெருக்கும்** risk-ஐயும் உண்டாக்கும்.

முக்கிய கேள்வி: *இந்த tool call safe to retry?*

## 3. How It Works

Retry logic பொதுவாக மூன்று பகுதிகள்:

**Trigger:** எந்த errors-க்கு retry பண்ண வேண்டும்?
Transient errors: timeout, 5xx, connection reset, rate limit 429
Non-retryable errors: 4xx client error, validation error, business rule violation

**Backoff:** உடனே retry பண்ணக்கூடாது. Exponential backoff + jitter.
1s, 2s, 4s... jitter சேர்த்து thundering herd தடுக்க.

**Idempotency guard:** Retry செய்யும்போது duplicate execution தடுக்க.

Agent layer-ல் retry பண்ணலாம். அல்லது tool service மட்டும் idempotent ஆக வடிவமைக்கலாம். Best practice: இரண்டையும் செய்ய.

## 4. Architectural Reasoning

Tool retries தேவைப்படும் போது:

* Tool external API-ஐ call பண்ணுகிறது. Network unreliable.
* Latency SLO tight ஆக இருக்கிறது. User-க்கு wait பண்ண முடியாது.
* Agent workflow multi-step. ஒரு step fail ஆனால் முழு workflow fail ஆகிறது.

Alternatives:

* No retry: Fast fail. Simple, ஆனால் flaky.
* Client-side retry with backoff: Resilience கூடும்.
* Server-side idempotency + at-least-once delivery: Stronger guarantee.

Architect choose பண்ணுவது constraint பொறுத்து. Availability முக்கியமானால் retry. Correctness முக்கியமானால் idempotency முதலில்.

## 5. Trade-offs

* **Availability vs Correctness**: Retry கூடுதல் availability தரும். ஆனால் non-idempotent operation-ல் duplicate side effect வரும்.
* **Latency vs Reliability**: Retry செய்தால் overall latency அதிகரிக்கும். Backoff வைத்தால் user wait நீளும்.
* **Complexity vs Operability**: Retry policy, circuit breaker, idempotency key எல்லாம் code மற்றும் observability-யை கூட்டும்.
* **Cost**: Retry என்பது extra API calls. Rate limit, cost, downstream load எல்லாம் அதிகரிக்கும்.

Failure modes:

* Retry storm: Service down ஆகும்போது எல்லா clients-உம் retry பண்ணி cascade failure.
* Infinite loop: Error condition மாறாமல் retry செய்வது.
* Partial success: Tool half executed, response lost. Retry பண்ணினால் state inconsistent.

## 6. Practical Example

Enterprise RAG agent with `create_support_ticket` tool.

Flow: LLM → Tool → Zendesk API.

Zendesk சில நேரம் 504 timeout தரும்.

Design:

* Agent layer-ல் retry policy: max 3 attempts, exponential backoff 1s, 2s, 4s + jitter.
* Retry only on 5xx, timeout, 429.
* Tool call-க்கு idempotency key generate பண்ணி request header-ல் `Idempotency-Key` அனுப்பு.
* Zendesk API idempotent ஆக handle பண்ணும், அல்லது agent service ஒரு local store-ல் key → ticket id map வைத்துக்கொள்ளும்.

Result: Transient glitch மறைந்து user-க்கு smooth experience. Duplicate ticket வராது.

## 7. Reasoning Challenge

உங்களிடம் payment tool உள்ளது. `create_payment` non-idempotent. Network timeout ஆகிறது. Response வரவில்லை.

Option A: உடனே retry.
Option B: User-க்கு ask பண்ணி confirm.
Option C: Idempotency key வைத்து retry.

எதை தேர்வு செய்வீர்கள்? ஏன்? Retry policy என்ன இருக்க வேண்டும்?

## 8. Key Takeaways

* Retry என்பது transient failure-க்கு மட்டும். Business error-க்கு அல்ல.
* Idempotency இல்லாமல் blind retry செய்யாதே. Duplicate side effect costly.
* Exponential backoff + jitter + max attempts = production ready retry.
* Tool calling-ல் retry decision என்பது architect decision, not just library config.
