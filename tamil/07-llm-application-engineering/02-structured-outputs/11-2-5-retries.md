# Retries

> **Learning Path:** LLM Application Engineering
> **Section:** 11.2.5 — Structured outputs

## 1. Problem

உங்கள் LLM application ஒரு external API-க்கு call பண்ணுது. Model provider, vector database, payment gateway, எதுவாக இருந்தாலும் network இருக்கிறது.

Network-ல transient failure வரும். Timeout, 5xx error, connection reset, rate limit 429. இது rare ஆனால் production-ல நிச்சயம் வரும்.

ஒரு user chat request வந்தது. LLM call போனது, timeout ஆனது. Client-க்கு response போகல. User refresh பண்ணார். அதே request மீண்டும் போனது.

இப்போது என்ன நடக்கும்? 
Request process ஆகாமல் போனால் user experience கெட்டுபோகும்.
Request process ஆகி இருந்தாலும் retry செய்யும் போது duplicate side effect வரும்.

இதற்கு தான் retry தேவைப்படுகிறது.

## 2. Mental Model

Retry என்பது **temporary failure-க்கு மீண்டும் முயற்சி செய்வது**.

இது "try again later" என்ற மனநிலை.

ஆனால் blind retry பண்ணினால் மோசமான நிலை வரும். 
Transient failure என்றால் network glitch, provider overload. அது few seconds-ல தீரும்.
Permanent failure என்றால் bad request 400, invalid schema. அதை மீண்டும் முயற்சி செய்தாலும் தீராது.

Retry-ன் core idea: **failure-ன் nature-ஐ புரிந்து கொண்டு, தகுந்த முறையில் மீண்டும் முயற்சி செய்ய வேண்டும்.**

## 3. How It Works

Basic retry loop:

1. Call செய்
2. Fail ஆனால் error type பார்
3. Retry policy-க்கு ஏற்ப wait செய், மீண்டும் முயற்சி
4. Max attempts முடியும் வரை repeat

முக்கியம்: **Backoff**.

உடனே மீண்டும் hit செய்தால் provider இன்னும் overloaded ஆகும். அதனால் wait time-ஐ அதிகரிக்கிறோம்.

Simple exponential backoff with jitter:
`wait = base * 2^(attempt-1) + random jitter`

LLM Application Engineering-ல structured outputs பற்றி பேசும் போது இது முக்கியம். Model சில நேரம் JSON schema-வுக்கு match பண்ணாமல் response தரும். அதை parse பண்ணும்போது error வரும். அது transient? இல்லை. Prompt தவறு. Retry பயனில்லை.

ஆனால் API timeout ஆனால்? அது retryக்கு உகந்தது.

## 4. Architectural Reasoning

Retry எப்போது உதவும்?

* Network blip, transient 5xx, timeout
* Rate limiting 429. Retry-After header இருந்தால் அதற்கு ஏற்ப wait செய்யலாம்
* LLM provider temporary overload

Retry எப்போது தேவையில்லை?

* 4xx client error, 400 Bad Request, 401 Unauthorized. Logic தவறு. Retry பண்ணினாலும் தீராது
* Idempotency இல்லாத operation. Payment charge, email send. மீண்டும் செய்தால் duplicate
* Structured output validation fail. Prompt fix வேண்டும், retry வேண்டாம்

Architect choice: 
**Retry policy-ஐ எங்கே வைக்கிறோம்?**
Client side, service side, or both? Usually service side with circuit breaker. Client side retry தேவைப்பட்டால் idempotency key தேவை.

## 5. Trade-offs

**Retry vs Latency**
Retry செய்தால் request latency அதிகரிக்கும். User wait time நீளும். 3 attempts with backoff என்றால் சில வினாடிகள் முதல் நிமிடம் வரை ஆகலாம். User experience vs reliability trade-off.

**Retry storm**
ஒரு provider down ஆனால், 1000 requests எல்லாம் retry செய்தால் provider recover ஆவதற்கு கஷ்டம். Thundering herd. இதற்கு jitter + circuit breaker தேவை.

**Duplicate side effects**
Retry செய்யும் போது non-idempotent operation மீண்டும் execute ஆகும். Payment double charge, message duplicate. இதற்கு idempotency key, exactly-once semantics தேவை.

**Cost**
LLM call ஒவ்வொன்றும் money. Retry செய்வது cost அதிகரிக்கும். Structured output generation fail ஆனால் blind retry செய்தால் cost waste.

## 6. Practical Example

Enterprise RAG chatbot. User query -> LLM call -> vector DB search -> LLM generation with structured output schema.

Flow-ல LLM generation step timeout ஆனது.

Architect decision:
* Retry policy: max 3 attempts, exponential backoff 1s, 2s, 4s with jitter
* Retry only on: timeout, 5xx, 429
* No retry on: 4xx, structured output validation error
* Idempotency: generation is read-only, safe to retry

ஆனால் user query-யை log செய்து audit trail வைக்கிறோம். அதற்கு idempotency key வேண்டும்.

இங்கே structured outputs-க்கு தொடர்பு: Model சில சமயம் schema match பண்ணாத JSON தரும். அது retry-க்கு உகந்ததல்ல. அதை handle பண்ண retry அல்ல, prompt refinement or output parsing with repair. Retry-ஐ அதற்கு use பண்ணினால் same error திரும்ப திரும்ப வரும்.

## 7. Reasoning Challenge

உங்கள் LLM application-ல் structured output-ஐ generate பண்ணும் service இருக்கு. 10% requests-ல் provider 503 தருகிறது. 5% requests-ல் model invalid JSON தருகிறது.

உங்களிடம் retry logic இருக்கிறது. அதை எப்படி configure செய்வீர்கள்? எந்த error-க்கு retry செய்வீர்கள், எந்த error-க்கு செய்ய மாட்டீர்கள்? Why?

## 8. Key Takeaways

* Retry என்பது transient failure-க்கு மட்டும். Permanent failure-க்கு அல்ல
* Backoff with jitter வேண்டும், immediate retry கூடாது
* Idempotency இல்லாத operation-ல் blind retry ஆபத்து
* LLM structured output validation error-க்கு retry பதில் prompt fix or repair logic தேவை
* Every retry adds latency, cost, and risk of retry storm
