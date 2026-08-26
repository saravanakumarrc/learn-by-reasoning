# Concurrency

> **Learning Path:** Distributed Systems
> **Section:** 3.1.3 — Core concepts

## 1. Problem

ஒரு API service sequential-ஆ request எடுத்து handle பண்ணுது. ஒரு request வந்தா அது முடியும் வரை அடுத்த request wait பண்ணும்.

அந்த request-ல payment gateway call 2 sec ஆகுது, DB query 200ms ஆகுது. இந்த 2.2 sec நீங்க எதுவும் பண்ணாமல் thread idle-ஆ இருக்கு.

Traffic peak-ல 1000 users ஒரே நேரத்தில் hit பண்ணும்போது என்ன ஆகும்? 
Queue பெருகும், latency spike ஆகும், timeout வரும், user experience கெட்டுப்போகும்.

ஒரு core CPU-வுக்கு ஒரு நேரத்தில் ஒரே task தான் run ஆகும். ஆனால் I/O wait நிறைய இருக்கும். அந்த wait time-ஐ வீணாக்காமல் வேறு request-ஐ handle பண்ண முடியுமா? இதுதான் concurrency தேவைப்படும் பிரச்சனை.

## 2. Mental Model

Concurrency = ஒரே நேரத்தில் பல வேலைகள் *progress* ஆவது. எல்லாம் உண்மையில் ஒரே நேரத்தில் run ஆக வேண்டும் என்று அவசியம் இல்லை.

நீங்க ஒரு restaurant-ல waiter ஒருவர். ஒரு table-க்கு order எடுக்கும் போது kitchen-ல food ready ஆகும் வரை நீங்க நிற்க முடியாது. அதே நேரத்தில் இன்னொரு table-க்கு order எடுக்கலாம்.

Concurrency இல்லாமல் waiter ஒரு table முடியும் வரை காத்திருக்கிறார். Concurrency-ல அவர் wait time-ல வேறு வேலை பார்க்கிறார்.

Parallelism என்பது உண்மையான simultaneous execution, multiple cores/threads. Concurrency என்பது overlapping progress.

## 3. How It Works

System-ல concurrency-ஐ ஆதரிக்க thread, async event loop, goroutine, actor model போன்றவை உதவுகின்றன.

Simple mental model:

```
Request A → I/O wait → Request B start
```

Thread-based concurrency-ல ஒவ்வொரு request-க்கும் ஒரு thread. I/O wait ஆனால் thread scheduler அந்த thread-ஐ park பண்ணி வேறு thread-ஐ run பண்ணும்.

Async/event-driven model-ல ஒரே thread-ல event loop இயங்கும். I/O operation complete ஆனதும் callback / promise resolve ஆகும்.

முக்கியம்: shared state இருந்தால் access-ஐ synchronize பண்ண வேண்டும். இல்லை என்றால் race condition வரும்.

## 4. Architectural Reasoning

Concurrency தேவைப்படுவது இந்த constraints வந்த போது தான்:

* **Throughput**: per second எத்தனை request handle பண்ண வேண்டும்
* **Latency hiding**: external call, DB, network wait நிறைய இருக்கும்
* **Resource utilization**: CPU idle இருக்கக்கூடாது

எப்போது choose பண்ணுவது?
* Service I/O bound ஆக இருந்தால் - API calls, DB queries, message queue consume
* Request processing independent ஆக இருந்தால்
* Peak traffic-ஐ smooth பண்ண வேண்டும் என்றால்

எப்போது avoid பண்ணுவது?
* Logic CPU bound ஆக இருந்தால், concurrency-ல context switch cost-க்கு மேல் gain இல்லை
* Shared mutable state அதிகம் இருந்தால், synchronization overhead வளரும்

Alternative: scale out more instances vs make single instance concurrent. இரண்டும் trade-off. Concurrency cheap ஆக ஆரம்பத்தில் உதவும். பின்னர் horizontal scaling தேவைப்படும்.

## 5. Trade-offs

**Throughput vs Complexity**: Concurrency-ல throughput பெருகும். ஆனால் code reasoning கடினமாகும். Bug reproduce பண்ண கஷ்டம்.

**Race condition & shared state**: இரண்டு request ஒரே in-memory cache object-ஐ update பண்ணினால் data corrupt ஆகும். Lock போடலாம். Lock போட்டால் contention வரும், deadlock வரும்.

**Resource limits**: Thread per request model-ல 10k concurrent request = 10k threads. Memory, context switch-ல system crash ஆகும். அதனால் thread pool, connection pool, backpressure தேவை.

**Ordering guarantees**: Concurrent processing-ல request order காப்பாற்றுவது கடினம். Idempotency, exactly-once semantics போன்ற design decisions தேவைப்படும்.

Failure mode: thread leak, unbounded queue growth, thundering herd on resource release.

## 6. Practical Example

Enterprise order service.

Flow: validate request → check inventory DB → call payment gateway → emit event to message queue → return response.

Payment gateway 1.5 sec latency. DB 50ms.

Sequential model-ல 1 request = ~1.55 sec. 1 instance-ல ~0.65 RPS மட்டுமே.

Concurrency model-ல event loop + connection pool 100. Payment call போகும் போது thread free ஆகி inventory check next request-க்கு போகும். Effective throughput 50-100 RPS ஆக உயரும்.

ஆனால் inventory counter in-memory இருந்தால், இரண்டு concurrent request ஒரே stock-ஐ decrement பண்ணும். Race condition வரும். அதனால் DB row level lock / atomic decrement பயன்படுத்த வேண்டும்.

## 7. Reasoning Challenge

உங்கள் service-க்கு 5000 RPS வ
