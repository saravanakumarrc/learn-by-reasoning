# Message delivery semantics

> **Learning Path:** Distributed Systems
> **Section:** 3.1.27 — Core concepts

## 1. Problem

ஒரு order service ஒரு payment success event அனுப்புது. அந்த event inventory service-க்கும், email service-க்கும், analytics-க்கும் போகணும்.

Network-ல glitch வந்தா என்ன ஆகும்?
Message consumer-க்கு சென்றதா தெரியாமல் போகலாம். Consumer process பண்ணினது, ஆனால் ack அனுப்ப முன்னாடி crash ஆகலாம். Producer retry பண்ணும்போது அதே message இரண்டு முறை வரலாம்.

இப்போது inventory இரண்டு முறை decrement ஆகி stock negative ஆகுது. Customer-க்கு இரண்டு முறை email போயிடுது. அல்லது முதல் முறையே message lost ஆகி inventory update ஆகவே இல்லை.

Message delivery semantics என்பது இந்த uncertainty-க்கு ஒரு contract தருவது. **Producer-க்கும் consumer-க்கும் இடையே message எத்தனை முறை deliver ஆகும் என்பதற்கான guarantee.**

## 2. Mental Model

இதை தபால் டெலிவரி மாதிரி நினைச்சுக்கோங்க.

* **At-most-once**: போஸ்ட்மேன் ஒரு முறை மட்டும் முயற்சி பண்ணுவான். வீட்டில் யாரும் இல்லைன்னா திரும்ப கொண்டு வந்துடுவான். Message lost ஆகலாம், ஆனால் duplicate வராது.
* **At-least-once**: போஸ்ட்மேன் கிடைக்கும் வரை திரும்ப திரும்ப வருவான். கண்டிப்பாக கிடைக்கும், ஆனால் duplicate கிடைக்கலாம்.
* **Exactly-once**: தபால் ஒரு முறை மட்டும் கிடைக்கும், அதுவும் சரியான முறையில். இதற்கு அட்ரஸ் மீது tracking number, signature எல்லாம் வேணும்.

## 3. How It Works

**At-most-once**
Producer message அனுப்பி விடும். Ack எதிர்பார்க்காது. Fire-and-forget. Broker / network failure நடந்தால் message போய்விடும். Simple, low latency. Reliability இல்லை.

**At-least-once**
Producer message அனுப்பும், consumer ack கொடுக்கும். Ack வரவில்லை என்றால் producer retry பண்ணும். Broker-லும் offset / delivery tracking இருக்கும். இது default ஆக பல message queue-கள் தரும் guarantee. RabbitMQ, Kafka consumer group முதலியவை இந்த pattern-ல் வேலை செய்யும்.

```
Producer -> [send] -> Broker -> [deliver] -> Consumer
                 ^                         |
                 |------ retry <---------- [no ack / crash]
```

Duplicate வருவது உறுதி. அதனால் consumer idempotent ஆக இருக்க வேண்டும்.

**Exactly-once**
At-least-once + deduplication. Message-க்கு unique id கொடுத்து, consumer side-ல் processed set வைத்து duplicate-ஐ filter செய்யும். அல்லது transactional outbox + idempotent receiver. Kafka idempotent producer, two-phase commit மூலம் சில systems இதை approximate செய்கின்றன.

Exactly-once என்பது பெரும்பாலும் **exactly-once processing** என்ற mental model-ல் தான் நடக்கும். True exactly-once distributed system-ல் கிடைப்பது கடினம்.

## 4. Architectural Reasoning

எந்த guarantee வேண்டும் என்பது business impact-ஆல் முடிவு ஆகும்.

* Notification, email, push: Duplicate பெரிய பிரச்சனை இல்லை. At-least-once போதும். Consumer idempotent ஆக இருந்தால் போதும்.
* Payment, financial ledger, inventory decrement: Duplicate fatal. Exactly-once semantics தேவை.
* Real-time metrics, logs: At-most-once கூட ஏற்றுக்கொள்ளலாம். Loss சில சதவீதம் acceptable.

Constraint என்ன?
Latency vs reliability vs complexity. At-least-once latency அதிகப்படுத்தும். Retry backoff, ack wait. Exactly-once என்பது state store, deduplication table, idempotency key management என்ற operational overhead கொண்டு வரும்.

## 5. Trade-offs

**Reliability vs Latency**
At-least-once / exactly-once க்கு ack மற்றும் retry தேவை. அது latency அதிகரிக்கும். At-most-once low latency, high loss risk.

**Duplicate handling cost**
At-least-once என்றால் consumer idempotent ஆக இருக்க வேண்டும். Database unique constraint, idempotency key table, upsert logic எல்லாம் வேண்டும். இது development மற்றும் DB cost.

**Operational complexity**
Exactly-once க்கு distributed transaction அல்லது outbox pattern தேவை. Failure modes அதிகம்: duplicate detection window எவ்வளவு நேரம் வைக்க வேண்டும்? Message id collision? State storage எங்கே?

**False sense of safety**
பல engineers exactly-once என்று நினைத்து at-least-once system-ல் non-idempotent consumer போட்டு விடுவார்கள். அது பின்னர் data corruption கொண்டு வரும்.

## 6. Practical Example

Order placed -> `order.created` event publish.

Inventory service: stock decrement. Consumer idempotent இல்லை என்றால் duplicate message வந்தால் stock -2 ஆகும். இங்கே `orderId` மீது idempotency key வைத்து `INSERT ... ON CONFLICT DO NOTHING` பண்ணலாம்.

Email service: duplicate email ஒரு UX problem. But not critical. Simple at-least-once போ
