# SOLID

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.2 — 1. Programming mastery

# SOLID — Code Change-ஐ Safe-ஆக வைக்கும் 5 கோட்பாடுகள்

## 1. Problem

உங்க team-க்கு 5 வருஷமா இருக்கும் `OrderService`. அதுல payment logic, tax calculation, email notification, invoice PDF generate எல்லாம் ஒரே class-ல இருக்கு.

இப்போ product சொல்லுது: UPI payment add பண்ணனும், email-க்கு பதிலா WhatsApp notification வேணும், tax rule மாறுது.

ஒரு small change பண்ணினா 3 இடத்துல bug வருது. Test எழுதுறது கஷ்டம். New developer join பண்ணா code-ஐ புரிஞ்சுக்க 2 வாரம் ஆகுது.

**What goes wrong?** Class-கள் பல காரணங்களுக்காக மாறுது, ஒன்னோட மாற்றம் இன்னொன்னை உடைக்குது. இதுதான் SOLID வந்த reason.

## 2. Mental Model

SOLID என்பது coding style இல்ல. **Change-ஐ localize பண்ணும் ஒரு design constraint set**.

ஒரு system grow ஆகும்போது, change இருக்கத்தான் செய்யும். அந்த change-ஐ எங்க எங்க impact படும்னு கட்டுப்படுத்துறதுதான் architect-ன் வேலை.

## 3. How It Works

**S — Single Responsibility Principle**
ஒரு class-க்கு ஒரே reason to change மட்டும் இருக்கணும்.

`OrderService` order lifecycle-ஐ மட்டும் handle பண்ணணும். Payment, Notification தனி.

இது change blast radius-ஐ குறைக்குது.

**O — Open/Closed Principle**
Existing code-ஐ modify பண்ணாம, extend பண்ணி புது behaviour add பண்ணணும்.

Payment provider வரும்போது `PaymentProcessor` interface-ஐ implement பண்ணி புது class போடு. Core order flow-ஐ touch பண்ணாதே.

**L — Liskov Substitution Principle**
Child class, parent-ன் contract-ஐ break பண்ணக்கூடாது.

`DigitalPayment` vs `COD` எடுத்துக்கோ. `processPayment()` எல்லாரும் implement பண்ணணும். COD-க்கு `refund()` immediate இல்ல. அதை handle பண்ணி, base interface-ஐ உடைக்காம இரு.

**I — Interface Segregation Principle**
Fat interface கொடுக்காதே. Client-க்கு தேவையானது மட்டும் கொடு.

`INotificationService` ல `sendEmail`, `sendSms`, `sendPush` எல்லாம் இருந்தா, email மட்டும் வேண்ண client-க்கும் push force ஆகுது. Small focused interfaces வை.

**D — Dependency Inversion Principle**
High-level module low-level module-ஐ நேரடியா depend பண்ணக்கூடாது. Both abstraction-ஐ depend பண்ணணும்.

`OrderService` நேரடியா `StripePayment` class-ஐ new பண்ணக்கூடாது. `PaymentGateway` interface-ஐ depend பண்ணணும். Implementation runtime-ல inject ஆகணும்.

```
OrderService -> PaymentGateway (interface)
            ^                ^
            |                |
        StripePayment    UpiPayment
```

## 4. Architectural Reasoning

SOLID useful ஆகும் போது:
- Team size பெருசாகுது, parallel development வேணும்
- Business rules அடிக்கடி மாறுது
- System-ஐ microservices-ஆ split பண்ண பிளான் இருக்கு

Alternative: One big class, procedural code. Short term-ல வேகமா. Long term-ல change cost exponential ஆகும்.

Architect choose பண்ணுறது: Change-ன் frequency மற்றும் cost-ஐ பார்த்து. Stable internal tool-க்கு SOLID over-engineer. Core domain model, payment, order flow போன்ற core business-க்கு must.

## 5. Trade-offs

* **Complexity & Boilerplate:** Interface, abstraction அதிகம். Small script-க்கு overkill.
* **Indirection cost:** Call stack deep ஆகும், debug கொஞ்சம் கஷ்டம்.
* **Initial speed:** முதல்ல slow. Refactor செய்ய வேண்டியது அதிகம்.
* **Learning curve:** New joiner-க்கு design intent புரியணும்.

Failure mode: SOLID-ஐ ritual-ஆ follow பண்ணி, abstraction for abstraction sake create பண்ணினா system unnecessarily complex ஆகும்.

## 6. Practical Example

Enterprise Order system.

அசல் design: `OrderService.createOrder()` உள்ளே Stripe call, tax calc, email send எல்லாம்.

Refactor:
`OrderService` depends on `PaymentGateway`, `TaxCalculator`, `NotificationPort` interfaces.

UPI வரும்போது `UpiPayment` class மட்டும் add. `OrderService` touch இல்ல.
Notification WhatsApp-க்கு மாறும்போது implementation மாற்று. Business logic untouched.

Test-க்கு mock பண்ண எளிது. Service boundary clear ஆகுது. Microservice split-க்கு தயார்.

## 7. Reasoning Challenge

உங்களிடம் `ReportGenerator` class இருக்கு. அது PDF generate பண்ணும், அதை S3-க்கு upload பண்ணும், அப்புறம் email அனுப்பும்.

இப்போ management சொல்லுது: PDF-க்கு பதிலா Excel வேணும், upload S3-க்கு பதிலா GCS வேணும், email-க்கு பதிலா Slack notification வேணும்.

இந்த class-ஐ SOLID படி refactor பண்ணினா எந்த 3 interfaces உருவாக்குவீங்க
