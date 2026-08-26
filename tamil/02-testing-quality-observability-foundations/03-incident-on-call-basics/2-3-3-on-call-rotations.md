# On-call rotations

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.3.3 — Incident & on-call basics

### 1. Problem

Production-ல 2 AM-க்கு error rate spike ஆகுது. Database connection pool exhaust ஆகுது. Alert Slack-ல வருது. யார் பார்ப்பது?

இப்போ team-ல 8 engineers இருக்காங்க. எல்லாரும் “நான் பார்க்கல”ன்னு சொன்னா? அல்லது ஒருத்தர் மட்டும் எப்பவும் பார்த்தா அவர் burn out ஆகிடுவார்.

System 24x7 run ஆகணும். Bug, deployment failure, traffic spike, third-party outage எப்போ வேணா வரும். ஒரு reliable response path இல்லாம, MTTR கூடிடும். Customer impact நீளும். SLO break ஆகும்.

இந்த பெயின் point-தான் on-call rotation-ஐ உருவாக்கியது.

### 2. Mental Model

On-call rotation என்பது **responsibility-ஐ நேரத்துக்கு ஏற்ப பகிர்ந்து கொடுப்பது**.

ஒரு குறிப்பிட்ட window-க்கு ஒரு engineer-க்கு “என்ன ஆனாலும் நான் தான் first responder” என்ற ownership கொடுக்கிறது. மற்றவங்க sleep பண்ணலாம்.

இது pager duty மாதிரி. Phone வந்ததும், context switch ஆகி, incident-ஐ stabilize பண்ணி, escalation செய்யணும்.

### 3. How It Works

ஒரு service அல்லது domain-க்கு ஒரு rotation schedule உருவாக்கப்படும்.

**Primary on-call**: alert வந்த உடனே பார்க்க வேண்டியவர்.  
**Secondary on-call**: primary 10-15 நிமிடத்தில் acknowledge பண்ணலைன்னா, escalate ஆகும்.  
**Manager / Architect**: last escalation.

Rotation weekly அல்லது bi-weekly. Team-ல எல்லாரும் சுழலுவாங்க.

Alerting rules SLO/SLI-க்கு bind ஆகும். False positive குறைவாக இருக்கணும். அதோடு runbook link alert-ல இருக்கும். Who to page, what to check என்பது தெளிவாக இருக்கும்.

```
graph LR
    Alert --> Primary
    Primary --> Acknowledge
    Primary --> Escalate
    Escalate --> Secondary
    Secondary --> Escalate
    Escalate --> Manager
```

On-call engineer-ன் job incident-ஐ fix பண்ணுவது மட்டும் இல்லை. Stabilize பண்ணி, impact குறைச்சி, proper owner-க்கு hand off பண்ணுவது.

### 4. Architectural Reasoning

On-call useful ஆகிறது எப்போ?

* Service external users-க்கு critical. Downtime cost உண்டு.
* System complex, failure modes அதிகம்.
* Team 24x7 coverage வேண்டும், ஆனால் எல்லாரும் எப்பவும் alert-க்கு காத்திருக்க முடியாது.

Constraint என்ன?
* Latency to response: alert -> human -> action
* Team size, expertise distribution
* Operational complexity

Alternatives:
* Follow-the-sun handoff between regions
* Paid dedicated SRE team for critical services
* No rotation, best-effort response

Architect ஏன் rotation தேர்வு செய்வார்?
Responsibility clear ஆகும். Bus factor குறையும். Incident response predictable ஆகும். On-call load measurable ஆகும்.

ஆனால் rotation மட்டும் போதாது. Good observability, alerting hygiene, runbooks இல்லாமல் rotation என்பது just burnout machine.

### 5. Trade-offs

**Coverage vs Burnout**: Short rotation = less fatigue, but context switch அதிகம். Long rotation = deep context, ஆனால் stress அதிகம்.

**Primary vs Secondary depth**: Secondary குறைவாக involve ஆகுவதால் learning குறையும். ஆனால் load spread ஆகும்.

**Automation vs Human**: Too much automation, false sense of safety. Too little, human fatigue. Balance தேவை.

**Failure modes**:
* Alert fatigue: எல்லாம் page ஆனால் எதையும் பார்க்க மாட்டார்கள்.
* On-call engineer-க்கு enough context இல்லை: runbook outdated, access இல்லை.
* Escalation too slow: primary stuck, secondary late.

### 6. Practical Example

Enterprise payment API service. Peak traffic 9 AM - 11 PM IST. US team follow-the-sun.

India team 5 engineers. Weekly rotation. Monday 10 AM -> next Monday 10 AM.

Primary on-call-க்கு PagerDuty schedule. Error budget burn > 5% in 10 min என்றால் page. Alert-ல runbook link: “DB connection pool exhaustion -> check RDS metrics -> check recent deploys -> scale read replicas”.

ஒரு தடவை payment gateway timeout ஆகி alert வந்தது. Primary on-call 7 min-ல acknowledge பண்ணி, circuit breaker enable பண்ணி traffic குறைத்தார். Secondary-க்கு brief கொடுத்து, postmortem next day schedule பண்ணினார்.

இல்லாமல் இருந்தால், எல்லாரும் காலை 9 மணிக்கு தான் பார்த்திருப்பாங்க. Impact 8 hours ஆகியிருக்கும்.

### 7. Reasoning Challenge

உங்க team-ல 4 engineers இருக்காங்க. Service 24x7 critical. ஒரு engineer-க்கு weekly on-call கொடுத்தால், வாரம் தோறும் ஒருவர் 24x7 disturbance-ல இருக்க வேண்டும். இதை தவிர்க்க நீங்கள் என்ன மாற்றம் செய்வீர்கள்? Primary/Secondary structure வைப்பீர்களா? Follow-the-sun வைப்பீர்களா? Automation எந்த அளவுக்கு வைப்பீர்கள்? ஏன்?

### 8. Key Takeaways

* On-call என்பது coverage-க்கான process, fix-க்கான process அல்ல. Stabilize, escalate, learn.
* Rotation clarity கொடுக்கும், ஆனால் observability, alert hygiene, runbook இல்லாமல் அர்த்தமில்லை.
* Burnout என்பது architectural trade-off. Team size, rotation length, automation level-ஐ balance பண்ண வேண்டும்.
* Good on-call culture = blameless postmortem, incident review, and load fairness.
