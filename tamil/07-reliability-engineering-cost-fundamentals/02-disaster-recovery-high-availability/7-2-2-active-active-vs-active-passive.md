# Active-active vs active-passive

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.2.2 — Disaster recovery & high availability

## Problem

உங்கள் service ஒரே region-ல் ஓடுது. அந்த region-ல் network outage, power failure, அல்லது cloud provider issue வந்தால் என்ன ஆகும்?

உங்கள் API down, database unreachable, users பார்க்க முடியாது. Business loss, SLA breach.

இதைத் தடுக்க disaster recovery-க்காக இன்னொரு region-ல் setup பண்ணீங்க. இப்போ கேள்வி: அந்த standby site-ஐ என்ன செய்ய வேண்டும்?

அதை எப்போதும் ஓய்வில் வைத்து, primary fail ஆனால் மட்டும் எழுப்புவதா? இல்லை இரண்டு site-உம் தொடர்ந்து traffic எடுப்பதா?

இதுதான் active-passive vs active-active முடிவு.

## Mental Model

**Active-passive** = ஒரு site தான் வேலை பார்க்கும், இன்னொன்று standby.

**Active-active** = இரண்டும் சேர்ந்து வேலை பார்க்கும், traffic split ஆகும்.

ஒன்று insurance policy மாதிரி. மற்றது two kitchens running same restaurant.

## How It Works

**Active-passive**

Primary region எழுதும், read/write எல்லாம் அங்கே. Standby region-க்கு data replicate ஆகும், async or semi-sync.

Health check / Route53 failover வைத்து primary down என்று தெரிந்தால் DNS / load balancer traffic-ஐ standby-க்கு மாற்றும்.

Failover manual or automatic. RTO பொதுவாக minutes.

**Active-active**

இரண்டு region-உம் active. Global load balancer user-ஐ nearest healthy region-க்கு அனுப்பும்.

Writes இரண்டு region-லயும் வரலாம். அதனால் cross-region replication, conflict resolution, global database மாதிரி DynamoDB Global Tables, CockroachDB, Spanner தேவைப்படும்.

Failover என்பது automatic, user-க்கு தெரியாது. RTO seconds.

## Architectural Reasoning

Active-passive தேர்வு செய்யும் போது:

* Cost குறைவு. Standby-ல் minimal instances, auto-scaling off.
* Data consistency எளிது. Single writer, no conflict.
* Failover slow, data loss risk உண்டு. Replication lag = RPO.
* Team size சிறியது எனில் operational complexity குறைவு.

Active-active தேர்வு செய்யும் போது:

* Availability அதிகம். Region failure என்பதே outage இல்லை.
* Latency குறைகிறது. Users-ஐ nearest region-க்கு route பண்ணலாம்.
* Throughput scale ஆகும். Load இரண்டு site-ல் பிரிகிறது.
* Operational complexity அதிகம். Split-brain, write conflict, clock skew, idempotency எல்லாம் முக்கியம்.

## Trade-offs

* **Cost vs Availability**: Active-passive-ல் infra cost ~1.3x. Active-active-ல் ~2x plus data transfer cost. ஒவ்வொரு request-க்கும் cross-region replication cost வரும்.
* **Consistency vs Latency**: Active-active-ல் strong consistency கொடுக்க global consensus தேவை, latency அதிகரிக்கும். Eventual consistency எடுத்தால் user-க்கு stale read வரலாம்.
* **RTO/RPO**: Active-passive-ல் RPO minutes ஆகலாம், RTO 5-15 min. Active-active-ல் RPO near zero, RTO seconds.
* **Failure modes**: Active-passive-ல் failover போது split-brain வராது. Active-active-ல் network partition வந்தால் two writers conflict-ல் data corruption வாய்ப்பு உண்டு.

## Practical Example

ஒரு payment gateway.

Active-passive: Primary Mumbai, standby Chennai. Normal-ல் Chennai warm standby-ல் இருக்கும். Mumbai down ஆனால் DNS flip, traffic Chennai-க்கு. கொஞ்சம் downtime ஏற்படும், ஆனால் cost கட்டுப்பாட்டில்.

Active-active: Mumbai + Singapore. User nearest region-க்கு செல்லும். Payment write both region-ல் replicate ஆகும். Conflict resolutionக்காக idempotent payment id + last-write-wins அல்லது vector clock வைக்க வேண்டும். Latency 50ms குறையும், cost double.

எந்த model தேர்வு? Business RTO < 1 min வேண்டுமா? இல்லை monthly cost கட்டுப்பாடு முக்கியமா?

## Reasoning Challenge

உங்களுக்கு e-commerce site இருக்கு. 90% users Chennai, 10% users Singapore. Peak sale-ல் traffic 10x ஆகும். Budget limited, team 5 engineers.

Region failure-க்கு RTO 30 min ஏற்றுக்கொள்ளக்கூடியது. Data loss 5 min-க்குள் ஏற்றுக்கொள்ளலாம்.

Active-active செய்வீர்களா? இல்லை active-passive + read replica in Singapore போதுமா? ஏன்?

## Key Takeaways

* Active-passive என்பது disaster recoveryக்கான insurance, active-active என்பது performance + availabilityக்கான architecture.
* Active-active தேவைக்கு காரணம் latency, throughput, zero-downtime failover இல்லாமல் data consistency மற்றும் conflict handling எளிதல்ல.
* ஒவ்வொரு architectural solution-க்கும் ஒரு trade-off உண்டு. Cost, complexity, consistency மூன்றும் ஒன்றாக வராது.
