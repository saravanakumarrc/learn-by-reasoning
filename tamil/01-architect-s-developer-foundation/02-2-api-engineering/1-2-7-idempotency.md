# Idempotency

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.7 — 2. API engineering

## Problem

ஒரு user checkout பண்ணும்போது `POST /payments` அனுப்புறார். Network glitch ஆகி response வரல. Client-க்கு தெரியாது payment success ஆச்சா இல்லையா.

Client என்ன பண்ணும்? Safe side-ல மறுபடியும் அதே request-ஐ retry பண்ணும்.

Server-ல முதல் request process ஆகியிருந்தா? இப்போ இரண்டாவது request வந்தா என்ன ஆகும்?

இரண்டு முறை charge ஆகும். Duplicate order உருவாகும். Inventory double deduct ஆகும்.

இது தான் real pain. Network unreliable, timeout நடக்கும். Client retry logic இருக்கும். Server side-ல நாம் அதை handle பண்ணாம விட்டால் business impact வரும்.

இதை தடுக்கத்தான் idempotency தேவை.

## Mental Model

Idempotency என்பது: **ஒரே operation-ஐ எத்தனை முறை apply பண்ணினாலும், effect ஒன்றாக இருக்கும்.**

GET ஒரு typical idempotent operation. 10 முறை call பண்ணினாலும் data மாறாது.

POST by default non-idempotent. 10 முறை call பண்ணினாலும் 10 resource create ஆகும்.

Mental model simple: `f(f(x)) = f(x)`. முதல் call-க்கு பிறகு மீண்டும் call பண்ணினாலும் state மாறக்கூடாது.

## How It Works

Idempotency-ஐ enforce பண்ணறதுக்கு system-க்கு request-ஐ uniquely identify பண்ண தெரியணும்.

Common pattern: **idempotency key**.

Client ஒரு request-ஐ create பண்ணும்போது unique key generate பண்ணி header-ல அனுப்பும். உதாரணமா `Idempotency-Key: 9f3c...`.

Server side logic:

1. Key வந்ததா? இதுக்கு முன்னாடி இந்த key-க்கு result store பண்ணியிருக்கோமா என்று check பண்ணு.
2. இருந்தா அதே response-ஐ return பண்ணு, operation மறுபடியும் execute பண்ணாதே.
3. இல்லைன்னா operation-ஐ execute பண்ணு, result-ஐ key உடன் store பண்ணு, response return பண்ணு.

இது stateful ஆகிறது. ஆனால் correctness-க்கு தேவை.

HTTP spec-ல PUT, DELETE idempotent ஆக கருதப்படும். GET தெளிவாக idempotent. POST-க்கு கட்டாயம் இல்லை. அதனால் POST-ல நாம் manually idempotency key add பண்ண வேண்டும்.

## Architectural Reasoning

எப்போ idempotency தேவை?

* Network unreliable ஆன distributed system-ல.
* Client retry பண்ணும் flow இருக்கும் போது.
* Money, inventory, order creation போன்ற non-reversible side effects உள்ள API-களில்.
* At-least-once delivery உள்ள message queue consumer-ல.

Alternatives?

* Client side-ல "did I get response?" polling. இது incomplete.
* Timeout அதிகமாக்கி retry குறைக்க. இது latency-யை அதிகப்படுத்தும்.
* Server side-ல duplicate detection by business key. உதாரணமா `userId + orderAmount + timestamp`. இது fragile.

Idempotency key தான் explicit contract. Client "இது ஒரே logical request" என்று சொல்கிறது.

Decision: Write API-களில், especially create operations, idempotency key compulsory ஆக்கு.

## Trade-offs

* **Storage cost and TTL**: Idempotency record-ஐ எவ்வளவு நேரம் வைக்க வேண்டும்? Too short -> late retry fail. Too long -> storage blow up. Usually 24h to 7 days.
* **Statefulness**: Stateless service assumption break ஆகும். Key store shared ஆக இருக்க வேண்டும். Redis / database தேவை.
* **Key generation responsibility**: Client generate பண்ண வேண்டும். Bad client key reuse பண்ணினால் different operation-ஐ block பண்ணும்.
* **Partial failure**: Operation halfway fail ஆனால் result store பண்ணுவதற்கு முன் crash ஆனால்? Need atomic write of result + store. இல்லைன்னா duplicate risk உள்ளது.

Failure mode: Clock skew இல்லாத distributed deployment-ல multiple instances same key-ஐ parallel process பண்ணலாம். Key store-ல locking / unique constraint தேவை.

## Practical Example

Payment service.

Client checkout flow:

```http
POST /payments
Idempotency-Key: 7a2c9e-...
{
  "userId": "u123",
  "amount": 5000,
  "currency": "INR"
}
```

First attempt: network timeout.

Client retry with same key.

Server:

* Key not seen → charge gateway, create payment record, store `7a2c9e... -> paymentId P987, status SUCCESS`
* Second attempt → key found → return same `P987` without charging again.

User-க்கு ஒரே charge, UX clean.

இதே pattern order creation, refund initiation, webhook processing-லயும் use பண்ணலாம்.

## Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. ஒரே event-ஐ process பண்ணணும். Producer at-least-once guarantee கொடுக்கிறார். Network-ல duplicate events வரலாம்.

ஒரு consumer தன்னுடைய processing-ஐ idempotent ஆக்காம விட்டால் என்ன problem வரும்? நீங்கள் idempotency-ஐ consumer level-ல implement பண்ணுவீர்களா, அல்லது producer / broker level-ல? ஏன்?

## Key Takeaways

* Idempotency என்பது retry safety-க்கான contract. Network failure தவிர்க்க முடியாது.
* Idempotency key + result store தான் practical implementation.
* Create operations, payment, order போன்ற irreversible side effects-ல இது must-have.
