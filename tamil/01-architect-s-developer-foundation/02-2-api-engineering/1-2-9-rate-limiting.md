# Rate limiting

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.9 — 2. API engineering

## 1. Problem

உங்க service-க்கு ஒரு popular API இருக்கு. ஒரு நாள் ஒரு customer தன்னோட mobile app-ல அந்த API-ஐ தொடர்ந்து hit பண்ண ஆரம்பிக்கிறார். அல்லது ஒரு bug வந்து loop ஆக request அனுப்புது. அல்லது ஒரு attacker brute force attempt பண்ணுது.

என்ன ஆகும்?

DB connection pool தீர்ந்துடும். CPU spike ஆகும். Latency போயிடும். Healthy users-க்கு கூட 5xx வரும். ஒரு service down ஆனா அது அடுத்த service-க்கு cascade ஆகும்.

அதாவது **அதிக request-கள் வரும்போது system-ஐ protect பண்ண வேண்டியிருக்கு**. இல்லைன்னா availability போயிடும்.

Rate limiting என்பது இந்த pain point-க்கு பதில்.

## 2. Mental Model

Rate limiting = **ஒரு client-க்கு per time window எத்தனை request அனுமதிக்கிறோம் என்பதை கட்டுப்படுத்துவது**.

நினைச்சுக்கோ: ஒரு water tap-க்கு flow restrictor போடுற மாதிரி. ஒரு client-க்கு அதிகமா water விடக்கூடாது, இல்லைன்னா pipe burst ஆகும்.

Key idea: **Fairness + Protection**. நல்ல users-க்கு service கொடுக்கணும், abusive users-க்கு block பண்ணணும்.

## 3. How It Works

Core mechanism என்பது counter + window.

Simple ஆ 3 வழிகள்:

**Fixed Window**: 1 minute-ஐ 10 requests என்று வைத்தால், window start ஆனதும் counter zero ஆகும். ஒரு client 9 requests அடிச்சு window end-க்கு கொஞ்ச நேரத்துக்கு முன், அடுத்த window start-ல மீண்டும் 10 அடிக்கலாம். Burst சாத்தியம்.

**Sliding Window**: கடந்த 60 seconds-ல எத்தனை request வந்தது என்று பார்க்கும். Smooth ஆ இருக்கும், implement செய்ய கொஞ்சம் கடினம்.

**Token Bucket**: ஒரு bucket-ல tokens fill ஆகும். ஒவ்வொரு request-க்கும் ஒரு token எடுக்கணும். Bucket empty ஆனா request reject. Burst-ஐ அனுமதிக்கும், average rate-ஐ control பண்ணும். இது மிகவும் common.

Distributed system-ல இதை enforce பண்ண centralized store வேணும். Redis with INCR + EXPIRE, அல்லது API Gateway-ல built-in rate limiter.

Flow:
```mermaid
graph LR
    Client -->|Request| API Gateway
    API Gateway --> RateLimiter
    RateLimiter --> Redis
    RateLimiter -->|Allow| Service
    RateLimiter -->|429 Too Many Requests| Client
```

## 4. Architectural Reasoning

Rate limiter எங்கே வைக்கணும்?

* **Edge / API Gateway level**: அனைத்து traffic-க்கும் முதலில் filter. Cost effective.
* **Service level**: Service-ன் internal resource-ஐ protect பண்ண.
* **Per client / per API key / per user / per IP**: Granularity முக்கியம்.

எப்போ useful?
* Public API, SaaS product
* Third-party integration
* Critical resource like payment, OTP
* Downstream service slow ஆ இருக்கும்போது backpressure கொடுக்க

எப்போ overkill?
* Internal trusted service-to-service call, அங்கே circuit breaker + retry போதும்.

Alternative: Throttling, load shedding, quota. Rate limiting என்பது preventive. Load shedding என்பது reactive.

## 5. Trade-offs

**Strict vs Burst friendly**: Fixed window simple ஆனா boundary burst உண்டு. Token bucket smooth ஆனா complex.

**Accuracy vs Performance**: Sliding window accurate ஆனா Redis operations அதிகம். Fixed window cheap.

**Distributed consistency**: Multiple API nodes இருந்தால் rate limit state shared ஆக இருக்கணும். Redis single point of failure ஆகலாம். Local in-memory limiter fast ஆனா inconsistent.

**Fairness vs Revenue**: Free tier user-க்கு 100 req/min, paid user-க்கு 10k req/min. Rate limit என்பது business decision கூட.

**Failure mode**: Rate limiter itself down ஆனால்? Fail open - அனுமதிக்கலாம், fail closed - block பண்ணலாம். முக்கிய decision.

## 6. Practical Example

Enterprise SaaS, `/invoices/generate` API. ஒரு customer-க்கு தினமும் 1000 invoice தான் generate பண்ண வேண்டும். ஒரு bug-ல client 10k request அனுப்பினால் DB-ல lock contention வரும்.

Architecture:
API Gateway-ல API key-க்கு token bucket: refill rate 10 req/sec, burst capacity 50.

Request வரும் போது Redis-ல `INCR user:{id}:req` பண்ணி TTL set. Limit மீறினால் 429 + `Retry-After` header return.

அதே நேரம் paid plan user-க்கு higher limit. Rate limit hit ஆனால் logs-ல alert, மற்றும் customer support-க்கு தெரியும்.

இது service-ஐ protect பண்ணும், மற்ற customers-க்கு latency maintain ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு, எல்லாருக்கும் same webhook events தேவை. ஒரு consumer slow ஆக process பண்ணுது. Producer-ஐ block பண்ணக்கூடாது. Replay வேணும்.

Rate limiting-ஐ இங்கே எங்கே போடுவீங்க? Producer side-லா, consumer side-லா? Limit என்ன basis-ல set பண்ணுவீங்க? Burst allowance தேவையா?

Think about backpressure and consumer fairness.

## 8. Key Takeaways

* Rate limiting என்பது protection, not punishment. System availability-க்காக.
* Token bucket பெரும்பாலும் practical choice for burst control.
* Distributed rate limiter-க்கு shared state வேணும், அது latency மற்றும் consistency trade-off கொண்டு வரும்.
* Limit policy என்பது technical decision மட்டும் இல்லை, business tiering மற்றும் abuse prevention கூட.
* Rate limiter fail ஆனால் என்ன நடக்கும் என்பதை முன்கூட்டியே முடிவு செய்யுங்கள்.
