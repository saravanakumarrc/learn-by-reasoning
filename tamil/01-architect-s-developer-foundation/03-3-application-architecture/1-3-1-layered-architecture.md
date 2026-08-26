# Layered architecture

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.3.1 — 3. Application architecture

## 1. Problem

ஒரு monolith app வளர ஆரம்பிச்சதும் என்ன ஆகும்?

Controller-ல DB query எழுதுறாங்க. Validation logic UI-ல இருக்கு. Business rule ஒன்னு change ஆனா 10 files மாறணும். Frontend developer DB schema-வை தெரிஞ்சிக்க வேண்டியிருக்கு. New feature add பண்ணும்போது யார் எந்த file-ஐ touch பண்ணலாம் என்பதே தெரியல.

Team-க்குள்ள conflict வரும். One change breaks another module. Test பண்ணவும் கஷ்டம். Deploy பண்ணும்போது risk அதிகம்.

இதற்கு root cause என்ன? **Responsibilities mix ஆகிடுச்சு.** Presentation, business logic, data access எல்லாம் ஒன்னா கலந்து இருக்கு.

இந்த pain தான் layered architecture வர காரணம்.

## 2. Mental Model

Layered architecture என்பது **responsibility-வை horizontal layers-ஆ பிரிப்பது.**

ஒரு building-ல பார்த்தா: Ground floor - utilities, first floor - office work, top floor - reception. யாரும் மேல floor-ல இருந்து நேரடியா குழாய் குழப்ப மாட்டாங்க.

அதே மாதிரி code-ல:

* **Presentation layer** - HTTP request/response, UI, API contract
* **Application / Business Logic layer** - use cases, orchestration, rules
* **Domain layer** - core entities, business invariants
* **Infrastructure / Data Access layer** - DB, external services, messaging

Flow எப்போதும் ஒரே திசையில்: Presentation → Application → Domain → Infrastructure. திரும்பி வரும்போதும் அதே order.

இது separation of concerns-ஐ enforce பண்ணும்.

## 3. How It Works

Request வந்தா என்ன நடக்கும்?

`API Gateway` → `Controller` presentation layer-ல validation மட்டும் பண்ணும். DTO-வை Business Service-க்கு pass பண்ணும்.

Business Service application layer-ல: transaction boundary set பண்ணும், multiple domain objects-ஐ coordinate பண்ணும்.

Domain model business invariant-ஐ enforce பண்ணும். Eg: Order total > 0, inventory check.

Repository infrastructure layer-ல DB-வோட பேசும். Domain model-க்கு தெரியாது இது SQL இல்ல Mongo.

```
graph TD
    Client --> Presentation[Presentation Layer<br/>Controller / API]
    Presentation --> Application[Application Layer<br/>Use Case / Service]
    Application --> Domain[Domain Layer<br/>Entities / Business Rules]
    Domain --> Infrastructure[Infrastructure Layer<br/>Repository / DB / External API]
    Infrastructure --> Domain
    Domain --> Application
    Application --> Presentation
    Presentation --> Client
```

Key rule: **Inner layer never knows about outer layer.** Domain knows nothing about HTTP or DB.

## 4. Architectural Reasoning

Layered architecture useful ஆகும் போது:

* Team size > 1, multiple developers same codebase-ல வேலை பண்ணும்போது
* Business logic frequently change ஆகும், UI/DB change ஆகும்
* Testability முக்கியம் - business rules-ஐ isolate பண்ணி unit test பண்ண வேண்டும்
* Long lived system, maintainability > initial speed

Alternatives என்ன?
* **Clean Architecture / Hexagonal** - layers-க்கு பதில் ports & adapters. More explicit dependency inversion.
* **Vertical Slice Architecture** - feature-wise organize பண்ணும். Small team, fast delivery-க்கு நல்லது.
* **Monolith** - very small app-க்கு over-engineering.

Architect choose layered when: domain stable ஆனா tech stack change ஆகலாம். Presentation மாறினாலும் business logic untouched இருக்க வேண்டும். Clear boundaries வேண்டும்.

## 5. Trade-offs

**Good parts:**
* Code organized, new joiner-க்கு புரியும்
* Test easy - business logic-ஐ mock infrastructure பண்ணி test பண்ணலாம்
* Tech change possible - DB மாறினாலும் domain மாறாது

**Important trade-offs:**
* **Abstraction overhead.** Simple CRUD app-க்கு 4 layers வைக்கறது overkill. Development slow ஆகும்.
* **Leaky abstraction.** Developers shortcut எடுத்து Controller-ல நேரடியா DB call பண்ண ஆரம்பிச்சா layer meaning இல்லாம போகும்.
* **Performance.** Layer crossing என்பது call stack அதிகம். High throughput low latency path-ல இது matter ஆகும். Sometimes direct query தேவைப்படும்.
* **Circular dependency risk.** Wrong dependency direction maintain பண்ணலைனா architecture break ஆகும்.

Failure mode: Anemic Domain Model. எல்லா logic application layer-ல இருக்கு, domain entities dumb data bags ஆகிடும். அப்போ layer இருந்தும் value இல்ல.

## 6. Practical Example

E-commerce order creation.

Presentation layer: `POST /orders` endpoint. Request validation - items array empty இல்லையா, auth check.

Application layer: `CreateOrderUseCase`. Payment service, inventory service, notification service-ஐ coordinate பண்ணும். Transaction begin/end manage பண்ணும்.

Domain layer: `Order`, `OrderItem` entities. Business invariant: `Order cannot be created with zero total`, `Item quantity > 0`. Discount rule இங்கே இருக்கும்.

Infrastructure layer: `OrderRepository` PostgreSQL-க்கு save பண்ணும். `InventoryClient` external API-க்கு call பண்ணும்.

Frontend React மாறினாலும், Mobile app வந்தாலும், Business logic மாறாது. DB MySQL-ல இருந்து Postgres-க்கு மாறினாலும் Domain மாறாது.

## 7. Reasoning Challenge

உங்களுக்கு internal reporting service இருக்கு. 3 endpoints மட்டும் இருக்கு, CRUD மட்டும். Team 2 developers. Feature release cycle 1 week.

Layered architecture 3 layers வைக்க வேண்டுமா? அல்லது vertical slice / simple controller-service-repo pattern போதுமா? 

ஏன்? Cost of abstraction vs benefit of separation இங்கே எப்படி balance பண்ணுவீங்க?

## 8. Key Takeaways

* Layered architecture solves responsibility mixing, not performance.
* Direction matters: outer depends on inner, inner knows nothing about outer.
* Use it when business logic needs protection from UI/DB changes, not for every small script.
* Every layer adds abstraction cost. Shortcut எடுக்க ஆரம்பிச்சால் architecture collapse ஆகும்.
* Domain layer is the heart. If logic leaks to application/infrastructure, you lost the benefit.
