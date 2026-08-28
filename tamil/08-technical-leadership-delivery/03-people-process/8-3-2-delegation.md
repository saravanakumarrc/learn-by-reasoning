# Delegation

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.3.2 — People & process

## 1. Problem

நீங்கள் senior engineer / tech lead. Team-ல 6 பேர் இருக்காங்க. ஒவ்வொரு PR-க்கும் நீங்களே review பண்ணணும், design decision எல்லாம் நீங்களே approve பண்ணணும், production incident வந்தா நீங்களே debug பண்ணணும்.

முதல் 2 sprint-கள் சரி. 3வது sprint-ல் bottleneck நீங்கள்தான். Team-ன் velocity உங்க availability-க்கு அடிமையாகிடுச்சு. நீங்க தூங்காம இருந்தாலும் system தூங்காது. New hire வந்தா அவருக்கு context கொடுக்க நேரம் இல்லை. நீங்களே தான் எல்லா knowledge-யும் வச்சிருக்கீங்க.

இதுதான் painful problem. Scaling ஆக முடியாது. Delivery slow ஆகும். Bus factor = 1.

## 2. Mental Model

Delegation என்பது task-ஐ தூக்கி போடுவது இல்லை. **Ownership-ஐ மாற்றுவது**.

ஒரு distributed system-ல service A service B-க்கு request அனுப்பும்போது, A-க்கு B எப்படி internally work பண்ணுதுன்னு தெரிய தேவையில்லை. Contract மட்டும் தெரிந்தால் போதும். அதே போல் delegation-ல:

**You define the contract: outcome, constraints, quality bar, escalation path. You don't define every implementation step.**

Mental model: Delegatee-க்கு autonomy கொடு, context கொடு, safety net கொடு.

## 3. How It Works

Effective delegation 4 பாகங்கள்:

**1. Outcome, not activity.** "இந்த API-யின் p95 latency 200ms-க்குள் வரணும்" என்பது outcome. "நீ Redisson cache use பண்ணு" என்பது activity. Outcome-ஐ தான் கொடுக்கணும்.

**2. Boundaries & constraints.** Non-negotiables சொல்லு: security, data privacy, backward compatibility, observability. இதுக்கு உள்ளே experiment செய்ய freedom கொடு.

**3. Context, not control.** Why this matters, what trade-offs we made earlier, what failure modes exist. இது தான் real speedup. Code review-ல் teach பண்ணாதே, up front context கொடு.

**4. Review points, not micromanagement.** Check-in points decide பண்ணு: design sketch, spike result, PR. Daily "என்ன பண்ணிட்டு இருக்கீங்க?" என்பது micromanagement.

## 4. Architectural Reasoning

Delegation useful ஆகும் போது:

* Team size > 3 மற்றும் delivery parallelize பண்ணணும்
* Repeated decisions எடுக்கணும், pattern establish பண்ண முடியும்
* Knowledge silo உருவாக்காம decentralize பண்ணணும்

என்ன constraint-ஐ address பண்ணுது? Throughput of decisions. ஒரு tech lead-ன் decision throughput limited. Delegation decision throughput-ஐ horizontally scale பண்ணும்.

Alternatives: micromanagement - short term quality high, long term team stagnates. Centralized architecture team - slow. Full autonomy - alignment loss.

Choose delegation when you trust team enough to learn, and cost of mistake recoverable.

## 5. Trade-offs

**Control vs Speed.** நீங்க எல்லாத்தையும் பார்த்தா quality predictable, speed குறையும். Delegation speed அதிகரிக்கும், short term variance வரும்.

**Quality vs Learning.** First time delegate பண்ணும்போது output நீங்க பண்ணினா விட கொஞ்சம் மெதுவா / imperfect ஆ இருக்கும். அது investment. 3rd time-க்கு அவங்களே better ஆகிடுவாங்க.

**Ownership vs Alignment.** Too much autonomy = team இஷ்டத்துக்கு architecture diverge ஆகும். Too little = bottleneck. Balance வேண்டும்.

Failure mode: Delegation without context. "இதை பண்ணு" என்று சொல்லி விட்டு விட்டால், rework அதிகம், engineer frustrated.

## 6. Practical Example

Enterprise payment service-ல idempotency key handling மாற்றணும்.

Micromanage approach: நீங்க design doc எழுதுறீங்க, table schema தீர்மானிக்கிறீங்க, PR-ல line-by-line review.

Delegation approach: 
Outcome: "Duplicate payment request வந்தாலும் double charge ஆகக்கூடாது. 99.99% idempotent இருக்கணும்."
Constraints: "DB schema change கூடாது, existing API contract மாறக்கூடாது, observability metrics add பண்ணணும்."
Autonomy: Junior engineer-க்கு delegate பண்ணுங்க.

அவர் spike பண்ணி options கொண்டு வருவார். நீங்க design review-ல trade-off discuss பண்ணுவீங்க. Final decision அவர் implement பண்ணுவார். Ownership அவருக்கு. நீங்க unblock பண்ணீங்க, coach பண்ணீங்க.

Result: நீங்க architecture-level decisions-ல focus பண்ண முடியும். அவர் ownership feel பண்ணுவார்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. எல்லாருக்கும் same event தேவை. Consumer processing speed வேறுபடுகிறது. Producer-ஐ block பண்ணக்கூடாது. Replay-ம் வேண்டும்.

இதே போல் உங்கள் team-ல 1 senior, 2 mid
