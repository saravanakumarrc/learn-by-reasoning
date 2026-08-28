# High-level design

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.3 — System design practice

## High-level design — System design practice

### 1. Problem
நீங்க ஒரு feature எடுத்து direct-ஆ code ஆரம்பிச்சிடுறீங்க. முதல் வாரம் smooth-ஆ ஓடும். Traffic வந்ததும் latency spike ஆகும், DB slow ஆகும், on-call alert வரும். Team expand ஆனதும் "யார் எதை own பண்றாங்க?"ன்னு குழப்பம். Cost ஏறும், rollback செய்ய முடியாது.

இதுக்கு காரணம் system-ஐ முழுசா பார்க்காமல் பகுதி பகுதியா build பண்ணது. High-level design என்பது build பண்ணுறதுக்கு முன்னாடி blueprint வரைவது. **What goes wrong if we don't have this?** Rework, hidden coupling, scaling pain.

### 2. Mental Model
High-level design என்பது implementation detail இல்லை. இது **system boundaries, data flow, components, failure modes**-ஐ decide பண்ணுவது.

ஒரு building ப்ளான் மாதிரி பாருங்க. Architect foundation, load, water, electricity path-ஐ முடிவு பண்ணுவார். Contractor பிறகு brick வைப்பார். நீங்க architect மாதிரி think பண்ணணும்.

### 3. How It Works
ஒரு HLD-ல நீங்க இதை மட்டும் clear பண்ணுவீங்க:

**Requirement clarification**: Functional + non-functional. `Throughput` எவ்வளவு? `Latency` SLA என்ன? Availability? Durability? Security constraints?
**Capacity estimate**: Daily active users, requests/sec, data growth. இதுலயிருந்து storage, bandwidth estimate வரும்.
**API contract**: System-ஐ எப்படி use பண்ணுவாங்க? REST / gRPC? Idempotency தேவையா?
**Data model**: What entities? Read/write pattern எப்படி? SQL vs NoSQL decision இங்கே start ஆகும்.
**Components**: API gateway, service, cache, database, message queue, object storage.
**Failure & scaling**: What fails first? DB connection, network partition, hot key? Auto-scale எங்கே?

இதை 30-60 நிமிடத்தில் sketch பண்ண முடியும்.

### 4. Architectural Reasoning
HLD useful ஆகிறது when:

* New system ஆரம்பிக்கும் போது
* Existing system bottleneck hit ஆன போது
* Team size > 3, multiple services interact பண்ணும் போது

Constraints-ஐ முதலில் list பண்ணுங்க. உதாரணமா: latency < 200ms, cost cap உள்ளது, team small. இந்த constraints-க்கு ஏற்ப options filter ஆகும்.

Alternatives always உண்டு. உதாரணமா read heavy workload-க்கு: single DB + read replica vs cache layer vs CQRS. ஒவ்வொன்றும் consistency, operational complexity, cost-ல வேறுபடும்.

Decision = constraint + trade-off accept பண்ணுவது.

### 5. Trade-offs
**Speed vs Rigor**: HLD எடுக்க நேரம் போகும். ஆனா பிறகு rework குறையும்.
**Simplicity vs Scale**: Monolith simple, fast to ship. Microservices scale ஆகும் ஆனா operational overhead அதிகம்.
**Consistency vs Availability**: Strong consistency simple logic, ஆனா latency & availability குறையும். Eventual consistency scale ஆகும்.
**Cost vs Durability**: 3 replicas safe, ஆனா cost 3x.

Failure modes முக்கியம். Network timeout ஆனால் retry logic இருக்கா? Cache miss storm வந்தால் DB crash ஆகுமா? இதை முன்கூட்டியே பார்க்கணும்.

### 6. Practical Example
ஒரு internal notification service. 2M users, daily 10M notifications. Email, SMS, push.

Constraints: delivery latency < 5 min, at-least-once delivery, cost sensitive.

High-level components:
Client -> API Gateway -> Notification Service -> Message Queue -> Workers -> Provider adapters -> DB for status.

Why queue? Producer rate bursty. Workers slow provider rate limit-க்கு respect பண்ணணும். Queue decouple பண்ணும். Replay
