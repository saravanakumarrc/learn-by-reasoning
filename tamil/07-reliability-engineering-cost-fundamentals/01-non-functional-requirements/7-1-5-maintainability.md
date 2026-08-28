# Maintainability

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.1.5 — Non-functional requirements

## 1. Problem

உங்கள் system இப்போது சரியாக வேலை செய்கிறது. Release கள் வருகின்றன, metrics நன்றாக இருக்கின்றன. ஆனால் 18 மாதங்களுக்கு பிறகு ஒரு சிறிய feature change க்கு கூட 3 engineers, 2 வாரங்கள், 5 files, மற்றும் production incident தேவைப்படுகிறது.

இதுதான் maintainability இல்லாததன் வலி.

New joiner ஒருவர் code-ஐ பார்த்து "இது என்ன செய்கிறது?" என்று கேட்க முடியாமல் போகிறது. ஒரு bug fix செய்தால் அது வேறு 3 flows-ஐ உடைக்கிறது. Tests இல்லை அல்லது flaky tests. Deploy செய்ய பயமாக இருக்கிறது. On-call engineer 2 மணி நேரம் debug செய்து தான் root cause கண்டுபிடிக்கிறார்.

System வேலை செய்யும், ஆனால் மாற்றுவது செலவானதாகவும் ஆபத்தானதாகவும் ஆகிறது.

## 2. Mental Model

Maintainability என்பது "code எவ்வளவு நேர்த்தியாக எழுதப்பட்டுள்ளது" என்பது அல்ல.

Maintainability = **Safe change-ன் செலவு மற்றும் நேரம்**.

ஒரு well-maintained system-ல்:
* என்ன மாற்ற வேண்டும் என்பது தெளிவாக தெரியும்
* மாற்றம் எங்கு impact ஆகும் என்பது கணிக்க முடியும்
* மாற்றத்தை உறுதியாக test செய்ய முடியும்
* மாற்றத்தை பாதுகாப்பாக deploy செய்ய முடியும்
* மாற்றத்திற்கு பிறகு என்ன நடந்தது என்பது தெரியும்

இது reliability மற்றும் cost உடன் நேரடியாக இணைக்கப்பட்டுள்ளது.

## 3. How It Works

Maintainability ஒரு feature அல்ல, அது ஒரு பண்பு. இது design decisions மூலம் கட்டமைக்கப்படுகிறது:

**Clear boundaries and ownership.** Service-கள் தெளிவான API-களுடன், minimal coupling உடன் இருக்க வேண்டும். "இந்த logic இந்த service-க்கு மட்டுமே" என்று தெரிய வேண்டும்.

**Observability as first class.** Logs, metrics, traces இல்லாமல் maintainability இல்லை. Bug-ஐ reproduce செய்ய முடியாவிட்டால் fix செய்ய முடியாது.

**Automated safety net.** Good unit tests, contract tests, integration tests. CI-ல் fast feedback. அதுவே change-ன் confidence-ஐ தருகிறது.

**Explicit over implicit.** Magic behavior, hidden dependencies, global state எல்லாம் future-ல maintenance cost-ஐ அதிகரிக்கும்.

**Operable deployment.** Feature flags, canary, rollback. Change-ஐ படிப்படியாக கொண்டு வர முடிந்தால் தான் தைரியமாக மாற்ற முடியும்.

## 4. Architectural Reasoning

Maintainability தேவைப்படும் போது?

* Team size வளரும்போது
* Ownership மாறும்போது
* Business requirements அடிக்கடி மாறும்போது
* System 3+ years வரை வாழ வேண்டும் என்று எதிர்பார்க்கும்போது

Alternatives?

* Fast and dirty, copy-paste, one big monolith: இப்போது வேகம், பின்னர் cost
* Over-engineered abstractions: இப்போது மெதுவாக, பின்னர் நிலைத்தன்மை

Architect-ன் decision: **Change frequency எங்கே அதிகம்?** அங்கு boundaries-ஐ தெளிவாக வைக்கவும். Stable parts-ஐ simple வைக்கவும்.

Maintainability என்பது always good என்று தோன்றும், ஆனால் அதற்கு cost உண்டு. Extra abstraction, extra tests, extra documentation எல்லாம் upfront time எடுக்கும்.

## 5. Trade-offs

**Maintainability vs Time-to-market**
இப்போது வேகமாக ship செய்ய வேண்டுமா, அல்லது 6 மாதங்களுக்கு பிறகு cheap change வேண்டுமா? Start-up early stage-ல் வேகம் முக்கியம். Platform level-ல் maintainability முக்கியம்.

**Maintainability vs Performance**
Clean abstraction சில நேரங்களில் extra hop / latency தரும். Payment reconciliation service-ல் clean domain model maintainability தரும், ஆனால் hot path-ல் overhead வேண்டாம் என்று தீர்மானிக்க வேண்டும்.

**Maintainability vs Team Cognitive Load**
Too many patterns, too many microservices, too many docs. Complexity itself unmaintainable ஆகும். Consistency > cleverness.

**Failure mode:** Maintainability-ஐ measure செய்யாவிட்டால் technical debt silently accumulate ஆகும். அதன் signal: mean time to understand, change failure rate, deployment frequency குறையும்.

## 6. Practical Example

Enterprise payment service.

Monolith-ல் payment, refund, ledger, notification எல்லாம் ஒன்றாக இருந்தது. 5 years-க்கு பிறகு, refund rule மாற
