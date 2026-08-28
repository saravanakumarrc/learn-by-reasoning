# Reliability

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.1.3 — Non-functional requirements

# Reliability — non-functional requirement ஆக பார்ப்பது எப்படி?

## 1. Problem

நீங்கள் ஒரு checkout service-ஐ launch பண்ணீங்க. Test-ல எல்லாம் சரி. Black Friday வந்ததும் traffic 10x ஆகுது. ஒரு downstream payment API slow ஆகுது, timeout ஆகுது. உங்க service அதுக்கு wait பண்ணி thread-கள் எல்லாம் block ஆகுது. Database connection pool exhaust ஆகுது. Error rate spike ஆகுது, users cart-ல stuck ஆகிறாங்க.

Feature வேலை செய்யுது, ஆனால் system dependable இல்லை.

இதுதான் reliability பிரச்சனை. Functional requirement = "payment செய்ய வேண்டும்". Non-functional requirement = "அது எப்போதும், எப்படி, எந்த தரத்தில் வேலை செய்ய வேண்டும்". அதை தெளிவாக define பண்ணாமல் architecture தேர்வு பண்ணினால், production-ல தான் cost தெரியும்.

## 2. Mental Model

Reliability என்பது "system தொடர்ந்து required function-ஐ சரியாக செய்கிறதா" என்பதன் probability.

அதாவது uptime மட்டும் இல்லை. Correctness + availability + performance under load + graceful degradation.

ஒரு mental model: reliability = **expectation management**. User, business, ops team எல்லாரும் என்ன எதிர்பார்க்கிறார்கள் என்பதை நீங்கள் quantify பண்ணி, அதுக்கு architecture-ஐ design பண்ணுவது.

## 3. How It Works

Reliability-ஐ build பண்ணுவது component reliability-ஐ மட்டும் சேர்ப்பது இல்லை. System reliability multiplicative ஆக குறையும்.

அதனால் architects மூன்று layer-ல வேலை பார்க்கிறார்கள்:

**Define target.** SLA / SLO எழுதுவது. உதாரணம்: 99.9% availability per month, p95 latency < 500ms, error budget 0.1%.

**Design for failure.** Failures inevitable. Network partition, process crash, disk full, human error. உங்க system எப்படி fail ஆகும், எப்படி recover ஆகும் என்பதை முன்கூட்டியே திட்டமிடுவது.

**Observe and learn.** Metrics, logs, traces, error budgets burn rate. System healthy-யா இல்லையா என்பதை நிஜ நேரத்தில் தெரிந்து கொள்ள வேண்டும்.

Reliability engineering என்பது feature development-க்கு எதிரானது இல்லை. இது trade-off-ஐ manage பண்ணுவது.

## 4. Architectural Reasoning

Reliability ஒரு requirement ஆக வரும்போது, முதல் கேள்வி: **what is acceptable failure?**

ஒரு internal dashboard down ஆனால் பரவாயில்லை. Payment capture down ஆனால் revenue நிற்கும்.

அதனால் architect:

* **Boundaries வரையறுக்கிறார்.** Critical path-ஐ கண்டுபிடித்து, அதற்கு redundancy, retries with backoff, circuit breaker, bulkhead isolation கொடுக்கிறார்.
* **Failure modes-ஐ குறைக்கிறார்.** Synchronous chain-ஐ குறைத்து, async message queue, idempotency, outbox pattern பயன்படுத்துகிறார்.
* **Recovery-ஐ எளிதாக்குகிறார்.** Blue-green deployment, feature flags, automated rollback, chaos testing.

Alternative உண்டு: reliability-ஐ முழுவதும் ignore பண்ணி, fast shipping செய்யலாம். அது early stage startup-ல சில சமயம் சரியாக இருக்கும். Scale ஆனதும் technical debt-ஆக வரும்.

## 5. Trade-offs

**Availability vs Consistency.** Distributed database-ல strong consistency கொடுத்தால் write latency அதிகரிக்கும். CAP theorem-ல தேர்வு தெளிவாகும்.

**Reliability vs Cost.** Multi-AZ deployment, replicas, extra capacity, autoscaling — எல்லாம் reliability கூட்டும், cost கூட்டும். Error budget-ஐ பார்த்து invest பண்ண வேண்டும்.

**Reliability vs Complexity.** Retry logic, circuit breaker, fallback, idempotency key — எல்லாம் reliability கூட்டும், code complexity கூட்டும். Operability குறையும்.

**Speed to market vs hardening.** More validation, canary release, chaos engineering — reliability கூட்டும், delivery slow ஆகும்.

முக்கிய failure modes: cascading failure, thundering herd on recovery, partial outage மறைந்து silent data corruption ஆகும்.

## 6. Practical Example

E-commerce checkout flow.

Problem: payment service 200ms normally, peak-ல 3s ஆகுது.

Architectural decision: synchronous call-ஐ அப்படியே வைக்காமல், payment initiation-ஐ async ஆக்குவது. API immediately 202 Accepted return பண்ணி, background worker payment provider-ஐ poll பண்ணி result-ஐ update பண்ணும். Client-க்கு status endpoint கொடுக்கப்படும்.

Circuit breaker வைத்து payment provider slow ஆனால் fast fail ஆகி fallback page காட்டுவது. Idempotency key-ஆல duplicate charge தடுப்பது.

Result: checkout API availability 99.95% maintain ஆகிறது, payment provider-ன் reliability issue checkout-ஐ முழுவதும் down பண்ணாது.

Cost: user experience-ல சிறிய delay வரும், but business continuity கிடைக்கும்.

## 7. Reasoning Challenge

உங்களிடம் 20 microservices உள்ளன. ஒரு core catalog service single node-ல ஓடுகிறது. அது daily peak-ல 2 முறை crash ஆகிறது, restart 5 நிமிடம் எடுக்கிறது. அ
