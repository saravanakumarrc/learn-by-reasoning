# Two-phase commit

> **Learning Path:** Distributed Systems
> **Section:** 3.1.15 — Core concepts

### 1. Problem

உங்களுக்கு ஒரு e-commerce order flow இருக்கு. Order create பண்ணும்போது மூன்று விஷயம் ஒரே சேர நடக்கணும்:

* Order DB-ல order record create ஆகணும்
* Inventory service-ல stock reduce ஆகணும்
* Payment service-ல payment capture ஆகணும்

இதில் ஒன்று மட்டும் success ஆகி மற்றது fail ஆனால் என்ன ஆகும்? Customer-க்கு charge ஆகி product இல்லாமல் போகும். அல்லது stock போய் order இல்லாமல் போகும்.

Single database-ல இதை ACID transaction-ல handle பண்ணலாம். ஆனால் distributed system-ல services வெவ்வேறு databases, வெவ்வேறு nodes-ல இருக்கும். Network failure, timeout, crash எல்லாம் வரும்.

> **Problem என்ன?** Multiple participants-ல atomic commit வேண்டும். All or nothing. ஆனால் network unreliable.

இதுதான் two-phase commit வந்ததுக்கு காரணம்.

### 2. Mental Model

2PC என்பது ஒரு coordinator + participants என்ற model.

Coordinator ஒருத்தன் இருப்பான். Participants என்பது transaction-ல இருக்கும் databases/services.

Coordinator சொல்வான்: "எல்லாரும் தயாரா?"

Participants சொல்வார்கள்: "Yes, I can commit" அல்லது "No, I can't".

Coordinator எல்லாரும் Yes என்றால் மட்டும் "Commit" சொல்வான். ஒருத்தன் கூட No என்றால் "Abort".

அனலாகி: ஒரு குழுவில் ஒரு decision எடுக்கணும். முதலில் எல்லாரிடமும் opinion கேட்கிறோம். எல்லாரும் சம்மதித்த பிறகு மட்டும் final செயல்படுத்துகிறோம்.

### 3. How It Works

இரண்டு phase-கள்:

**Phase 1 - Prepare:**
Coordinator எல்லா participants-க்கும் `PREPARE` message அனுப்பும்.
Participant என்ன செய்யும்?
* Transaction changes-ஐ write பண்ணி, undo/redo log-ல தயார் பண்ணும்
* Resource lock போடும்
* Commit செய்ய முடியுமா என்று check பண்ணும்
* முடிந்தால் `YES` + ready state-ல wait செய்யும். முடியாவிட்டால் `NO`

**Phase 2 - Commit/Abort:**
Coordinator எல்லா `YES` வந்தால் `COMMIT` அனுப்பும், இல்லை என்றால் `ABORT`.
Participant message வாங்கியதும் change-ஐ finalize செய்யும்.

```
Coordinator --> Participant A : PREPARE
Coordinator --> Participant B : PREPARE
Participant A --> Coordinator : YES
Participant B --> Coordinator : YES
Coordinator --> Participant A : COMMIT
Coordinator --> Participant B : COMMIT
```

Coordinator fail ஆனால்? Participants தங்கள் state-ஐ hold பண்ணிக்கொண்டு coordinator-ஐ மீண்டும் poll பண்ணும். இது blocking behavior.

### 4. Architectural Reasoning

2PC எப்போது useful?

* Strong consistency கட்டாயம் வேண்டும். All participants-ல atomicity guarantee வேண்டும்.
* Small number of participants, low latency network, rare transactions.
* Financial transfer, inventory reservation போன்ற scenarios.

Alternatives என்ன?
* **Saga pattern**: Local transactions + compensating transactions. Eventual consistency. No blocking.
* **Best-effort 1PC**: Assume success. Risk of inconsistency.
* **TCC - Try Confirm Cancel**: Explicit prepare phase.

Architect ஏன் 2PC தேர்வு செய்வான்? Because he values **consistency over availability** for that specific operation. அவன் network partition-ல system stop ஆகும் risk-ஐ accept பண்ண தயாராக இருப்பான்.

### 5. Trade-offs

**1. Blocking & Availability**
Participant `YES` சொன்ன பிறகு coordinator decision வரும் வரை lock hold பண்ணும். Coordinator down ஆனால் participants stuck ஆகி resources block ஆகும். Availability குறையும்.

**2. Single Point of Failure**
Coordinator தான் bottleneck மற்றும் failure point. Coordinator fail ஆனால் whole transaction in-doubt state-ல stuck ஆகும்.

**3. Latency**
Two round trips mandatory. Network latency கூடினால் transaction latency கூடும். Cross-region 2PC செய்வது painful.

**4. No partition tolerance**
Network partition வந்தால் system either block அல்லது inconsistent ஆகும். CAP theorem-ல CP தேர்வு.

Failure modes முக்கியம்: Coordinator crash after sending COMMIT to some participants but not all. Participants எப்படி recover செய்யும்? Persistent log + timeout + recovery protocol தேவை.

### 6. Practical Example

Bank transfer service.

Account A service, Account B service. Transfer $100.

Coordinator = Transaction Manager.

Prepare phase-ல A service debit log write பண்ணி YES, B service credit log write பண்ணி YES.
Coordinator COMMIT அனுப்பும்.

இங்கே 2PC correct because money must not disappear or duplicate. Eventual consistency acceptable இல்லை.

ஆனால் உண்மையான production-ல இதை direct 2PC-ல செய்வது rare. காரணம் availability முக்கியம். பெரும்பாலும் Saga with idempotent compensations பயன்படுத்துவார்கள்.

### 7. Reasoning Challenge

உங்களுக்கு Order service US-East-ல இருக்கு, Inventory service EU-West-ல இருக்கு, Payment service APAC-ல இருக்கு. Network latency ~200ms each hop. Peak traffic-ல 1000 TPS வரை வரும். Strong consistency தேவைப்படுகிறது.

இங்கே 2PC use பண்ணுவீங்களா? ஏன் / ஏ
