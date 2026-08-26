# Postmortems

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.3.1 — Incident & on-call basics

## 1. Problem

3 AM-க்கு on-call alert வருது. Payment service timeout ஆகுது. Team wake up ஆகி, rollback பண்ணி, DB connection pool increase பண்ணி fix பண்ணிட்டாங்க. Service மீண்டும் வருது. Ticket close.

இரண்டு வாரம் கழித்து அதே incident மீண்டும் நடக்குது. அதே symptoms, அதே hotfix, அதே firefighting.

இங்கே என்ன miss ஆகுது? Fix பண்ணினோம், ஆனால் *ஏன்* நடந்தது என்பதை system கத்துக்கல.

இதுதான் postmortem இல்லாமல் ஆகும் நிலை. Incident-க்கு மீண்டும் மீண்டும் பணம் கட்டிக்கொண்டே இருக்கிறோம்.

## 2. Mental Model

Postmortem என்பது blame document இல்லை. இது **learning artifact**.

Incident ஒரு signal. அது system-ல ஒரு hidden assumption, missing safeguard, அல்லது bad trade-off இருக்குன்னு சொல்லுது.

Postmortem-ன் வேலை: **What happened? Why did it happen? How do we prevent it from happening again?** என்பதை clear-ஆக capture பண்ணி, அதை repeatable improvement ஆக்குவது.

ஒரு experienced engineer பார்க்கும் போது postmortem-ல என்ன இருக்கணும்? Timeline, impact, root cause, corrective actions. Not who messed up.

## 3. How It Works

ஒரு good postmortem குறைந்தபட்சம் இதை cover பண்ணும்:

**Timeline:** Detection எப்போது ஆச்சு, first response எப்போது, mitigation எப்போது, full resolution எப்போது. இதுல எங்கே delay ஆச்சுன்னு தெரியும்.

**Impact:** Users எத்தனை பேர் பாதிக்கப்பட்டார்கள். Revenue loss, SLA breach, data loss இருந்ததா? MTTR என்ன ஆச்சு?

**Root cause analysis:** Symptom அல்ல. 5 Whys போல root-க்கு போ. Example: Timeout -> DB connection exhausted -> connection leak in new release -> code review-ல check missing.

**Corrective actions:** Concrete, owner உள்ள, deadline உள்ள tasks. `Improve alerting`, `Add circuit breaker`, `Add integration test` போன்ற vague items அல்ல. Specific.

Postmortem write-up செய்யும் team-ல incident-ல direct-ஆக involved ஆனவர்களும் இருக்கணும், அப்படி இல்லாதவர்களும் இருக்கணும். Fresh eyes கிடைக்கும்.

## 4. Architectural Reasoning

Postmortem தேவைப்படுவது எப்போது? System complexity அதிகமாகும் போது, failure modes repeat ஆகும் போது, on-call load அதிகமாகும் போது.

Constraints இங்கே என்ன? Availability, reliability, team cognitive load, operational cost.

Alternative என்ன? "Fix and forget". அது short term-ல வேகமானது. Long term-ல technical debt accumulate ஆகும். Same incident-க்கு நேரம், trust, customer goodwill இழக்கிறோம்.

Architect ஆக நீங்கள் postmortem-ஐ process ஆக பார்க்கணும். System-க்கு memory கொடுக்கும் mechanism. Without it, organization learns nothing.

Postmortem culture-ஐ வளர்க்கும்போது blameless ஆக இருப்பது முக்கியம். Engineer blame பண்ணினால் people hide incidents. Hide பண்ணினால் learning stop ஆகும்.

## 5. Trade-offs

**Speed vs Depth:** Incident-க்கு பிறகு immediate-ஆக postmortem நடத்தினால் context fresh-ஆ இருக்கும். ஆனால் people exhausted-ஆ இருப்பார்கள். 24-48 hrs gap வச்சு shallow first draft, then finalize என்பது practical.

**Blameless vs Accountability:** Blameless என்றால் no punishment. ஆனால் corrective actions-க்கு owner இருக்கணும். Accountability = who will do what by when. Blame != Accountability.

**Internal detail vs External share:** Customer-க்கு public postmortem வேண்டுமா? Security, brand risk இருக்கு. Most teams internal detailed version + public summary என்று இரண்டு version வைக்கிறார்கள்.

**MTTR focus vs Prevention focus:** Team-கள் quick mitigation-ல மட்டும் focus பண்ணி prevention-க்கு time கொடுக்க மாட்டார்கள். Postmortem இதை balance பண்ண வேண்டும்.

Failure mode: Postmortem-கள் நடக்கும், action items create ஆகும், ஆனால் follow up இல்லை. அப்போ அது ritual ஆகி போகும்.

## 6. Practical Example

உங்கள் e-commerce platform-ல checkout service 15 நிமிடம் down.

Timeline: 02:10 alert, 02:18 engineer acknowledge, 02:35 root cause identified as Redis cache eviction causing thundering herd to DB, 02:50 mitigation via rate limit, 03:05 full recovery.

Impact: ~12% checkout failures, ~$45k revenue at risk, SLO breach.

Root cause: New flash sale feature cache TTL-ஐ 5 min-ல இருந்து 30 sec-க்கு மாற்றியது. Eviction spike ஆனபோது DB connection pool saturate ஆனது. Existing load test scenario-ல இந்த pattern test செய்யப்படவில்லை.

Corrective actions:
- Add cache stampede protection with probabilistic early expiration. Owner: Backend team. Due 2 weeks.
- Add DB pool saturation alert with < 20% headroom. Owner: SRE. Due 1 week.
- Add load test for flash sale spike pattern to CI pipeline. Owner: QA. Due 3 weeks.

இது இல்லாமல் இருந்தால் அடுத்த flash sale-லும் அதே outage வரும்.

## 7
