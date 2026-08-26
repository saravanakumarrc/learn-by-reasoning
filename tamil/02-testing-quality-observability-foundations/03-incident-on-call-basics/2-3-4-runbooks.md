# Runbooks

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.3.4 — Incident & on-call basics

## 1. Problem

3 AM-ல் pager போகிறது. Payment service-ல் error rate spike. On-call-ல் இருப்பது நீங்கள். Service-ஐ நீங்கள் build பண்ணவில்லை. Team-ல் 3 பேர் மாத்திரம் தெரியும்.

என்ன செய்வீர்கள்?
Dashboard-களை திறந்து பார்க்கலாம். Logs-ல் தேடலாம். Slack-ல் கேட்கலாம். ஆனால் time இல்லை. MTTR ஏறும். Business impact ஏறும்.

ஒரு engineer-க்கு context இல்லாமல் system-ஐ தெரிந்து கொள்ளும் நேரம் இல்லை. அப்போது சரியான diagnostic steps, safe remediation steps, escalation path எல்லாம் தெரியாமல் blind trial பண்ணுவோம். அதுதான் incident-ஐ பெரிதாக்கும்.

இந்த pain தான் runbook தேவையை உருவாக்குகிறது.

## 2. Mental Model

Runbook என்பது documentation அல்ல. அது **incident-time playbook** ஆகும்.

ஒரு cricket match-ல் captain-க்கு சூழ்நிலைக்கு ஏற்ற field setting வரையறுக்கப்பட்டிருப்பது போல, runbook என்பது failure scenario-க்கு ஏற்ற step-by-step action ஆகும்.

அது யார் என்ன முடிவு எடுக்கலாம், என்ன முடிவு எடுக்கக்கூடாது என்பதை சொல்லும். Not a wiki page with architecture diagrams.

## 3. How It Works

ஒரு நல்ல runbook மூன்று பகுதிகளை கொண்டிருக்கும்.

**1. Detect & Triage**
Alert என்ன சொல்கிறது? Which SLO breach? Dashboard link, metric name, log query ready. False positive-ஆ? Quick validation steps.

**2. Mitigate**
நேரம் குறைவு. Business impact-ஐ குறைக்கும் immediate action. 
Example: traffic drain, feature flag off, circuit breaker open, scale up. 
எந்த command run பண்ண வேண்டும், யாருக்கு escalate பண்ண வேண்டும்.

**3. Restore & Verify**
Service normal-க்கு வந்ததா என்பதை எப்படி confirm பண்ணுவது. Rollback steps. Post-incident data collect பண்ணுவது.

Runbook-ல் copy-pasteக்கு தயாராக command snippets, kubectl commands, curl examples இருக்கும். Engineer தான் தேடி எழுதக்கூடாது.

## 4. Architectural Reasoning

Runbook useful ஆகும் போது?

System complexity அதிகம், team size பெரிது, on-call rotation frequent. Service-களுக்கு interdependency இருக்கும் போது. Blast radius பெரியது.

Constraints:
Latency to resolution vs accuracy. On-call engineer-க்கு domain knowledge இல்லாமல் செயல்படும் திறன் தேவை. Operational complexity குறைக்க வேண்டும்.

Alternatives:
Runbook இல்லாமல் tribal knowledge. அது key person risk உருவாக்கும். அல்லது fully automated remediation via automation. அது சிறந்தது ஆனால் எல்லா failure-க்கும் சாத்தியம் இல்லை.

Architect ஆக தேர்வு: Critical path service-களுக்கு runbook mandatory. Low impact service-களுக்கு minimal runbook. Runbook-கள் automation-ஐ நோக்கி evolve ஆக வேண்டும்.

## 5. Trade-offs

**Staleness vs Accuracy.** System மாறும். Runbook update ஆகாவிட்டால் dangerous. Wrong step follow பண்ணுவது worse than no runbook.

**Detail vs Speed.** Too much detail = engineer read பண்ண நேரம் இல்லை. Too little = incomplete action.

**Automation temptation.** Runbook steps-ஐ auto run பண்ண வேண்டும் என்ற pressure இருக்கும். ஆனால் blind automation production-ல் தவறு செய்யலாம். Human in the loop தேவை.

Failure mode: Runbook-ல் escalation contact outdated. On-call engineer 30 நிமிடம் தேடுவார். அதனால் runbook change management, ownership clear ஆக இருக்க வேண்டும்.

## 6. Practical Example

Enterprise payment gateway-ல் timeout spike வருகிறது.

Runbook: `Payment Gateway - High Timeout`

Detect: Grafana dashboard link, metric `payment_timeout_rate > 1% for 5m`. Check log query: `service=payment AND level=ERROR AND error_code=TIMEOUT`.

Triage: DB latency check. `SELECT * FROM pg_stat_activity`. Recent deploy? ArgoCD history link.

Mitigate: If DB CPU > 90%, scale read replica. If specific provider API slow, toggle feature flag `payment.provider.x.enabled = false`. Command snippet ready.

Escalate: If error persists >10 min, page DB on-call + payment lead.

Verify: Timeout rate <0.1% for 10 min, successful payment sample logs present.

Engineer 3 AM-ல் இதை follow பண்ணி 8 நிமிடத்தில் mitigation செய்வார்.

## 7. Reasoning Challenge

உங்கள் service-க்கு 20 alerts வருகிறது. ஒவ்வொரு alert-க்கும் runbook இருக்கிறது. ஆனால் அவை எல்லாம் 6 மாதங்களாக update ஆகவில்லை. On-call engineer சொல்கிறார்: "Runbook-கள் confusing, நான் ignore பண்ணுகிறேன்."

நீங்கள் architect ஆக இருந்தால் என்ன செய்வீர்கள்? எல்லா runbook-களையும் update பண்ணுவீர்களா? அல்லது வேறு அணுகுமுறை எடுப்பீர்களா? எப்படி prioritize பண்ணுவீர்கள்?

## 8. Key Takeaways

* Runbook என்பது knowledge transfer அல்ல, incident-time action guide ஆகும்.
* Good runbook = Detect, Mitigate, Verify steps + copy-paste commands + clear escalation.
* Runbook-கள் stale ஆகாமல் பார்த்துக்கொள்ளாவிட்டால் அது liability.
* Automation வரும் வ
