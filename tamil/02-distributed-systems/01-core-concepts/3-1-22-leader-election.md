# Leader election

> **Learning Path:** Distributed Systems
> **Section:** 3.1.22 — Core concepts

### Problem

ஒரு distributed system-ல 3 replicas இருக்கு. எழுத்து operations-க்கு ஒரே source of truth வேண்டும். அதனால் ஒரு node-ஐ primary/leader ஆக்கி மற்றவை follower ஆக இருக்கும்.

Leader crash ஆனால் என்ன ஆகும்? Writes stop ஆகும். New leader வராமல் system stuck ஆகும். Manual intervention வேண்டும் என்றால் SLA போய்விடும்.

அதனால் தேவை: **leader இல்லாத போது automatic ஆக ஒரு புது leader-ஐ தேர்ந்தெடுக்க வேண்டும்.** மேலும் எல்லா nodes-க்கும் அதே leader தெரிய வேண்டும்.

இதுவே leader election-ன் root problem.

### Mental Model

Leader election என்பது ஒரு group-ல் இருக்கும் nodes-க்கு **who is in charge now** என்பதை ஒத்திசைவாக தீர்மானிப்பது.

அணி விளையாட்டில் captain திடீரென கீழே விழுந்தால் அடுத்த captain-ஐ உடனடியாக தேர்வு செய்ய வேண்டும். ஆனால் இரண்டு captain இருந்தால் அணி குழம்பும். அதே split-brain பிரச்சனை.

ஒரு leader மட்டும் active, மற்றவை standby. Leader failure detect ஆனதும் election trigger ஆகும். பெரும்பாலும் **quorum** அடிப்படையில் vote நடக்கும்.

### How It Works

Core idea மூன்று விஷயம்:

1. **Failure detection**: Leader-ல இருந்து heartbeat வரவில்லை என்றால் follower timeout ஆகி candidate ஆக மாறும்.
2. **Election**: Candidate ஒரு term ஐ start செய்து மற்ற nodes-ஐ vote கேட்கும். Majority vote வந்தால் leader ஆகிறது.
3. **Stabilization**: Leader திரும்ப வந்தாலும் term பழையது என்பதால் follower ஆகவே இருக்கும்.

Raft இதை சுத்தமாக செய்கிறது. Term என்பது logical clock. Candidate தனக்கு சமீபத்திய log இருந்தால் மட்டுமே vote பெறும். இது safety க்கு உதவும்.

ZooKeeper-ல Zab protocol இருக்கும். etcd Raft-ஐ உபயோகிக்கிறது. Bully algorithm போன்ற simple வழிகள் உள்ளன, ஆனால் production-ல Raft போன்ற quorum-based protocol தான் common.

எல்லா node-க்கும் same view வர வேண்டும் என்பதற்கு **majority quorum** தேவை. 5 nodes இருந்தால் 3 vote போதும்.

### Architectural Reasoning

Leader election எப்போது தேவை?

* Single writer constraint உள்ள distributed state machine: database primary, etcd, Consul, Kafka controller.
* Coordination தேவைப்படும் தருணங்கள்: distributed lock, leader for shard assignment.
* Failover automatic ஆக வேண்டும், manual intervention வேண்டாம்.

Alternative என்ன? Static leader, manual failover, அல்லது leader இல்லாத fully decentralized design.

Static leader simple ஆனால் downtime அதிகம். Manual failover SLA-க்கு ஆகாது. Fully decentralized சில வேலைகளுக்கு சாத்தியம் இல்லை, எ.கா. linearizable writes.

அதனால் architect தேர்வு செய்வது: **high availability வேண்டும், ஆனால் split-brain ஆகக்கூடாது என்றால் quorum-based leader election தான் பதில்.**

### Trade-offs

**Availability vs Safety**: Network partition ஆனால் majority இல்லாத பகுதியில் leader தேர்ந்தெடுக்க முடியாது. System unavailable ஆகும், ஆனால் split-brain தடுக்கப்படும். இது safety first design.

**Detection latency vs False positive**: Heartbeat timeout குறைவாக வைத்தால் fast failover, ஆனால் transient network glitch-ல் unnecessary election வரும். Election storm வரும். Timeout அதிகம் என்றால் failover slow.

**Complexity vs Operability**: Leader election கொண்டு வருவது operational complexity அதிகரிக்கும். Logs, terms, votes, pre-vote, leadership transfer என பல விஷயங்கள். ஆனால் manual intervention குறையும்.

**Split-brain**: இதுதான் மிகப்பெரிய failure mode. Two partitions ஒவ்வொன்றிலும் majority இருந்தால்? Quorum-ன் காரணமாக ஒரே partition தான் leader தேர்வு செய்யும். Fencing mechanism வேண்டும், பழைய leader-ஐ stop செய்ய வேண்டும்.

### Practical Example

நீங்கள் ஒரு multi-AZ PostgreSQL cluster ஐ Patroni + etcd உடன் run செய்கிறீர்கள்.

Primary node leader ஆக இருக்கிறது. Follower-கள் streaming replication செய்கின்றன. etcd cluster Raft-ஐ உபயோகித்து leader election நடத்துகிறது.

Primary AZ-ல network partition ஆகிறது. Heartbeat 10 sec timeout. 2 follower AZ-கள் quorum பெற்று புதிய primary-ஐ தேர்ந்தெடுக்கின்றன. பழைய primary fencing செய்யப்பட்டு writes stop ஆகின்றன.

Result: 10-15 sec downtime, ஆனால் data loss இல்லை, split-brain இ
