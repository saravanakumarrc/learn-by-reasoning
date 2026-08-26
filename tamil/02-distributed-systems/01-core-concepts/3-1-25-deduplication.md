# Deduplication

> **Learning Path:** Distributed Systems
> **Section:** 3.1.25 — Core concepts

## 1. Problem

நீங்க ஒரு payment service build பண்ணிட்டு இருக்கீங்க. Client `POST /pay` அனுப்புது. Network ல திடீர் lag வருது. Client-க்கு response வரல. Client என்ன பண்ணும்? அதே request-ஐ retry பண்ணும்.

இப்போ server-ல முதல் request process ஆகி payment success ஆகிடுச்சு, ஆனா response போகும் வழியில் தொலைஞ்சுது. Retry வந்ததும் server இன்னொரு payment process பண்ணிடும்.

அதே பிரச்சனை distributed system-ல எல்லா இடத்துலயும் வரும். Message queue-ல at-least-once delivery இருக்கும். Consumer crash ஆனா message re-deliver ஆகும். Network partition வந்தா duplicate webhook வரும். 

**Problem என்ன?** ஒரு logical operation ஒரு தடவை மட்டும்தான் நடக்கணும், ஆனா physical delivery பல தடவை நடக்கலாம்.

இதை handle பண்ணாம விட்டா double charge, double order, double email, data inconsistency.

## 2. Mental Model

Deduplication = ஒரே logical event-ஐ ஒரு தடவை மட்டும் process பண்ணுவது.

நினைச்சுக்கோங்க post office-ல duplicate letter filter பண்ற மாதிரி. Letter-க்கு unique tracking number இருக்கு. அதே number மறுபடி வந்தா அதை தூக்கி போட்டுடுங்க.

Distributed system-ல அந்த tracking numberதான் **deduplication key / idempotency key**.

## 3. How It Works

Basic idea simple தான்:

1. **Identify the operation uniquely.** Client request-க்கு idempotency key கொடுக்கணும். அல்லது message-ஐ content hash பண்ணி fingerprint உருவாக்கணும்.
2. **Seen set maintain பண்ணணும்.** இந்த key முன்னாடி process பண்ணியிருக்கோமா என்று பார்க்க ஒரு store வேணும்.
3. **Window maintain பண்ணணும்.** எப்போதும் store வைக்க முடியாது. TTL / sliding window வச்சு பழைய keys-ஐ clean பண்ணுங்க.

Flow:

```mermaid
graph LR
    Client -->|request + idempotencyKey| Service
    Service -->|key exists?| DedupStore
    DedupStore -->|Yes| Return cached result
    DedupStore -->|No| Process --> Save result + Mark key
```

Implementation options:
* **In-memory Set / Redis Set** with TTL - fast, simple
* **Bloom Filter** - memory efficient, false positive possible
* **Database unique constraint** on business key - persistent but slower
* **Kafka / message queue dedupe** using partition key + offset tracking

## 4. Architectural Reasoning

Deduplication எங்கே தேவை?

* **Retry-heavy flows:** payment, order creation, webhook ingestion
* **At-least-once delivery systems:** Kafka, RabbitMQ, SQS
* **Idempotent consumer required:** API gateway retries, saga steps

Choose பண்ணும்போது யோசிக்க வேண்டியது:

* **Who owns dedupe?** Producer-side generate key vs consumer-side fingerprint. பெரும்பாலும் client generate பண்ணும் idempotency key தான் safe.
* **Scope:** Per service instance vs cluster-wide. Cluster-wide என்றால் shared store வேணும்.
* **Window size:** எவ்வளவு நேரம் duplicate வரலாம்? 24h? 7 days? Window குறைவா இருந்தா storage குறைவு, ஆனா late duplicate miss ஆகும்.

Alternative: exactly-once semantics. அது practically கஷ்டம். அதனால் at-least-once + dedupe தான் real world pattern.

## 5. Trade-offs

* **Memory vs Correctness:** Seen keys-ஐ நீண்ட நேரம் வைத்தால் correctness அதிகம், storage cost அதிகம். Bloom filter memory save பண்ணும் ஆனா false positive-ல legitimate request drop ஆகும்.
* **Latency vs Safety:** Dedup check செய்ய DB call போனால் latency add ஆகும். Cache hit rate முக்கியம்.
* **Stateful vs Stateless:** Dedup store ஒரு single point of failure / bottleneck ஆகும். Redis cluster, sharding தேவைப்படும்.
* **False Negative risk:** Window expire ஆனதும் duplicate மறுபடி process ஆகும். Business ரிஸ்க் அனுமதிக்கிறதா பார்க்கணும்.

Failure mode: Dedup store down ஆனால்? Fail open பண்ணி process பண்ணி duplicate risk எடுக்கலாம், அல்லது fail closed பண்ணி availability குறைக்கலாம்.

## 6. Practical Example

Enterprise order system. Client app order create API-க்கு call பண்ணுது. Network timeout.

Client generates `idempotencyKey = UUID` and sends header `Idempotency-Key`. API Gateway அதை pass பண்ணும்.

Order service:
1. Redis-ல `idempotency:{key}` check பண்ணு
2. இருந்தா stored response-ஐ திருப்பி கொடு
3. இல்லைனா order create பண்ணு, response-ஐ Redis-ல 24h TTL-ல save பண்ணு, key-ஐ set பண்ணு

Kafka consumer case: Payment event topic-ல event வருது. Consumer `eventId` + `source` வச்சு dedupe window maintain பண்ணும். Rebalance ஆனாலும் consumer group restart ஆனாலும் same event மறுபடி வந்தாலும் ஒரு தடவை மட்டும் process.

## 7. Reasoning Challenge

உங்கிட்ட 20 consumers இருக்கு, எல்லாரும் same Kafka topic-ஐ consume பண்ணணும். Producer at-least-once. Consumer processing speed வேறுபடும். Replay வேண்டும். Duplicate
