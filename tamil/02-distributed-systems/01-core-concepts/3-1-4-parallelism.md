# Parallelism

> **Learning Path:** Distributed Systems
> **Section:** 3.1.4 — Core concepts

## 1. Problem

உங்க service-க்கு ஒரு single request வருது. அது ஒரு 10 MB image-ஐ process பண்ணி, resize பண்ணி, 5 different filters apply பண்ணனும். Single core-ல ஒரே thread ஓடினா, ஒரு request 2 sec எடுக்குது.

இப்போ traffic spike வருது. 100 requests per second வருது. ஒரே core-ல தொடர்ந்து queue ஆகும். Latency போய் 20 sec ஆகுது. Timeout ஆகுது. User experience கெட்டுபோகுது.

இதே மாதிரி, ஒரு nightly batch job இருக்கு. 10 million records-ஐ scan பண்ணி aggregate பண்ணனும். Single machine-ல ஓடினா 8 மணி நேரம் ஆகுது. Business window முடிஞ்சிடும்.

இங்கே painful point என்ன? **Throughput வரம்பு மற்றும் latency வளர்ச்சி.** ஒரே வேலையை ஒரே நேரத்தில் ஒன்றுக்கு மேற்பட்ட execution unit-ல செய்ய முடியல.

## 2. Mental Model

Parallelism என்பது **same time-ல multiple things நடக்குது** என்பது.

Concurrency என்பது multiple things *overlap* ஆகும். Parallelism என்பது அவை உண்மையாகவே same time-ல run ஆகும்.

ஒரு kitchen-ல ஒரே cook இருந்தா, ஒரு order எடுத்து முடிச்சிட்டு அடுத்த order-க்கு போவார். இது concurrency. ஆனா 4 cooks இருந்தா, 4 orders ஒரே நேரத்தில் cook ஆகும். இது parallelism.

Core level-ல: multi-core CPU, multiple machines, multiple containers.

System level-ல: data parallelism vs task parallelism.

Data parallelism: ஒரே வேலை, வெவ்வேறு data. 10 million records-ஐ 10 shards-க்கு பிரிச்சு parallel-ல process பண்ணுவது.

Task parallelism: வெவ்வேறு வேலை. API gateway request-ஐ auth service, pricing service, inventory service-ல parallel-ல call பண்ணுவது.

## 3. How It Works

Parallelism-க்கு தேவை: **independent units** மற்றும் **coordination mechanism**.

Independent units = cores, pods, nodes, workers. அவை ஒன்னுக்கொன்னு தொடர்பில்லாமல் வேலை செய்ய முடியுமா?

Coordination = partition key, work queue, load balancer, message queue.

Simple flow:

`Request -> Partition -> Worker1, Worker2, WorkerN -> Merge Result`

Partitioning தப்பா செஞ்சா, duplicate work அல்லது missing work வரும். Merge செஞ்சா ordering அல்லது consistency issue வரும்.

Amdahl's law ஒன்னு முக்கியம்: serial part எவ்வளவு இருக்கோ, அவ்வளவு parallelism gain குறையும். 90% work parallel ஆகி, 10% serial-ஆ இருந்தா, max speedup ~10x தான்.

## 4. Architectural Reasoning

Parallelism useful ஆகும் போது:

* Throughput தேவை, latency குறையனும். e.g., image processing, video transcoding, search indexing.
* Work independent. No strict ordering dependency.
* Cost of coordination < gain from parallelism.

எப்போ avoid பண்ணனும்?

* Strong consistency தேவைப்படும், serial order முக்கியம். e.g., bank account transfer.
* Work overhead அதிகம். Tiny tasks-ஐ parallel பண்ணினா scheduling overhead-ல தான் முடியும்.
* State shared ஆகி contention ஏற்படும். Multiple workers same database row-ஐ lock பண்ண முயற்சிக்கும்.

Alternatives: vertical scaling - bigger machine. அது simple ஆனா limit உண்டு, cost அதிகம், single point of failure. Horizontal parallelism = more small units.

Architect choose பண்ணும்போது constraint பார்க்கனும்: latency budget, cost per request, operational complexity, failure blast radius.

## 5. Trade-offs

**Throughput vs Complexity.** Parallel ஆக்கினா throughput போகும். ஆனா code complex ஆகும். Partition logic, idempotency, retry, deduplication எல்லாம் வரும்.

**Latency vs Coordination overhead.** Parallel calls செய்யும்போது overall latency = max of parallel calls, not sum. ஆனா result merge, synchronization-க்கு extra latency வரும்.

**Consistency vs Availability.** Parallel writers same data-ஐ touch பண்ணா race condition வரும். Lock, optimistic concurrency, versioning தேவைப்படும். அது availability குறைக்கும்.

**Failure modes.** ஒரு worker fail ஆனா அதன் work மறுபடியும் retry ஆகனும். Partial failure-ல result incomplete ஆகும். Exactly-once semantics கஷ்டம்.

Every architectural solution creates new trade-off. Parallelism தரும் throughput-க்கு பதிலாக coordination cost வாங்கிக்கனும்.

## 6. Practical Example

Enterprise e-commerce-ல order report generate பண்ணனும். Daily 50 million order events. Single node-ல scan பண்ணினா 6 மணி நேரம்.

Decision: data parallelism use பண்ணுவோ
