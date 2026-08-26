# Modular monolith

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.3.5 — 3. Application architecture

# Modular monolith

## 1. Problem

நீங்கள் 3 வருஷமா வளர்ந்து வரும் ஒரு monolith-ஐ பார்த்திருப்பீங்க. ஆரம்பத்தில் ஒரே team, ஒரே codebase, வேகமா feature விட முடிஞ்சது. இப்போ team 4 ஆகி இருக்கு.

Catalog team-க்கு product search மாற்றம் தேவை. Order team-க்கு checkout flow மாற்றம் தேவை. இரண்டும் ஒரே `src/` folder-ல, ஒரே database-ல table-களை touch பண்ணுது. 

என்ன நடக்கும்?
* Merge conflict எப்போதும்
* ஒரு சின்ன bug fix-க்கு கூட full app-ஐ build-test-deploy பண்ண வேண்டும்
* "இந்த file-ஐ தொடாதே" என்று code ownership இல்லை
* New developer-க்கு எங்கு என்ன இருக்கு என்பதே புரியாது

இதுக்கு தீர்வு என்று microservices சொல்வார்கள். ஆனால் microservices என்றால் network call, distributed transaction, independent deploy, observability, data ownership என்று operational complexity அதிகம் ஆகும். Small to mid size system-க்கு அது overkill ஆகும்.

இந்த இடைவெளிக்கு தான் modular monolith வருகிறது.

## 2. Mental Model

Modular monolith என்பது **ஒரே deployable unit, ஆனால் உள்ளே தெளிவான module boundaries உள்ள monolith**.

ஒரு apartment building போல் நினைத்துக்கொள்ளுங்கள். வெளியில் இருந்து பார்த்தால் ஒரே கட்டிடம். உள்ளே flat-கள் தனித்தனி, ஒவ்வொன்றுக்கும் தனி lock, தனி responsibility.

ஒரு module என்பது bounded context-ஐ follow செய்கிறது. அதற்கு தனி public API, தனி internal implementation, மற்ற module-களை அறியாமல் வேலை செய்யும்.

## 3. How It Works

Code level-ல் இது package / folder structure + dependency rule மூலம் enforce ஆகும்.

```
com.company.app
  ├── catalog  // module
  │   ├── domain
  │   ├── application
  │   └── api
  ├── order
  │   ├── domain
  │   ├── application
  │   └── api
  ├── payment
  └── shared
```

முக்கிய விஷயங்கள்:
* **Dependency direction:** `order` module `catalog`-ஐ read-only API மூலம் use பண்ணலாம். `catalog` `order`-ஐ தெரிந்து கொள்ளக்கூடாது. Circular dependency இல்லை.
* **Module boundary enforcement:** ArchUnit / import-linter போன்ற tools மூலம் `order` package `catalog` internal package-ஐ நேரடியாக access பண்ண முடியாது என்று block பண்ணுவது.
* **Shared database, but logical separation:** ஒரே Postgres இருக்கலாம். ஆனால் ஒவ்வொரு module-க்கும் தனி schema / table ownership உண்டு. Order module Catalog table-ஐ modify பண்ணாது.
* **ஒரே process, ஒரே transaction:** அதே request-ல் Catalog + Order + Payment ஒன்றாக run ஆகும். Distributed transaction தேவையில்லை.

## 4. Architectural Reasoning

இது எப்போது useful?
* Team size 3-8, service count 3-10 domain-கள் வரை
* Low latency internal call தேவை, network hop தேவையில்லை
* Strong consistency, ACID transaction வேண்டும்
* Operational complexity குறைக்க வேண்டும், ஆனால் code coupling அதிகரிக்க வேண்டாம்

Alternatives:
* **Classic monolith:** வேகமாக start பண்ணலாம். ஆனால் boundaries இல்லாமல், எல்லாம் ஒன்றோடொன்று கலந்து விடும்.
* **Microservices:** Independent deploy, independent scale. ஆனால் network failure, eventual consistency, distributed tracing, data duplication செலவு.

Modular monolith தேர்வு என்பது: monolith-ன் simplicity-ஐ வைத்துக்கொண்டு, microservices-ன் logical separation-ஐ கொண்டு வருவது.

## 5. Trade-offs

**Good:**
* ஒரே codebase, ஒரே deploy pipeline. CI/CD simple.
* In-process call = low latency, no serialization overhead.
* ACID transaction cross-module-க்கு எளிது. Order + Inventory update ஒரே DB transaction-ல்.
* Refactor செய்ய எளிது, IDE support full.

**Bad:**
* Scale granularity இல்லை. Catalog heavy traffic இருந்தாலும் full app-ஐ scale பண்ண வேண்டும்.
* Module boundaries leak ஆனால், கட்டுப்பாடு இழக்கும். "நாம் temporary-ஆக இந்த table-ஐ access பண்ணலாம்" என்று ஆரம்பித்தால் மீண்ட
