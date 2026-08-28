# Design review & critique

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.8 — System design practice

## 1. Problem

நீங்கள் ஒரு new payment service design பண்ணினீர்கள். API design சரி, database schema சரி, code clean. Launch ஆன 2 வாரத்தில் peak traffic-ல latency spike, duplicate payments, மற்றும் data inconsistency வருகிறது.

ஏன்? ஏனென்றால் design-ஐ ஒருவர் மட்டும் பார்த்தார். System boundaries, failure modes, scale, cost எல்லாம் local optimization-க்குள் மறைந்து விட்டது.

Design review & critique இருந்தால் என்ன ஆகியிருக்கும்? அந்த design production pain உருவாகும் முன் கேள்விகள் கேட்கப்பட்டிருக்கும்.

Design review என்பது code review அல்ல. Code-ல bug இருக்கா என்பதல்ல, design-ல trade-off சரியா என்பது.

## 2. Mental Model

Design review என்பது **decision audit**.

ஒரு design ஒரு set of decisions. Every decision has a reason, a constraint, and a consequence.

Reviewer-ன் வேலை: 
* That decision எதற்காக எடுக்கப்பட்டது?
* அந்த constraint உண்மையில் உள்ளதா?
* அந்த decision எந்த failure mode-ஐ உருவாக்கும்?
* வேறு option இருந்ததா? அதை ஏன் தள்ளுபடி செய்தீர்கள்?

ஒரு நல்ல review என்பது "இது தப்பு" என்று சொல்வது அல்ல. "இந்த assumption உடைந்தால் என்ன ஆகும்?" என்று கேட்பது.

## 3. How It Works

ஒரு effective design review process மூன்று படிகள்:

1. **Design doc / ADR**: Problem statement, constraints, options considered, chosen option with reasoning, risks. Implementation details குறைவு.
2. **Pre-read + async comments**: Reviewers doc-ஐ படித்து specific questions post செய்வார்கள். Live meeting-க்கு முன் context build ஆகும்.
3. **Live critique**: 45-60 min. Designer presents 10 min. மீதி time-ல் constraints, failure modes, trade-offs மீது கேள்விகள்.

Review checklist எப்போதும் system-level:
* Load & scale எப்படி estimate பண்ணினீர்கள்? Peak, p99 latency?
* Failure modes என்ன? Service down ஆனால்? Network partition? Database slow?
* Data consistency எந்த level? Eventual consistency accept பண்ண முடியுமா?
* Observability எப்படி? Metrics, logs, traces, alerts?
* Security & compliance? Auth, audit, PII?
* Cost & operability? Team size, on-call burden?

## 4. Architectural Reasoning

Design review எப்போது தேவை?

* New service, critical path-ல் இருக்கும் service.
* Existing service-ல் major change: data model, consistency model, scaling strategy.
* Cross-team dependency உருவாகும் போது.

அது address பண்ணும் constraint: **cognitive bias and local optimum**.

ஒரு engineer தனது service-ஐ மட்டும் optimize பண்ணுவார். Reviewers system view கொண்டு வருகிறார்கள்.

Alternatives:
* No review: வேகம் அதிகம், production surprise அதிகம்.
* Formal architecture board: slow, good for org-level standards.
* Lightweight peer review: fast, good for most teams.

Choose பண்ணும் போது trade-off: speed vs safety. Critical path systems-க்கு formal review, internal tools-க்கு light review.

## 5. Trade-offs

* **Depth vs Speed**: Deep review கண்டுபிடிக்கும், ஆனால் ship delay ஆகும். Review scope-ஐ define பண்ண வேண்டும்.
* **Generality vs Specificity**: Too generic comments waste time. Good critique is specific to constraints. "Make it scalable" என்பது உபயோகமற்றது. "Order service 10k RPS peak-ல் DB read replica lag 2s ஆகும், read-your-writes உடைந்து விடும்" என்பது உபயோகமானது.
* **Blame vs Learning**: Review culture blame ஆகிவிட்டால் engineers risk எடுக்க மாட்டார்கள். Good review focuses on decision, not person.
* **Documentation debt**: Design doc write செய்வது overhead. ஆனால் அதுவே future review, onboarding, incident postmortem-க்கு source of truth.

Failure mode: Reviewers "nice to have" feature requests சேர்த்து விடுவது. Scope creep. Reviewer-ன் role question, not design.

## 6. Practical Example

Enterprise-ல் order processing pipeline design review.

Designer சொன்னார்: Orders API -> synchronous call to Inventory service -> synchronous call to Payment service -> DB write. All in one transaction.

Reviewer கேட்டார்:
* Inventory service 500ms எடுத்தால்? API timeout ஆகுமா? User retry பண்ணினால் duplicate order?
* Payment service down ஆனால் order என்ன ஆகும்? Partial state?
* Peak Black Friday-ல் 5k orders/sec. Synchronous chain-ல் latency எப்படி? Thread pool exhaust ஆகுமா?
* Payment success ஆனாலும் inventory confirm ஆகவில்லை என்றால் consistency?

Design மாறியது: API accepts order, returns 202. Order written to outbox table. Event published via message queue. Inventory & Payment separate consumers, idempotent processing. Compensating transaction for failure.

Cost: complexity அதிகரித்தது. ஆனால் availability & consistency trade-off clear ஆனது.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers same event தேவை. Consumer processing speed வேறுபடுகிறது. Producer-ஐ block பண்ணக்கூடாது. Replay வேண்டும்.

ஒரு engineer Kafka பயன்படுத்தி design பண்ணி இருக்கிறார், ஒரே partition-ல் publish செய்து, ஒவ்வொரு consumer-ம் separate consumer group-ல் subscribe செய்கிறார்.

Review-ல் நீங்கள் என்ன கேள்வி கேட்பீர்கள்? Partition count, ordering guarantee, retention policy, consumer lag monitoring, poison message handling பற்றி எப்படி கேட்பீர்கள்?

உங்கள் கேள்விகள் design decision-ஐ validate செய
