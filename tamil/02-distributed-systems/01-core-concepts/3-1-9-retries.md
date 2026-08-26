# Retries

> **Learning Path:** Distributed Systems
> **Section:** 3.1.9 — Core concepts

## 1. Problem

ஒரு distributed system-ல Service A, Service B-ஐ call பண்ணுது. Network-ல ஒரு brief glitch வந்தது, packet drop ஆச்சு. அல்லது Service B-க்கு temporary CPU spike, request timeout ஆகி போச்சு.

இப்போ என்ன பண்ணுவீங்க? உடனே user-க்கு error கொடுத்துடுவீங்களா? 

Real world-ல network failure, timeout, 5xx error எல்லாம் *transient* ஆக இருக்கும். 1-2 seconds-க்குள்ள தீர்ந்து போயிடும். ஆனால் அந்த ஒரு முறை failure நமக்கு permanent failure மாதிரி தெரியும்.

இதனால் தான் **retry** தேவைப்படுது. “ஒரு முறை முயற்சி தோல்வி அடைஞ்சா, மறுபடியும் முயற்சி பண்ணலாமா?” என்ற கேள்வியிலிருந்து இது வருது.

## 2. Mental Model

Retry என்பது simple ஆக “மறுபடியும் கேளு” என்பது தான். ஆனால் blind ஆக மறுபடியும் கேட்டால் பிரச்சனை பெரிதாகும்.

Mental model: **Transient failure-க்கு tolerance கொடு, permanent failure-க்கு உடனே விட்டுடு.**

நாம் என்ன retry பண்ணுறோம் என்பதும் முக்கியம். Read operation vs Write operation-க்கு பதில் வேறுபடும்.

## 3. How It Works

Practical retry என்பது 3 decisions உடன் வரும்:

**When to retry?** எந்த error-க்கு retry பண்ண வேண்டும்?
- Network timeout, connection reset, 5xx server error → retry செய்யலாம்
- 4xx client error, 404 Not Found, 400 Bad Request → retry பண்ணாதீங்க, logic தப்பு

**How long to wait?**
Immediate retry = தவறு. Service already overloaded, நீங்கள் மேலும் load போடுவீங்க.
அதனால் **backoff** use பண்ணுவோம். Exponential backoff + jitter standard pattern.
1s, 2s, 4s, 8s... மாதிரி வளரும். Jitter சேர்த்தால் எல்லா client-ம் ஒரே நேரத்தில் retry பண்ணி **thundering herd** உருவாகாது.

**How many times?**
Infinite retry இல்லை. Max attempts + total timeout set பண்ணுங்க. 3-5 attempts போதும் பெரும்பாலும்.

Pseudo logic:
```
attempt = 0
while attempt < max_attempts:
  try response = call()
  if success: return
  if non-retryable error: break
  sleep(backoff(attempt) + jitter)
  attempt += 1
return failure
```

## 4. Architectural Reasoning

Retry எப்போது useful?

- Cross service call over unreliable network
- External third-party API call
- Database connection pool temporary exhaustion
- Message queue produce fail transient ஆக

Retry choose பண்ணுறதன் பின்னால் இருக்கும் constraint: **Availability vs Correctness**.

நீங்கள் fail fast செய்தால் user-க்கு error விரைவாக தெரியும், ஆனால் transient glitch-க்கும் fail ஆகும். Retry செய்தால் success rate அதிகரிக்கும், ஆனால் latency அதிகரிக்கும், duplicate processing risk வரும்.

Alternative options:
- Circuit breaker: repeated failure-ஐ தடுக்க
- Timeout tuning: முதல் call-க்கே அதிக wait கொடு
- Idempotent design: retry safe ஆக்கு

Retry என்பது standalone solution இல்லை. இது idempotency, timeout, backoff கூடவே வர வேண்டும்.

## 5. Trade-offs

1. **Duplicate processing risk.** Retry செய்தால் request இரண்டு முறை process ஆகலாம். Payment double charge, order double create ஆகலாம். இதற்கு idempotency key தேவை.

2. **Cascading failure.** Service B down ஆக இருந்தால், Service A retry பண்ணி பண்ணி B-க்கு load அதிகரிக்கும். அது மற்ற services-க்கும் பரவும்.

3. **Latency amplification.** 3 retries with backoff என்றால் user request 10-15 seconds ஆகலாம். SLA break ஆகும்.

4. **Thundering herd.** Failure recovery time-ல எல்லா client-ம் ஒரே நேரத்தில் retry பண்ணும். இதை தவிர்க்க jitter முக்கியம்.

எனவே retry = power. Power-ஐ control பண்ண வேண்டும்.

## 6. Practical Example

Order service -> Payment gateway call.

User checkout பண்ண
