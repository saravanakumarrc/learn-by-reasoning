# Performance requirements

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.1.6 — Non-functional requirements

## 1. Problem

உங்க service சரியா work ஆகுது. Tests pass ஆகுது. Code review கூட முடிஞ்சுருக்கு. Production-ல release பண்ணினதும் first hour-லயே support Slack full ஆகுது.

"Checkout page load ஆக 8 seconds ஆகுது"
"Search result வர 4 seconds எடுக்குது"
"Mobile-ல app hang ஆகுது"

Feature இருக்கு, ஆனா user use பண்ண முடியல. Business metric கீழே போகுது. Cost மட்டும் ஏறுது.

இதுதான் performance requirement இல்லாம விட்டதின் வலி. Functional requirement சரியா இருந்தாலும், latency, throughput, scalability மாதிரி non-functional requirements define பண்ணாம இருந்தா system architecturally fail ஆகும்.

## 2. Mental Model

Performance requirement என்பது feature spec இல்லை. அது system-க்கு கொடுக்கப்படும் **contract**.

> எத்தனை request per second handle பண்ணனும்? ஒரு request-க்கு எவ்வளவு time-ல respond பண்ணனும்? Peak load-ல என்ன நடக்கனும்?

இதை நீங்கள் முன்னாடியே தெளிவா சொல்லாவிட்டால், team ஒரு வேலையை முடிச்சதா நினைக்கும், user அதை use பண்ண மாட்டார்.

Mental model simple: **Performance is a constraint, not an optimization afterthought.**

## 3. How It Works

நீங்கள் measure பண்ண வேண்டியது SLI - Service Level Indicator.

அதை முடிவு பண்ணுவது SLO - Service Level Objective.

உதாரணமா:
* Latency: p95 < 200ms, p99 < 500ms
* Throughput: 10,000 RPS sustained, 20,000 RPS peak
* Error rate: < 0.1%
* Availability: 99.9%

இதை எல்லாம் production-ல observe பண்ணி error budget calculate பண்ணுவீங்க. Error budget தீர்ந்தால், new feature stop, performance fix start.

இதுதான் performance requirement-ஐ architectural decision-ஆ மாற்றுறது.

## 4. Architectural Reasoning

Performance requirement வந்ததும் உங்க design choices மாறும்.

Latency குறைக்க வேண்டும்னா:
* Network hop குறைக்கிறீங்க
* Cache வச்சு read path குறுக்குறீங்க
* Synchronous call-க்கு பதில் async பயன்படுத்துறீங்க
* Database query-ஐ index பண்ணுறீங்க

Throughput கூட்ட வேண்டும்னா:
* Horizontal scaling செய்ய முடியுமா என்பதை பார்க்கிறீங்க
* Stateless service design பண்ணுறீங்க
* Message queue வச்சு decouple பண்ணுறீங்க
* Connection pool, batching போன்ற things handle பண்ணுறீங்க

ஆரம்பத்திலேயே requirement இருந்தா, நீங்கள் over-provision பண்ணாமல், right architecture தேர்வு செய்ய முடியும்.

## 5. Trade-offs

Performance-க்கு முக்கியமான 3 trade-offs:

**Latency vs Cost**
Latency குறைக்க cache, bigger instance, read replica வைக்கலாம். ஆனா cost ஏறும். p99 200ms வேணும்னா, p50 20ms service-க்கு 10x cost ஆகலாம்.

**Throughput vs Consistency**
High throughput வேணும்னா eventual consistency தேர்வு செய்ய வேண்டி வரும். Strong consistency க்கு coordination வேணும், அது latency கூட்டும்.

**Performance vs Operability**
Complex optimization - caching layer, CDN, sharding - இவை latency குறைக்கும். ஆனா failure modes கூடும். Cache invalidation தவறினால் stale data. Sharding செய்தால் operational complexity பெரும்.

Tail latency மறந்துவிடக்கூடாது. Average latency நல்லா இருக்கலாம். p99 பயங்கரமா இருந்தால் user experience spoil ஆகும்.

## 6. Practical Example

Enterprise payment gateway. Business சொல்றாரு: Checkout flow p95 < 300ms இருக்கனும், Black Friday-ல 5x traffic spike handle பண்ணனும்.

இப்போ architectural decision என்ன?

Database-ல direct read பண்ணா latency 150ms வரும். User profile, offer data கூட வேணும். அதனால cache layer வச்சு 20ms-க்குள் கொண்டு வர்றீங்க.

Payment authorization synchronous call. அதை timeout 2 seconds-க்குள் வைத்து, retry with idempotency key பயன்படுத்துறீங்க.

Throughput-க்கு service stateless-ஆ வைத்து Kubernetes-ல autoscale பண்ணுறீங்க. Rate limiter வச்சு downstream bank API-ஐ protect பண்ணுறீங்க.

Performance
