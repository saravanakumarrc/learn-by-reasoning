# Wide-column databases

> **Learning Path:** Data Architecture
> **Section:** 4.1.13 — Databases

## 1. Problem

ஒரு large-scale service-ல user profile ஒன்றுக்கு 2000-க்கும் மேற்பட்ட attributes இருக்கு. Analytics, personalization, third-party integrations எல்லாம் சேர்ந்து column அதிகமாகிக்கிட்டே போகுது. ஆனால் ஒரு single request-க்கு தேவைப்படுவது வெறும் 10-20 columns தான்.

Relational database-ல இதை செய்தால் என்ன ஆகும்?

* `ALTER TABLE` பண்ணி column add செய்ய வேண்டும். Schema change = lock, downtime, migration.
* Row மிக wide ஆகி page read அதிகம். Sparse data-க்கு நிறைய wasted space.
* Horizontal scale பண்ணும்போது sharding logic நாமளே manage பண்ண வேண்டும். Hotspot வரும்.
* Write throughput அதிகமானால் single node bottleneck ஆகும்.

இதுவே painful ஆனதும், wide-column database தேவைப்பட்ட காரணம்.

## 2. Mental Model

Wide-column database என்பது **row key மூலம் organize பண்ணப்பட்ட, columns dynamic ஆக grow பண்ணக்கூடிய store**.

நினைத்துக்கொள்ள:

`row key` → ஒரு user_id / device_id போல primary identifier
`column family` → ஒரு logical group, உதாரணமாக `profile`, `events`, `metrics`
ஒவ்வொரு column-க்கும் `column key` + `value` + `timestamp` உண்டு.

Row ஒன்று ஒரு shelf, column families ஒரு section, columns ஒரு shelf-ல உள்ள books. ஒரு row-ல தேவையான column மட்டும் இருக்கும், மற்றவை இருக்காது. Sparse என்பது natural.

## 3. How It Works

Data disk-ல இப்படி store ஆகும்:
`row key` → sorted columns inside each column family → sorted by column key, timestamp versioning உண்டு.

Cassandra, Bigtable, HBase போன்ற systems இதை distributed ஆக செய்கின்றன.
Row key range படி data nodes-க்கு partition ஆகும். ஒரு node-க்கு ஒரு token range.

Read/write path:
Client request வந்தால் coordinator node row key-ன் hash/ range பார்த்து எந்த replica set-ல இருக்கு என்று தெரிந்து, partition க்கு direct IO போகும். Disk layout row-local ஆக இருப்பதால் seek குறைவு.

Schema என்பது almost non-existent. Column add செய்ய `CREATE TABLE` மாற்ற தேவையில்லை. Application புது column key வைத்து எழுத ஆரம்பித்தால் போதும்.

## 4. Architectural Reasoning

எப்போது wide-column பயன்படும்?

* **Access pattern predictable ஆக row key மூலம்**: `GET /user/{id}` மாதிரி point lookups, range scans on column key.
* **Data sparse and schema evolves fast**: New feature flag, new metric வந்தால் migration இல்லாமல் போக வேண்டும்.
* **High write throughput, append heavy**: Time series events, logs, IoT telemetry.
* **Horizontal scale முக்கியம்**: 10M+ rows, TBs of data, availability முக்கியம்.

Alternative என்ன?
Relational sharded = strong consistency, complex queries கிடைக்கும், ஆனால் operational overhead அதிகம்.
Document store = flexible schema, ஆனால் nested updates, wide sparse columns-க்கு less efficient.
Key-value = simple, ஆனால் column grouping, timestamp versioning இல்லை.

Architect choose பண்ணும்போது trade-off பார்க்கிறார்: query flexibility vs write scale and schema flexibility.

## 5. Trade-offs

* **Query model limited**: Ad-hoc joins, secondary indexes கடினம். You design table around read pattern. Wrong model = full scan.
* **Consistency model**: Most wide-column systems tunable consistency. Cassandra default eventual consistency. Strong consistency வேண்டுமானால் latency and availability குறையும்.
* **Operational complexity**: Data modeling மிக முக்கியம். Row key design தவறினால் hotspot, uneven distribution, hot partitions வரும். Compaction
