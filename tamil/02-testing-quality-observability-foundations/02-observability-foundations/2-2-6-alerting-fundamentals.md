# Alerting fundamentals

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.2.6 — Observability foundations

## 1. Problem

நள்ளிரவு 2 மணிக்கு checkout service மெதுவாக ஆரம்பிக்கிறது. Latency 200ms இலிருந்து 3s ஆகிறது. காலையில் customer support-க்கு complaints வரும்போதுதான் நீங்கள் தெரிந்துகொள்கிறீர்கள்.

Monitoring dashboard இருக்கிறது. Metrics எடுக்கிறோம். ஆனால் யாரும் பார்க்கவில்லை. இதுதான் பிரச்சனை.

Monitoring = data காட்டும். Alerting = தேவையான நேரத்தில் சரியான நபருக்கு தெரியப்படுத்தும். Data இருந்தால் மட்டும் போதாது, action தேவைப்படும்போது signal வேண்டும்.

## 2. Mental Model

Alerting என்பது ஒரு decision rule: **இந்த condition வந்தால், மனிதன் தலையிட வேண்டும்**.

இது 3 பாகங்களைக் கொண்டது:
* **Signal**: metrics, logs, traces, business events
* **Rule**: threshold, anomaly, SLO burn rate
* **Notification**: யாருக்கு, எப்படி, எப்போது

நோக்கம் alert fatigue அல்ல. நோக்கம் *actionable* signal. Dashboard-ல் பார்க்க வேண்டியது dashboard-க்கு போகட்டும். Wake up பண்ண வேண்டியது மட்டுமே alert ஆக வேண்டும்.

## 3. How It Works

ஒரு typical flow:

`Metrics/Logs/Traces` -> `Rule Evaluation` -> `Alertmanager` -> `Routing` -> `PagerDuty/Slack/Email`

Prometheus போன்ற system ஒவ்வொரு 15s-க்கு scrape செய்யும். Rule engine `error_rate > 1% for 5m` போன்ற condition-ஐ evaluate செய்யும். Condition true ஆனால் alert fires ஆகும். Alertmanager deduplicate செய்யும், group செய்யும், silencing/escalation handle செய்யும்.

Important: alert evaluate ஆவது stateless. Same condition மீண்டும் மீண்டும் fire ஆகாமல் இருக்க state management வேண்டும். `for: 5m` என்பது flapping-ஐ தடுக்கும்.

```
graph TD
A[Metrics / Logs / Traces] --> B[Rule Evaluation: threshold / SLO burn]
B --> C{Condition met for duration?}
C -->|Yes| D[Alertmanager: dedupe, route, inhibit]
D --> E[PagerDuty / Slack / Email]
E --> F[Human Ack / Resolve]
```

## 4. Architectural Reasoning

Alert எப்போது தேவை?

* **Service down / error rate அதிகம் / latency SLO breach** - immediate action தேவை
* **Error budget burn rate அதிகம்** - trend, பிற்பாடு action தேவை
* **Business critical event** - payment failure spike, fraud pattern

Alert எப்போது தேவையில்லை?

* Normal operational noise, deployment time spike, known maintenance window. இவை dashboard-ல் போதும்.

Alternative approaches:
* **Threshold based**: simple, `latency > 500ms for 5m`. தெளிவு, ஆனால் seasonality-ஐ கணக்கில் எடுக்காது.
* **SLO / error budget based**: `99.9% availability over 28 days` burn rate > 14d. Noise குறைவு, business aligned.
* **Anomaly detection**: historical pattern vs current. Smart ஆனால் false positive அதிகம்.

Architect choose செய்யும்போது constraint பார்க்கிறார்: team size, on-call burden, cost of missed incident vs cost of false page.

## 5. Trade-offs

**Sensitivity vs Noise**. Threshold குறைவாக வைத்தால் early detection கிடைக்கும், alert fatigue வரும். அதிகமாக வைத்தால் missed incidents.

**Paging vs Notification**. PagerDuty wake up செய்யும். Slack notification பார்க்கலாம். Wrong channel = either burnout or silent failure.

**Granularity**. Per service alert simple. Per tenant / per region alert தேவைப்படலாம், ஆனால் cardinality அதிகமாகி alert storm வரும்.

**Flapping**. Service recover ஆகி மீண்டும் fail ஆகும். Alert resolve/firing loop fatigue உண்டாக்கும். `for` duration, inhibition rules, alert grouping தேவை.

Failure mode: alert rule broken, but no one knows. அதனால் alert on alerting - dead man's switch வேண்டும்.

## 6. Practical Example

E-commerce checkout service.
