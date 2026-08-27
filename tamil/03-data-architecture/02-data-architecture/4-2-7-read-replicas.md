# Read replicas

> **Learning Path:** Data Architecture
> **Section:** 4.2.7 — Data architecture

## 1. Problem

உங்க system-ல ஒரு PostgreSQL / MySQL primary இருக்கு. Order create பண்ணுறது, payment update பண்ணுறது, inventory decrement பண்ணுறது மாதிரி writes குறைவு. ஆனா product list பார்ப்பது, order history பார்ப்பது, search பண்ணுறது மாதிரி reads மிக அதிகம்.

Peak time-ல primary CPU 90%+, I/O wait அதிகமாகுது. Read query-க்கே latency spike ஆகுது. Writes-ஐ slow பண்ணக்கூடாது. Vertical scale பண்ணினாலும் cost அதிகம், மேலும் single node-ன் limit வரும்.

என்ன வேணும்? Writes ஒரு இடத்தில் தான் போகணும், reads-ஐ பல இடத்தில் spread பண்ணனும். அதான் read replica தேவைப்படுறது.

## 2. Mental Model

Read replica என்பது primary DB-ன் copy. ஒரே writer, பல readers concept.

Primary எல்லா writes-ஐயும் accept பண்ணும். Change-கள் replication log-ல பதிவாகி replicas-க்கு propagate ஆகும். Replicas read-only. Client-கள் read traffic-ஐ replicas-க்கு route பண்ணலாம்.

அதாவது library-ல ஒரே librarian எழுதுவார், பலர் புத்தகத்தை படிக்கலாம். எழுதுபவர் ஒருவர், படிப்பவர்கள் பலர்.

## 3. How It Works

Primary-ல write வந்தால், transaction commit ஆனதும் WAL / binlog-ல entry create ஆகும். Replica-கள் அந்த log-ஐ pull / stream பண்ணி apply பண்ணும்.

Replication synchronous ஆகவோ asynchronous ஆகவோ இருக்கலாம்.

Async replication தான் பெரும்பாலும் use ஆகும். அதாவது primary commit ஆன உடனே acknowledge பண்ணிடும், replica apply ஆகும் நேரத்தில் lag இருக்கும்.

இந்த lag தான் முக்கியம். Primary-க்கும் replica-க்கும் milliseconds முதல் seconds வரை difference வரும்.

Application layer-ல read vs write routing தீர்மானிக்கணும். Writes எப்பவும் primary-க்கு, reads replica-க்கு.

## 4. Architectural Reasoning

Read replica useful ஆகும் போது:

* Read-heavy workload. Read:Write ratio 10:1, 100:1 மாதிரி இருந்தால்.
* Read latency குறையணும். Replica-களை different AZ / region-ல வைத்து geographic latency குறைக்கலாம்.
* Primary-ன் read load-ஐ offload பண்ணி write throughput protect பண்ணணும்.

Alternatives என்ன?
* Vertical scale primary. Simple ஆனா limit உண்டு, cost அதிகம்.
* Caching with Redis. Hot reads-க்கு நல்லது. ஆனா cache invalidation complexity.
* Sharding. Write scale-க்கு. Read scale-க்கு அவ்வளவு நேரடி இல்லை.
* Read replica தேர்வு என்பது read scale-ன் cheapest first step.

Decision point: Consistency requirement என்ன? User தன்னுடைய தான் படைத்த record-ஐ உடனே பார்க்க வேண்டுமா? அப்படி இருந்தால் replica read பிரச்சனை.

## 5. Trade-offs

**Eventual consistency, not strong consistency.** Replica lag இருக்கும். User order create பண்ணிட்டு உடனே order history-ல பார்த்தால் replica-ல இல்லாமல் போகலாம்.

**Stale reads.** Reporting, analytics மாதிரி use case-க்கு ஓகே. Financial balance, inventory check மாதிரி critical read-க்கு பிரச்சனை.

**Operational complexity.** Replication lag monitor பண்ணணும். Replica fail ஆனால் auto failover logic வேண்டும். Split brain avoid பண்ணணும்.

**Cost.** Replicas run பண்ணுவது cost. ஆனால் primary scale-விட cheaper.

Failure mode: Network partition-ல replica lag அதிகமாகி minutes ஆகும். Application stale data திருப்பி கொடுக்கும். Replica primary ஆக promote பண்ணும் போது data loss ஆகும் possibility.

## 6. Practical Example

E-commerce platform.

Primary DB-ல order write, payment write, inventory update நடக்கும். 

Product catalog read, product listing, search, order history list போன்ற reads replica-களுக்கு route ஆகும்.

Application-ல request type பார்த்து:
`GET /products`, `GET /orders?userId=...` -> read replica
`POST /orders`, `PUT /inventory` -> primary

Replica-களை 2 zones-ல வைத்தால் read latency குறையும். Promotions time-ல read traffic 5x ஆனாலும் primary stable-ஆ இருக்கும்.

ஆனால் user order confirm page-ல just placed order-ஐ காட்ட வேண்டுமென்றால், அந்த read-ஐ primary-க்கு route பண்ண வேண்டும் அல்லது session pinning வேண்டும்.

## 7. Reasoning Challenge

உங்களுக்கு banking app இருக்கு. Balance inquiry 1000x அதிகம், funds transfer writes குறைவு. Compliance காரணமாக user தன் transfer-க்கு பின் balance-ஐ 2 வினாடிக்குள் சரியாக பார்க்க வேண்டும். Read replica use பண்ணலாமா? எப்படி design பண்ணுவீர்கள்? Lag என்ன impact பண்ணும்?

## 8. Key Takeaways

* Read replica என்பது read scale-க்கான architectural tool,
