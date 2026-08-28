# API design

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.4 — System design practice

### 1. Problem

உங்களுக்கு இரண்டு service இருக்கு: `Order Service` மற்றும் `Payment Service`.

`Order Service` ஒரு order create பண்ணும்போது `Payment Service`-க்கு `POST /payments` அனுப்புது. இரண்டு team-ம் வெவ்வேறு velocity-ல வேலை பண்றாங்க.

ஒரு நாள் Payment team `amount` field-ஐ `number`-ல இருந்து `string`-க்கு மாற்றி, `currency` default-ஐ நீக்கிடுறாங்க. அவங்க local-ல test பண்ணி release பண்ணிட்டாங்க.

Order Service உடனே 500 errors, failed orders, money stuck ஆக ஆரம்பிக்குது.

இது ஏன் நடந்துச்சு? ஏன்னா API ஒரு **contract** மாதிரி design ஆகல. Two sides communicate பண்ற interface எப்படி evolve ஆகும், எப்படி break ஆகாம இருக்கும், எப்படி different clients-க்கு serve பண்ணும் என்பது தெளிவா இல்ல.

இதுதான் API design வர காரணம்.

### 2. Mental Model

API design என்பது **interface contract + evolution strategy**.

ஒரு API என்பது:

* What resources expose பண்றோம்
* அதை எப்படி access பண்ணணும்
* request/response என்ன shape-ல இருக்கும்
* எப்போது break ஆகும், எப்போது safe ஆக change பண்ணலாம்

அவ்வளவுதான். Documentation அல்ல, contract.

நல்ல API design பண்றது = **உங்க service-ஐ மற்றவங்க தவறா use பண்ண முடியாதபடி** பண்றது.

### 3. How It Works

நடைமுறையில் API design என்பது இந்த decisions-ஐ எடுப்பது:

**Resource modeling**: Nouns-ஐ மையமா வைத்து design பண்ணுங்க. `GET /orders/{id}`, `POST /orders`. Action-ஐ verb-ஆக அனுப்பாதீங்க. Business capability-ஐ resource ஆக expose பண்ணுங்க.

**Contract stability**: Request/response schema, status codes, error shape எல்லாம் stable ஆக இருக்கணும். Field-ஐ add பண்ணலாம், remove பண்ணக்கூடாது. Optional field-ஐ required ஆக்கக்கூடாது.

**Versioning**: Breaking change வரும்போது `v1`, `v2` மாதிரி version பண்ணுங்க. URL-ல `/v1/orders` அல்லது header-ல `Accept-Version`. Version ஆரம்பத்துலயே plan பண்ணுங்க.

**Idempotency & safety**: `POST` create, `PUT` replace, `PATCH` partial update. Retry செய்யும்போது double charge வரக்கூடாதுன்னா idempotency key வாங்குங்க. `DELETE` மற்றும் `POST` idempotent இல்ல.

**Operational concerns**: Pagination, filtering, sorting. `GET /orders?page=2&limit=50`. Rate limiting, timeouts, clear error codes. Error response-ல `code`, `message`, `requestId` கொடுங்க. 200-க்கு பதிலா 4xx/5xx சரியா use பண்ணுங்க.

**Evolution**: Backward compatible change மட்டுமே default. New field optional, old field deprecate பண்ணி காலம் கொடுத்து remove பண்ணுங்க.

### 4. Architectural Reasoning

API design useful ஆகிறது எப்போ?

* Multiple clients: web, mobile, partner integration. ஒவ்வொன்றுக்கும் different data need இருக்கும்.
* Team boundaries: Service A team vs Service B team. Contract தெளிவா இருந்தால் தான் independent deploy பண்ண முடியும்.
* Longevity: API months/years live இருக்கும். Breaking change = production incident.

Options உங்களுக்கு:

* REST with resources, HTTP semantics
* RPC/GraphQL for flexible queries
* Event-driven async API for loose coupling

Architect choose பண்ணும்போது கேட்க வேண்டியது: Clients எத்தனை? Change frequency எவ்வளவு? Read heavy ஆ? Write heavy ஆ? Strong consistency தேவையா?

### 5. Trade-offs

**REST vs GraphQL**: REST simple, cacheable, மொத்த system-க்கு predictable. GraphQL client-க்கு exact fields தேவை, over-fetching குறையும். ஆனா complexity, N+1 problem, caching கஷ்டம்.

**Versioning vs Backward Compatibility**: Versioning clean ஆ இருக்கும், ஆனா maintenance cost அதிகம். Backward compatible evolve பண்ணினால் long term simple, ஆனா schema clutter ஆகும்.

**Strict contract vs Flexible contract**: Strict schema validation safety கொடுக்கும். Flexible schema evolution எளிதாக்கும். Trade-off reliability vs agility.

**Synchronous vs Asynchronous**: Sync API low latency, immediate response. Async என்றால் eventual consistency, retry, outbox pattern தேவை.

Failure modes: Breaking change, missing pagination leading to OOM, no rate limiting leading to cascade failure, unclear error leading to client retry storm.

### 6. Practical Example

E-commerce `Order API` design:

```
POST /v1/orders
{
  "customerId": "c123",
  "items": [{"sku":"A1","qty":2}],
  "idempotencyKey": "uuid"
}
Response 201:
{
  "orderId": "o789",
  "status": "created",
  "links": {"self":"/v1/orders/o789"}
}
```

Rules:
* `customerId` required, `items` non-empty validation.
* `createdAt` server generate.
* Error: `400` with `{ "code":"INVALID_ITEM","message":"..." ,"requestId":"..."}`

Later you need `couponCode`. You add optional field, no
