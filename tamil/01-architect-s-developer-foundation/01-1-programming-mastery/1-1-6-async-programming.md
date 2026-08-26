# Async programming

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.6 — 1. Programming mastery

## 1. Problem

Flash sale API. 10,000 users ஒரே நேரத்தில் request அனுப்புகிறார்கள். ஒவ்வொரு request-க்கும் DB read, Redis cache check, payment gateway call 200ms எடுக்கும்.

Thread-per-request பண்ணினால் என்ன ஆகும்? ஒரு thread ~1MB stack memory. 10k thread = 10GB memory, context switch overhead பெரிதாகும். Server க்ராஷ் ஆகும் அல்லது latency பறக்கும்.

உங்களுக்கு தேவை: **ஒரே request முடியாமல் wait பண்ணும்போது, மற்ற request-களை handle பண்ண வேண்டும்.** Network I/O wait நேரத்தை waste பண்ணக்கூடாது.

இதுதான் async programming வந்த reason.

## 2. Mental Model

Async என்பது **single thread-ல் பல tasks-ஐ cooperative-ஆக மாற்றி மாற்றி ஓட வைப்பது**.

Thread model: OS ஒவ்வொரு request-க்கும் thread கொடுக்கும். I/O wait-ல் இருக்கும்போதும் thread உயிரோடு இருக்கும்.

Async model: ஒரு event loop இருக்கும். Task I/O-க்கு காத்திருக்கும்போது `await` பண்ணி control-ஐ loop-க்கு திருப்பி கொடுக்கும். Loop அடுத்த ready task-ஐ ஓட விடும். I/O complete ஆனதும் callback மூலம் task-ஐ திரும்ப resume பண்ணும்.

Analogy: ஒரே chef இருக்கார். Thread model-ல் ஒவ்வொரு order-க்கும் ஒரு chef. Async-ல் ஒரே chef, ஆனால் சூப் boil ஆகும் போது அவர் idle ஆகாமல் அடுத்த order-க்கு cut பண்ணுவார்.

## 3. How It Works

Core pieces:

* **Event loop** - ready tasks-ஐ schedule பண்ணும் single loop
* **Coroutine** - `async def` function. `await` பார்த்தால் execution pause ஆகும்
* **Non-blocking I/O** - DB client, HTTP client async version. Call பண்ணினால் immediately return ஆகும், result வந்ததும் loop resume பண்ணும்

Flow:
```
Client request -> event loop -> async handler -> await db.query() -> yield
-> next request handle -> I/O complete -> resume handler
```

Blocking call `time.sleep()` or sync DB driver போட்டால் முழு loop-மே freeze ஆகும். இதுதான் மிகப்பெரிய failure mode.

## 4. Architectural Reasoning

Async useful ஆகும் போது:

* Workload **I/O bound**: network call, DB query, file read, message queue consume
* High concurrency, low memory footprint தேவை
* Latency முக்கியம், throughput வேண்டும்
* Limited CPU cores

Async useful இல்லாத போது:

* Workload **CPU bound**: image processing, encryption, heavy computation. Event loop block ஆகும்.
* இதற்கு thread pool / process pool / separate worker தேவை.

Alternatives:
* Thread pool: simple code, true parallelism on multi-core, but high memory and context switch cost
* Async event loop: low memory, high concurrency, but code complexity அதிகம்
* Reactive streams: backpressure க்கு, very complex

Architect decision: API gateway, web server, message consumer போன்ற I/O heavy services-க்கு async. Compute worker-க்கு sync + thread/process.

## 5. Trade-offs

* **Memory vs Complexity**: ஒரு event loop ஆயிரக்கணக்கான connection handle பண்ணும். ஆனால் code-ல் blocking செய்யக்கூடாது. எல்லா library-யும் async compatible ஆக இருக்க வேண்டும்.
* **No true parallelism**: Single thread ஆதலால் CPU bound task செய்தால் முழு system stall. CPU work-ஐ run_in_executor பண்ணி offload செய்ய வேண்டும்.
* **Debugging & Error handling**: Stack trace confusing, cancellation propagation, timeout handling tricky. `await` மறந்தால் deadlock.
* **Failure mode**: ஒரு slow I/O operation அல்லது blocking call அனைத்து request-களையும் தாமதப்படுத்தும். Isolation இல்லை.

## 6. Practical Example

Python FastAPI async endpoint:

Service A ஒரு order create பண்ணும்போது:
1. Redis-ல் user cart read - await redis.get
2. Postgres-ல் inventory check - await db.fetch
3. Payment gateway HTTP call - await httpx.post
4. Event publish to Kafka - await producer.send

எல்லாம் network wait. Thread model-ல் 3 thread-கள் block ஆகி இருக்கும். Async-ல் ஒரே thread-ல் 10k connections handle ஆகும்.

ஆனால் inventory calculation CPU heavy ஆனால் அதை async handler-ல் செய்யக்கூடாது. அதற்கு separate worker pool அனுப்ப வேண்டும்.

```mermaid
graph LR
A[Client]
