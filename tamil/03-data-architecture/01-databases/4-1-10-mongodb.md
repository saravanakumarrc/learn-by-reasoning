# MongoDB

> **Learning Path:** Data Architecture
> **Section:** 4.1.10 — Databases

## Problem

உங்க team ஒரு SaaS product build பண்ணுது. User profile-க்கு base fields இருக்கு: name, email. இப்போ product team வாரத்துக்கு ஒரு தடவை புது field கேக்குது: `preferences`, `onboarding_flow_version`, `device_metadata`, `consent_flags`.

Relational database-ல இதுக்கு என்ன ஆகும்? Migration எழுதி, table lock போட்டு, `ALTER TABLE` பண்ணி, downtime பார்க்கணும். ஒரு field optional ஆ இருந்தா கூட null column உருவாக்கணும். 

அதே நேரத்துல traffic grow ஆகுது. Write throughput அதிகரிக்கணும், read latency குறையணும். Vertical scaling-க்கு limit வருது. Read replicas add பண்ணலாம், ஆனால் schema change cost இன்னும் இருக்கு.

இந்த இரண்டு வலி சேர்ந்து தான் document model-ன் தேவை வந்தது.

## Mental Model

MongoDB-ஐ ஒரு **schemaless document store** ஆ பார்க்கணும். 

Relational-ல நீங்க table, row, column define பண்ணீங்க. MongoDB-ல நீங்க **collection**-க்குள்ள **documents** store பண்ணுறீங்க. Document என்பது JSON போன்ற BSON structure.

> ஒரு user என்பது ஒரே ஒரு document. அந்த document-க்குள்ள nested objects, arrays எல்லாம் இருக்கலாம்.

Schema enforce பண்ணாம இருந்தாலும் production-ல schema validation பயன்படுத்தலாம். Core idea: data shape application-க்கு தேவைப்படும்போது evolve ஆகும், database அதை தடுக்காது.

## How It Works

MongoDB-ல core unit `document` with `_id` primary key.

Collection என்பது documents-ன் group. Indexing B-tree based, compound indexes possible.

Replication: replica set = 3+ nodes, primary + secondary. Write to primary, async replication. Automatic failover.

Scaling: sharding. ஒரு collection-ஐ multiple shards-ல split பண்ணுறது. Shard key decide பண்ணுது எந்த document எங்க போகும். Horizontal scale out செய்ய முடியும்.

Query language MongoDB Query Language, aggregation pipeline இருக்கு. Join இல்லை, denormalization தான் pattern.

## Architectural Reasoning

MongoDB useful ஆகும் போது:

* **Schema evolves frequently.** Feature flags, product config, user profile போன்ற domain-ல fields unpredictable-ஆ வரும்.
* **Write heavy, high throughput.** IoT telemetry, event ingestion, log store.
* **Read pattern document centric.** ஒரு request-ல ஒரு user-ன் முழு profile தேவைப்படும், multiple joins தேவையில்லை.
* **Horizontal scale out must.** Data volume predictable-ஆ grow ஆகும், shard பண்ண வேண்டும்.

Relational choose பண்ணுவீங்க போது:

* Strong ACID transactions across multiple documents வேண்டும்.
* Complex joins, referential integrity critical.
* Financial ledger, order fulfillment போன்ற strict consistency தேவை.

Architect decision என்பது data model முதல் constraint-ஐ பார்க்கணும்: consistency vs flexibility, operational complexity vs development velocity.

## Trade-offs

* **Flexibility vs Data Integrity.** Schema flexible ஆ இருக்கும், ஆனால் bad data உள்ளே வரும் risk அதிகம். Validation layer application-ல அல்லது DB validation-ல கட்டாயம் வைக்கணும்.
* **No joins.** Denormalization performance கொடுக்கும், ஆனால் update amplification வரும். Same data பல documents-ல duplicate ஆகும்.
* **Consistency model.** Replica set default eventual consistency. Multi-document transactions support உண்டு, ஆனால் relational ACID-க்கு கொஞ்சம் குறைவு. Sharded cluster-ல transaction limits உண்டு.
* **Operational complexity.** Sharding key தேர்வு மிக முக்கியம். Bad shard key = hot shard, write amplification, balancer pain.

Failure mode: Network partition-ல primary failover ஆகும், ஆனால் application write concern எப்படி set பண்ணீங்க அதை பொறுத்து data loss risk வரும்.

## Practical Example

E-commerce product catalog.

PostgreSQL-ல `products`, `product_variants`, `product_attributes`, `product_images` என 4 tables join பண்ணி ஒரு product page render பண்ணணும். New attribute வந்தா migration.

MongoDB-ல ஒரு collection `products`. ஒரு document:

```
{
  _id: ObjectId,
  sku: "ABC123",
  name: "Wireless Headphones",
  price: 2990,
  variants: [{color:"black", stock:12}, ...],
  attributes: {brand:"X", warranty_months:12},
  images: [...]
}
```

Read ஒரே query-ல முடியும். Variant stock update பண்ணும்போது single document update. Shard key = `sku` அல்லது `category_id`.

RAG system-ல vector metadata store பண்ணவும் MongoDB Atlas Vector Search பயன்படுத்தலாம். Document + embedding ஒரே
