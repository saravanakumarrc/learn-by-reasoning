# Trade-off analysis

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.7 — System design practice

## Problem

நீங்க ஒரு order service design பண்ணணும். Business கேட்கிறது:
- Latency 100ms கீழே இருக்கணும்
- 99.99% availability வேணும்
- Strong consistency வேணும், duplicate order வரக்கூடாது
- Cost குறைவா இருக்கணும்

இதையெல்லாம் ஒரே நேரத்துல கொடுக்க முடியாது. இதுதான் architect-ன் real job.

Trade-off analysis என்பது "perfect solution இல்லை"ன்னு ஏற்றுக்கொண்டு, எந்த constraint-ஐ prioritize பண்ணறோம், எதை sacrifice பண்ணறோம்னு conscious-ஆ decide பண்ணுறது.

## Mental Model

System design என்பது feature list இல்லை, constraint management.

ஒவ்வொரு decision-க்கும் ஒரு price இருக்கு. Low latency வேணும்னா, strong consistency கொடுக்க முடியாது. High availability வேணும்னா, cost ஏறும். Simple operability வேணும்னா, scalability limit ஆகும்.

Trade-off என்பது good vs bad இல்லை. It's painful vs painful.

## How It Works

Trade-off analysis-ஐ reasoning-ஆ பண்ண 4 step போதும்:

1. **Constraints-ஐ list பண்ணு.** Technical + business. Latency, throughput, consistency, availability, durability, security, cost, team size, time to market.
2. **Priority order கொடு.** எல்லாம் important இல்லை. Business-க்கு இப்போ என்ன painful? Payment-ல correctness > latency. Search-ல latency > strong consistency.
3. **Options-ஐ compare பண்ணு.** ஒவ்வொன்னுக்கும் என்ன கிடைக்கும், என்ன lose பண்ணுவோம் என்பதை explicit-ஆ எழுது.
4. **Decision-ஐ document பண்ணு.** ஏன் இதை தேர்ந்தெடுத்தோம், எந்த trade-off accept பண்ணோம் என்பதை note பண்ணு. 6 மாசம் கழித்து அதே debate வராம இருக்க.

## Architectural Reasoning

ஒரு architect-க்கு technology தெரிஞ்சா போதாது. Problem context-ஐ புரிஞ்சுக்கணும்.

Example: Read-heavy product catalog.
- Option A: Single Postgres with primary only. Simple, strong consistency, low cost. But read latency spikes under load, no HA.
- Option B: Primary + read replica. Read scale ஆகும், latency குறையும். Replica lag வரும், eventual consistency accept பண்ணணும். Operational complexity அதிகம்.
- Option C: Postgres + Redis cache. Latency மிகவும் குறையும், cost effective. Cache invalidation complexity, stale data risk.

எது சரி? Traffic pattern, consistency requirement, team capability பார்த்துதான் முடிவு.

## Trade-offs

System design-ல அடிக்கடி வரும் core trade-offs:

**Consistency vs Availability.** CAP theorem practically இதுதான். Network partition நடந்தா, consistency maintain பண்ணனும்னா unavailable ஆகணும், availability வேணும்னா stale/incorrect data accept பண்ணணும்.

**Latency vs Durability/Consistency.** Synchronous write to database + replication confirm பண்ணினா latency அதிகம். Async queue use பண்ணினா fast, but data loss risk.

**Cost vs Reliability.** 3 AZ replication, multi-region, auto-scaling எல்லாம் reliability கொடுக்கும். Bill பெரியதாகும். Early stage-ல over-engineering cost-ஐ kill பண்ணும்.

**Simplicity vs Scalability.** Monolith simple to operate, fast to ship. Scale ஆகும்போது change risky. Microservices scale ஆகும், but distributed failure modes, observability cost அதிகம்.

## Practical Example

E-commerce payment service.

Requirement: Exactly-once processing, low latency < 500ms, 99.9% availability.

Option 1: Synchronous API -> DB write with ACID transaction -> response.
Trade-off: Strong consistency, simple mental model. Peak load-ல DB write latency spike ஆகும், DB single point of failure. Availability குறையும்.

Option 2: API -> write to Kafka -> async consumer process payment.
Trade-off: High throughput, availability high. Delivery guarantee-க்கு idempotency handle பண்ணணும். User-க்கு immediate confirmation கொடுக்க முடியாது. Complexity அதிகம்.

Architect decision: Core payment authorization sync-ஆ, settlement async-ஆ. Critical path-ல consistency prioritize பண்ணி, non-critical path-ல availability prioritize பண்ணோம். இதுதான் trade-off.

## Reasoning Challenge

உங்க user profile service-க்கு 10M reads/day, 10K writes/day. Latency p95 < 50ms வேணும். Cost குறைக்கணும். Team-ல 2
