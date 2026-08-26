# Isolation levels

> **Learning Path:** Data Architecture
> **Section:** 4.1.8 — Databases

## 1. Problem

நீங்க ஒரு payment service-ல வேலை பார்க்கிறீங்கன்னு வச்சுக்கோங்க. 
Transaction A ஒரு account balance-ஐ update பண்ணிக்கிட்டு இருக்கு. Transaction B அதே balance-ஐ read பண்ணிக்கிட்டு இருக்கு.

இரண்டும் ஒரே நேரத்தில் ஓடும்போது என்ன பிரச்சனை வரும்?

* A இன்னும் commit ஆகல, ஆனா B அதன் intermediate value-ஐ பார்த்துட்டா?
* A ஒரு row-ஐ read பண்ணி, அதே transaction-ல மறுபடியும் read பண்ணும்போது value மாறிட்டா?
* ஒரு range query-ஐ இரண்டு முறை ஓட்றப்போ புது rows தோன்றிட்டா?

இது தான் concurrent transactions-ஐ நம்பி build பண்ணும்போது வரும் real pain. Data correct-ஆ இருக்கணும், ஆனா concurrency-ஐ block பண்ணாமலும் வேகமா இருக்கணும்.

அதுக்கு தான் isolation levels வந்தது.

## 2. Mental Model

Isolation level என்பது **ஒரு transaction இன்னொரு transaction-ஐ எவ்வளவு காணும்** என்பதை கட்டுப்படுத்தும் fence.

அதிக isolation = அதிக consistency, ஆனா அதிக waiting / locking.
குறைவான isolation = அதிக throughput, ஆனா அதிக weird reads.

நீங்க தேர்வு பண்ணுவது எந்த anomalies-ஐ allow பண்ணுவீங்க, எதை தடுப்பீங்கன்னு.

## 3. How It Works

Database ஒரு transaction-க்கு visibility rules கொடுக்குது.

* **Read Uncommitted**: ஒரு transaction இன்னொன்னோட uncommitted changes-ஐயும் பார்க்கும். Fast, ஆனா dirty read வரும்.
* **Read Committed**: மற்ற transaction commit ஆனதுக்கு அப்புறம் தான் changes தெரியும். Dirty read தடுக்கும். ஆனா non-repeatable read வரும்.
* **Repeatable Read**: transaction முழுவதும் ஒரு row-ஐ முதல் முறை பார்த்த value தான் திரும்பவும் கிடைக்கும். Snapshot பயன்படுத்துவாங்க. Phantom read வரலாம்.
* **Serializable**: strictest. Transactions ஒன்றுக்கொன்று serial-ஆ ஓடுவது போல enforce பண்ணும். Full consistency, ஆனா அதிக lock contention.

PostgreSQL default Repeatable Read, MySQL InnoDB default Repeatable Read. SQL Server default Read Committed Snapshot.

## 4. Architectural Reasoning

எப்போது இது matter ஆகும்?

* Financial ledger, inventory decrement, stock trading போன்றது: correctness முக்கியம். Serializable அல்லது Repeatable Read.
* Reporting / analytics read heavy service: fresh data வேண்டாம், speed வேண்டும். Read Committed அல்லது snapshot isolation போதும்.
* High throughput counter / click tracking: eventual correctness போதும். Read Committed போதும்.

Alternative என்ன? Application level locking, optimistic concurrency with version column, or redesign to append-only event log. ஆனா அது complexity-ஐ application-க்கு மாற்றும்.

Architect ஆக நீங்க கேட்க வேண்டியது: **எந்த anomaly-ஐ நாம் afford பண்ண முடியும்?** அதுக்கு ஏத்த isolation level-ஐ தேர்வு பண்ணுங்க.

## 5. Trade-offs

* **Consistency vs Latency**: Higher isolation = more locks / MVCC overhead = slower, timeout / deadlock அதிகம்.
* **Throughput vs Correctness**: Read Committed-ல் நிறைய concurrent reads ஓடும். Serializable-ல் contention அதிகம்.
* **Operational complexity**: Serializable phantom reads-ஐ தடுக்க deadlock retry logic வேண்டும். Team-க்கு அதை handle பண்ண தெரியணும்.
* **Failure modes**: Long running transaction + Repeatable Read = old snapshot hold பண்ணி bloat. Deadlock retry logic இல்லாம Serializable use பண்ணினா availability போய்விடும்.

## 6. Practical Example

E-commerce order placement.

Two requests same time: inventory 1 உள்ள product-க்கு order வருது.

* Read Committed-ல், transaction A inventory read = 1, transaction B inventory read = 1. இரண்டும் decrement பண்ணி -1 ஆக்கிடும். Lost update.
* Solution: Repeatable Read + SELECT ... FOR UPDATE row lock, அல்லது optimistic version check.

அதே system-ல reporting dashboard real-time sales-ஐ காட்டுது. அது long running read query. அதுக்கு Serializable வேண்டாம். Read Committed Snapshot போதும். Data 1 sec late ஆனாலும் பரவாயில்லை.

## 7. Reasoning Challenge

உங்களிடம் bank transfer service இருக்கு. 10k TPS write. மாலை 6 மணிக்கு daily statement report generate ஆகுது, அது 5 நிமிடம் ஓடும் read-only query.

Report-க்கு latest committed data வேண்டும், ஆனா transfers-ஐ block பண்ணக்கூடாது. Transfer-க்கு correctness முக்கியம், duplicate debit/credit கூடாது.

நீங்க isolation level-ஐ எப்படி set பண்ணுவீங்க? Transfer transaction-க்கும், report query-க்கும்? ஏன்?

## 8. Key Takeaways

* Isolation level என்பது **எந்த anomalies-ஐ accept பண்ணுவது** என்பதன் trade-off, free lunch இல்லை.
* Dirty read → Read Committed, Non-repeatable read → Repeatable Read, Phantom read → Serializable.
* High write contention உள்ள domain-ல default isolation போதாது, locking அல்லது optimistic concurrency தேவை.
*
