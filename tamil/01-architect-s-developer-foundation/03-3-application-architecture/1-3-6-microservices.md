# Microservices

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.3.6 — 3. Application architecture

## Problem

உங்க company-ல ஒரு monolith application இருக்கு. 5 வருஷமா வளர்ந்துட்டு வருது. User service, Catalog service, Payment service, Notification service எல்லாம் ஒரே code base-ல, ஒரே database-ல.

இப்போ team 40 engineers ஆகி இருக்கு. ஒரு small bug fix-க்கு கூட full regression test பண்ணி, 2 வாரம் wait பண்ணி deploy பண்ணணும். ஒரு developer Catalog-ல ஒரு change பண்ணும்போது Payment-ஐ break பண்ணிட்டான். எல்லா customers-க்கும் impact.

Black Friday-ல traffic 10x ஆகும். Catalog read heavy, Payment low volume but critical. ஆனால் monolith-ஐ scale பண்ணினால் எல்லா module-உம் scale ஆகும். Cost waste.

ஒரு team Java-ல இருக்கு, இன்னொரு team Go-ல try பண்ண விரும்புது. Monolith-ல அது சாத்தியமில்லை.

இந்த pain தான் microservices-ஐ உருவாக்கியது.

## Mental Model

Microservices என்பது **ஒரு பெரிய application-ஐ சிறிய, independent services-ஆக பிரிப்பது**. 

ஒவ்வொரு service-க்கும் தனி business capability இருக்கும். தனி deploy pipeline, தனி database, தனி team ownership.

அது apartment complex மாதிரி. Monolith ஒரு பெரிய bungalow. ஒரு குழாய் leak ஆனால் முழு வீடும் பாதிக்கும். Microservices-ல ஒவ்வொரு flat-க்கும் தனி water connection, தனி maintenance.

## How It Works

Core idea bounded context. Domain-ஐ logical boundary-களாக வெட்டுறது.

ஒரு service வெளி உலகத்தோடு API மூலம் மட்டும் பேசும். Internal implementation மறைக்கப்படும்.

Service A Service B-ஐ call பண்ணும்போது network call ஆகும். HTTP / gRPC. Timeout, retry, circuit breaker எல்லாம் தேவைப்படும்.

Data ownership முக்கியம். Catalog service-க்கு catalog DB. Payment service-க்கு payment DB. Direct DB access கிடையாது. Service boundary தாண்டி data share செய்ய API மட்டுமே.

Deploy independence. Catalog team வாரம் ஒரு முறை deploy பண்ணலாம். Payment team month once deploy பண்ணலாம். ஒன்று fail ஆனால் மற்றது run ஆகும்.

```mermaid
graph LR
Client --> API Gateway
API Gateway --> Catalog[Catalog Service<br/>Postgres]
API Gateway --> Cart[Cart Service<br/>Redis]
API Gateway --> Payment[Payment Service<br/>Postgres]
API Gateway --> Notification[Notification Service<br/>Kafka]
```

## Architectural Reasoning

Microservices useful ஆகும் போது:

* Team scale பெரியதாகும்போது, Conway's Law. Teams independent ஆக வேலை செய்ய வேண்டும்.
* Different scaling requirement இருக்கும்போது. Catalog 1000 RPS, Payment 50 RPS.
* Different tech stack தேவைப்படும்போது.
* Fault isolation முக்கியமாகும்போது. Payment down ஆனாலும் catalog browse ஆக வேண்டும்.

Alternatives என்ன? 
Modular monolith, service-oriented architecture. Modular monolith ஆரம்பத்தில் சிறிய team-க்கு குறைவான complexity-ல வேலை செய்யும்.

அதனால் choose பண்ணுவது constraint-ஐ பார்த்து. Team size > 15-20, deploy frequency வேறுபடும், availability requirement வேறுபடும் என்றால் microservices பொருத்தமானது.

## Trade-offs

**Complexity அதிகரிக்கும்.** Distributed system problems வரும். Network latency, partial failure, retry storm.

**Data consistency கடினம்.** Monolith-ல
