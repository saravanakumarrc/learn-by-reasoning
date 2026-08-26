# SLI/SLO introduction

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.2.7 — Observability foundations

### 1. Problem

உங்கள் service எப்போதும் “up” ஆக இருக்கு. Monitoring dashboard-ல் green. ஆனாலும் customer-கள் complain பண்ணுகிறார்கள்: checkout slow ஆகுது, app hang ஆகுது.

Team-க்குள்ளே வாதம் ஆரம்பம் ஆகும்.
Dev சொல்வான்: “என்னோட code-ல bug இல்லை”.
Ops சொல்வான்: “Server healthy தான்”.
Product சொல்வான்: “User experience மோசம்”.

எப்போது alert raise பண்ண வேண்டும்? எப்போது deploy stop பண்ண வேண்டும்? எப்போது “good enough” என்று சொல்லலாம்?

இந்த ambiguity-க்கு தீர்வு தான் SLI/SLO.

### 2. Mental Model

SLI = Service Level Indicator. நீங்கள் measure பண்ணும் ஒரு concrete signal.
SLO = Service Level Objective. அந்த signal-க்கு நீங்கள் வைத்த target.

ஒரு analogy: Car-ல் speedometer இருக்கு. SLI = actual speed. SLO = “highway-ல் 80-100 kmph மேலே போக கூடாது”. Error budget = அந்த limit-ஐ மீற அனுமதிக்கப்பட்ட மொத்த நேரம்.

SLI என்பது உண்மை, SLO என்பது ஒப்பந்தம். Service-க்கும் user-க்கும் இடையே இருக்கும் contract.

### 3. How It Works

முதலில் choose பண்ணுங்கள்: **என்ன முக்கியம்?**

அதற்கு 4 golden signals போதும்:
* Latency - request எவ்வளவு நேரம் எடுக்கிறது
* Traffic - எத்தனை requests per second
* Errors - எத்தனை requests fail ஆகிறது
* Saturation - resource use, CPU, memory, queue length

இதிலிருந்து SLI-களை define பண்ணுங்கள். உதாரணமாக:
* Availability SLI = successful requests / total requests
* Latency SLI = requests completed within 300ms

அதன் மேல் SLO வையுங்கள். உதாரணமாக:
* 99.9% requests should succeed in 30 days window
* 95% requests should complete within 300ms

Error budget = SLO-வை மீற அனுமதிக்கப்பட்ட அளவு. 99.9% availability என்றால் error budget = 0.1% = ~43 minutes downtime per month.

Error budget burn ஆகும்போது deploy-ஐ stop செய்யலாம், capacity add செய்யலாம். Budget healthy இருக்கும்போது experiment செய்யலாம்.

### 4. Architectural Reasoning

ஏன் uptime மட்டும் போதாது? Service “up” ஆக இருந்தாலும் slow ஆக இருக்கலாம். Users-க்கு latency தான் பிரச்சனை.

SLI/SLO வைப்பது என்பது trade-off-ஐ explicit ஆக்குவது.
Latency SLO strict ஆக வைத்தால் cost அதிகம். Availability strict ஆக வைத்தால் release velocity குறையும்.

Architect-க்கு இது decision-making framework தருகிறது. “We need 99.95% availability” என்றால் multi-region active-active தேவைப்படும். “99% போதும்” என்றால் single region with good retry போதும்.

Alternatives: ad-hoc alerting, “feels slow” based on support tickets. அது reactive, inconsistent. SLO makes it proactive and measurable.

### 5. Trade-offs

* **Availability vs Latency vs Cost.** 99.99% SLO வைத்தால் redundancy, multi-AZ, autoscaling, circuit breakers எல்லாம் வேண்டும். Cost உயரும். 99% வைத்தால் செலவு குறைவு, ஆனால் user pain அதிகம்.

* **Strict SLO kills velocity.** Error budget காலியாகி விட்டால் feature deploy-ஐ block பண்ண வேண்டும். Team-க்கு pressure வரும். நல்லது தான், ஆனால் business-க்கு slow release தெரியும்.

* **Wrong SLI = blind spot.** நீங்கள் latency மட்டும் measure பண்ணினால் timeout ஆன requests தெரியாது. Error rate மட்டும் பார்த்தால் slow degradation தெரியாது. SLI-கள் user experience-ஐ முழுமையாக capture செய்ய வேண்டும்.

Failure mode: SLI noisy ஆக இருந்தால் false paging. அதனால் SLI-கள் stable window-ல் aggregate செய்ய வேண்டும், percentile அல்லது rolling window use செய்ய வேண்டும்.

### 6. Practical Example

Checkout API.

நீங்கள் define பண்ணுங்கள்:
SLI 1: Availability = 2xx responses / total requests
SLO 1: 99.9% over 28 days

SLI 2: Latency p95 < 500ms
SLO 2: 99% of requests meet target

இப்போது monthly error budget = 0.1% downtime ~ 4.3 minutes. ஒரு deployment பிறகு error rate 0.08% increase ஆனது. Budget half burn ஆகிறது. அடுத்த experiment-ஐ stop பண்ணுங்கள், root cause fix பண்ணுங்கள்.

Budget healthy இருக்கும்போது team-க்கு permission இருக்கு: canary release, new model deploy, risky optimization try பண்ண.

### 7. Reasoning Challenge

உங்களிடம் payment service இருக்கு. Current SLO:
