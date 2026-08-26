# Error handling

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.8 — 1. Programming mastery

## 1. Problem

ஒரு API call பண்ணினீங்க. Network ல கொஞ்சம் jitter. Request timeout ஆயிடுச்சு. Client-க்கு response வரல.

Client என்ன பண்ணும்? அதே request-ஐ மறுபடியும் அனுப்பும்.

Server side-ல முதல் request success ஆகி, payment charge ஆகி இருந்தா? இரண்டாவது retry வந்தா duplicate charge.

இதே மாதிரி service A -> service B call பண்ணும்போது service B slow ஆகி இருக்கு. A wait பண்ணிக்கிட்டு இருக்கு. Thread pool full ஆகுது. அப்புறம் முழு service-மே unavailable ஆகிடும்.

Error-ஐ மறைச்சிட்டா போதுமா? இல்லை. Error ஒரு signal. System எப்படி behave பண்ணணும் என்பதை சொல்லும் signal.

Error handling இல்லாமல் என்ன ஆகும்? Cascade failure, data inconsistency, user-க்கு confusing UX, ops team-க்கு blind debugging.

## 2. Mental Model

Error handling என்பது `try catch` போடுவது இல்லை. 

இது ஒரு **contract** மாதிரி.

Caller-க்கும் callee-க்கும் இடையில்: என்ன errors வரலாம், எவ்வளவு நேரம் wait பண்ணுவது, retry பண்ணலாமா, fail பண்ணிடலாமா, fallback என்ன என்பதை முன்கூட்டியே decide பண்ணுவது.

Mental model: **Detect → Classify → Decide → Communicate**.

Detect: timeout, 5xx, business validation fail.
Classify: transient vs permanent, retryable vs non-retryable.
Decide: retry, circuit break, fallback, fail fast.
Communicate: caller-க்கு clear error, user-க்கு meaningful message, system-க்கு observable log.

## 3. How It Works

ஒரு call chain-ல error propagate ஆகும்.

Service layer-ல நீங்கள் errors-ஐ மூன்று வகையாக பார்க்கணும்:

* **Transient errors**: network glitch, temporary overload, timeout. இதை retry பண்ணலாம்.
* **Permanent errors**: bad request, validation fail, not found. Retry வேலைக்காது.
* **Systemic errors**: downstream service down. இதை தனியாக isolate பண்ணணும்.

Implementation pattern:

* Timeout + retry with exponential backoff + jitter. அப்படியே blind retry பண்ணினா thundering herd வரும்.
* Idempotency key. Payment, order create மாதிரி non-idempotent operation-ல client ஒரு idempotency key தரணும். Server அதை store பண்ணி duplicate-ஐ தடுக்கணும்.
* Circuit breaker. Downstream தொடர்ந்து fail ஆனா, கொஞ்ச நேரம் calls-ஐ block பண்ணி அதை protect பண்ணு. Health recover ஆனதும் மெதுவாக resume.
* Bulkhead. Critical path-க்கு தனி thread pool / connection pool. ஒரு slow dependency மற்ற எல்லா request-ஐயும் மூழ்கடிக்கக் கூடாது.
* Graceful degradation. Core feature work ஆகணும், nice-to-have fail ஆகலாம். Example: recommendations fail ஆனாலும் checkout work ஆகணும்.

## 4. Architectural Reasoning

Error handling எப்போ important ஆகும்?

* Service boundary கடக்கும்போது. In-process call vs network call.
* Async processing-ல. Message queue-ல message process fail ஆனா dead letter queue-க்கு போகணும்.
* User-facing API-ல. 500 error-ஐ user-க்கு காட்டக்கூடாது. Structured error response + correlation id தேவை.

Alternative options:

* Fail fast and let caller handle. Simple, but caller-க்கு burden அதிகம்.
* Centralize error handling via middleware / interceptor. Consistent logging, metrics, response format.
* Retry everything vs no retry. இரண்டுமே தப்பு.

Architect choose பண்ணும் போது constraint பார்க்கணும்: latency budget, availability target, data consistency requirement, cost of duplicate operation.

## 5. Trade-offs

* **Retry vs Latency**: Retry reliability கூட்டும், latency அதிகரிக்கும். User wait பண்ண முடியாத flow-ல retry background-ல பண்ண வேண்டும்.
* **Fail fast vs Graceful degradation**: Fail fast simplicity கொடுக்கும். Degradation availability கூட்டும், complexity அதிகரிக்கும்.
* **Detailed error vs Security**: Detailed error debugging-க்கு உதவும், attacker-க்கும் உதவும். External API-ல generic message, internal log-ல full context.
* **Observability cost**: Every error-ஐ log பண்ணி, trace பண்ணி, metric போட்டா cost அதிகம். Sample or aggregate பண்ணணும்.

Failure mode: மோசமான error handling தான் cascade failure-ஐ உருவாக்கும். ஒரு downstream slow ஆனா upstream அதை hold பண்ணி, அதன் upstream-ஐ hold பண்ணும். அப்புறம் whole system down.

## 6. Practical Example

Enterprise payment flow.

Frontend -> API Gateway -> Order Service -> Payment Service -> Bank API.

Bank API timeout ஆகுது. Order Service என்ன பண்ணும்?

* Timeout 3s set பண்ணு.
* Idempotency key-ஐ use பண்ணி request-ஐ retry பண்ணு, max 2 times with jitter.
* Bank API circuit breaker open ஆனா, immediate fallback: user-க்கு "payment processing delayed, we will notify" என்று திருப்பு. Async worker retry பண்ணும்.
* Correlation id எல்லா log-லயும் இருக்கும். User complain வந்தா trace பண்ண முடியும்.
* Success ஆனா Order status updated, fail permanent ஆனா user-க்கு clear reason.

இங்கே error handling business outcome-ஐ பாதிக்கும்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers ஒரு Kafka topic-ஐ consume பண்ணுகிறார்கள். Producer-ஐ block பண்ணக்கூடாது. Consumer processing speed வேறுபடுகிறது. Poison message வரலாம். Retry தேவை.

Error handling-க்கு
