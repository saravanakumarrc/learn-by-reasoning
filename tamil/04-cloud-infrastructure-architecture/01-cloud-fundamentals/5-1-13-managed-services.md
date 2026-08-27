# Managed services

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.1.13 — Cloud fundamentals

# Managed services

## 1. Problem

நீங்கள் ஒரு service launch பண்ண வேண்டும். அதுக்கு PostgreSQL வேண்டும்.

Self-manage பண்ணினால் என்ன நடக்கும்?
OS install, Postgres install, config tune பண்ணணும். Security patch வரும், downtime window பார்த்து apply பண்ணணும். Disk full ஆனால் alert வரும். Backup எடுக்கணும், restore test பண்ணணும். Traffic grow ஆனால் read replica add பண்ணணும். Node crash ஆனால் failover automate பண்ணணும்.

இது எல்லாம் உங்கள் product logic இல்லை. இது undifferentiated heavy lifting.

Team size 3-5 engineers என்றால், ஒருத்தர் முழுக்க database ops பார்க்க வேண்டும். அது cost, slow down delivery, மற்றும் on-call burnout create பண்ணும்.

இங்கே தான் pain point வருகிறது: **you need capability, not servers.**

## 2. Mental Model

Managed service என்பது cloud provider உங்களுக்காக control plane ஓட வைக்கிறார். நீங்கள் data plane மட்டும் use பண்ணுவீர்கள்.

Analogy: நீங்கள் வீடு கட்ட வேண்டாம், flat rent பண்ணுகிறீர்கள். Maintenance, security, painting provider பார்த்துக்கொள்வார். நீங்கள் உள்ளே furniture வைத்துக்கொள்ளலாம்.

Provider promise பண்ணுவது: availability, patching, autoscaling, backup, monitoring. நீங்கள் promise பண்ணுவது: data, schema, access policy.

## 3. How It Works

Provider இரண்டு layer வைத்திருப்பார்:

* **Control plane**: cluster provisioning, version upgrade, failover, scaling, patching, metrics. இது provider own code.
* **Data plane**: உங்கள் actual database nodes, storage, network.

நீங்கள் API / console மூலம் request பண்ணுவீர்கள். Provider control plane அதை enforce பண்ணும்.

```
Client App -> API call
      |
      v
Managed Service API
      |
      v
Provider Control Plane -> Data Plane (your DB nodes)
```

நீங்கள் OS patch பார்க்க வேண்டாம். Provider maintenance windowல் rolling upgrade பண்ணுவார். HA என்பது multi-AZ replica automatic.

## 4. Architectural Reasoning

Managed service choose பண்ணுவது இது கேள்விக்கு பதில்:

* இந்த component எங்கள் core differentiation ஆ?
* Ops burden அதிகமா, value low-ஆ?

Database, cache, message queue, object storage, Kubernetes control plane, managed AI inference போன்றவை பொதுவாக managed ஆக இருப்பது நல்லது.

நீங்கள் choose பண்ணும்போது:

* **Constraint**: team size, on-call capacity, latency sensitivity, compliance.
* **Options**: self-managed open source, managed open source, fully managed proprietary.
* **Decision**: managed service = ops cost down, time-to-market up.
* **Consequence**: less control over internals, config knobs limit ஆகலாம்.

## 5. Trade-offs

**Operational burden vs control**
Managed: patching, HA, backup provider handle. நீங்கள் config tuning depth குறையும். Custom kernel patch வேண்டுமா? சாத்தியம் இல்லை.

**Speed vs lock-in**
Managed service quickly spin up. ஆனால் API, IAM integration provider specific ஆகும். Migration cost உருவாகும். Data egress cost கவனிக்க வேண்டும்.

**Cost predictability**
Small scale-ல் managed cheaper: no DBA hire. Large scale-ல் self-managed can be cheaper per unit, ஆனால் hidden cost: people, incident cost, downtime.

**Failure modes**
Provider outage உங்கள் outage. Multi-region strategy தேவை. Provider control plane bug உங்களால் fix பண்ண முடியாது. SLA மட்டுமே உங்கள் safety net.

## 6. Practical Example

Enterprise SaaS, user activity events store பண்ண வேண்டும்.

Option A: Self-managed Kafka on EC2. 3 brokers, ZooKeeper, monitoring, disk management, partition rebalancing manual.

Option B: Managed Kafka / MSK.

Team 4 engineers. Feature delivery priority high. On-call already database and API.

Decision: Managed Kafka. Provider autoscaling, broker replacement, patching handle பண்ணுகிறார். நீங்கள் topic design, consumer group, retention policy மட்டும் handle பண்ணுவீர்கள்.

Trade-off ஏற்பட்டது: cost per hour high, custom JMX tuning limited. ஆனால் 2 engineers full-time ops save ஆனது.

இது product speed-க்கு justify ஆகும்.

## 7. Reasoning Challenge

உங்களுக்கு logs & search தேவை. Daily 2TB ingestion. Team-ல் DevOps engineer ஒருவர் மட்டும். Compliance காரணமாக data region lock வேண்டும்.

Managed OpenSearch vs self-hosted Elasticsearch on Kubernetes.

எது தேர்வு? ஏன்? என்ன trade-off accept பண்ணுவீர்கள்?

## 8. Key Takeaways

* Managed service என்பது capability rent பண்ணுவது, infrastructure own பண்ணுவது அல்ல.
* Core differentiation இல்லாத components-க்கு managed
