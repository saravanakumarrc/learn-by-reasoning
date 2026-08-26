# Transactions

> **Learning Path:** Data Architecture
> **Section:** 4.1.7 — Databases

## Problem

ஒரு e-commerce order place பண்ணும்போது என்னென்ன நடக்கணும்?

- wallet-ல இருந்து amount debit பண்ணனும்
- order table-ல row create பண்ணனும்
- inventory-ல stock குறைக்கணும்

மூன்றும் ஒன்னா நடக்கணும். ஒன்னு மட்டும் நடந்துட்டா என்ன ஆகும்?

Payment success ஆச்சு, order create ஆகல. Customer காசு போச்சு, order இல்ல.

அல்லது inventory குறைஞ்சுடுச்சு, payment fail ஆயிடுச்சு. Stock waste.

Network glitch, timeout, service crash எல்லாம் நடக்கும். Partial update வந்துட்டா data corrupt ஆகும். Support ticket, refund, trust loss.

இந்த partial failure-ஐ தடுக்க தான் transaction concept வந்துச்சு.

## Mental Model

Transaction என்பது ஒரு logical unit of work. அது **all-or-nothing**.

ஒரு குறிப்பிட்ட boundary-க்குள்ள நடக்கும் எல்லா changes-உம் ஒன்னா commit ஆகும், இல்லையெனில் எதுவும் persist ஆகாது. Rollback ஆகும்.

Bank ATM-ல cash withdraw பண்ணும்போது balance குறைக்கிறது + cash dispense பண்ணுவது ஒன்னா நடக்கணும். நடுவுல power cut ஆனா பணம் போகக்கூடாது. அதே mental model தான் database-லும்.

## How It Works

Single database-ல transaction என்பது basic-ஆ:

1. **Begin** - ஒரு session start ஆகும்
2. Changes memory-ல stage ஆகும், persistent ஆக இல்லை
3. **Commit** ஆனால் write-ahead log-ல write செய்து disk-க்கு flush பண்ணி changes visible ஆக்கும்
4. **Rollback** ஆனால் staged changes discard ஆகும்

ACID என்பது இதை guarantee பண்ணும் 4 properties:

- **Atomicity**: all or nothing
- **Consistency**: valid state-ல இருந்து valid state-க்கு மட்டும் மாறும்
- **Isolation**: concurrent transactions interfere பண்ணாது. Read committed, repeatable read, serializable போன்ற isolation levels இதை control பண்ணும்
- **Durability**: commit ஆனதும் crash ஆனாலும் data survive ஆகும்

Implementation-ல locks, MVCC, undo log, write-ahead log பயன்படுத்துவார்கள். ஆனால் architect-க்கு தேவை இந்த guarantees எப்போது வேண்டும் என்பது தான்.

## Architectural Reasoning

Single service, single database என்றால் transaction எளிது. `BEGIN; UPDATE ...; INSERT ...; COMMIT;`

Problem வருவது distributed system-ல.

Order service, Payment service, Inventory service என்று 3 microservices, 3 databases. ஒரே transaction-ஐ cross service-க்கு எடுத்துப் போக முடியுமா?

இங்கே options:

1. **Monolith + single DB transaction**: எளிது, strong consistency. ஆனால் scalability, team autonomy குறையும்
2. **Distributed transaction - 2PC**: Prepare + Commit phase. Strong consistency கிடைக்கும். ஆனால் latency அதிகம், coordinator single point of failure, availability குறையும்
3. **Saga pattern**: Local transaction + compensating actions. Eventually consistent. High availability, scalable. ஆனால் complexity அதிகம்

Architect தேர்வு செய்வது constraint பார்த்து தான்:
- Consistency எவ்வளவு முக்கியம்? Money move என்றால் strong
- Latency எவ்வளவு tolerate பண்ணலாம்?
- Team size, operational complexity?

## Trade-offs

**Strong ACID vs Availability**
2PC use பண்ணினால் network partition வந்தால் transaction hang ஆகும். Availability குறையும். Saga use பண்ணினால் system up இருக்கும், ஆனால் intermediate inconsistent state தெரியும்.

**Isolation vs Performance**
Serializable isolation சிறந்த consistency தரும். ஆனால் lock contention, throughput குறையும். Read Committed எடுத்தால் performance வரும், phantom read risk வரும்.

**Consistency vs Coupling**
Distributed transaction க்கு services tightly coupled ஆகும். Saga loosely coupled, ஆனால் failure modes அதிகம். Compensating transaction fail ஆனால் manual intervention வேண்டும்.

Failure mode முக்கியம்: timeout ஆன transaction retry பண்ணும்போது idempotency இல்லாமல் duplicate payment நடக்கும். Transaction boundary decide பண்ணும்போது retry safety-யும் பார்க்கணும்.

## Practical Example

Bank transfer: A -> B 1000 INR

Monolith DB-ல:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = A;
UPDATE accounts SET balance = balance + 1000 WHERE id = B;
COMMIT;
```

இது atomic. Power cut வந்தாலும் balance correct இருக்கும்.

இதை microservices-க்கு பிரித்தால்:

Transfer service A account debit பண்ணி event publish பண்ணும். B service event consume பண்ணி
