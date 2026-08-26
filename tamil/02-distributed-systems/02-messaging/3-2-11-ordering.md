# Ordering

> **Learning Path:** Distributed Systems
> **Section:** 3.2.11 — Messaging

## 1. Problem

நீங்க ஒரு e-commerce platform build பண்ணுறீங்க. Order service ஒரு event publish பண்ணுது: `OrderCreated`, `PaymentSuccess`, `ItemShipped`.

Inventory service, Notification service, Accounting service எல்லாம் அந்த events-ஐ consume பண்ணணும்.

நெட்வொர்க் jitter, retry, multiple partitions, multiple consumers — இதனால் events வரும் வரிசை மாறிடும்.

`PaymentSuccess` முதல் வந்து, `OrderCreated` பின்னால் வந்தா என்ன ஆகும்? Inventory நிராகரிக்குமா? Notification தப்பா அனுப்புமா?

இதுதான் ordering பிரச்சனை. System-ன் state ஒரு sequence-ஐ depend பண்ணும்போது, event order மாறினால் business invariant break ஆகும்.

## 2. Mental Model

Ordering என்பது **causality-ஐ preserve பண்ணுவது**.

ஒரு key-க்குள், events-க்கு ஒரு logical sequence இருக்கு. அதே sequence-ல தான் process ஆகணும்.

மூன்று level இருக்கு:

* **No ordering**: எந்த guarantee இல்லை
* **Per-key / Per-partition ordering**: ஒரே partition / key-க்குள் FIFO
* **Total ordering**: எல்லா consumers-க்கும் global order

நீங்க எப்போதும் total order வேண்டாம். பெரும்பாலும் per-key order போதும்.

## 3. How It Works

Message broker-ல் ordering உறுதி செய்ய மூன்று விஷயங்கள் வேண்டும்.

**Partitioning**: ஒரு key-க்கான எல்லா events-ஐயும் ஒரே partition-க்குள் வைக்கிறோம். Kafka-ல் partition key, RabbitMQ-ல் single queue.

**Sequence number / offset**: ஒவ்வொரு message-க்கும் monotonically increasing offset. Consumer அதை track பண்ணி, gap இருந்தா wait பண்ணும்.

**Single consumer per partition**: ஒரு partition-ஐ ஒரே consumer instance process பண்ணும். Parallelism இழக்காமல் ordering காப்பாற்ற.

Producer retry பண்ணினாலும், idempotent producer + deduplication வேண்டும். இல்லைனா duplicate வந்து order confuse ஆகும்.

## 4. Architectural Reasoning

Ordering தேவைப்படும் போது மட்டும் தான் கட்டுப்படி.

எப்போ use பண்ணணும்?
* State machine transition: `Created -> Paid -> Shipped`. Step skip ஆகக்கூடாது.
* Financial ledger: debit/credit sequence முக்கியம்.
* Same aggregate-ன் updates: ஒரு user profile-க்கான updates.

எப்போ தேவையில்லை?
* Independent events: different orders, different users. Parallel process பண்ணலாம்.
* Eventual consistency மட்டும் போதும்.

Alternatives:
* **Application-level sequencing**: consumer-ல் buffer வைத்து reorder. Latency அதிகம்.
* **Synchronous call**: ordering தானாக வரும், ஆனால் coupling + availability குறையும்.
* **Single partition**: strict ordering, ஆனால் throughput limit.

Architect decide பண்ணும்போது கேட்க வேண்டியது: "இந்த key-க்கு order மாறினால் business தப்பா போகுமா?" ஆமான்னா per-key ordering must.

## 5. Trade-offs

**Ordering vs Throughput**: Ordering க்கு parallelism குறையும். ஒரே partition-ல் எல்லாம் serial ஆகும். High throughput வேணும்னா partition அதிகம், ஆனால் ordering scope குறையும்.

**Ordering vs Latency**: Slow consumer முன்னால் வந்தால், அடுத்த message wait ஆகும். Head-of-line blocking வரும்.

**Total ordering vs Scalability**: Global order வேணும்னா single writer / single partition தேவை. Scale ஆகாது.

**Failure modes**: Partition leader fail ஆனா, replay window-ல் gap வரும். Consumer crash ஆனா offset commit தாமதம் ஆனால் duplicate process ஆகும்.

ஒவ்வொரு ordering guarantee-க்கும் ஒரு cost இருக்கு.

## 6. Practical Example

Bank account service.

`Deposit 100`, `Withdraw 50`, `Withdraw 60` events publish ஆகுது.

Account balance ஒரு aggregate. Order மாறினால் overdraft detection தப்பும்.

Design: accountId-ஐ partition key ஆக்கு. Kafka topic `account.events` with 32 partitions. ஒவ்வொரு accountId ஒரே partition-ல் மட்டும் போகும்.

Consumer group-ல் ஒவ்வொரு partition-ஐ ஒரே consumer handle பண்ணும். Offset commit பண்ணுவது at-least-once. Idempotent apply logic வைத்து
