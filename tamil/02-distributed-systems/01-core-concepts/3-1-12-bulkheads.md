# Bulkheads

> **Learning Path:** Distributed Systems
> **Section:** 3.1.12 — Core concepts

## Problem

ஒரு order service இருக்கு. அது payment service, inventory service, notification service, recommendation service-ஐ call பண்ணும்.

ஒரு நாள் recommendation service slow ஆகுது. latency 5 sec ஆகுது. அல்லது அது crash ஆகுது.

என்ன ஆகும்? Order service-ல உள்ள thread pool common-ஆ இருந்தா, அந்த slow calls எல்லா threads-ஐயும் occupy பண்ணும். Payment, inventory எல்லாம் healthy-ஆ இருந்தாலும் அவங்களுக்கு thread கிடைக்காது.

ஒரு dependency fail ஆனதால் முழு service-மே unavailable ஆகிடும். இதுதான் cascading failure.

"ஒரு service-ல எல்லா work-ஐயும் ஒரே pool-ல run பண்ணுனா, ஒரு கெட்ட tenant / slow dependency எல்லாரையும் கொன்னுடும்." இதை தடுக்கத்தான் bulkhead வருது.

## Mental Model

Ship-ல bulkhead என்பது watertight compartment. ஒரு compartment-ல hole விழுந்தாலும் மற்ற compartment-கள் safe-ஆ இருக்கும்.

Distributed system-ல bulkhead என்பது **resource isolation**. CPU, thread, connection, memory, rate limit எல்லாத்தையும் logical boundaries-க்குள் பிரிச்சு, ஒரு பகுதி fail ஆனாலும் மற்ற பகுதி run ஆகும்.

ஒரே service-க்குள்ளே கூட isolation வேணும். மொத்த system-க்கும் isolation வேணும்.

## How It Works

Bulkhead என்பது implementation pattern. Concept ஒன்று, technique பல.

1. **Thread / Connection pool per dependency**
Order service-ல payment-க்கு ஒரு dedicated thread pool, recommendation-க்கு தனி thread pool. Recommendation pool exhaust ஆனாலும் payment pool free-ஆ இருக்கும்.

2. **Bulkhead per tenant / customer**
Enterprise SaaS-ல Tenant A-க்கு ஒரு bulkhead, Tenant B-க்கு தனி bulkhead. ஒரு tenant traffic spike அடிச்சாலும் மற்ற tenant-க்கு impact இல்ல.

3. **Bulkhead per request type**
Critical path requests - checkout, payment -க்கு ஒரு pool. Background jobs - email, analytics -க்கு வேற pool.

4. **Bulkhead per downstream service**
DB read pool vs write pool. External API call pool vs internal service call pool.

இதோடு சேர்த்து timeout, retry, circuit breaker வரும். Bulkhead resource-ஐ limit பண்ணும். Circuit breaker அதை open பண்ணி fast fail பண்ணும்.

## Architectural Reasoning

Bulkhead useful ஆகும் போது:

* Multiple downstream dependencies உள்ள service. ஒன்று slow ஆனாலும் மற்றது survive பண்ணணும்.
* Multi-tenant system. Noisy neighbor problem இருக்கும்.
* Critical vs non-critical workloads coexist பண்ணும்.

Alternatives என்ன?
* Single shared pool + priority queue. Simple ஆனால் isolation இல்ல.
* Rate limiting / throttling மட்டும். Spike-ஐ கட்டுப்படுத்தும் ஆனால் resource starvation-ஐ முழுசா தடுக்காது.
* Auto-scaling. Helpful ஆனால் slow, cost high.

Architect ஏன் bulkhead தேர்வு செய்வார்?
ஒரு failure domain-ஐ limit பண்ணி blast radius குறைக்க. Availability-ஐ protect பண்ண.

Consequence? New trade-off create ஆகும்.

## Trade-offs

**Isolation vs Utilization**
Resource-ஐ பிரிச்சால் utilization குறையும். Payment pool-ல 80 threads idle இருக்க, recommendation pool-ல thread இல்லாம starve ஆகும். Over-provisioning வேணும்.

**Complexity**
Pool எத்தனை? எவ்ளோ size? Per dependency, per tenant எல்லாம் manage பண்ணணும். Observability கடினம்.

**Latency vs Protection**
Bulkhead limit அதிகமா வச்சா protection குறையும். குறைவா வச்சா legitimate traffic-க்கு 429 வரும்.

**Failure mode**
Bulkhead முறையாக configure பண்ணலைனா, one bulkhead exhaust ஆனாலும் அது retry storm create பண்ணி மற்ற bulkhead-ஐயும் கொல்லும்.

## Practical Example

E-commerce checkout service.

Dependencies:
* Payment Gateway - critical, low latency தேவை
* Inventory - critical
* Recommendation - non-critical
* Notification - non-critical

Architecture:
* Payment & Inventory-க்கு தனித்தனி thread pool, size 50 each, timeout 2s.
* Recommendation-க்கு pool size 10, timeout 500ms.
* Notification-க்கு separate worker queue.

Recommendation service down ஆனாலும் checkout requests fail ஆகாது. Users-க்கு "Recommendations unavailable" log பண்ணிட்டு checkout continue ஆகும்.

Tenant isolation: Plus plan customers-க்கு dedicated pool, Free plan-க்கு shared pool. Free plan traffic spike ஆனாலும் Plus plan SLA protect ஆகும்.

## Reasoning Challenge

உங்க API gateway-க்கு 3 downstream services உள்ளது: User Profile - p95 50ms, Search - p95 300ms, Recommendation - p95 800ms.

ஒரே shared thread pool-ல எல்லா calls-ஐயும் run பண்ணுகிறீர்கள். Black Friday-ல Search slow ஆகி 2 sec ஆகுது.

இங்கே bulkhead எப்படி design பண்ணுவீங்க? Pool size எப்படி decide பண்ணுவீங்க? Recommendation-ஐ fail fast பண்ணுவதற்கு என்ன கூடுதல் mechanism வேண்டும்?

சிந்தித்துப் பாருங்கள். Decision-ன் trade-off என்ன?

## Key Takeaways

* Bulkhead = failure isolation for resources. ஒரு பகுதி fail ஆனாலும் முழு system down ஆகாது.
* Thread/connection pool per dependency, per tenant, per criticality னு பிரிப்பது தான் core implementation.
* Isolation-க்கு கட்டணம் உண்டு: complexity, lower utilization, operational overhead.
* Bulkhead-ஐ மட்டும் வச்சா போதாது. Timeout, circuit breaker, rate limit உடன் சேர்ந்து தான் வேலை செய்யும்.
