# Idempotency

> **Learning Path:** Distributed Systems
> **Section:** 3.1.13 — Core concepts

## 1. Problem

ஒரு payment API-க்கு client ஒரு `POST /payments` request அனுப்புது. Network-ல கொஞ்சம் blip வந்து response client-க்கு திரும்ப வரல. Client-க்கு தெரியாது request success ஆச்சா இல்லையா.

என்ன பண்ணும்? Safe choice என்னன்னா retry பண்ணுவது. அதே request-ஐ மறுபடியும் அனுப்பும்.

இப்போ server side-ல என்ன ஆகும்?
முதல் request process ஆகி ₹1000 debit ஆகி இருந்தாலும், second retry வந்தா இன்னொரு ₹1000 debit ஆகும். Duplicate payment.

இதே பிரச்சனை order creation, fund transfer, email send, inventory reserve எல்லாத்துக்கும் வரும்.

Distributed system-ல network failure, timeout, client crash எல்லாம் normal. Retry பண்ணாம இருக்க முடியாது. ஆனா retry பண்ணும்போது side effect duplicate ஆகக்கூடாது.

இந்த பிரச்சனைக்கு தான் idempotency வருது.

## 2. Mental Model

Idempotency என்பது: **ஒரே request-ஐ எத்தனை முறை அனுப்பினாலும், system-ல effective effect ஒரே முறை தான்.**

GET போல. நீங்க ஒரு resource-ஐ 10 முறை fetch பண்ணினாலும் data மாறாது.

POST போல. Create operation normally non-idempotent. Same request twice => two resources.

நமக்கு வேண்டியது: non-idempotent operation-ஐ idempotent ஆக மாற்றுவது.

## 3. How It Works

Server-க்கு request வந்ததும் அதை uniquely identify பண்ண ஒரு idempotency key வேணும்.

Typical flow:

1. Client ஒரு unique key generate பண்ணும், எடுத்துக்காட்டாக `Idempotency-Key: 9f3c...` header-ல அனுப்பும்.
2. Server அந்த key + client id + operation type ஆகியவற்றை combine பண்ணி ஒரு record பார்க்கும்.
3. Key முதல் முறை என்றால்: request-ஐ process பண்ணி result-ஐ store பண்ணி, same response திருப்பி அனுப்பும்.
4. Key மீண்டும் வந்தால்: process பண்ணாமல், முன்னாடி store பண்ணின result-ஐ திரும்ப அனுப்பும்.

இதனால் client retry பண்ணினாலும் server duplicate effect create பண்ணாது.

Key எங்கே store பண்ணுவது? In-memory cache குறுகிய காலத்துக்கு, அல்லது persistent store like Redis / database. TTL வைத்து cleanup செய்ய வேண்டும்.

Important: Idempotency key என்பது business key அல்ல. Client generate பண்ணும் correlation id தான்.

## 4. Architectural Reasoning

எப்போது இது useful?

* Network unreliable ஆன distributed system
* Client retries தானாக நடக்கும் HTTP client, message queue consumer
* Financial transactions, payments, order creation போன்ற side-effect உள்ள operations
* Exactly-once semantics வேண்டும் ஆனால் at-least-once delivery தான் கிடைக்கும் சூழல்

Alternatives:
* Client-side de-duplication: server state-ஐ poll பண்ணி duplicate ஆகுமா என்று பார்ப்பது. Flaky, race condition உண்டு.
* Natural idempotency: resource already exists என்றால் update மட்டும் செய்யும் upsert. அனைத்து case-க்கும் பொருந்தாது.

Architect choose idempotency when cost of duplicate > cost of storing keys.

## 5. Trade-offs

**State storage cost.** ஒவ்வொரு request-க்கும் key store பண்ணணும். High throughput system-ல Redis memory cost + DB write வரும்.

**Key scope definition.** Key எவ்வளவு காலம் valid? 24 hours? 7 days? Too short => legitimate retry miss ஆகும். Too long => storage blow up.

**Correctness of key generation.** Client ஒரே business request-க்கு ஒரே key தரணும். Different key வந்தால் duplicate process ஆகும். Key generation logic client team-ஐ நம்ப வேண்டும்.

**Partial failure.** Process பண்ணும்போது halfway fail ஆனால் key store ஆகி இருந்தால், real failure-ஐ மறைத்துவிடும். இதனால் process பண்ணி வெற்றி ஆன பிறகே key commit செய்ய வேண்டும்.

**Distributed consistency.** Multiple service instances இருந்தால் key store shared இருக்கணும். Local in-memory மட்டும் போதாது.

## 6. Practical Example

Payment service.

Client app: `POST /payments` with body `{ amount: 1000, to: "UPI123" }` and header `Idempotency-Key: abc-123`.

First call: Service key not found. Payment processor call செய்து debit success. Result `{ paymentId: p_001, status: success }` ஐ Redis-ல `abc-123 -> p_001` என்று store பண்ணி response அனுப்பு.

Network timeout. Client retry with same key `abc-123`.

Server key கிடைத்தது. Processor call செய்யாமல் stored `p_001` திருப்பி அனுப்பு. User-க்கு duplicate debit இல்லை.

இதே pattern order creation-லும்: `Idempotency-Key` + userId + cart snapshot hash. Replay safe.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு, same event stream-ஐ consume பண்ணுது. Producer-ஐ block பண்ணக்கூடாது. Consumer processing speed வேறுபடுது. Replay தேவை.

இப்போது consumer-கள் network glitch ஆனதும் at-least-once delivery காரணமாக same event-ஐ மீண்டும் process பண்ணும். ஒரு consumer-க்கு duplicate side effect ஆகக்கூடாது.

இங்கே idempot
