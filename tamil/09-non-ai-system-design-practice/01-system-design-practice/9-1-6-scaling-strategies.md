# Scaling strategies

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.6 — System design practice

# Scaling Strategies — Demand-க்கு capacity எப்படி match பண்ணுறது

## 1. Problem

உங்கள் API இப்போ 100 RPS-ல சரியா ஓடுது. Latency 50ms, error rate 0%. 
ஒரு sale அறிவிச்சதும் traffic 10x ஆகுது. 

என்ன நடக்கும்?
CPU saturate ஆகும், request queue ஆகும், latency 2 sec ஆகும், timeout ஆகும், database connection pool full ஆகும். 

இந்த pain தான் scaling-ஐ தேவைப்படுத்துது. Capacity-ஐ demand-க்கு match பண்ணாம இருந்தா system crash ஆகும்.

## 2. Mental Model

Scaling என்பது ஒரே machine-ஐ பெருசாக்குறதா இல்லை, work-ஐ பல machine-க்கு பிரிச்சு கொடுக்குறதா.

System-ல எப்போவும் ஒரு bottleneck இருக்கும். CPU, memory, network, disk I/O, database, network bandwidth.

அந்த bottleneck-ஐ நீங்கள் move பண்ணுறீர்கள். புது bottleneck வரும் வரை.

## 3. How It Works

**Scale Up — Vertical Scaling**
இருக்கும் machine-ஐ பெருசாக்குறது. 4 core, 16GB இருந்து 16 core, 64GB.

Pros: Simple. Architecture மாற்றம் இல்லை. Stateless service-க்கு ஒரே deploy.
Cons: Ceiling இருக்கு. Single point of failure. Downtime வேண்டும் upgrade-க்கு. Cost non-linear.

**Scale Out — Horizontal Scaling**
ஒன்னு இல்லை, பல same service instances. Load balancer மூலம் traffic distribute.

Stateless service-ஐ scale out பண்ண எளிது. Session server side-ல இருந்தா sticky session அல்லது external session store வேண்டும்.

```
Client --> Load Balancer --> Service A
                         --> Service B
                         --> Service C
```

Autoscaling இங்கே வேலை செய்யும். CPU/memory அல்லது request queue length பார்த்து new instance add/remove.

**Data Scaling**
Service scale out பண்ணினாலும் database ஒன்னு இருந்தா அங்கே bottleneck.

Options:
* **Read Replica**: Read heavy workload-க்கு read replica-கள். Write still primary-ல.
* **Cache**: Hot data-ஐ Redis/memcached-ல வைக்க. Database hit குறையும். Cache invalidation தான் கஷ்டம்.
* **Sharding / Partitioning**: Data-ஐ partition key-படி பிரித்து multiple shards-ல வைக்க. Write throughput scale ஆகும். Cross-shard query கஷ்டம்.
* **Async**: Heavy work-ஐ queue-க்கு அனுப்பு. Producer-கள் block ஆக மாட்டாங்க. Consumers scale independently.

## 4. Architectural Reasoning

Scale out எப்போ useful?
Service stateless ஆக இருக்கும் போது. Request independent ஆக process ஆகும் போது.

Database scale out எப்போ?
Read scale தேவைப்படும் போது replica. Write scale தேவைப்படும் போது sharding.

Cache எப்போ?
Read-heavy, read pattern predictable, stale data acceptable. Cost of miss குறைவு.

ஒரு architect முடிவு எடுக்கும் போது constraints பார்க்கணும்:
Latency budget, traffic growth rate, data consistency requirement, team size, operational complexity, cost.

## 5. Trade-offs

* **Complexity vs Elasticity**: Horizontal scaling elastic ஆனால் service discovery, health check, distributed tracing, session management complex ஆகும்.
* **Consistency vs Scale**: Read replica lag வரும். Sharding-ல cross-partition transaction இல்லை. CAP trade-off visible ஆகும்.
* **Cost**: Scale up ஆரம்பத்தில் cheap. Scale out ஆகும் போது management overhead + network cost ஏறும்.
* **Failure modes**: More instances = more failure points. Autoscaling lag இருக்கும். Scale up பண்ணும்போது cold start latency வரும்.

Every scaling solution creates new problem. Scale out பண்ணினால் data locality problem வரும். Cache போட்டால் stale data problem வரும்.

## 6. Practical Example

E-commerce checkout service.

Normal day: 200 RPS. 2 instances enough.
Sale day: 5000 RPS peak.

Solution:
API service stateless ஆக இருக்கு. Load balancer பின்னால் autoscaling group. CPU >70% ஆனால் new pod add. 30 sec முன் scale up செய்ய predictive scaling.

DB: Primary CPU 90%. Write குறைவு, read அதிகம்.
Read replica 2 add பண்ணி, read queries replica-க்கு route.
Product catalog cache-ல வைக்க. Cache miss rate <5%.

Payment processing async ஆக்கு. Synchronous call slow. Queue-க்கு போட்டு worker scale out.

Result: Latency stable, error rate <0.1%, cost peak
