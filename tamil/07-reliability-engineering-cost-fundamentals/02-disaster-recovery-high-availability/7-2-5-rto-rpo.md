# RTO / RPO

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.2.5 — Disaster recovery & high availability

## 1. Problem

Production down ஆச்சு. 2 மணி நேரம் கழித்துதான் service திரும்ப வந்தது. அதுக்குள்ள 15 நிமிஷ data மறைஞ்சு போச்சு.

இப்போ business கேட்குது: *எவ்வளவு நேரம் down இருக்கலாம்? எவ்வளவு data loss ஏற்றுக்கொள்ள முடியும்?*

இதுக்கு பதில் இல்லாம design பண்ணினா, architect என்ன செய்யணும் என்பதே தெரியாது. எல்லாத்துக்கும் multi-region, synchronous replication, hot standby வச்சா cost பறந்துடும். எதுவுமே வச்சா outage-ல revenue, trust எல்லாம் போகும்.

RTO / RPO என்பது இந்த trade-off-ஐ எண்ணால் பேச வைக்கும்.

## 2. Mental Model

RTO = **Recovery Time Objective**. Failure ஆனதில் இருந்து service-ஐ மீண்டும் usable ஆக்க எவ்வளவு நேரம் ஆகலாம். Clock time.

RPO = **Recovery Point Objective**. Failure நடந்த நேரத்துக்கு முன்னால் எவ்வளவு தூரம் வரை data recover பண்ண முடியும். Data time.

ஒரு analogy: RTO என்பது வீடு தீப்பிடிச்சா குடியேற தயாராகும் நேரம். RPO என்பது எத்தனை நாள் பழைய புகைப்படங்கள் இழக்கலாம்.

## 3. How It Works

இது metric, not a feature.

RTO measure பண்ண: last healthy state முதல் users-க்கு normal request serve ஆக ஆரம்பிக்கும் வரை.

RPO measure பண்ண: last durable commit முதல் fail நேரம் வரை இருக்கும் data gap.

இதை decide பண்ணுவது business impact + cost.

RTO 0 என்பது impossible. RPO 0 என்பது synchronous replication மற்றும் zero data loss தேவை.

## 4. Architectural Reasoning

இந்த இரண்டும் design choices-ஐ drive பண்ணும்.

**RTO குறைக்கணும்னா:**
* Hot standby / active-active deployment வேண்டும்
* Automated failover, health checks, DNS failover
* Runbooks அல்லது chaos engineering-ஆல் தானாக promote ஆகும்

**RPO குறைக்கணும்னா:**
* Synchronous replication across AZ/region
* Write-ahead log shipping, continuous backup
* Durable storage, WAL archiving

Alternative: Cold backup. Cost குறைவு, RTO மணிகள், RPO மணிநேரம். 

ஏன் choose பண்ணுறோம்? Constraint என்ன? 
Latency sensitive, revenue critical service-க்கு RTO < 5 min, RPO < 1 min வேணும். 
Internal analytics dashboard-க்கு RTO 4 hours, RPO 24 hours போதும்.

Decision = business impact / cost.

## 5. Trade-offs

1. **RPO vs Cost & Latency**: Synchronous replication RPO-வை குறைக்கும், ஆனால் write latency அதிகரிக்கும், cross-region bandwidth cost அதிகம்.

2. **RTO vs Complexity**: Automated failover RTO-வை குறைக்கும், ஆனால் split-brain, flapping, false positive risks வரும். Manual failover simple, ஆனால் human delay.

3. **Consistency vs Availability**: Strong consistency கொடுக்க RPO குறையும், ஆனால் partition-ல் availability பாதிக்கும்.

4. **Operability**: Multi-region active-active maintain பண்ணுவது team size, monitoring, data reconciliation எல்லாம் கேட்கும்.

Failure mode: Failover பண்ணும்போதே data divergence வந்தால், recovery என்பது merge conflict ஆக மாறும்.

## 6. Practical Example

Payment service.

Business says: நாளொன்றுக்கு 5 Cr transaction. 1 மணி downtime = 20L loss + brand damage.

Target: RTO < 15 min, RPO < 1 min.

Architecture: 
Primary DB in region A with synchronous replica in same region AZ-1/AZ-2. Async replication to region B. 
App deployed active-passive with Route53 health check failover. 
WAL shipped continuously to S3, point-in-time recovery enabled.

Disaster ஆனால்: AZ fail -> automatic promotion < 5 min. Region fail -> manual promote region B, data loss max 60 sec.

Cost high, ஆனால் acceptable.

ஒரு internal reporting service-க்கு நாம் RTO 8 hours, RPO 24 hours வைத்து daily snapshot + weekly cold backup போதும்.

## 7. Reasoning Challenge

உங்களிடம் user profile service இருக்கு. 50M users. Read heavy. 
Option A: Single region, nightly backup. Cost low.
Option B: Cross-region async replication + automated failover. Cost 3x.

Business கேட்குது: downtime 4 hours க்கு மேல் ஆகக்கூடாது, data loss 1 day க்கு மேல் ஆகக்கூடாது.

இங்கே RTO/RPO target என்ன? Option A/B எது சரி? ஏன்? Failover செய்த பிறகு read stale ஆகும் risk-ஐ எப்படி handle பண்ணுவீங்க?

## 8
