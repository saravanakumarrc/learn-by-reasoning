# Functional concepts

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.4 — 1. Programming mastery

## 1. Problem

உங்கள் service-ல் ஒரு `Order` object இருக்கு. அதே object-ஐ பல functions மாற்றி மாற்றி touch பண்ணுது.
ஒரு function discount apply பண்ணும், இன்னொரு function tax calculate பண்ணும், மூன்றாவது function status update பண்ணும்.

Local-ல் எல்லாம் சரி. Production-ல் load வந்ததும் எதிர்பாராத total வருது. Test flaky ஆகுது.

ஏன்? ஏன்னா state mutable ஆக இருக்கு. யார் எப்போ எந்த field-ஐ மாற்றினாங்கன்னு track பண்ண முடியல. Concurrency-ல race condition வருது. Retry பண்ணும்போது same operation twice run ஆனாலும் side effect repeat ஆகுது.

இந்த pain தான் functional concepts வந்ததுக்கு காரணம்.

## 2. Mental Model

Function-ஐ ஒரு black box transformation ஆக பாருங்கள்.

> Input → Function → Output

Pure function என்றால்: **same input எப்போதும் same output**, மற்ற எதையும் touch பண்ணாது. No hidden dependency, no side effect.

Mutable state-க்கு பதிலாக **immutability**. Data மாறாது, புது version உருவாகும்.

Functions themselves values. First-class functions, higher-order functions, closures மூலம் behavior-ஐ compose பண்ணலாம்.

Mental model: code-ஐ procedure sequence இல்லாமல், data flowing through small predictable transformations ஆக பார்க்கணும்.

## 3. How It Works

ஒரு pure function-க்கு இரண்டு rules மட்டும்:

1. **Referential transparency**: `f(x)`-ஐ `x` வைத்து எப்போது வேண்டுமானாலும் replace பண்ணலாம்.
2. **No side effects**: DB write, API call, log, random, time போன்றது இல்லை.

Immutability: object-ஐ modify பண்ணாமல், copy with change திருப்பி கொடுக்கணும்.

Composition: `price -> applyDiscount -> applyTax -> round` போல small pure functions-ஐ chain பண்ணலாம். Order மாறினாலும் composition மாறாது.

Closure என்பது function தன்னுடன் சில data capture பண்ணி வைத்துக் கொள்வது. Side effect தவிர்க்க, configuration-ஐ isolate பண்ண உதவும்.

## 4. Architectural Reasoning

Architect-க்கு functional concepts தேவைப்படுவது logic-ஐ predictable ஆக்க, system-ஐ scalable ஆக்க.

**When useful:**
* Core domain logic: pricing, eligibility, risk scoring. இங்கே correctness > performance.
* Event processing pipelines, RAG pipelines, agent tool chains. Steps independent, replay தேவை.
* Concurrent workloads. Immutable data-ல் race condition இல்லை.

**Why choose:**
Pure functions எளிதாக test பண்ணலாம். Input-output மட்டும் பார்த்தால் போதும். Mock தேவை இல்லை.
Caching trivial ஆகும். Same input வந்தால் result reuse பண்ணலாம்.
Parallelism safe. No shared mutable state = no lock.

Alternatives: OOP with encapsulated mutable state. அது local team-க்கு intuitive ஆனால் large distributed system-ல் reasoning கடினம்.

## 5. Trade-offs

* **Memory & performance**: Immutability என்றால் copy/create அதிகம். Hot path-ல் allocation cost பார்க்கணும். Most business logic-ல் acceptable.
* **Learning curve**: Engineers procedural thinking-ல் இருந்து shift ஆக நேரம் எடுக்கும்.
* **IO handling**: Real world-ல் DB, API தேவை. அதை pure core-ல் வைத்து, side effects-ஐ thin boundary layer-ல் isolate பண்ணணும். Discipline வேண்டும்.
* **Debugging**: Stack trace simple ஆனால் immutable chain-ல் data flow trace பண்ண தெரிஞ்சிருக்கணும்.

Failure mode: Pure function-ஐ impure ஆக்கி உள்ளே hidden state வைத்தால், எல்லா benefit-ம் போய் விடும்.

## 6. Practical Example

Enterprise order pricing.

Impure way:
```
order.total = order.subtotal
order.total -= discount(order)
order.total += tax(order)
db.save(order)
```
order object shared, test-ல் order-ஐ setup பண்ணி teardown பண்ணணும்.

Functional way:
```
price = applyDiscount(subtotal, customerTier)
price = applyTax(price,
