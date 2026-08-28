# Scalability

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.1.1 — Non-functional requirements

## 1. Problem

உங்கள் service இப்போது 1,000 requests per minute handle பண்ணுது. ஒரு நல்ல product launch, Diwali sale, அல்லது viral video-க்கு பிறகு traffic 50,000 RPM ஆக உயருது.

என்ன நடக்கும்?
Latency spike ஆகும், API timeout ஆகும், database connection pool exhaust ஆகும், error rate climb ஆகும். Business சொல்லும்: "System down ஆகுது".

Scale பண்ணலைன்னா growth-க்கு cost கொடுக்க முடியாது. இங்கேதான் scalability என்கிற non-functional requirement வருது.

> Scalability = load அதிகரிக்கும்போது performance degrade ஆகாமல் system-ஐ grow செய்யும் திறன்.

## 2. Mental Model

Scalability-க்கு இரண்டு basic வழிகள்.

**Scale Up - Vertical Scaling:** அதே machine-ஐ பெரிதாக்குறது. More CPU, more RAM. Simple, ஆனால் limit உண்டு. Single point of failure.

**Scale Out - Horizontal Scaling:** அதே வேலையை செய்யும் கூடுதல் instances-ஐ சேர்ப்பது. 1 service → 10 replicas. இது distributed system-ன் core idea.

ஒரு mental model: ஒரு கடையில் ஒரு cashier இருந்தால் queue வளரும். ஒரே cashier-க்கு பெரிய desk கொடுப்பது scale up. 10 cashiers போடுவது scale out.

Scalability என்பது hardware மட்டும் இல்லை. Architecture, data model, network, ops எல்லாம் சேர்ந்தது.

## 3. How It Works

Scalable architecture மூன்று விஷயங்களை செய்கிறது:

**Stateless services.** ஒரு request எந்த instance-க்கு போனாலும் handle ஆக வேண்டும். Session data local memory-ல் வைக்கக் கூடாது. அப்போதான் load balancer request-ஐ distribute பண்ண முடியும்.

**Shared state முறையாக manage பண்ணுவது.** Database, cache, message queue போன்ற shared components-ஐ bottleneck ஆகாமல் பார்த்துக்கொள்ள வேண்டும். Read replica, sharding, partitioning.

**Asynchronous processing.** Synchronous request-response எல்லாவற்றையும் block பண்ணக்கூடாது. Heavy work-ஐ background worker-க்கு தள்ளுவது. Event driven flow, message queue.

## 4. Architectural Reasoning

Scalability எப்போது useful?
Traffic predictable-ஆக வளரும் போது, peak load சீசனல் ஆகும் போது, availability 99.9%+ வேண்டும் போது.

Constraints பார்க்கணும்:
- Latency budget: 200ms-க்குள் வேண்டுமா?
- Cost: scale out செய்யும் போது instance cost, data transfer cost.
- Team size & ops complexity: Kubernetes cluster manage பண்ண திறமை இருக்கா?
- Data consistency requirement: strong consistency வேண்டுமா?

Options:
1. Cache layer சேர்க்க - Redis, CDN
2. Database read/write split
3. Sharding by tenant / geography
4. Async queue - Kafka / RabbitMQ
5. Auto-scaling group with HPA

Decision எப்படி? முதலில் bottleneck எது? CPU? DB? Network? Bottleneck-ஐ மட்டும் scale பண்ணினால் போதும்.

## 5. Trade-offs

**Scale Out vs Complexity.** Horizontal scaling cheap, but distributed system problems வரும்: network partition, eventual consistency, idempotency, distributed tracing.

**Consistency vs Availability.** More replicas = more availability, ஆனால் strong consistency கடினம். CAP theorem இங்கே வேலை செய்யும்.

**Cost vs Performance.** Over-provision பண்ணினால் cost waste. Under-provision பண்ணினால் outage. Auto-scaling helps, ஆனால் cold start latency வரும்.

**Stateless vs Local state.** Stateless scaling easy. ஆனால் session affinity தேவைப்படும் சில workflows-க்கு சிக்கல்.

Important failure modes: thundering herd on cache miss, DB connection exhaustion, hot shard.

## 6. Practical Example

Enterprise e-commerce, flash sale.

Request flow:
```
User -> API Gateway -> Product Service x10 -> Cache Redis -> DB Read Replica
```
Cart update -> Message Queue -> Order Worker

Sale start-ல் 10x traffic. API Gateway rate limit பண்ணும். Product Service HPA-ல் replicas 3-ல் இருந்து 30-க்கு auto scale ஆகும். Redis cache hit ratio 95% வைத்திருக்கிறார்கள். DB writes மட்டும் primary-க்கு, reads replica-க்கு.

இங்கே scale out பண்ணினாலும் DB primary bottleneck ஆகும். அதனால் write sharding அல்லது write buffer queue பயன்படுத்துகிறார்கள்.

Cost: idle time-ல் replicas குறைக்கிறார்கள். Peak time-ல் scale up. இதுதான் cost-aware scalability.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. Same event தேவை. Consumer processing speed வேறுபடுகிறது. Producer-ஐ block பண்ணக்கூடாது. Replay-ம் வேண்டும்.

இங்கே என்ன architecture தேர்வு செய்வீர்கள்? Queue போதுமா? அல்லது event streaming platform தேவையா? ஏன்?

## 8. Key Takeaways

- Scalability என்பது feature அல்ல, design constraint. முதல் நாளிலேயே மனதில் வைக்க வேண்டும்.
- Stateless service + shared external state = horizontal scaling-ன் அடிப்படை.
- Bottleneck-ஐ கண்டுபிடி, அதற்கு மட்டும் scale பண்ணு. Blind scaling cost-ஐ அதிகரிக்கும்.
- Every scaling decision creates new trade-off: complexity, consistency, cost, operability.

Scalability-ஐ ஒரு திட்டமாக பார்க்காதே. இது ஒரு continuous reasoning process.
