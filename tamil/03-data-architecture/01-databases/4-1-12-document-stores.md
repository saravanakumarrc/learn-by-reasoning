# Document stores

> **Learning Path:** Data Architecture
> **Section:** 4.1.12 — Databases

## Document Stores — schema ஐ மெனக்கெடாமல் grow பண்ண வேண்டிய நேரம்

### 1. Problem

நீங்க ஒரு product catalog service பண்ணிக்கிட்டு இருக்கீங்க. Relational database-ல `products` table இருக்கு. 

Version 1-ல `id, name, price, category` போதும்.

Version 2-ல marketplace வந்ததும் `seller_id, commission_rate` வேணும்.
Version 3-ல international launch. `price` இப்போ currency உடன் வரணும்.
Version 4-ல some products-க்கு `specs` JSON வேணும், some-க்கு `attributes` array வேணும்.

ஒவ்வொரு முறையும் `ALTER TABLE`, migration script, downtime, backward compatibility, null columns... team-உம் slow ஆகுது. 

இன்னொரு பக்கம் user profile service. ஒரு user-க்கு preferences, settings, device tokens, social links. எல்லாம் வெவ்வேறு shape-ல வளருது. Join பண்ணி வாங்குவது latency ஆகுது.

**Pain point:** Schema evolution cost > data model flexibility need. Relational model-ன் strong schema, ACID transactions நல்லது, ஆனால் fast iteration, heterogeneous documents-க்கு painful ஆகுது.

### 2. Mental Model

Document store-ல ஒரு collection என்பது `documents` -ன் குவியல்.

ஒவ்வொரு document-ம் self-contained JSON-like blob. `_id` + arbitrary fields.

```json
{
  "_id": "prod_123",
  "name": "Phone X",
  "price": 39900,
  "specs": { "ram": "8GB", "storage": "256GB" },
  "tags": ["new", "sale"]
}
```

அடுத்த document-க்கு `specs` இல்லாமல் `variants` இருக்கலாம். Schema enforce பண்ண வேண்டாம். Application layer-ல validate பண்ணிக்கலாம்.

Mental model: **Store by document, retrieve by document, evolve by document.**

### 3. How It Works

Collection = bucket of documents. Primary key-ல get, secondary index-ல query.

MongoDB, Couchbase, Firestore இப்படித்தான் வேலை செய்யும்.

Write path: document முழுவதையும் write பண்ணு. Partial update possible.

Read path: `_id` தெரிந்தால் O(log n) fetch. Field-based index இருந்தால் filter பண்ணலாம்.

No joins. Related data-ஐ embed பண்ணு அல்லது reference id வைத்து separate collection-ல வை. Denormalization encouraged.

### 4. Architectural Reasoning

Document store useful ஆகும் constraints:

* **Schema volatility:** Product, content, user profile மாதிரி fields அடிக்கடி மாறும்.
* **Heterogeneous data:** Same collection-ல வெவ்வேறு shape documents.
* **Low-latency read of whole aggregate:** One read-ல ஒரு user profile முழுவதையும் வாங்க வேண்டும்.
* **Horizontal scale need:** Write throughput அதிகம், sharding natural.

Alternatives:

* Relational + JSON column: schema flexibility கொஞ்சம் கிடைக்கும், ஆனால் query, indexing கட்டுப்படி குறைவு.
* Key-value store: structure இல்லை. Query முடியாது.
* Column store: analytics-க்கு நல்லது, OLTP-க்கு இல்லை.

Architect choose பண்ணும்போது கேட்க வேண்டியது: **நமக்கு cross-document transactions, strong consistency வேணுமா?** இல்லை, document-level isolation போதுமா?

### 5. Trade-offs

* **Flexibility vs Query power.** Document store flexible ஆனால் relational-போல complex joins, multi-document ACID transactions இல்லை அல்லது கட்டுப்படி குறைவு. Reporting heavy workload painful ஆகும்.
* **Denormalization vs Data duplication.** Embed பண்ணினால் read fast, update complex. Reference வைத்தால் consistency manage செய்ய வேண்டும்.
* **Eventual consistency & sharding.** Horizontal scale எளிது, ஆனால் distributed writes-ல read-after-write guarantee கவனம் தேவை.
* **Failure modes:** Unbounded document growth, large array fields, missing indexes lead to collection scan. Hot shard if key distribution bad.

### 6. Practical Example

E-commerce product catalog.

Relational-ல `products`, `product_variants`, `product_attributes` tables join செய்ய வேண்டும். Page load 3-4 queries.

Document store-ல ஒரு document:

```json
{
  "_id": "prod_123",
  "name": "Phone X",
  "base_price": 39900,
  "variants": [
    {"sku": "X-BLK-128", "color":"black", "stock": 120},
    {"sku": "X-WHT-256", "color":"white", "stock": 45}
  ],
  "metadata": { "brand": "A", "launched_at": "2024-01-10" }
}
```

One read = full page data. New field `eco_rating` வந்தால் code deploy பண்ணி, பழைய documents-க்கு default கொடுக்கலாம். Migration zero downtime.

Operational trade-off: Inventory update-க்கு `variants` array-ல atomic update தேவை. அது work
