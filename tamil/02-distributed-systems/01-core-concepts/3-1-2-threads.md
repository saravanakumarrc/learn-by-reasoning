# Threads

> **Learning Path:** Distributed Systems
> **Section:** 3.1.2 — Core concepts

### 1. Problem

உங்கள் service-க்கு ஒரு HTTP request வருது. Request-ஐ handle பண்ண நீங்கள் database-க்கு query அனுப்பணும், அப்புறம் ஒரு external API-க்கு call பண்ணணும்.

DB call 40 ms எடுக்குது. API call 60 ms எடுக்குது. ஒரே ஒரு thread மட்டும் இருந்தா, அந்த thread அந்த 100 ms முழுக்க block ஆகி இருக்கும். அந்த நேரத்துல வரும் மற்ற requests எல்லாம் queue-ல காத்திருக்கும்.

Throughput குறையும். Latency spike ஆகும். ஒரு slow downstream முழு service-ஐயும் கெடுக்கும்.

இதுதான் painful problem. **I/O wait நேரத்தை வீணாக்காமல்** மற்ற request-களை முன்னேற்ற வேண்டும்.

### 2. Mental Model

Thread என்பது ஒரு process-க்குள் இருக்கும் independent execution context.

ஒரு process-க்கு memory space ஒன்று. அதுக்குள் பல threads ஓடும். அவை stack, program counter மாதிரி state-ஐ தனித்தனியா வைத்திருக்கும். Memory மற்றும் file handles போன்ற resources-ஐ share பண்ணும்.

அனலாகி: ஒரு restaurant kitchen. Process = kitchen. Thread = chef. ஒரு chef soup கொதிக்க வைத்துவிட்டு காத்திருக்கும் போது, மற்ற chef next order-ஐ start பண்ணலாம்.

### 3. How It Works

OS kernel thread scheduler-ஐ வைத்து CPU time slice allocate பண்ணும்.

Thread-per-request model-ல்:
Client request வந்ததும் thread pool-ல் இருந்து ஒரு thread எடுக்கப்படும். அந்த thread request-ஐ முழுவதும் handle பண்ணும். I/O call பண்ணும் போது thread block ஆகும். OS அந்த thread-ஐ preempt பண்ணி வேறு ready thread-ஐ run பண்ணும்.

Blocking I/O-க்கு thread idle ஆனாலும் memory-ல stack வைத்திருக்கும். Typically 1 MB - 2 MB per thread.

Thread pool என்பது create/destroy cost-ஐ தவிர்க்க வைத்திருக்கும் worker threads pool.

### 4. Architectural Reasoning

Thread எப்போது useful?

**I/O bound workloads.** DB call, HTTP call, file read, message queue consume போன்றவை. CPU idle இருக்கும் போது thread switch பண்ணி மற்ற request-ஐ run பண்ணலாம்.

CPU bound workloads-ல் thread அதிகம் உதவாது. அப்போது multiple processes or machines தேவை.

Distributed system node-ல் ஒரு service எவ்வளவு concurrent request handle பண்ணும் என்பது thread pool size, downstream latency, target latency-ஐ வைத்து decide ஆகும்.

Alternatives:
* Single threaded event loop with non-blocking I/O - Node.js, Go runtime
* Thread-per-request - traditional Java, Python with threads
* Async/await coroutines - lightweight than OS threads

Architect choose பண்ணும்போது team familiarity, ecosystem, library blocking behavior பார்க்கணும்.

### 5. Trade-offs

**Context switch cost.** ஆயிரக்கணக்கான threads இருந்தால் scheduler overhead ஏறும். CPU cache locality குறையும்.

**Memory footprint.** ஒவ்வொரு thread-க்கும் stack memory தேவை. 10k threads = 10-20 GB memory waste.

**Shared memory = shared bugs.** Threads ஒரே memory-ஐ share பண்ணுவதால் race condition, deadlock, data corruption வரும். Synchronization primitives like lock, mutex, semaphore தேவைப்படும். அது contention உண்டாக்கும்.

**Scalability ceiling.** ஒரு single machine-ல் threads எ
