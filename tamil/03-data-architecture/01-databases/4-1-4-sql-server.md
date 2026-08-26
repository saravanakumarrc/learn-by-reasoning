# SQL Server

> **Learning Path:** Data Architecture
> **Section:** 4.1.4 — Databases

## 1. Problem

ஒரு enterprise system-ல் orders, payments, inventory, customer master எல்லாம் ஒன்றோடு ஒன்று link ஆகி இருக்கும். ஒரு order create ஆகும் போது stock குறையணும், payment ledger-ல் entry வரணும், அதே transaction-ல் fail ஆகக்கூடாது.

File system-ல் அல்லது custom store-ல் இதை நீங்களே manage பண்ண முயற்சித்தால், partial write, lost update, inconsistent read மாதிரி பிரச்சினை வரும். Team scale ஆகும் போது, multiple services ஒரே data-வை touch பண்ணும். 

அதனால் தேவைப்படுவது: **strong consistency, ACID transactions, declarative query, மற்றும் operations team-க்கு mature tooling**. இந்த பிரச்சினை தான் SQL Server போன்ற relational database-ஐ தேவைப்படுத்துகிறது.

## 2. Mental Model

SQL Server என்பது ஒரு relational engine + storage + query optimizer + high availability layer ஆகியவற்றின் combo.

மனதில் வைத்துக்கொள்ள வேண்டியது:

> SQL Server = ACID guarantees கொடுக்கும் single source of truth, T-SQL மூலம் விதிகளை enforce செய்யும், Windows / .NET ecosystem-ல் native ஆக இணையும்.

இது document store அல்ல. Join-heavy, transactional workload-க்கு பொருத்தமானது.

## 3. How It Works

அடிப்படை mechanism புரிந்தால் போதும்.

Writes எல்லாம் write-ahead log-க்கு முதலில் போகும். Buffer pool memory-ல் data cache ஆகி, பின் disk-க்கு flush ஆகும். Lock manager மற்றும் isolation levels மூலம் concurrent access control செய்யப்படுகிறது.

Query optimizer statistics பார்த்து execution plan தேர்வு செய்யும். Indexes, Columnstore, in-memory OLTP போன்ற feature-கள் workload-க்கு ஏற்ப performance tune செய்ய உதவும்.

High availability-க்கு Always On Availability Groups இருக்கு. Primary replica writes எடுக்கும், secondary replica read-only scale out செய்யும், automatic failover செய்யும்.

## 4. Architectural Reasoning

SQL Server தேர்வு செய்யும் போது நீங்கள் பார்ப்பது ecosystem மற்றும் operational constraints.

**When it helps:**

* App stack .NET / ASP.NET Core ஆக இருந்தால், integrated Windows Authentication, Active Directory groups, connection pooling எல்லாம் natural ஆக work ஆகும்.
* Finance, ERP, Healthcare போன்ற audit, compliance, row-level security தேவைப்ப
