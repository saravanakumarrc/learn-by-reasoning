# Conflict resolution

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.3.5 — People & process

# Conflict resolution

## 1. Problem

Team-ல ஒரு architectural decision வருது. Service-ஐ microservice-ஆ cut பண்ணலாமா, monolith-லயே வைக்கலாமா? 
ஒரு senior engineer `latency` குறையும், independent deploy செய்யலாம் என்கிறார். இன்னொரு senior engineer operational complexity, data consistency கஷ்டம் என்கிறார்.

இருவரும் technical point-ல சரியாக இருக்கலாம். ஆனால் discussion எப்போதும் same point-ல திரும்ப திரும்ப வருது. Slack-ல thread நீளுது. Code review-ல comments personal ஆகுது. Standup-ல ஒருத்தர் ஒருத்தரை பார்த்து பேச மாட்டேங்கிறார்.

இதை விட்டுட்டா என்ன ஆகும்?
Decision stuck ஆகும். Sprint goal miss ஆகும். Team trust குறையும். Best people quit பண்ண ஆரம்பிப்பாங்க. Technical debt accumulate ஆகும், ஏனென்றால் யாரும் ownership எடுக்க மாட்டாங்க.

Conflict இல்லாத team இல்லை. Conflict-ஐ ignore பண்ணினால் அது architecture problem ஆக மாறும்.

## 2. Mental Model

Conflict = Misaligned constraints, not bad people.

ஒரு engineer `throughput` பார்க்கிறார், இன்னொருவர் `operability` பார்க்கிறார். இருவரும் system health-க்கு care பண்றாங்க, priority மட்டும் வேற.

மாடல் இப்படி: **People → Position → Interest → Need**

Position = "microservice வேண்டாம்". Interest = "on-call burden குறைய வேண்டும்". Need = "predictable delivery, low incident".

Position-ஐ attack பண்ணாதே. Interest-ஐ uncover பண்ணு.

## 3. How It Works

Effective conflict resolution என்பது debate win பண்ணுவது இல்லை. Shared context create பண்ணுவது.

1. **Separate people from problem.** "நீ முட்டாள்" இல்லை. "இந்த design-ல data consistency risk இருக்கு" என்று பேசு.
2. **Name it early.** 1:1-ல "நமக்கு இங்கே alignment இல்லை, open-ஆ discuss பண்ணலாமா?" என்று சொல்.
3. **Constraints-ஐ explicit ஆக்கு.** Latency budget என்ன? Team size என்ன? Deploy frequency target என்ன? Cost constraint என்ன?
4. **Options generate, then evaluate.** "Microservice now", "Modular monolith now + extract later", "Hybrid with bounded context" - மூன்றையும் write பண்ணு.
5. **Decision criteria agree செய்.** அதன் பிறகு தான் option choose பண்ணு. Criteria post-hoc இல்லை.
6. **Close the loop.** யார் decide பண்ணார், ஏன், what we are not doing, review when. Document பண்ணு.

## 4. Architectural Reasoning

Conflict resolution என்பது soft skill இல்லை. Delivery risk-ஐ manage பண்ணும் architectural tool.

When useful:
* Cross-team dependency தெளிவில்லாத போது
* Estimation-ல wide variance இருக்கும்போது
* Ownership unclear ஆக இருக்கும்போது
* Code review-ல recurring friction வரும்போது

Alternatives:
* **Escalate to manager** - fast, but trust குறையும். Learner culture கெடும்.
* **Vote** - democratic, ஆனால் best idea தோற்கலாம்.
* **Let it fester** - zero cost now, high cost later.

ஏன் facilitator approach choose பண்ணுறோம்? Because technical leadership-ல decision quality matters, not just speed. Team size பெரிதாகும் போது, context switching cost உயரும், அப்போ explicit resolution protocol தேவை.

## 5. Trade-offs

* **Speed vs Psychological safety.** Quick decision எடுக்கலாம், ஆனால் minority voice suppress ஆகும். Safe space கொடுத்தால் time எடுக்கும், ஆனால் commitment அதிகம்.
* **Principle vs Relationship.** Principle-ஐ force பண்ணினால் relationship damage. Relationship preserve பண்ணினால் compromise quality drop ஆகலாம்.
* **Transparency vs Politics.** Open debate transparent ஆக இருக்கும், ஆனால் some engineers public disagreement விரும்ப மாட்டாங்க. Private alignment முதல், public commitment பிறகு என்பது ஒரு pattern.
* **Resolution cost now vs Delivery risk later.** Facilitate பண்ண 2 மணி நேரம் செலவு. Stuck ஆகி 2 sprint waste ஆகும்.

Failure mode: Conflict-ஐ "team bonding exercise" ஆக்காதே. Facilitation without decision = discussion theater.

## 6. Practical Example

Enterprise payment platform. Team A: API gateway team. Team B: fraud detection team.

Fraud service SLA 200ms. Gateway team rate limiting strict ஆக்க விரும்புகிறது. Fraud team அப்படி செய்தால் false negative அதிகம் ஆகும் என்கிறது.

Tech lead conflict-ஐ position-ல இருந்து interest-க்கு மாற்றினார்.

Constraints explicit ஆக்கினார்: P99 latency budget 300ms, fraud miss cost = $5k per incident, rate limit breach cost = $50k per incident.

Three options மேசைக்கு வந்தது. Option B: adaptive rate limit with circuit breaker +
