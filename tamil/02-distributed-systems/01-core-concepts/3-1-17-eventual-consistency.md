# Eventual consistency

> **Learning Path:** Distributed Systems
> **Section:** 3.1.17 — Core concepts

# Eventual consistency

## 1. Problem

உங்களுக்கு ஒரு global service இருக்கு. Users US, EU, Singapore-ல இருந்து access பண்றாங்க. Data 3 regions-ல replicate பண்ணியிருக்கீங்க.

ஒரு user profile update செய்யணும். Strong consistency வேணும்னா என்னாகும்?

Write-ஐ accept பண்ண முன், majority replicas-ல acknowledge வாங்கணும். அதாவது cross-region round trip போகணும். Latency 200-500ms ஆகும்.

இன்னும் மோசம்: network partition வந்தா? CAP theorem-ப்படி strong consistency + partition tolerance வைக்கணும்னா availability-வை கொடுக்க முடியாது. Write reject ஆகும், service down போல தெரியும்.

இது painful. Userக்கு "Save successful" காட்ட 1 second wait பண்ண முடியாது. Business-ம் 24x7 availability கேட்கும்.

இங்கே தான் eventual consistency வருது.

## 2. Mental Model

Eventual consistency என்பது: **நீங்கள் எழுதியது உடனே எல்லா replicas-லயும் தெரிய வேண்டும் என்று கட்டாயம் இல்லை. ஆனால், எந்த external interference இல்லாமல் போனால், காலப்போக்கில் எல்லா replicas-ம் ஒரே state-க்கு converge ஆகும்.**

அதாவது multiple notebooks-ல ஒரே தகவல் எழுதப்படுது. ஒருத்தர் உடனே எல்லா notebook-ஐயும் update பண்ண முடியாது. ஆனால் sync ஆகும்போது கடைசியில் எல்லாம் ஒத்துவரும்.

Guarantee இல்லை: *when* என்பது தெரியாது. ஆனால் *will* என்பது guarantee.

## 3. How It Works

System ஒரு write-ஐ local replica-ல accept பண்ணி, user-க்கு fast ack கொடுக்கும். பிறகு அந்த update asynchronous-ஆக gossip அல்லது replication log மூலம் மற்ற replicas-க்கு propagate ஆகும்.

Read எந்த replica-ல வந்தாலும் கிடைக்கும். அது latest update-ஐ பார்க்கலாம், கொஞ்சம் பழையதை பார்க்கலாம்.

Conflict வரும் போது resolution rule தேவை:
- last-write-wins with vector clock / timestamp
- application-level merge
- CRDT for commutative operations

Implementation heavy இல்லை. Key idea: accept write locally, propagate later.

## 4. Architectural Reasoning

எப்போது useful?

- **Low latency முக்கியம், perfect freshness அவசியமில்லை.** Social feed, product catalog, user profile.
- **High write throughput தேவை.** Coordinated write bottleneck ஆகும்.
- **Partition tolerance + availability முக்கியம்.** Multi-region deploy.

Alternatives:
- Strong consistency: read-your-writes, monotonic reads. Linearizable DB.
- Causal consistency: more guarantee than eventual, less cost than strong.

Architect choose eventual consistency when:
Business can tolerate temporary staleness. Example: inventory count 2 sec late acceptable, but checkout should not fail due to cross-region latency.

Decision consequence: application layer-ல stale read handle பண்ண வேண்டும். UI-ல "might be outdated" pattern.

## 5. Trade-offs

**Availability vs Freshness.** Write always succeeds locally. Read may be stale.

**Simplicity vs Correctness.** No coordination means simpler ops, higher throughput. ஆனால் bugs subtle ஆகும்.

**Failure modes:** Read stale data, write lost during replica crash before replication, conflicts need merge logic.

**Operability:** Monitoring replication lag முக்கியம். Lag எவ்வளவு நேரம், எந்த keys affected என்பது தெரிய வேண்டும்.

Every solution creates new problem: eventual consistency gives you availability, ஆனால் application logic இப்போது inconsistency-ஐ handle பண்ண வேண்டும்.

## 6. Practical Example

E-commerce product price update.

Price service 3 regions-ல run ஆகுது. Marketing team EU-ல price change பண்ணும்போது, அந்த write local EU replica-ல accept ஆகும், 50ms-ல user-க்கு success.

US replica-க்கு propagation 800ms எடுக்கும்.

ஒரு US user அதே நேரத்தில் product page open பண்ணா, old price தெரியும். 1 sec கழித்து refresh பண்ணா new price தெரியும்.

இது acceptable. Customer experience-க்கு price mismatch 1 sec ஆகவே தெரியாது. ஆனால் checkout flow-ல final price fetch-ஐ strongly consistent source-ல இருந்து செய்யலாம்.

இதே pattern social media likes, follower count, search index-ல பயன்படுத்தப்படுது.

## 7. Reasoning Challenge

உங்களிடம் global chat app இருக்கு. Messages write ஆனதும் அனைவருக்கும் உடனே தெரிய வேண்டும் என்று விரும்புகிறீர்கள். ஆனால் network partition ஆனாலும் app online இருக்க வேண்டும்.

Message delivery order-ல eventual consistency போதுமா? அல்லது causal consistency தேவையா? எந்த read pattern-ல stale read தீங்கு செய்யும்?

நீங்கள் எந்த consistency level தேர்வு செய்வீர்கள், எதற்காக?

## 8. Key Takeaways

- Eventual consistency என்பது availability-க்காக freshness-ஐ தியாகம் செய்வது.
- Writes fast ஆக accept ஆகும், propagation asynchronous.
- Application-க்கு stale reads, conflicts, merge logic handle பண்ணும் பொறுப்பு வரும்.
- Use it when latency, partition tolerance முக்கியம், மற்றும் business temporary staleness தாங்கும்.
