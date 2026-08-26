# Backpressure

> **Learning Path:** Distributed Systems
> **Section:** 3.1.10 — Core concepts

# Backpressure — Producer வேகமாக இருக்கும்போது system-ஐ எப்படி protect பண்ணுவது?

## 1. Problem

ஒரு distributed system-ல ஒரு service இன்னொரு service-ஐ call பண்ணும், அல்லது producer consumer-க்கு event அனுப்பும்.

Producer வேகமாக உற்பத்தி பண்ணுது. Consumer slow-ஆ process பண்ணுது.

என்ன ஆகும்?
Request queue நிரம்பும். Memory நிரம்பும். Thread pool தீர்ந்து போகும். Latency spike ஆகும். இறுதியில் service crash ஆகும் அல்லது OOM ஆகும்.

இதை தடுக்க backpressure தேவை. Producer-க்கு சொல்லணும்: "இப்போ process பண்ண முடியாது, slow down பண்ணு".

Problem painful enough ஆகும்போதுதான் backpressure concept வரும்.

## 2. Mental Model

Pipe-ல தண்ணீர் போடறோம். Inlet வேகம் அதிகம், outlet slow.

Pipe-ல pressure build ஆகும். Pipe burst ஆகும்.

அதனால் inlet valve-ஐ close பண்ணுவோம். அதுதான் backpressure.

System-ல இது: fast producer -> slow consumer என்ற mismatch-ஐ handle பண்ணும் signal mechanism.

## 3. How It Works

Backpressure என்பது flow control. Consumer-ன் capacity-க்கு ஏற்ப producer-ன் rate-ஐ adjust பண்ணுவது.

முக்கிய வழிகள்:

**1. Blocking / Synchronous backpressure**
Producer request செய்த உடனே consumer ready ஆகாமல் wait பண்ணும். TCP flow control இதுதான். Connection pool full ஆனால் client block ஆகும்.

**2. Buffering with limit**
Producer-க்கு short term burst handle பண்ண buffer கொடு. Queue size limit வை. Limit அடைந்ததும் signal send பண்ணு.

**3. Explicit signalling**
Consumer full ஆனதை producer-க்கு சொல்லும் protocol. TCP window size, HTTP 429 Too Many Requests, gRPC flow control, Kafka consumer lag -> producer throttle.

**4. Shedding / Dropping**
Buffer full ஆனால் new request-ஐ drop பண்ணு. `503 Service Unavailable` or `429`. System-ஐ protect பண்ண இது தேவை.

சரியான backpressure என்பது producer-ஐ gracefully slow down பண்ணுவது, system-ஐ collapse ஆக விடாமல்.

## 4. Architectural Reasoning

Backpressure useful ஆகும் போது:

* Producer rate unpredictable. Traffic spike வரும்.
* Consumer downstream resource limited. DB connection, CPU, external API rate limit.
* System-ல cascading failure தடுக்க வேண்டும்.

Alternatives என்ன?

* No backpressure + infinite buffer: Memory blow up, OOM.
* No backpressure + drop everything: Data loss, bad UX.
* Scale consumer immediately: Cost high, autoscaling lag உண்டு.

Architect முடிவு பண்ண வேண்டியது: slow down பண்ணுவதா, drop பண்ணுவதா, buffer பண்ணுவதா?

உதாரணமாக, payment processing queue-ல backpressure தேவை. Order service fast-ஆ order உருவாக்கும். Payment service slow-ஆ இருந்தால், orders-ஐ accumulate பண்ணி database-ஐ fill பண்ணாமல், order API-ல rate limit போட வேண்டும்.

Message queue மாதிரி Kafka இதை built-in ஆக கொடுக்கும். Consumer lag அதிகமானால் producer-க்கு pressure தெரியும்.

## 5. Trade-offs

**Latency vs Throughput vs Stability**
Backpressure apply பண்ணினால் producer slow ஆகும். Latency அதிகரிக்கும். ஆனால் system stable ஆக இருக்கும். Drop பண்ணினால் latency குறைவு, ஆனால் data loss.

**Buffer size**
பெரிய buffer = burst absorb ஆகும், ஆனால் memory cost + stale data risk. சிறிய buffer = quick backpressure, ஆனால் throughput குறையும்.

**Who absorbs pressure?**
Upstream service block ஆகலாம், அல்லது API gateway-ல 429 திருப்பலாம். Gateway-ல shed பண்ணினால் upstream protect ஆகும், user-க்கு error தெரியும். Upstream block ஆனால் user experience slow ஆகும், ஆனால் no data loss.

**Failure mode**
Backpressure mechanism fail ஆனால் silent overload வரும். Timeout மிகப்பெரியதாக set பண்ணினால் thread leak ஆகும். Metrics கண்காணிக்க வேண்டும்: queue depth, consumer lag, rejection rate.

## 6. Practical Example

Enterprise e-commerce order flow.

Order Service -> Message Queue -> Inventory Service, Payment Service, Notification Service.

Flash sale-ல Order Service 10k req/s generate பண்ணுது. Payment Service external bank API-க்கு call பண்ணி, rate limit 500 req/s.

என்ன நடக்கும்?
Queue நிரம்பும். Payment Service thread pool exhaust ஆகும். Latency 2 sec -> 30 sec ஆகும். Timeout ஆகி retry storm வரும்.

Backpressure design:
API Gateway-ல rate limiter வைத்து Order Service-க்கு 500 req/s மட்டுமே allow பண்ணு. அல்லது queue depth > 10k ஆனால் Order API 429 return பண்ணு. Message queue consumer-க்கு max in-flight limit வை.

இப்போது producer slow down ஆகும், system stable இருக்கும். User-க்கு clear error தெரியும், retry backoff பண்ணலாம்.

RAG pipeline-லும் இதே. Embedding service fast, vector database slow. Request flood ஆனால் embedding worker-ஐ backpressure பண்ணி queue length control பண்ண வேண்டும்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. எல்லாருக்கும் same event தேவை. Consumer processing speed வேறுபடுகிறது. Producer-ஐ block பண்ணக்கூடாது. Replay-ம் வேண்டும்.

இங்கே backpressure எங்கே apply பண்ணுவீர்கள்? Producer-க்கு signal அனுப்புவீர்களா, consumer-க்குள்ளே buffer பண்ணுவீர்களா, அல்லது drop பண்ணுவ
