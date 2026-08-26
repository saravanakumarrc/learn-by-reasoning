# Incident severity levels

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.3.5 — Incident & on-call basics

## 1. Problem

நள்ளிரவு 2 மணிக்கு Pager அடிக்கிறது. Dashboard-ல் ஒரு alert.

அதே நேரத்தில் வேறொரு team-க்கும் alert வருது. இரண்டும் ஒரே priority-ல handle பண்ணுறீங்களா?

ஒன்னு production payment service முழுசா down. ஒன்னு staging-ல் ஒரு non-critical UI bug. இரண்டுக்கும் ஒரே வேகத்தில் respond பண்ணினால் என்ன ஆகும்?

எல்லா incidents-க்கும் எல்லாரையும் எழுப்புறீங்க. On-call engineer burnout ஆகிறார். சின்ன விஷயத்துக்கு manager escalation ஆகிறது. முக்கியமான outage-க்கு response slow ஆகிறது.

இந்த confusion-தான் severity levels தேவைப்பட காரணம்.

## 2. Mental Model

Severity என்பது technical complexity அல்ல. **Impact + Urgency** தான்.

ஒரு incident எவ்வளவு users-ஐ பாதிக்கிறது, revenue-ஐ பாதிக்கிறது, business-ஐ பாதிக்கிறது, எவ்வளவு வேகமா fix பண்ணணும் என்பதை அளவிடுறது.

அதை base பண்ணி, நாம யாரை எழுப்பணும், எவ்வளவு resources allocate பண்ணணும், எப்படி communicate பண்ணணும் என்பதை decide பண்ணலாம்.

## 3. How It Works

பெரும்பாலான orgs SEV 1 to SEV 4 பயன்படுத்துவாங்க.

**SEV 1 - Critical / P0:** Production service முழுசா down அல்லது core functionality பயன்படுத்த முடியாது. Revenue impact உள்ளது. உடனே fix வேண்டும்.
Response: All hands, manager + senior engineer immediate join, war room.

**SEV 2 - Major / P1:** Core service degraded, பெரிய user segment பாதிக்கப்படுகிறது. Workaround இல்லை அல்லது மோசமான workaround.
Response: On-call lead + team, 30 min SLA.

**SEV 3 - Moderate / P2:** Service partially degraded, limited users பாதிக்கப்படுகிறது. Workaround உள்ளது.
Response: On-call handles during business hours, fix in next sprint if needed.

**SEV 4 - Minor / P3-P4:** Non-production, small bug, cosmetic issue, logging problem.
Response: Ticket create பண்ணி backlog-ல் வைக்கலாம். No pager.

Severity classify பண்ணும்போது customer impact பாருங்க, technical cause அல்ல.

## 4. Architectural Reasoning

Severity levels உண்மையில் resource allocation system தான்.

Constraint என்ன? Limited people, limited attention, limited time.

Options: எல்லா alert-க்கும் same response அல்லது triage பண்ணி prioritize.

நீங்கள் SEV 1-ஐ define பண்ணும்போது உங்கள் SLO / SLA-வோடு align பண்ணுங்க. உதாரணமா payment API 99.95% availability இருக்கணும் என்றால், அந்த threshold cross ஆனால் தான் SEV 1.

இது incident commander-க்கு decision framework கொடுக்கிறது. Who to escalate, communication channel எது, status page update வேணுமா என்பதை severity decide செய்யும்.

## 5. Trade-offs

**Over-classification:** எல்லாத்தையும் SEV 1 என்று சொன்னால், எல்லாரும் எல்லா நேரமும் panic mode-ல் இருப்பாங்க. Alert fatigue வரும். முக்கியமானது கூட ignore ஆகும்.

**Under-classification:** Critical outage-ஐ SEV 3 என்று மதிப்பிட்டால், response slow ஆகும். Revenue loss.

**Ambiguity:** Definition clear இல்லை என்றால், two engineers same incident-க்கு வெவ்வேறு severity assign பண்ணுவாங்க. Tribal knowledge ஆகும்.

**Escalation cost:** SEV 1-க்கு manager wake up பண்ணுவது செலவு. அதை justified ஆக்க, definition tight ஆக இருக்கணும்.

## 6. Practical Example

Enterprise e-commerce platform.

Black Friday sale. Checkout service-ல் error rate 5% ஆக உயர்ந்தது.

On-call engineer incident open பண்ணினார். Initial assessment: 20% users check out முடியவில்லை, retry பண்ணினாலும் fail. Payment gateway timeout. Revenue loss visible.

இது SEV 1. Immediately incident commander assign ஆகிறார். Backend team, payment team, SRE எல்லாரும் bridge call-ல் join. Status page update ஆகிறது. CEO communication trigger ஆகிறது.

மறுபுறம், same time-ல் internal admin dashboard-ல் ஒரு button color wrong என்று bug report வந்தது. இது SEV 4. Jira ticket create பண்ணி next sprint-க்கு.

இல்லாமல் இருந்தால் இரண்டுக்கும் ஒரே team effort போய், actual revenue loss அதிகமாகும்.

## 7.
