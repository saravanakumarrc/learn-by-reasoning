# Partial failures

> **Learning Path:** Distributed Systems
> **Section:** 3.1.7 — Core concepts

## 1. Problem

நீங்கள் 3 availability zone-ல ஒரு order service, payment service, inventory service ஓட்றீங்க. ஒரு customer order place பண்ணும்போது order service -> payment service call பண்ணுது, அதே நேரத்துல inventory service-க்கும் call பண்ணுது.

இங்கே என்ன நடக்கும்? Network-ல packet drop ஆகும். ஒரு AZ-ல network latency spike ஆகும். payment service-ன் ஒரு instance crash ஆகும். inventory service slow ஆகும்.

முழு system-மே down ஆகல. சில parts வேலை செய்யுது, சில parts fail ஆகுது. இதுதான் **partial failure**.

இதை handle பண்ணாம விட்டா என்ன ஆகும்? Client-க்கு request timeout ஆகும், retry பண்ணும், duplicate charge வரும். Inventory reserve ஆகி payment fail ஆகும். User-க்கு order created என்று தெரியும், ஆனால் payment pending. Data inconsistent ஆகும்.

> Partial failure என்பது total outage இல்லை. System-ன் ஒரு பகுதி மட்டும் sick ஆக இருக்கும், மீதி healthy ஆக இருக்கும்.

## 2. Mental Model

Distributed system-ஐ ஒரு குழு வேலை பார்க்கும் office-ஆக நினைச்சுக்கோங்க. எல்லாரும் ஒரே நேரத்துல வேலைக்கு வர மாட்டாங்க. ஒருத்தர் late வருவார், ஒருத்தர் network issue-ல phone-க்கு respond பண்ண மாட்டார், ஒருத்தர் temporary offline ஆவார்.

நீங்கள் இன்னொருவரை depend பண்ணி இருந்தால், அவர் respond பண்ணலைன்னா அது failure ஆ? அவர் dead ஆ? அவர் busy ஆ? network slow ஆ? **நீங்கள் உறுதியாக சொல்ல முடியாது.**

இந்த uncertainty தான் partial failure-ன் core.

## 3. How It Works

Partial failure-ஐ detect பண்ண முடியாது, முழுமையாக தெரிஞ்சுக்க முடியாது. நாம் செய்யுறது heuristics.

* **Timeout**: Call-க்கு காத்திருக்கும் காலம். 500ms-க்கு மேல் வரலைன்னா call failed ன்னு assume பண்ணு.
* **Retry with backoff**: Temporary glitch என்று நம்பி மறுபடி try பண்ணு. ஆனால் immediate retry storm உருவாகும்.
* **Health checks / heartbeats**: Service தன்னை healthy என்று சொல்லிக்கொண்டே இருக்கணும். Heartbeat நிற்கும்போது node unhealthy.
* **Circuit breaker**: Same service தொடர்ந்து fail ஆனால் அதை temporarily திறந்து விடு, அதனால் cascading failure தடு.
* **Idempotency**: Retry செய்தாலும் side effect ஒரு முறை தான்.

Problem என்னவென்றால், timeout-ஐ குறைவாக வைத்தால் false positive failure அதிகம். அதிகமாக வைத்தால் user wait அதிகம்.

## 4. Architectural Reasoning

Partial failure என்பது assumption அல்ல, fact.

எனவே architect ஆக நீங்கள் எப்போதும்:

* **Assume the network is unreliable.** Call succeed ஆகாது என்று design பண்ணு.
* **Make operations idempotent.** Retry safe ஆக இருக்கணும்.
* **Decouple with async.** Synchronous call chain-ஐ குறை. Event queue use பண்ணு.
* **Design for observability.** Which service is slow? Which link failed? அதை தெரிஞ்சுக்க முடியாதா, blind ஆக இருப்பீங்க.

நீங்கள் availability வேண்டுமா, consistency வேண்டுமா என்று decide பண்ணும் போது partial failure தான் trade-off-ஐ drive பண்ணும்.

## 5. Trade-offs

**Timeout vs accuracy**
Timeout குறைவு -> fast failure, ஆனால் healthy service-ஐ unhealthy என்று நினைக்கும். Timeout அதிகம் -> user experience மோசம்.

**Retry vs thundering herd**
Retry தேவை, ஆனால் எல்லா client-உம் ஒரே நேரத்துல retry பண்ணினால் downstream collapse ஆகும். Jitter, exponential backoff must.

**Synchronous vs asynchronous**
Synchronous simple, ஆனால் one partial failure whole request fail. Async resilient, ஆனால் ordering, eventual consistency complex.

**Failure detection latency**
நீங்கள் தெரிஞ்சுக்கும் வேகம் vs false positive. Heartbeat interval குறைவு -> overhead அதிகம்.

**Partial failure முக்கிய failure mode** ஆனதால், system-ன் correctness proof செய்ய முடியாது, நீங்கள் probability-ல மட்டுமே manage பண்ண முடியும்.

## 6. Practical Example

E-commerce checkout flow:

Order service payment service-ஐ call பண்ணி charge செய்யுது. அதே நேரத்துல inventory service-ஐ call பண்ணி stock reserve பண்ணுது.

Payment service respond பண்ணுது, ஆனால் inventory service slow. Timeout hit ஆகுது. Order service என்ன செய்யும்?

Bad
