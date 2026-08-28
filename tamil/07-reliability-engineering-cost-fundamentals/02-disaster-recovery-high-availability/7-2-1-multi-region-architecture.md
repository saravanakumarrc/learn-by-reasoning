# Multi-region architecture

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.2.1 — Disaster recovery & high availability

## Problem

உங்கள் service ஒரே region-ல ஓடுது. Mumbai region. ஒரு நாள் network partition வருது, provider outage வருது, அல்லது முழு region-மே down ஆகுது.

இப்போ என்ன ஆகும்?

Users-க்கு 100% downtime. API timeout, checkout fail, data loss. Business impact ஒரு நிமிஷத்துக்கு லட்சக்கணக்கில்.

அதே நேரம் உங்க users global-ஆ இருக்காங்க. US-ல இருந்து call பண்ணும்போது Mumbai-க்கு latency 250ms+. Page load slow ஆகுது, conversion drop ஆகுது.

Single region உங்களுக்கு இரண்டு பிரச்சனை தருது:
1. Availability இல்லை — region fail ஆனா service முடிஞ்சது
2. Latency / user experience மோசம் — தூரத்தில் இருக்கும் users கஷ்டப்படுறாங்க

இந்த pain தான் multi-region architecture-ஐ கொண்டு வந்தது.

## Mental Model

Multi-region என்பது **உங்கள் system-ஐ இரண்டு அல்லது அதற்கு மேற்பட்ட geographic regions-ல run பண்ணுவது**.

ஒவ்வொரு region-ம் independent infrastructure, compute, storage வச்சிருக்கும். Regions-க்கு இடையே data replicate ஆகும்.

எளிமையாக: உங்களிடம் ஒரே shop இல்லை, Chennai-ல ஒன்று, Frankfurt-ல ஒன்று, US-East-ல ஒன்று. Customer எங்க இருந்தாலும் அருகில் உள்ள shop-க்கு route ஆகிறார். ஒரு shop எரிஞ்சாலும் மற்ற shop வேலை செய்யும்.

இரண்டு முக்கிய மாடல்:

* **Active-Passive**: Primary region active, secondary region standby. Failover மட்டும்.
* **Active-Active**: இரண்டு regions-மே traffic-ஐ serve பண்ணும். Users எப்போதும் closest region-க்கு போவார்கள்.

## How It Works

Core capability replication + routing.

**Data replication**: Database, cache, object storage region-க்கு region replicate ஆக வேண்டும். Synchronous replication latency குறைவு ஆனால் cross-region latency add ஆகும். Asynchronous replication performance கெடுக்காது ஆனால் RPO > 0.

**Traffic routing**: Global DNS / latency-based routing. Route53, Cloudflare, anycast IP மூலம் user-ஐ nearest healthy region-க்கு அனுப்புவது.

**Failover**: Health checks fail ஆனால் traffic automatic-ஆ மாற்றுதல். Active-passive-ல promotion தேவை. Active-active-ல traffic drain செய்து unhealthy region-ஐ isolate பண்ணுவது.

Implementation-ல மூன்று layer தேவை:
1. Application layer stateless ஆக இருக்க வேண்டும், அல்லது session replicate ஆக வேண்டும்
2. Data layer multi-region consistency model தேர்வு செய்ய வேண்டும்
3. Control plane: failover policy, RTO/RPO definition

## Architectural Reasoning

Multi-region எப்போது useful?

* SLA 99.99%+ வேண்டும், region outage-ஐ tolerate செய்ய வேண்டும்
* Global users, latency sensitive
* Regulatory data residency requirement உள்ளது

Constraint-ஐ பார்க்கணும்:

* **Consistency**: Cross-region write latency 50-150ms. Strong consistency வைக்க முடியாது. அதனால் most systems eventual consistency ஏற்றுக்கொள்கின்றன.
* **Cost**: Data transfer, replication, duplicate compute. Cost 2-3x ஆகும்.
* **Complexity**: Split-brain, clock skew, conflict resolution. Operability கடினம்.

Alternatives:
Single region + good DR backup: cost குறைவு, ஆனால் RTO hours. Multi-region தேவை இல்லாத small business-க்கு போதும்.

Active-passive vs active-active:
Active-passive simple, cost குறைவு, failover slow. Active-active complex ஆனால் low latency + no downtime failover.

## Trade-offs

**Availability vs Consistency**: Multi-region active-active-ல write எங்கு போகிறது? If you write to local region, other region stale ஆகும். Read-your-writes guarantee கொடுக்க வேண்டுமென்றால் routing logic சிக்கலாகும்.

**Cost vs Resilience**: Every region-ல duplicate fleet, storage, network egress. Data transfer inter-region expensive. Small team-க்கு operational overhead அதிகம்.

**Latency vs Data freshness**: Synchronous replication latency add செய்யும். Asynchronous replication stale reads risk.

**Failure modes**: Split-brain. Network partition-ல இரண்டு regions-ம் write accept பண்ணினால் data conflict. Fencing, leader election, quorum தேவை. Failover மெதுவாக நடந்தால் users stuck ஆவார்கள். DNS TTL காரணமாக old IP-க்கு திரும்புவார்கள்.

## Practical Example

Indian bank with customers in India, US, Europe.

Core accounts DB PostgreSQL with async replication to US-East and Frankfurt. Writes always go to Mumbai primary. Reads for dashboard, statement from nearest read replica.

Checkout / payment API active-active with local Redis cache. Payment write must go to primary, so API route writes to Mumbai, reads locally.

DNS latency-based routing: in.in.yourbank.com -> Mumbai, us.yourbank.com -> US-East.

Region down ஆனால், health check fail -> DNS removes region. US users automatically go to Frankfurt. RPO ~ 1 min data loss possible due to async replication lag. RTO ~ 2-5 min DNS propagation.

Cost: 3x compute, inter-region data transfer ~ $10k/month. Ops team must run chaos drills quarterly.

## Reasoning Challenge

உங்களுக்கு SaaS product உள்ளது. Users India மற்றும் US. Writes 80% India-ல இருந்து. SLA 99.95%. Budget limited.

Active-active வைக்கலாமா? Active-passive போதுமா? Database synchronous replication வேண்டுமா asynchronous போதுமா?

எந்த constraint-ஐ முதலில் accept செய்வீர்கள் — latency, cost, அல்லது consistency? ஏன்?

## Key Takeaways

* Multi-region என்பது availability மற்றும் latency-க்கான தீர்வு, cost மற்றும் complexity-க்கான பிரச்சனை.
* Active-passive simple DR க்கு, active-active true global availability க்கு. Choice RTO/RPO target மற்றும் budget-ல இருந்து வரும்.
* Cross-region replication strong consistency கொடுக்காது. Write routing, conflict resolution திட்டமிட வேண்டும்.
* Failover automate பண்ணாமல் multi-region வேலை செய்யாது. DNS TTL, health checks, fencing எல்லாம் பார்க்க வ
