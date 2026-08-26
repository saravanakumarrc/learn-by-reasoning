# Unit vs integration vs e2e testing

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.1.2 — Testing strategy

## Problem

நீங்க ஒரு service-ஐ மாத்துனீங்க. Unit test எல்லாம் பச்சை. Code review முடிஞ்சுது. Release பண்ணினதும் payment flow break ஆகுது. Customer-க்கு double charge ஆகுது.

ஏன்? ஏன்னா ஒரு unit-க்குள்ள logic சரியா இருக்குன்னு தெரியும், ஆனா அது உண்மையான database-உடன், real API-யுடன், real network-உடன் எப்படி behave பண்ணும்னு தெரியாது.

ஒரே test-ஆல எல்லாத்தையும் பிடிக்க முடியாது. வேகமா feedback வேணும், அதே நேரத்தில் production-க்கு போறதுக்கு முன் confidence வேணும். இந்த tension-தான் unit vs integration vs e2e testing strategy-ஐ உருவாக்கியது.

## Mental Model

Test-ஐ pyramid மாதிரி பாருங்க.

Bottom-ல நிறைய fast unit tests. Middle-ல குறைவான integration tests. Top-ல மிக குறைவான e2e tests.

ஒவ்வொன்றும் வேறு boundary-ஐ validate பண்ணுது.

Unit test = **one unit in isolation**
Integration test = **two or more real components together**
E2E test = **user journey through whole system**

## How It Works

**Unit test**
ஒரு function / class method-ஐ மட்டும் பார்க்கும். External dependency எல்லாம் mock பண்ணப்படும். Database இல்லை, HTTP call இல்லை. Speed மிக முக்கியம்.

> `calculateTax(amount, country)`-க்கு input கொடுத்து output சரியா வருதான்னு பார்க்கறது. இங்கு tax rules logic மட்டும் test ஆகுது.

**Integration test**
Mock இல்லாமல், real components-ஐ connect பண்ணி பார்க்கும். Database + Repository, Service + Message Queue, Service A + Service B API.

இதுல boundary-கள் எப்படி work ஆகுதுன்னு பார்க்கிறோம். Data serialization, transaction, error propagation இங்கே தெரியும்.

**E2E test**
உண்மையான user-போல ஒரு flow-ஐ முழுசா run பண்ணுவது. Browser / API client -> API Gateway -> Service -> DB -> Queue -> Worker.

இது "can a user actually complete a payment?" என்று கேட்குது. Slow, expensive, flaky.

## Architectural Reasoning

நீங்க architect-ஆ பார்க்கும்போது constraint என்ன?

* **Feedback loop speed**: developer ஒரு change பண்ணின உடனே தெரியணும்.
* **Confidence**: production break ஆகக்கூடாது.
* **Cost**: test maintain பண்ண cost, CI time cost.

Unit test வேகமா, cheap-ஆ. ஆனா integration gap இருக்கும். 
E2E test confidence அதிகம். ஆனா slow, brittle.

அதனால் pyramid: நிறைய unit, கொஞ்சம் integration, மிக குறைவு e2e.

Decision எப்படி? 
Core business logic-க்கு unit test must. 
Service boundary அதிகம் மாறும் இடத்தில் integration test. 
Critical user journey மட்டும் e2e.

## Trade-offs

* **Speed vs Confidence**: Unit fast, low confidence. E2E slow, high confidence.
* **Isolation vs Realism**: Mock பண்ணினா isolate ஆகும், ஆனா real failure தெரியாது. Real components வச்சா realistic, ஆனா flaky ஆகும்.
* **Cost of maintenance**: E2E test data setup, environment, external dependencies-ஐ handle பண்ணணும். ஒரு UI மாறினாலும் test break ஆகும்.
* **Failure mode**: Unit test பிடிக்காத bug என்ன? Timeout, retry logic, serialization mismatch, DB constraint violation. இவை integration / e2e-ல தான் வரும்.

Every solution creates trade-off. Unit test அதிகம் வச்சாலும் integration gap வரும். E2E அதிகம் வச்சாலும் CI slow ஆகி developer productivity குறையும்.

## Practical Example

Order service பார்ப்போம்.

Unit: `OrderValidator.validate(order)` logic. Mock இல்லாமல் pure logic.

Integration: Order Service + Postgres. Real DB container-ல `createOrder` பண்ணி, transaction commit ஆகுதான்னு பார்க்கிறது. Order Service + Kafka producer. Event publish ஆகுதான்னு பார்க்கிறது.

E2E: Test user login பண்ணி, product add பண்ணி, checkout பண்ணி, payment success ஆகுதான்னு முழு flow.

இங்கே architect decision: Payment flow-க்கு ஒரே ஒரு e2e test போதும். ஆனா order creation logic-க்கு 20 unit tests + 3 integration tests.

## Reasoning Challenge

உங்களிடம் 3 microservices இருக்கு: API Gateway, Order Service, Inventory Service. Order create பண்ணும்போது inventory reserve ஆகணும். 

இப்போது Inventory Service-இன் API contract மாறியிருக்கு. 

இந்த மாற்றம் break ஆகாம இருக்க unit test மட்டும் போதுமா? இல்லை integration test வேணுமா? E2E வேணுமா? ஏன்? எந்த level-ல என
