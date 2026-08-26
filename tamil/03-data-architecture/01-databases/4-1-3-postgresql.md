# PostgreSQL

> **Learning Path:** Data Architecture
> **Section:** 4.1.3 — Databases

## 1. Problem

உங்கள் system-ல் `orders`, `customers`, `payments` மூன்றும் ஒன்றோடு ஒன்று தொடர்புடையது. ஒரு order create பண்ணும்போது customer balance update ஆகணும், inventory குறையணும், payment status set ஆகணும். 

SQLite போதாது. MySQL வச்சா JOINs நல்லா வேலை செய்யும், ஆனால் product attributes dynamic ஆக மாறுகிறது, full-text search வேணும், custom data types வேணும். NoSQL எடுத்தா consistency மற்றும் complex reporting கஷ்டம்.

**என்ன வலி?** Data integrity உறுதியாக வேண்டும், schema evolve ஆகணும், ad-hoc queries வேண்டும், ஆனால் one database-ல் எல்லாம் கிடைக்கவில்லை.

PostgreSQL இந்த வலிக்கு பதில்.

## 2. Mental Model

PostgreSQL-ஐ ஒரு **system of record** + **extensible query engine** ஆக நினைக்கவும்.

அது relational model-ஐ கடைபிடிக்கிறது, ACID transactions-ஐ கொடுக்கிறது, ஆனால் அதே நேரம் JSON, arrays, custom types, full-text search, GIS போன்றவற்றை native-ஆக support செய்கிறது.

அதனால்: rigid schema வேண்டாம் என்றாலும், relational guarantees வேண்டும் என்றாலும் PostgreSQL உங்களுக்கு வேலை செய்யும்.

## 3. How It Works

Architect-க்கு தேவையான core ideas மட்டும்:

* **MVCC**: Reader writer-ஐ block செய்யாது. ஒவ்வொரு transaction-க்கும் snapshot கொடுக்கிறது. High concurrency-க்கு இது முக்கியம்.
* **WAL + Durability**: ஒரு commit நடந்தால் Write-Ahead Log-ல் flush ஆகும். Crash வந்தாலும் data மீண்டும் வரும்.
* **Extensibility**: Types, indexes, operators எல்லாம் extend செய்யலாம். `jsonb`, `GIN index`, `ltree` போன்றவை இதன் விளைவு.
* **Planner**: Complex JOINs, subqueries-க்கு cost-based optimizer உள்ளது. Ad-hoc reporting-க்கு இது பெரிய asset.

இவை technical deep-dive இல்லை. Decision எடுக்க இந்த mental model போதும்.

## 4. Architectural Reasoning

PostgreSQL எப்போது useful?

* Strong consistency தேவை, மற்றும் transactions அடுக்கடுக்காக இருக்கும்.
* Schema evolve ஆகும், ஆனால் relational integrity வேண்டும். Foreign keys, unique constraints ஆகியவை application code-ல் enforce பண்ணுவது risky.
* Operational team small. Managed Postgres, backups, point-in-time recovery எளிது.
* Read-heavy reporting, analytical queries OLTP DB-விலேயே தேவைப்படும் போது.

Alternatives யோசிப்போம்:
MySQL: Simpler, but extensibility குறைவு. MySQL 8 இப்போது நல்லது, ஆனால் custom types, advanced indexing குறைவு.
NoSQL like MongoDB/DynamoDB: Schema flexibility + horizontal scale. ஆனால் complex JOINs, multi-document ACID கஷ்டம்.
NewSQL: CockroachDB, Yugabyte. Horizontal scale தேவைப்பட்டால் இங்கே பார்க்கலாம்.

Choose PostgreSQL when correctness + flexibility > raw write scale.

## 5. Trade-offs

* **Write scalability**: Single primary node. Vertical scaling வரைதான். 10k+ writes/sec தொடர்ந்தால் sharding அல்லது NewSQL பார்க்க வேண்டும்.
* **Read scale**: Streaming replication + read replicas வேலை செய்யும், ஆனால் replication lag உள்ளது. Strongly consistent reads வேண்டுமெனில் primary-க்கு திரும்ப வேண்டும்.
* **Operational complexity**: Vacuum, bloat, index maintenance தேவை. Long-running transactions MVCC bloat உண்டாக்கும்.
* **Cost**: Large data set + complex queries = memory தேவை. Cloud-ல் instance size விலை ஏறும்.

Failure mode முக்கியம்: Long transaction + hot row update = contention. Write amplification. Backup/restore time பெரிய dataset-ல் மணிகள் ஆகும்.

## 6. Practical Example

Enterprise order system.

Orders table relational ஆக உள்ளது: `orders(id, customer_id, total, status)`. Product attributes மாறிக்கொண்டே இருக்கிறது. ஒரு column-ஆக வைக்க முடியாது.

PostgreSQL-ல் `items` table-ல் `metadata jsonb` வைக்கிறோம். GIN index போட்டு `metadata->>'color'` search பண்ணலாம். Full-text search-க்கு `tsvector` use பண்ணி product description search பண்ணலாம்.

பணம் கட்டும் flow: ஒரு transaction-ல் order status update + payment record insert + inventory decrement. ACID இருப்பதால் ஒன்று முழுமையாக நடக்கும், இல்லையெனில் எதுவும் நடக்காது.

இங்கே PostgreSQL தேர்வு ஆகிறது ஏனெனில் consistency முக்கியம், ஆனால் schema flexibility வேண்டும்.

## 7. Reasoning Challenge

உங்களிடம் 20 microservices உள்ளன. ஒவ்வொரு
