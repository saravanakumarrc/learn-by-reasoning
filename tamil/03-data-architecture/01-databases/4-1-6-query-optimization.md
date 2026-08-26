# Query optimization

> **Learning Path:** Data Architecture
> **Section:** 4.1.6 — Databases

### 1. Problem

உங்கள் service ஒரு simple query ஓடுகிறது:
```sql
SELECT * FROM orders WHERE customer_id = 12345 AND status = 'PAID' ORDER BY created_at DESC LIMIT 10
```
Development-ல 50 ms. Production-ல 8 seconds. Same code.

என்ன ஆச்சு? Data 10x ஆகி இருக்கு. `orders` table இப்போ 200M rows. Query எப்படி data எடுக்கிறது என்பதே மாறி விட்டது.

இதை fix பண்ண `SELECT *` ஐ `SELECT id, created_at` ஆக்கலாம். `status` filter மாற்றலாம். `LIMIT` எடுக்கலாம். ஆனால் core பிரச்சனை என்ன? **Database-க்கு ஒரே logical result-க்கு பல physical வழிகள் இருக்கு, அது தானாக சரியானதை தேர்ந்தெடுக்க முயற்சிக்கிறது.**

Query optimization என்பது அந்த தேர்வை சரியாக்குவது.

### 2. Mental Model

Database ஒரு librarian மாதிரி. உங்களுக்கு "நேற்று பணம் கட்டிய 12345 கஸ்டமரின் கடைசி 10 orders" வேண்டும்.

Librarian-க்கு இரண்டு வழி:
* **Sequential scan**: அனைத்து புத்தகங்களையும் ஒவ்வொன்றாக புரட்டி பார்க்க.
* **Index scan**: customer_id க்கான index-ல் தேடி, அதற்கு பிறகு தேவையான rows மட்டும் எடுக்க.

எந்த வழி வேகமானது என்பது data distribution, row size, index இருக்கிறதா என்பதை பொறுத்தது. Query optimizer தான் அந்த cost-ஐ estimate பண்ணி plan தேர்ந்தெடுக்கிறது.

### 3. How It Works

Query run ஆகும்போது DB இப்படி சிந்திக்கிறது:

1. **Parse & Rewrite**: SQL-ஐ logical plan ஆக்கு.
2. **Plan Generation**: ஒரே query-க்கு பல alternative physical plans உருவாக்கு. `nested loop join` vs `hash join`, `index scan` vs `sequential scan`.
3. **Cost Based Choice**: Statistics பார்த்து cost estimate பண்ணு. `cardinality`, `selectivity`, `page reads`, `CPU`.
4. **Execute**: தேர்ந்த plan-ஐ run பண்ணு.

```
User Query -> Parser -> Logical Plan -> Optimizer -> Execution Plan -> Executor
                         ^ statistics
```

முக்கியம்: Optimizer perfect அல்ல. Statistics stale ஆனால் தவறான plan தேர்ந்தெடுக்கும்.

### 4. Architectural Reasoning

Query optimization தேவைப்படும் சூழல்:

* **Read-heavy workload** with growing data. Scan cost linearly increase ஆகும்.
* **Ad-hoc reporting / analytics** queries எங்கே filters unpredictable.
* **Low latency SLA** உள்ள APIs, p95 < 100ms வேண்டும்.

Architect ஆக நீங்கள் செய்ய வேண்டியது optimizer-க்கு உதவுவது, அதை override பண்ணுவது அல்ல.

Options உங்களிடம்:
* **Index design**: query pattern-க்கு ஏற்ற composite index.
* **Schema & Query rewrite**: `SELECT *` தவிர்க்க, proper filtering, avoid functions on indexed column.
* **Partitioning**: hot data separate, prune partitions.
* **Materialized view / summary table**: pre-compute expensive aggregation.
* **Caching layer**: Redis for read heavy, rarely changing data.

Decision எப்போது? Data size > memory, மற்றும் query pattern stable ஆனால் index invest பண்ணலாம். Query pattern தொடர்ந்து மாறும், then caching / read replica முன்னுரிமை.

### 5. Trade-offs

* **Read vs Write**: Index read-ஐ வேகப்படுத்தும், write-ஐ மெதுவாக்கும். INSERT/UPDATE/DELETE க்கு index maintenance cost உண்டு. High write throughput system-ல அதிக index = write amplification.
* **Optimizer reliance vs hinting**: Optimizer-ஐ நம்புவது maintainable. Force index hint கொடுத்தால் data distribution மாறும்போது plan degrade ஆகும்.
* **Plan stability vs adaptability**: Statistics refresh செய்யாவிட்டால் bad plan cache ஆகி இருக்கும். Auto analyze cost உண்டு.
* **Complexity**: Composite index order matters. `customer_id, status, created_at DESC` vs `status, customer_id`. தவறான order selective column முன்னால் இருக்க வேண்டும்.

Failure mode: Stale statistics + sudden data skew. Optimizer நினைத்தது 100 rows, உண்மையில் 10M rows. Nested loop join disaster.

### 6. Practical Example
