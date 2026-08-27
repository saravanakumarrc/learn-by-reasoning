# Platform APIs

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.4.9 — Platform engineering

## 1. Problem

உங்க company-ல 15 product teams இருக்கு. எல்லாருக்கும் தேவை ஒன்னுதான்: service deploy பண்ணணும், database வேணும், observability வேணும், secrets manage பண்ணணும்.

இப்போ ஒவ்வொரு team-ம் தனியா figure out பண்ணுது. ஒருத்தர் Terraform எழுதுறார், இன்னொருத்தர் manual cloud console-ல கிளிக் பண்றார். ஒரு team-க்கு security policy வேற, இன்னொரு team-க்கு வேற. Incident வந்தா யார் காரணம் என்றே தெரியாது.

Platform team இருக்கு, ஆனால் அவங்க ticket basis-ல வேலை செய்யறாங்க. “Database வேணும்”ன்னா 3 நாள் wait. Product team-ன் velocity குறைஞ்சிடுது. Toil அதிகமாகுது.

இந்த pain-தான் Platform API-ஐ தேவைப்படுத்துது.

## 2. Mental Model

Platform API என்பது platform team product teams-க்கு கொடுக்கும் **internal self-service interface**. 

External API மாதிரி, ஆனால் customer வெளியில்லை, internal developer தான் customer.

அது ஒரு golden path-ஐ encode பண்ணி வைக்கும். “இப்படி செய்தால் best practice, security, cost, observability எல்லாம் automatic-ஆ வரும்” என்று.

உதாரணமாக ஒரு `create-service` API call பண்ணா, அது பின்னால் Kubernetes namespace, monitoring, logging, tracing, secret injection, network policy எல்லாம் provision ஆகும்.

Mental model: **Platform is a product, with APIs as the interface, not Slack tickets.**

## 3. How It Works

அடிப்படையில் 3 layer இருக்கும்:

`Product Team` -> `Platform API / Developer Portal` -> `Control Plane` -> `Infrastructure`

Product team ஒரு declarative request கொடுக்கும். `POST /services` with spec: name, region, replicas, db size.

Platform API அதை validate பண்ணும். Policy as code check: allowed region? cost limit? naming convention?

Validate ஆனதும், அது backend-ல Infrastructure as Code, Kubernetes Operator, Terraform provider, அல்லது internal service-க்கு call பண்ணும்.

Response-ல service URL, dashboard link, status வரும். அதன் பின் lifecycle-ம் API மூலமே: scale, update, delete.

Developer portal என்பது human-friendly UI, ஆனால் முக்கிய interface API தான். CI/CD pipeline-களும் அதே API-ஐ call பண்ணும்.

## 4. Architectural Reasoning

Platform API useful ஆகும் போது:

* **Repetition உள்ளது.** 10 teams same infra pattern build பண்ணறாங்க.
* **Standardization தேவை.** Security, compliance, observability consistent-ஆ இருக்கணும்.
* **Speed தேவை.** Self-service வேண்டும், ticket wait வேண்டாம்.

Alternatives:
1. **Centralized ticket model.** Platform team எல்லாம் செய்யும். Slow, bottleneck.
2. **Fully decentralized.** ஒவ்வொரு team-மும் தனியா manage பண்ணும். Fast ஆனால் chaos.
3. **Platform API + Golden Path.** Best of both. Team autonomy வைத்து, guardrails கொடுக்கும்.

Architect decide பண்ணும்போது பார்க்க வேண்டியது: abstraction level எவ்வளவு? Too low-level API வேண்டாம், அப்போ team-கள் திரும்ப தானே build பண்ணும். Too high-level API, flexibility போய்விடும்.

## 5. Trade-offs

**Standardization vs Flexibility.** Golden path எளிதாக்கும், ஆனால் edge cases-க்கு அது கஷ்டமாகும். Escape hatch வேண்டும்.

**Abstraction leakage.** Platform API simple ஆக்க முயற்சி செய்யும்போது, அடிப்படை cloud behavior hide ஆகும். Debugg பண்ணும்போது team-க்கு தெரியாது.

**Operational complexity shifts.** Platform team-க்கு now uptime SLA இருக்கும். API down ஆனால் எல்லா teams-ம் blocked. Platform-ஐ product மாதிரி run பண்ண வேண்டும்.

**Versioning & breaking change.** Internal API-யும் evolve ஆகும். Product teams-க்கு migration support வேண்டும்.

Failure mode: API allow பண்ணிய policy-ல hole இருந்தால், அது எல்லா teams-லயும் replicate ஆகும். One mistake = systemic risk.

## 6. Practical Example

ஒரு fintech company-ல payment service deploy பண்ண 40 minutes எடுத்தது.

Platform team `deploy-service` API-ஐ உருவாக்கினார்கள். Request:

```json
{
  "name": "payments-api",
  "tier": "critical",
  "region": "in-mum-1",
  "replicas": 3
}
```

API பின்னால்:
* Namespace + resource quotas create
* Pod security standard apply
* ServiceMonitor for Prometheus auto-create
* Log routing to central Loki
* Secrets from Vault inject
* Network policy restrict ingress to API gateway only
* Cost tag auto-apply

Team CI/CD-ல `curl platform.internal/api/v1/services` call பண்ணினால் போதும். Review time 2 நாள் to 5 minutes ஆனது. Security audit-ல எல்லா services-ம் same baseline follow பண்ணின.

## 7. Reasoning Challenge

உங்களுக்கு 20 microservices இருக்கு. 5 teams manage பண்ணறாங்க. ஒவ்வொரு team-மும் தங்கள் service-க்கு database தேவைப்படும்போது தனித்தனியா RDS instance create பண்ணி, backup, monitoring மறந்துடறாங்க.

நீங்கள் Platform API design பண்ண போறீங்க. `provision-database` API வச்சால் என்ன parameters கொடுப்பீங்க? எந்த guardrails வைப்பீங்க? Escape hatch எப்படி கொடுப்பீங்க? Why?

## 8. Key Takeaways

* Platform API என்பது internal developer experience-ஐ accelerate பண்ணும் product interface.
* Self-service + guardrails = autonomy with safety. Golden path encode பண்ணுவது முக்கியம்.
* API design-ல consistency, policy enforcement, observability mandatory.
* Every abstraction has a cost: flexibility, debugg
