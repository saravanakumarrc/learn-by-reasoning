# Consumer groups

> **Learning Path:** Distributed Systems
> **Section:** 3.2.9 — Messaging

## 1. Problem

உங்களிடம் ஒரு event stream இருக்கு. உதாரணமா `order.created` events.

இதை process பண்ண 3 விஷயங்கள் வேண்டும்: email notification அனுப்பணும், fraud check பண்ணணும், analytics-க்கு store பண்ணணும்.

ஒரே consumer வச்சா அது bottleneck ஆகும். Latency போகும், scale பண்ண முடியாது.

அதனால் 3 consumer instances ஆரம்பிச்சீங்க.

இப்போ பிரச்சனை: எல்லா consumer-க்கும் ஒரே event போயிட்டா? அப்போ duplicate work.

ஒரு consumer fail ஆனா அதோட work யார் எடுப்பா?

Producer-ஐ block பண்ணாம consumers வேற வேற speed-ல process பண்ணணும்.

இந்த பிரச்சனைக்கு தேவை: **ஒரு logical work-ஐ பல instances பகிர்ந்து செய்யணும், ஆனா ஒரு message ஒரு தடவை மட்டும் process ஆகணும்.**

## 2. Mental Model

Consumer group என்பது ஒரு team.

ஒரே `group.id` வச்ச consumer-கள் ஒரு team-ல இருக்காங்க. அந்த team-க்கு ஒரு topic-ன் partitions ஒதுக்கப்படும். Team-ல இருக்கிற members partitions-ஐ பகிர்ந்து சாப்பிடுவாங்க.

ஒரே group-க்குள்ள ஒரு message ஒரு consumer மட்டும் பார்க்கும்.

வெவ்வேறு group-க்கு ஒரே message தேவைப்பட்டால், அவங்க தனித்தனியா subscribe பண்ணலாம்.

Bank counter analogy: ஒரு queue-ல நிறைய customer. 5 counters இருந்தால் ஒவ்வொரு counter-க்கும் ஒரு customer. ஒரு counter நின்னுட்டா அந்த customer அடுத்த counter-க்கு போவான்.

## 3. How It Works

Event streaming system-ல, உதாரணமா Kafka, ஒரு topic என்பது பல partitions-ஆக பிரிக்கப்பட்டிருக்கும்.

Consumer group join பண்ணும்போது group coordinator ஒரு assignment பண்ணும்:

```
Topic: orders, 6 partitions
Group: payment-processors, 3 consumers
```

Assignment ஒன்று: C1 -> P0,P1 ; C2 -> P2,P3 ; C3 -> P4,P5

ஒவ்வொரு consumer தன்னோட partitions-ல இருந்து offset-ஐ முன்னோக்கி நகர்த்தும்.

ஒரு consumer down ஆனால் rebalance trigger ஆகும். Coordinator partitions-ஐ மறுபங்கீடு செய்யும்.

ஒரே partition-ல வரும் messages-க்கு order guarantee இருக்கும். வெவ்வேறு partition-ல order guarantee இல்லை.

இதுதான் consumer group-ன் core contract: **ஒரு group-க்குள் ஒரு record ஒரு முறை மட்டும் process ஆகும்.**

## 4. Architectural Reasoning

Consumer group எப்போ useful?

* Horizontal scale தேவை. Throughput அதிகரிக்கணும்.
* Fault tolerance வேண்டும். Consumer fail ஆனாலும் processing நிற்கக்கூடாது.
* Same logical work-ஐ multiple instances பகிர்ந்து செய்யணும்.

Constraints அது address பண்ணும்:

* Partition-level parallelism
* Load balancing without producer involvement
* Failover and rebalancing automatic

Alternatives என்ன?

* Single consumer with queue in memory: scale இல்லை
* Each consumer subscribes independently: duplicate processing, no sharing
* Manual work stealing: operational complexity அதிகம்

Architect decision: Partition count-ஐ எப்படி choose பண்ணுவது? Max expected consumer count-க்கு equal or அதிகமா வச்சுக்கணும். இல்லைன்னா scale பண்ண முடியாது.

## 5. Trade-offs

**Partition = parallelism limit.** Consumer group size partitions-க்கு மேல போக முடியாது. 6 partitions இருந்தா 10 consumers வச்சாலும் 4 idle-ஆ இருக்கும்.

**Rebalance cost.** Consumer join/leave ஆனால் rebalance நடக்கும். அப்போ processing pause ஆகும். Large group, frequent churn = latency spike.

**Ordering guarantee குறைவு.** Group-க்குள்ள overall order இல்லை. Per partition மட்டும் order உண்டு. அதனால் order-sensitive workload-க்கு partition key design முக்கியம்.

**At-least-once semantics.** Consumer crash ஆனால் offset commit ஆகாத message reprocess ஆகும். Exactly-once க்கு extra logic வேண்டும்.

**
