# Capacity estimation

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.2 — System design practice

## 1. Problem

உங்க service production-ல போனதும் Black Friday-க்கு ஒரு நாள் முன்னாடி traffic 10x ஆகுது. API latency spike ஆகுது, database connection pool exhaust ஆகுது, autoscaling பண்ணும் நேரத்துக்குள்ள errors வந்துடுது.

இதுக்கு காரணம் என்ன? உங்களுக்கு எவ்வளவு request வரும், ஒரு request எவ்வளவு resource எடுக்கும், peak எப்போ வரும் - இதையெல்லாம் முன்கூட்டி எஸ்டிமேட் பண்ணல.

Capacity estimation இல்லாம design பண்ணா நடக்கிறது: over-provision பண்ணி காசு வீண், under-provision பண்ணி outage. இரண்டுமே architect-க்கு ஏற்க முடியாதது.

## 2. Mental Model

Capacity estimation என்பது crystal ball பார்க்கிறது இல்ல. இது **workload-ஐ quantify பண்ணி, அதுக்கு தேவையான resources-ஐ map பண்ணுவது**.

மூன்று கேள்வி மட்டும்:

1. எத்தனை request வரும்? RPS, concurrent users
2. ஒரு request எவ்வளவு செலவாகும்? CPU, memory, I/O, network, DB queries
3. எப்போ peak வரும்? growth எப்படி இருக்கும்?

இதை தப்பா estimate பண்ணா system design-ன் எல்லா decision-மே தப்பா போகும்.

## 3. How It Works

பிராக்டிகல் flow:

**Workload characterization**
Realistic traffic pattern எடுக்கணும். Average RPS, P95/P99 latency target, peak factor. உதாரணமா 1000 RPS average, peak 3x = 3000 RPS.

**Per-request cost**
Load test அல்லது production metrics-ல இருந்து ஒரு request-க்கு எவ்வளவு CPU ms, memory, DB read/write எடுக்குதுன்னு கண்டுபிடி.

**Resource mapping**
ஒரு instance எவ்வளவு handle பண்ணும்? உதாரணமா 2 vCPU instance 500 RPS handle பண்ணுது, latency <100ms வரை. அப்ப 3000 RPS-க்கு minimum 6 instances.

**Headroom + failure**
Autoscaling reaction time, node failure, traffic burst-க்கு 20-50% headroom வை.

Formula simple ஆக:
```
Required Instances = ceil( Peak RPS / RPS per instance ) * headroom
```

Database-க்கு தனியா estimate பண்ணணும். Read/write QPS, connection pool size, disk IOPS.

## 4. Architectural Reasoning

இது எப்போ useful?

* New service design முன் cost vs reliability trade-off பண்ண
* DB sharding, read replica, cache layer தேவையா என முடிவு பண்ண
* Autoscaling policy, instance type தேர்வு
* On-prem vs cloud, reserved capacity plan பண்ண

Alternatives: Just autoscale blindly. அது work ஆகும் ஆனால் cold start latency, cost spike, DB bottleneck-ஐ autoscaling fix பண்ணாது.

Architect முடிவு எடுக்கும் போது constraints பார்க்கணும்:
latency budget, availability target 99.9%, cost per request, team ops capacity.

## 5. Trade-offs

**Accuracy vs Speed**
Perfect data வேண்டும்னா time ஆகும். Early design-ல rough estimate + margin போதும். Production-ல மெதுவா refine பண்ணலாம்.

**Over-provision vs Under-provision**
Over-provision = safe but cost waste. Under-provision = saving but outage risk. Financial system-ல under-provision ஏற்க முடியாது. Internal tool-ல ஏற்கலாம்.

**Vertical vs Horizontal**
Bigger instance எடுக்கலாம், அல்லது small instances அதிகம் வைக்கலாம். Horizontal scale பண்ண latency மற்றும் fault tolerance better, ஆனால் network overhead அதிகம்.

**Failure mode**
Capacity estimate தப்பா போனா முதல் symptom latency spike. அப்புறம் timeout cascade, retry storm, DB connection exhaustion. இதை தடுக்க circuit breaker, rate limiting, backpressure வேணும்.

## 6. Practical Example

ஒரு payment API. Target: 5000 RPS peak, P95 latency <200ms.

Load test-ல கண்டுபிடிச்சது:
* 1 c6i.large instance = ~800 RPS, CPU 70% limit
* Each request = 2 DB reads + 1 write, ~5ms DB latency
* DB connection pool per instance = 50

Calculation:
Instances = 5000 / 800 = 6.25 → 7 instances. Headroom 30% → 10 instances.

DB side: 5000 RPS * 3 queries = 15k QPS. Single primary handle பண்ண முடியாது. Read replica 2, write primary 1. Connection pool 10 instances * 50 = 500 connections. Max connections limit check பண்ணி pool size adjust.

Cache தேவையா? 80% read same data. Redis cache போட்டா DB QPS 3x குறையும். இது capacity estimate-ஆல தான் தெரியும்.

Result: Cost estimate, instance type, DB topology எல்லாம் capacity number-ல இருந்து வந்தது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு video streaming API இருக்கு. Average 2000 RPS, peak time-ல 15 minutes-க்கு 15000 RPS வருது. Current setup 8 instances, autoscaling trigger 2 minutes. DB read heavy.

இங்கே bottleneck எங்கே இருக்கலாம்? Capacity estimate எப்படி பண்ணுவீங்க? Autoscaling மட்டும் போதுமா? என்ன architectural change யோசிப்பீங்க?

## 8. Key Takeaways

* Capacity estimation என்பது guess அல்ல, workload quantification + resource mapping.
* Peak, not average. Burst மற்றும் growth-க்கு headroom கண்டிப்பாக வை.
* Service மட்டும் இல்ல, DB, network, cache எல்லாத்துக்கும் தனித்தனியா estimate பண்ணு.
* Estimate தப்பானாலும் ஆகும் loss-ஐ trade-off பண்ணி முடிவு எடு. Over-provision செலவு vs outage
