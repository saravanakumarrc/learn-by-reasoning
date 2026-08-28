# Business continuity planning

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.2.7 — Disaster recovery & high availability

## 1. Problem

உங்க company-க்கு ஒரு Black Friday sale இருக்கு. Payment service 2 மணி நேரம் down ஆயிடுச்சு. 

என்ன நடக்கும்?
- Revenue stop ஆகும்
- Customer support ticket flood ஆகும்
- Finance team settlement செய்ய முடியாது
- Compliance audit-ல penalty வரும்

இப்போ engineer மட்டும் fix பண்ணினா போதாது. Who decides which process first recover பண்ணனும்? Customer refund எப்போ start பண்ணனும்? External vendor-ஐ எப்போ contact பண்ணனும்? இது தெரியாம engineer அலையறார்.

**What goes wrong if we don't have this?** Outage நடந்தப்போ எல்லாரும் improvisation பண்ணுவாங்க. Decisions slow ஆகும், blame game ஆகும், recovery chaotic ஆகும்.

இதுதான் Business Continuity Planning-ன் problem.

## 2. Mental Model

Business Continuity Planning = **இடையூறு வந்தா business எப்படி தொடரும் என்கிற playbook**.

இது மூன்று layer-ஆக பார்க்கணும்:

* **Business Continuity**: Business process தொடரணும். People, process, data, tech எல்லாம் சேர்ந்தது.
* **Disaster Recovery**: IT systems-ஐ recover பண்ணுவது. RTO / RPO target-ஐ meet பண்ணுவது.
* **High Availability**: Downtime-ஐ குறைக்கிறது. Failover automatic ஆக நடக்கணும்.

BCP என்பது technology மட்டும் இல்லை. யார் decide பண்ணுவார், எந்த order-ல recover பண்ணுவோம், communication எப்படி இருக்கும் என்பதும்.

## 3. How It Works

Architect ஒரு BCP உருவாக்கும்போது இந்த வரிசையை follow பண்ணுவார்:

**Business Impact Analysis - BIA**
எந்த process எவ்வளவு critical? Payment processing, order fulfillment, customer login - இதற்கு downtime cost என்ன? இதிலிருந்து RTO - Recovery Time Objective, RPO - Recovery Point Objective define ஆகும்.

**Risk Assessment**
Data center fire, cloud region failure, key person unavailable, third-party API down - இதை likelihood மற்றும் impact-ஆல் rank பண்ணு.

**Recovery Strategies**
* Active-Active multi-region
* Active-Passive DR site
* Pilot light / Warm standby
* Backup + restore

**Runbooks & Communication Plan**
"Database primary down ஆனா யார் page பண்ணுவது? Failover trigger யார் decide பண்ணுவது? Customer-க்கு எப்போ notification போகும்?" இது documented இருக்கணும்.

**Test**
Tabletop exercise மற்றும் real failover drill. Plan work ஆகுதான்னு verify பண்ணனும்.

## 4. Architectural Reasoning

BCP useful ஆகும்போது?

* Regulatory requirement இருக்கும் - banking, healthcare, fintech
* Revenue directly tied to uptime
* Data loss unacceptable ஆனால்
* Single point of failure தெரியும்

Choice என்ன?

```
graph LR
A[Primary Region] -->|async replication| B[DR Region Active-Passive]
A -->|sync replication| C[DR Region Active-Active]
```

Active-Passive: Cost குறைவு, RTO 30-60 mins. Manual failover வேண்டும்.

Active-Active: RTO near zero, cost high, data consistency complex. Cross-region latency, split-brain problem வரும்.

Architect decision என்பது business-ன் RTO/RPO-வை பார்த்து வரும். 99.9% uptime வேண்டுமா, 99.99% வேண்டுமா? அதற்கு எவ்வளவு cost தர தயார்?

## 5. Trade-offs

**Cost vs Availability**
Multi-region replication, cross-region data transfer, idle DR capacity - எல்லாம் cost. Business அதற்கு தயாரா?

**Consistency vs RPO**
Strong consistency வேண்டுமானால் synchronous replication வேண்டும். Latency அதிகரிக்கும். Async replication RPO அதிகரிக்கும் - சில data lose ஆகலாம்.

**Complexity vs Operability**
Automated failover simple ஆக தெரியும். ஆனால் false positive failover ஆனா split-brain ஆகும். Manual approval வேண்டும் என்றால் RTO increase ஆகும்.

**Testing vs Production risk**
Real failover test பண்ணினால் production-க்கு risk. ஆனால் test பண்ணாமல் plan useless.

Important failure mode: DR site-ஐ மறந்து விடுவார்கள். Data drift ஆகும். Failover time-ல DR site outdated ஆக இருக்கும்.

## 6. Practical Example

Enterprise core banking system.

BIA சொல்லுது: Payment processing RTO < 15 min, RPO < 1 min. Customer portal RTO 2 hours.

Decision:
* Payment service: Active-Active across Mumbai + Hyderabad, synchronous replication for ledger DB, async for read replicas.
* Customer portal: Active-Passive, pilot light in DR.

Runbook: Primary region health check fails 3 times → automated failover trigger →
