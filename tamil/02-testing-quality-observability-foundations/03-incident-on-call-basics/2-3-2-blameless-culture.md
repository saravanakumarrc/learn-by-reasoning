# Blameless culture

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.3.2 — Incident & on-call basics

## 1. Problem

நள்ளிரவு 3 மணிக்கு pager அடிக்கிறது. Production down. On-call engineer லாக்கை பார்த்து ஒரு config change தான் காரணம் என்று தெரிகிறது. Slack-ல உடனே blame ஆரம்பம்.

> "யார் இந்த change-ஐ approve பண்ணினா?"
> "இதுக்கு testing இல்லையா?"
> "எப்படி இது prod-க்கு போச்சு?"

இந்த கேள்விகள் சரியானவை தான், ஆனால் engineer-க்கு பதில் சொல்ல பயம் வருகிறது. அடுத்த முறை பிரச்சனை நடந்தால், அது உடனே surface ஆகாது. Workaround பண்ணி மறைக்க ஆரம்பிக்கிறார்கள்.

இங்கே problem என்ன? Incident நடந்தது, ஆனால் system-ஐ improve பண்ண வேண்டிய learning-ஐ நாம் lose பண்ணுகிறோம்.

## 2. Mental Model

Blameless culture என்பது "யாரும் தப்பு பண்ணவில்லை" என்று சொல்வது அல்ல.

அது **system-ஐ தப்பு பண்ண அனுமதித்தது எது?** என்று கேட்பது.

Human error என்பது inevitable. Fatigue, pressure, unclear runbook, missing guardrails — இவை எல்லாம் normal working conditions தான்.

Blameless culture-ல் focus, person-இல் இல்லை. Focus, conditions-ல் இருக்கிறது.

> Incident = Symptom. Real problem = System design, process, tooling, observability gap.

## 3. How It Works

Practice பின்வருமாறு வேலை செய்கிறது:

**Incident ஆன பிறகு, பேச்சு இப்படி மாறுகிறது**

Bad: "நீ ஏன் அந்த flag-ஐ enable பண்ணினாய்?"
Good: "அந்த flag-ஐ enable பண்ண ஒரு க்ளிக் தான் போதும். அது எப்படி production-க்கு பாதுகாப்பற்றது?"

Blameless postmortem-ல்:

* Timeline-ஐ மட்டும் reconstruct பண்ணு. Who did what is not interesting.
* What went well, what went wrong, what was confusing.
* Contributing factors-ஐ list பண்ணு. Eg: missing canary, alert noise, runbook outdated.
* Action items system-க்கு மட்டும். Eg: add automated rollback, improve rollout guardrails, add better alerting.

Language-க்கு முக்கியம். "I pushed bad code" என்பதை "The change bypassed review because we allowed direct merge to main" என்று மாற்று.

## 4. Architectural Reasoning

இது ஏன் useful?

On-call engineer-க்கு psychological safety வேண்டும். அவர் incident-ஐ hide பண்ணாமல், சீக்கிரம் escalate பண்ண வேண்டும்.

Reliability என்பது process மட்டுமல்ல. Observability, change management, deployment safety, error budgets — இவை எல்லாம் தான் system.

Blameless culture உள்ள team-ல் postmortem-கள் உண்மையான root cause-க்கு போகும். மேற்பூச்சு blame-ல் நின்று விடாது.

இது architect-க்கு என்ன அர்த்தம்? நீங்கள் தேர்வு செய்யும் architecture-இன் failure modes-ஐ திறந்த மனதோடு பேச முடியும். "இந்த design fail ஆனால் என்ன ஆகும்?" என்று கேட்க முடியும்.

## 5. Trade-offs

**Pros**

* Faster incident detection & reporting. People hide பண்ண மாட்டார்கள்.
* Better learning loop. Same failure repeat ஆகாது.
* Psychological safety -> retention, better on-call experience.

**Cons / Trade-offs**

* Time consuming. Proper blameless postmortem எழுதுவது கஷ்டம்.
* Initial resistance. Managers/teams-க்கு "யாரும் பொறுப்பேற்க மாட்டார்கள்" என்ற பயம் வரும்.
* Accountability blur ஆகலாம். Blameless என்பது responsibility இல்லை என்று அர்த்தம் அல்ல. Recurring negligence, process violation போன்றவற்றை handle பண்ண தனி mechanism வேண்டும்.

Most important failure mode: Blameless ஆக fake பண்ணுவது. Postmortem-ல் "human error" என்று முடித்து விட்டு எதையும் fix பண்ணாமல் close பண்ணுவது.

## 6. Practical Example

Enterprise payment service-ல் 20 mins downtime. Root cause: DB migration script prod-ல run ஆகி table lock ஆகியது.

Blame culture: "DBA ஏன் production-ல முதல் முறையே run பண்ணினார்?" DBA அடுத்த முறை risk எடுக்க மாட்டார், அல்லது மறைக்க முயற்சி பண்ணுவார்.

Blameless view:

* Migration tool-ல production guard இல்லை.
* Staging data size production-க்கு நிகராக இல்லை, lock impact தெரியவில்லை.
* Runbook-ல "first run in prod" என்று அனுமதி இருந்தது.
* Alert வர 7 mins தாமதம்.

Action items: migration dry-run mandatory, prod-like env, automated check blocking large migrations during peak, faster alert.

இதில் DBA-ஐ திட்டுவது zero improvement கொடுக்கும். Guardrails வைப்பது improvement கொடுக்கும்.

## 7. Reasoning Challenge

உங்கள் team-ல் 3 முறை தொடர்ந்து அதே alert noise-க்கு on-call engineer தவறான action எடுத்து, incident-ஐ பெரிதாக்கினார்.

Blameless postmortem-ல் என்ன கேள்விகள் கேட்பீர்கள்? Engineer-ஐ blame பண்ணாமல் system-ஐ improve பண்ண என்ன 2 architectural changes செய்வீர்கள்?

நீங்கள் decide பண்ண
