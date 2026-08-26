# Indexing

> **Learning Path:** Data Architecture
> **Section:** 4.1.5 — Databases

# Indexing — Database-ல தேடலை வேகமாக்குவது எப்படி?

## 1. Problem

உங்க system-ல 100 million rows உள்ள `orders` table இருக்கு. ஒரு query வருது:

```sql
SELECT * FROM orders WHERE customer_id = 12345 AND order_date >= '2024-01-01'
```

Index இல்லாமல் database என்ன பண்ணும்? Full table scan. ஒவ்வொரு row-ஐயும் படிச்சு, customer_id match ஆகுதான்னு பார்க்கும்.

இது சின்ன table-க்கு ஓகே. ஆனால் table பெரிதாகும்போது, I/O cost பெருகும். Latency seconds-ல இருந்து minutes-க்கு போகும். API timeout ஆகும். User wait பண்ண முடியாது.

அதே பிரச்சனை `ORDER BY`, `JOIN` என்று வரும்போதும் வரும். Sort பண்ண வேண்டும் என்றால் எல்லா row-ஐயும் memory-க்கு கொண்டு வந்து sort பண்ண வேண்டும்.

**Pain point:** Read speed தேவை. Data size வளரும். Full scan sustainable இல்லை.

## 2. Mental Model

Index என்பது book-ல உள்ள index போல.

Book-ல ஒரு topic கண்டுபிடிக்க, முழு book-ஐயும் படிக்காமல் index பார்த்து page number கிடைக்கும். அதே மாதிரி database index என்பது column value -> row pointer மேப்.

முக்கியமானது: Index data-ஐ duplicate பண்ணுவது இல்லை. Data page எங்கே இருக்குன்னு சொல்லும் pointer-ஐ வைத்திருக்கும்.

## 3. How It Works

சாதாரண database index என்பது B-Tree / B+Tree.

Key sorted order-ல வைக்கப்படும். ஒவ்வொரு node-லும் keys இருக்கும், child pointer இருக்கும்.

Query வரும்போது:
`WHERE customer_id = 12345` → B-Tree-ல customer_id-க்கு binary search மாதிரி traverse பண்ணி, relevant data page pointer-ஐ கண்டுபிடிக்கும். பிறகு அந்த page மட்டும் read பண்ணும்.

```mermaid
graph LR
A[Query: customer_id=12345] --> B[B+Tree Index]
B --> C[Row Pointer]
C --> D[Data Page]
```

Full scan = millions of pages read. Index scan = few pages read.

Range query மற்றும் ORDER BY-க்கும் index உதவும். Keys sorted இருப்பதால் sequential read ஆகும்.

Covering index என்றால் index-லேயே தேவையான columns இருக்கும். Data page-க்கே போக வேண்டாம். இது read latency-ஐ மேலும் குறைக்கும்.

## 4. Architectural Reasoning

Index எப்போது useful?

* Read heavy workload, where specific columns-ல filter / sort அடிக்கடி நடக்கும்
* Large table, high cardinality column
* Low latency SLA தேவைப்படும் API path

Constraint அது address பண்ணுவது: read latency மற்றும் I/O cost.

Alternatives:
* Full table scan - சின்ன data-க்கு மட்டும்
* In-memory structure like hash map - application level cache
* Column store / inverted index - analytics use case
* Secondary index vs primary clustered index

Architect choose பண்ணும்போது யோசிக்க வேண்டியது: எந்த column-ல query pattern consistent ஆக இருக்கு. அதற்கு மட்டும் index போடு. எல்லா column-க்கும் போட்டால் write cost அதிகமாகும்.

## 5. Trade-offs

**Read vs Write.** Index read-ஐ வேகமாக்கும், write-ஐ slow ஆக்கும். INSERT/UPDATE/DELETE நடக்கும்போது index-ஐயும் update பண்ண வேண்டும். Write amplification வரும்.

**Memory vs Disk.** Index hot data memory-ல இருந்தால் தான் fast. RAM limited. Large index disk-ல spill ஆனால் benefit குறையும்.

**Space.** Index data size-ஐ கூட்டும். Disk cost, backup cost கூடும்.

**Maintenance.** Index fragmentation, stale statistics. Rebuild / reindex தேவைப்படும்.

Failure mode: Over-indexing. Team எல்லா column-க்கும் index போட்டுவிட்டால், write throughput குறையும், deadlock chance கூடும். Operability கெட்டுபோகும்.

## 6. Practical Example

Enterprise e-commerce system. `orders` table: 200M rows.

Common queries:
1. `WHERE customer_id = ?` - customer dashboard
2. `WHERE order_date >= ? AND status = ?` - daily report
3. `JOIN orders ON user_id` - billing service

Decision:
* `customer_id` மீது B-Tree index
* `order_date, status` composite index - order முக்கியம், status filter அதற்குள்
* Primary key `order_id` already clustered index

Result: Customer dashboard latency 4 sec → 40 ms ஆகிறது.

ஆனால் order creation throughput 15% குறைகிறது. Team அதை accept பண்ணுகிறது, ஏனெனில் read 100x, write 10% of traffic.

## 7. Reasoning Challenge

உங்களிடம்
