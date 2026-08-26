# REST

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.1 — 2. API engineering

# REST — Resource Oriented API Design

## 1. Problem

நீங்கள் 3 teams-உம் வெவ்வேறு clients-உம் கொண்ட ஒரு product-ல் வேலை செய்கிறீர்கள். Mobile app, web frontend, partner integration — எல்லாம் backend services-ஐ call பண்ணணும்.

முதலில் ஒவ்வொரு team-ம் தனக்கு வசதியாக RPC style-ல் API வடிவமைத்தது. ஒன்று `callGetUserData`, இன்னொன்று `fetchUserInfo`, மற்றொன்று SOAP envelope-ல் `GetUser`.

Client-க்கு மாற்றம் வந்தால், server-ஐயும் மாற்றணும். Versioning குழப்பம். Caching எப்படி பண்ணுவது தெரியாது. Auth, retry, timeout எல்லாம் custom logic.

இந்த coupling வளர வளர, **ஒரு change பண்ணினால் எல்லா client-மும் break ஆகுது**. Operability குறைகிறது.

இந்த chaos-ஐ தீர்க்க தான் web-இன் existing primitives-ஐ use பண்ணி, predictable interface கொடுக்கும் ஒரு discipline வந்தது. அதுதான் REST.

## 2. Mental Model

REST என்பது ஒரு architecture style. முக்கிய idea: **Everything is a resource**.

Resource என்பது நீங்கள் name பண்ணக்கூடிய ஒன்று: `user`, `order`, `payment`. அதை identify பண்ண URI கொடுக்கிறோம். `/users/123`, `/orders/456`.

Action-ஐ நீங்கள் URI-ல் வைக்கவில்லை. Action-ஐ HTTP verb-ல் வைக்கிறோம்.

`GET /users/123` = read
`POST /users` = create
`PUT /users/123` = replace
`PATCH /users/123` = partial update
`DELETE /users/123` = delete

Client-server relationship clear ஆகிறது. Server resource-ஐ maintain பண்ணும். Client request அனுப்பும். மத்தியில் network எப்போதும் unreliable.

## 3. How It Works

REST 4 core constraints-ஐ பயன்படுத்துகிறது.

**Uniform interface:** எல்லா resource-க்கும் அதே pattern. URI + HTTP verb + representation JSON. Client கற்றுக்கொண்டால் போதும்.

**Stateless:** ஒவ்வொரு request-ம் self-contained. Server session state-ஐ store பண்ணாது. Auth token, context எல்லாம் request-ல் வரணும். இதனால் any instance-க்கு request route பண்ணலாம், scale பண்ண easy.

**Cacheable:** HTTP headers `Cache-Control`, `ETag` மூலம் response-ஐ cache பண்ணலாம். `GET` என்பது safe and idempotent என்று அர்த்தம்.

**Layered system:** Client-க்கு தெரியாது எத்தனை proxy, gateway, service இருக்கு. Load balancer, API gateway எல்லாம் transparent.

Implementation-ல் REST என்பது கண்டிப்பாக `GET`, `POST`, `PUT`, `DELETE` மட்டும் பயன்படுத்துவது அல்ல. Resource naming consistent, stateless, cache friendly ஆக இருப்பது.

## 4. Architectural Reasoning

REST useful ஆகும் போது:

* Public API, partner integration, mobile/web clients — long-lived evolution தேவை.
* HTTP/HTTPS infrastructure இருக்கும். Firewall friendly.
* Caching, CDN, edge performance தேவை.
* Team-களுக்கு இடையே loose coupling வேண்டும்.

Alternatives:
* gRPC / GraphQL — internal service-to-service, low latency, strong typing வேண்டுமானால்.
* RPC / SOAP — legacy enterprise.

Architect ஏன் REST choose பண்ணுவார்? **Operability and evolution**. HTTP already understood. Monitoring, logging, retry, rate limiting எல்லாம் standard tools உள்ளன. New client வந்தால் கூடுதல் learning குறைவு.

## 5. Trade-offs

**Simplicity vs Expressiveness.** REST simple ஆனால் complex queries-க்கு awkward. `/orders?status=paid&customer=123&date_from=...` வளர்ந்து கொண்டே போகும்.

**Stateless overhead.** ஒவ்வொரு request-லும் auth, context repeat ஆகும். Session state server-ல் வைத்தால் latency குறையும் ஆனால் scale கடினம்.

**Idempotency கவனம்.** `POST` non-idempotent, `PUT` idempotent. Network retry பண்ணும்போது duplicate payment வராமல் பார்த்துக்கொள்ள வேண்டும். Idempotency key தேவைப்படும்.

**Failure modes.** 404, 409, 429 எல்லாம் meaning full ஆக இருக்க வேண்டும். Inconsistent error schema-ல் client handling குழப்பம்.

## 6. Practical Example

E-commerce order service.

Resources:
* `/customers/{id}`
* `/orders`
* `/orders/{id}`

Flow:

```mermaid
sequenceDiagram
Client->>API Gateway->>Order Service
Order Service->>Database
Order Service-->>API Gateway
API Gateway-->>Client
```

`POST /orders`
