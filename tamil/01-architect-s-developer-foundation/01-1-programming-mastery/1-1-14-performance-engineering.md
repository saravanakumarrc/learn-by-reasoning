# Performance engineering

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.14 — 1. Programming mastery

# Performance Engineering

## 1. Problem

Dev-ல API 50ms-ல return ஆகுது. Production-ல launch பண்ணினதும் peak hour-ல p99 latency 2 sec ஆகுது, timeout, error rate ஏறுது, cost double ஆகுது. 

இது "code work ஆகுது" என்பதற்கும் "system work ஆகுது" என்பதற்கும் வித்தியாசம். Performance engineering வருவதற்கு காரணம் இதுதான். Feature complete ஆனதும் performance பிரச்சனை தெரியும். அப்போது fix பண்ணுவது costly.

என்ன தவறு? Guess பண்ணி code optimize பண்ணினோம், ஆனால் உண்மையான bottleneck எங்கே இருக்கு என்று தெரியாமல். Performance என்பது feeling அல்ல, measurement.

## 2. Mental Model

Performance engineering என்பது **faster code எழுதுவது அல்ல**. இது constraints-ஐ manage பண்ணுவது.

ஒரு system-க்கு மூன்று விஷயங்கள் முக்கியம்:
* **Latency** - ஒரு request-க்கு எவ்வளவு நேரம்
* **Throughput** - ஒரு unit time-ல எத்தனை requests handle பண்ண முடியும்
* **Resource utilization** - CPU, memory, network, DB connections எவ்வளவு use ஆகுது

இவை எல்லாம் trade-off-ல இருக்கு. ஒன்றை improve பண்ணினால் இன்னொன்று பாதிக்கும்.

Mental model: **Measure → Find bottleneck → Reason → Fix → Verify**. Guess பண்ணாதே.

## 3. How It Works

நடைமுறையில் performance engineering என்பது 3 step loop.

**1. Observe**
p50, p95, p99 latency பார். Average போதாது. Tail latency தான் user experience-ஐ decide பண்ணும்.
Throughput, error rate, saturation metrics-ஐ பார். RED / USE method.

**2. Profile**
CPU hot path எது? Memory allocation அதிகமா? I/O wait? Network round trip?
Production-like load-ல profile பண்ணு. Local laptop-ல 10 requests test பண்ணி conclusion எடுக்காதே.

**3. Isolate bottleneck**
Amdahl's Law மனசில் வை. 80% time spend ஆகும் 20% code தான் matter.
Database query slowவா? N+1 query வருதா? Lock contention இருக்கா? Cold start? Serialization overhead?

Fix பண்ணிய பிறகு மீண்டும் measure பண்ணு. Performance without measurement என்பது religion.

## 4. Architectural Reasoning

Performance problem code level மட்டும் இல்லை. Architecture decision தான் root cause.

எப்போது care பண்ண வேண்டும்?
* Request path-ல synchronous external call இருந்தால்
* Shared resource - DB, cache, message queue - limit அடைந்தால்
* Hotspot / single point - ஒரு service எல்லா traffic-ஐயும் பார்த்தால்

Options எப்போதும் இருக்கு:
* Optimize existing - query, batch, cache
* Scale out - horizontal scaling, read replica
* Async பண்ணு - queue, background job
* Reduce work - pagination, pre-compute, denormalize

ஒரு architect ஏன் choose பண்ணுவார்? Constraint பார்த்து.
Latency sensitive checkout flow-க்கு cache + read replica. Background report generation-க்கு async queue.

Decision-க்கு consequence இருக்கும். Cache சேர்த்தால் stale data, invalidation complexity வரும்.

## 5. Trade-offs

**Latency vs Throughput**: Low latency maintain பண்ண low concurrency வைக்கலாம். Throughput வேண்டுமென்றால் batching, larger payload.

**Optimization vs Maintainability**: Clever code performance கொடுக்கும், ஆனால் readability கெடும். Premature optimization தவிர்க்கணும். Measure பண்ணி பிறகு தான்.

**Consistency vs Availability for performance**: Strong consistency வேண்டும் என்றால் DB round trips அதிகம். Eventual consistency எடுத்தால் latency குறையும், ஆனால் correctness risk.

**Cost vs Performance**: Bigger instance, more replicas, better network - performance வரும், cost போகும். Performance engineering-ன் இறுதி goal cost efficient performance.

Failure mode முக்கியம்: Optimization செய்து
