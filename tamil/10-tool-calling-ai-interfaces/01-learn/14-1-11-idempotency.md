# Idempotency

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.11 — Learn

## 1. Problem

ஒரு payment API-க்கு client ஒரு `POST /payments` request அனுப்புது. Network glitch ஆனதால் response client-க்கு திரும்ப வரல. Client-க்கு தெரியாது request success ஆச்சா இல்லையா.

அப்படியே client retry பண்ணுது. இரண்டாவது request-க்கு server இன்னொரு payment create பண்ணிடுது.

இதே situation API call, order placement, webhook delivery, LLM tool call எல்லாத்துலயும் வரும்.

**Problem என்ன?** Network unreliable, client timeout, server crash, retry logic இருக்கும். Same request பல முறை வந்தாலும் business effect ஒன்றாக இருக்கணும்.

இல்லைன்னா duplicate charge, duplicate order, double inventory deduction, double email send ஆகும்.

## 2. Mental Model

Idempotency என்பது: **ஒரு operation-ஐ எத்தனை முறை call பண்ணாலும், final state ஒரே மாதிரி இருக்கணும்.**

ஒரு முறை call பண்ணினா கிடைக்கும் result, மூன்று முறை call பண்ணினாலும் அதே result.

எளிய analogy: Light switch. On ஆனது On தான். Switch-ஐ 5 முறை அழுத்தினாலும் light On தான்.

API context-ல, `GET` by definition idempotent. `POST` by default அப்படி இல்லை.

## 3. How It Works

Idempotency-க்கு server-க்கு request-ஐ identify செய்ய தேவை.

சாதாரண வழி: **Idempotency Key**.

Client ஒவ்வொரு logical operation-க்கும் ஒரு unique key generate பண்ணி `Idempotency-Key` header-ல அனுப்பும்.

Server flow:
1. Key வந்ததா பார்.
2. இதுக்கு முன்னாடி process பண்ணி result save பண்ணியிருக்கா? இருந்தா அதே response-ஐ திரும்ப return பண்ணு.
3. இல்லைன்னா operation-ஐ execute பண்ணு, result-ஐ key-உடன் store பண்ணு, response return பண்ணு.

இதனால் retry வந்தாலும் duplicate effect இல்லை.

Key storage-க்கு Redis, database table with unique constraint பயன்படுத்தலாம். TTL வச்சு cleanup பண்ணணும்.

Tool calling / AI Interfaces-ல: LLM ஒரு tool-ஐ call பண்ணி network timeout ஆனா, agent மறுபடியும் அதே tool call-ஐ அனுப்பும். Idempotency இல்லைன்னா bank transfer double ஆகும்.

## 4. Architectural Reasoning

**எப்போது useful?**
- Non-idempotent HTTP methods `POST`, `PATCH` மீது retry வேண்டிய systems
- Payment, order creation, refund, transfer போன்ற financial operations
- Distributed systems-ல eventual delivery உறுதி செய்ய வேண்டும்
- API gateway / client SDK-ல automatic retry உள்ளது
- Tool calling, webhook delivery போன்ற AI interfaces

**Alternatives**
- Client side deduplication: தவறானது, server state தெரியாது.
- At-least-once delivery + downstream dedupe: சாத்தியம், ஆனால் complex.
- Exactly-once semantics via transactional messaging: கடினம், cost அதிகம்.

Idempotency key என்பது practical middle ground. Exactly-once guarantee இல்லை, ஆனால் duplicate effect தடுக்கும்.

## 5. Trade-offs

**State storage cost:** ஒவ்வொரு request-க்கும் result store பண்ணணும். High volume-ல storage மற்றும் lookup latency வரும்.

**Key lifetime:** Key எவ்வளவு நேரம் வைக்க வேண்டும்? Too short = retry miss, Too long = storage bloat.

**Scope:** Key per client vs per resource. தவறான scope வைத்தால் valid retry-கள் block ஆகும்.

**Failure modes:** Key store itself fail ஆனால் idempotency break ஆகும். Store-ஐ highly available ஆக்க வேண்டும். அதே நேரம், key lookup மற்றும் operation execution atomic ஆக இருக்க வேண்டும், இல்லைன்னா race condition-ல duplicate வரும்.

**Design complexity:** Developer எல்லா critical endpoint-லயும் idempotency layer add பண்ணணும்.

## 6. Practical Example

Payment service.

Client request:
```
POST /payments
Idempotency-Key: 9f3c2a1b-...
Body: { amount: 500, to: "user123" }
```

First attempt: Server process பண்ணி payment_id `pay_101` create பண்ணி, key -> result mapping save பண்ணி 201 return.

Timeout. Client retry same key உடன்.

Second attempt: Server key-ஐ பார்த்து mapping இருக்கு. Payment create பண்ணாமல் stored response `pay_101` திரும்ப அனுப்பும்.

Result: User-க்கு ஒரே charge, client-க்கு consistent response.

Tool calling scenario: Agent `create_invoice` tool-ஐ call பண்ணும். LLM response timeout. Agent retry பண்ணும். Idempotency key இருந்தால் invoice duplicate ஆகாது.

## 7. Reasoning Challenge

உங்கள் system-ல 20 microservices உள்ளன. ஒவ்வொரு service-மும் event-driven. Producer crash ஆன பிறகு message queue-ல message re-deliver ஆகிறது. Consumer-கள் duplicate message-ஐ process பண்ணும்.

நீங்கள் idempotency-ஐ எங்கே implement செய்வீர்கள்? Consumer level-லா, database level-லா? Key என்னவாக இருக்க வேண்டும்? Replay-க்கு என்ன பாதிப்பு?

## 8. Key Takeaways

- Idempotency என்பது duplicate effect தடுப்பது, network reliability-க்கு தேவை.
- `Idempotency-Key` வழியாக server state-ஐ remember செய்து same request-க்கு same response கொடுப்பது core pattern.
- Retry-safe APIs, payments, tool calls போன்ற critical paths-ல கட்டாயம்.
- Trade-off: correctness vs storage/operational complexity. Key lifetime மற்றும் atomicity முக்கியம்.
- இது exactly-once அல்ல, ஆனால் architecturally practical.
