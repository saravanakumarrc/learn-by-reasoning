# Failover design

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.2.6 — Disaster recovery & high availability

## Failover design

### 1. Problem

உங்க company-ல peak sale time-ல payment service down ஆகுது. ஒரே instance, ஒரே database, ஒரே AZ-ல run ஆகுது.

Network blip வந்ததும், node crash ஆனதும், disk full ஆனதும் உடனே users-க்கு 5xx error. Retry பண்ணினாலும் same place-க்கு தான் போகும்.

இதை fix பண்ணாம விட்டால் என்ன ஆகும்? Revenue loss, SLA breach, customer trust போகும். Manual intervention வரை காத்திருக்க முடியாது.

Failover-ன் core question இது தான்: **Primary fail ஆனதும், traffic-ஐ healthy path-க்கு எப்படி automatic-ஆக மாற்றுவது?**

### 2. Mental Model

Failover என்பது spare tyre மாதிரி. Car-ல ஒரு tyre puncture ஆனதும், நீங்க நிறுத்தி மாற்றுறீங்க. System-ல அதே வேலை, ஆனால் automatic.

ஒரு primary component fail ஆனதும், அதன் role-ஐ standby / replica எடுக்கும். User-க்கு தெரியாம அல்லது minimal downtime-ல switch ஆகணும்.

முக்கியம்: Failover detection ஆகணும், decision ஆகணும், traffic shift ஆகணும். இது மூணும் சரியாக நடந்தால் தான் availability காப்பாறும்.

### 3. How It Works

Basic flow:

**Health check → Detection → Promotion → Traffic shift**

Health check என்பது heartbeat, liveness probe, read/write test. Load balancer / orchestrator / control plane இதை தொடர்ந்து பார்க்கும்.

Detection time = failure ஆன நேரம் முதல் நீங்க அதை realize பண்ணும் நேரம். இது timeout, probe interval, unhealthy threshold-ல depend ஆகும்.

Promotion: Active-passive setup-ல standby-ஐ active ஆக்குவது. Active-active setup-ல already active, traffic மட்டும் மாற்றுவது.

Traffic shift: DNS failover, load balancer pool update, service mesh routing rule change. RTO - Recovery Time Objective - இது தான் குறைக்கணும்.

Database failover-ல இன்னொரு layer: replication lag. Primary-க்கு writes நடந்துட்டு இருந்தா, அது standby-க்கு sync ஆகலன்னா data loss ஆகும். அதான் RPO.

### 4. Architectural Reasoning

Failover தேவைப்படும் constraint என்ன? **Downtime cost > failover complexity cost.**

உதாரணம்: Internal batch job fail ஆனாலும் ஓகே. Customer facing payment, auth, checkout fail ஆகக்கூடாது.

Options:

* **No failover, retry + circuit breaker மட்டும்**: Cheap, ஆனால் single point of failure இருக்கும்.
* **Active-passive failover**: Standby ready, primary fail ஆனால் promote. Simple, cost effective. Failover time அதிகம்.
* **Active-active multi-region**: Write/read both regions. Lowest downtime, highest complexity.

ஏன் ஒன்னை தேர்வு பண்ணுறோம்? RTO / RPO target பார்த்து.

RTO 5 min, RPO 0 வேணும்னா synchronous replication + automatic promotion தேவை. RTO 30 min ஏற்றுக்கொள்ளலாம்னா manual failover கூட போதும்.

### 5. Trade-offs

**Detection speed vs false positive.** Probe interval குறைச்சா வேகமா detect பண்ணலாம், ஆனால் transient network glitch-க்கு false failover ஆகும். Flapping ஆகும்.

**Consistency vs availability.** Synchronous replication failover-ல data loss குறைவு, ஆனால் latency அதிகம். Asynchronous replication-ல availability அதிகம், ஆனால் failover சமயம் recent writes lost ஆகலாம்.

**Cost vs complexity.** Failover க்கு duplicate infra, cross-region data transfer, health check system, automation எல்லாம் cost. Small team-க்கு over-engineering ஆகலாம்.

**Split brain.** Network partition ஆனால் primary + standby இரண்டும் active ஆகி தனித்தனியா writes ஏற்றுக்கொள்ளும். இது data corruption. Fencing / STONITH, quorum போன்ற mechanism தேவை.

ஒவ்வொரு failover solution-ம் புது failure mode உருவாக்கும். அதை design பண்ணத்தான் வேண்டும்.

### 6. Practical Example

Order service + Postgres.

Primary DB Chennai region AZ1, read replica AZ2-ல synchronous replication. API service 3 replicas behind ALB, 2 AZ-ல spread.

DB primary crash ஆனதும், Patroni / cloud managed failover standby-ஐ promote பண்ணும். Application connection pool auto retry பண்ணி new primary-க்கு reconnect ஆகும்.

API instance crash ஆனால், ALB health check fail ஆனதும் instance-ஐ pool-ல இருந்து remove பண்ணும். Kubernetes-ல
