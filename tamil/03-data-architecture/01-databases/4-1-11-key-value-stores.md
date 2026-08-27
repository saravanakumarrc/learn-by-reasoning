# Key-value stores

> **Learning Path:** Data Architecture
> **Section:** 4.1.11 — Databases

## Problem

உங்க e-commerce site-ல ஒவ்வொரு request-க்கும் user session, cart, feature flags, product metadata போன்றதை தேட வேண்டி வருது. ஆரம்பத்தில் ஒரு relational database போதுமானது. 

Traffic பெருகும்போது என்ன நடக்கும்? `SELECT * FROM users WHERE id = ?` போன்ற simple lookup கூட index seek, join, transaction overhead எடுக்குது. Schema change வந்தால் migration நீளும். Write throughput அதிகரிக்கும்போது row lock contention, replication lag வருது.

இன்னொரு பக்கம் cache layer-ல Redis போன்றதை பயன்படுத்தினால் latency நல்லா இருக்கு, ஆனால் persistence, scale, multi-region replication நமக்கு கட்டுப்பாடு தேவை.

இந்த painful point தான் key-value store வந்ததுக்கு காரணம்: **simple get by key, massive throughput, low latency, schema-less.**

## Mental Model

Key-value store என்பது ஒரு பெரிய distributed hash map. 

`key -> value`

அவ்வளவு தான். Value என்பது blob ஆக இருக்கலாம் - JSON, binary, string. Secondary index இல்லை, join இல்லை.

மனதில் வைக்க வேண்டியது: இது **access pattern** க்கு optimize ஆனது. Primary key access மட்டும்.

உதாரணமாக `user:12345` என்ற key க்கு `{name, email, tier}` என்ற value இருக்கு. நீங்கள் தேடுவது key மூலம் மட்டுமே.

## How It Works

Core operations மூன்று தான்: `GET key`, `PUT key value`, `DELETE key`. சில stores TTL, conditional write, atomic increment கொடுக்கும்.

Scale எப்படி?

```
Client -> Router -> Hash(key) -> Partition -> Node
```

Key ஐ hash பண்ணி partition decide ஆகும். ஒவ்வொரு node-ம் ஒரு key range / hash slot வைத்திருக்கும். Read/write path predictable ஆக இருப்பதால் latency குறைவு.

Consistency model store to store மாறும். Many choose eventual consistency for availability and partition tolerance. Strong consistency வேண்டுமெனில் quorum read/write வேண்டும்.

Data model simple ஆக இருப்பதால் storage engine-க்கு log-structured merge tree போன்றது பயன்படுத்தி sequential writes மட்டும் optimize செய்ய முடியும்.

## Architectural Reasoning

Key-value store useful ஆகும் போது:

* Access pattern key-based மட்டுமே. `GET user:123`, `GET session:abc`. Scan, filter, join தேவை இல்லை.
* Throughput முக்கியம், latency sensitive. 100k+ ops/sec வேண்டும்.
* Schema evolve அடிக்கடி. Value ஐ JSON ஆக வைத்து application side evolve பண்ணலாம்.
* Cache, session store, rate limiter, feature flag, real-time counters போன்ற use cases.

Alternative என்ன?
Relational DB: complex queries, ACID transactions தேவை என்றால் அதுவே சரி.
Document store: key lookup + flexible schema + secondary indexes வேண்டுமென்றால்.
Wide column store: ordered range scans வேண்டுமென்றால்.

Architect முடிவு எடுக்கும் கேள்வி: **எனக்கு query flexibility வேண்டுமா, அல்லது pure speed + scale வேண்டுமா?**

## Trade-offs

* **Query power vs speed.** Key-value store-ல secondary index இல்லை. `find users by email` செய்ய வேண்டுமென்றால் நீங்கள் தனியாக inverted index maintain செய்ய வேண்டும், அல்லது relational/ search engine use பண்ண வேண்டும்.
* **Data modeling complexity moves to app.** Normalization இல்லை. Denormalization, duplication, pre-computed views app side செய்ய வேண்டும். 
* **Consistency vs availability.** Partition tolerance வேண்டும் என்றால் eventual consistency ஏற்றுக்கொள்ள வேண்டும். Strong consistency கொடுத்தால் latency, cost அதிகரிக்கும்.
* **Failure modes.** Hot keys, key distribution skew. ஒரு சில keys-க்கு தான் அதிக traffic என்றால் அந்த partition overload ஆகும். TTL மற்றும் eviction policy-யை சரியாக set செய்யாவிட்டால் memory pressure வரும்.

## Practical Example

E-commerce product catalog.

Hot path: `GET product:{sku}` → name, price, stock, images. 95% requests key lookup மட்டுமே.

Architecture:
API gateway → key-value store cluster for product cache. Write path: catalog service update ஆனதும் key-value store-க்கு `PUT product:{sku}` + message queue-க்கு event publish. Consumer side cache invalidation.

Why key-value? Read latency <5ms, 200k RPS handle ஆகும், schema change செய்ய product attribute add செய்தாலும் migration இல்லை. Stock counter atomic increment support இருந்தால் மேலும் உதவும்.

Relational DB இன்னும் source of truth ஆக இருக்கும், key-value store read-optimized view.

## Reasoning Challenge

உங்க fintech app-ல payment idempotency keys maintain செய்ய வேண்டும். `idempotency_key` → `{status, response}`. 30 நாள் கழித்து auto expire வேண்டும். Traffic 50k writes/sec peak. Duplicate request வந்தால் same response return செய்ய வேண்டும்.

Relational DB, key-value store, அல்லது hybrid எதை தேர
