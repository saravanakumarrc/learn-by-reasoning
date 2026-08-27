# NoSQL

> **Learning Path:** Data Architecture
> **Section:** 4.1.9 — Databases

## Problem

உங்களிடம் ஒரு மாதத்திற்கு 10 million users வரும் ஒரு product catalog service இருக்கு. ஒவ்வொரு product-க்கும் 50 fields இருக்கு. ஆனால் ஒவ்வொரு merchant வித்தியாசமான custom attributes சேர்க்கிறார். 

Relational DB-ல் இதை வைத்தால் என்ன ஆகும்?
- Schema change-க்கு migration வேண்டும். `ALTER TABLE` பெரிய table-ல் நேரம் எடுக்கும், downtime வரும்.
- Write throughput அதிகமாகும் போது single primary node bottleneck ஆகும். Vertical scale மட்டுமே செய்ய முடியும்.
- Read pattern mostly key-based: `product_id` கொடுத்தால் full object தேவை. JOIN அவசியமில்லை.

இங்கே problem என்ன? **Schema rigidity + scale முறை + access pattern mismatch**. இதுதான் NoSQL-க்கு வழிவகுத்தது.

## Mental Model

NoSQL என்பது "SQL இல்லாதது" அல்ல. **Not only SQL**.

ஒரே data model அல்ல. 4 முக்கிய மாடல்கள்:

* **Key-Value:** `key -> value` . Cache போல். Redis.
* **Document:** JSON-like document. `product_id` -> `{name, price, attributes: {...}}`. MongoDB.
* **Wide-Column:** Row = key, columns dynamically added. Time series, Cassandra.
* **Graph:** Nodes + edges. Relationships முக்கியம். Neo4j.

முக்கிய mental model: **Data model-ஐ access pattern-க்கு ஏற்றாற்போல் தேர்வு செய்வது. Normalization குறைவு, denormalization அதிகம்.**

## How It Works

RDBMS ஒன்று consistency-ஐ முன்னுரிமை கொடுத்து design ஆகியிருக்கு. NoSQL systems பெரும்பாலும் **CAP theorem-ல் availability + partition tolerance**-ஐ தேர்வு செய்கின்றன.

எனவே:
- Horizontal scale எளிது: Data-ஐ hash partition பண்ணி பல nodes-க்கு spread பண்ணலாம்.
- Schema flexible: Document-க்கு new field சேர்த்தால் migration தேவையில்லை.
- Eventual consistency சாத்தியம்: Write fast, read later converge.

Implementation simple ஆக இருக்கும்: single table, no JOIN, primary key lookup மிக வேகம்.

## Architectural Reasoning

NoSQL useful ஆகும் போது:

* **Write throughput அதிகம், low latency தேவை.** 100k writes/sec செய்ய வேண்டும்.
* **Schema மாறிக்கொண்டே இருக்கும்.** Product attributes, user profile fields.
* **Access pattern key-based.** `get(user_id)` போன்றது.
* **Global distribution தேவை.** Multiple regions-ல் low latency read.

Alternatives என்ன?
- RDBMS + sharding manually. Operational complexity அதிகம்.
- NewSQL: CockroachDB, Spanner. Strong consistency + scale. ஆனால் cost அதிகம்.

Architect ஏன் NoSQL தேர்வு செய்வார்? **Scale constraint-ஐ solve பண்ண, team velocity-ஐ maintain பண்ண.** Schema change-க்காக release போட வேண்டாம்.

## Trade-offs

1. **Consistency vs Availability.** NoSQL பெரும்பாலும் eventual consistency. Banking transaction-க்கு ஒத்துவராது.
2. **Query flexibility.** Ad-hoc JOIN, complex aggregate கடினம். Data model-ஐ query pattern-க்கு ஏற்ப முன்கூட்டியே design செய்ய வேண்டும்.
3. **Operational complexity.** Data modeling தப்பாக ஆனால் migration கஷ்டம். RDBMS-ல் ORM உதவும், இங்கே application logic-ல் handling வரும்.
4. **Transactional guarantees.** Multi-document ACID transactions சில systems-ல் limited.

Failure mode முக்கியம்: Network partition ஆனால் writes பல replicas-ல் diverge ஆகலாம். Conflict resolution strategy தேவை.

## Practical Example

User Profile Service.

Requirement: 50M users, profile read 10x write, profile fields dynamic based on country.

Choice: Document store like MongoDB / DynamoDB.

Design:
`user_id` = partition key
Document = `{name, email, preferences, locale_specific_fields}`

Read path: `GET /users/{user_id}` → single key lookup, <10ms.
Write path: Partial update of document.

இங்கே relational DB வைத்திருந்தால் 30 tables JOIN வேண்டும். NoSQL-ல் one read.

Trade-off: `find users where age > 30` போன்ற query தேவைப்பட்டால் secondary index அல்லது separate read model வேண்டும்.

## Reasoning Challenge

உங்களிடம் ஒரு payment ledger system இருக்கு. Strong consistency, audit, multi-row transaction தேவை. அதே நேரம் 1B rows/நாள் transaction volume. 

இங்கே NoSQL Document store use பண்ணுவீர்களா? ஏன்/ஏன் இல்லை? Alternative என்ன?

## Key Takeaways

* NoSQL என்பது scale + flexible schema + specific access pattern க்கான தீர்வு, RDBMS replacement அல்ல.
* Data model-ஐ access pattern-க்கு ஏற்ப தேர்வு செய், JOIN-ஐ avoid செய்.
* CAP-ல் availability தேர்வு செய்வது eventual consistency-ஐ கொண்டுவரும். அதை accept செய்ய முடியுமா என்பதே முடிவு.
* ஒவ்வொரு NoSQL தேர்வும் query flexibility-ஐ குறைத்து, operational simplicity-ஐ கொடுக்கும்.
