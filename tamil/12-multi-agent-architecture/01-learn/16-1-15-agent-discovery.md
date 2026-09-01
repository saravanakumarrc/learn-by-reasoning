# Agent discovery

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.15 — Learn

## 1. Problem

நீங்கள் ஒரு Multi-Agent system கட்டுகிறீர்கள். 
Order agent, Inventory agent, Payment agent, Notification agent, Fraud agent என்று 10-20 agents இருக்கு.

ஒரு request வரும்போது, 
*யார் இதை handle பண்ணுவார்?*
*யாரிடம் இன்னும் capability இருக்கு?*
*எந்த agent online-ல இருக்கு? எது overloaded?*

இதை hard-code பண்ணினால் என்ன ஆகும்? New agent deploy பண்ணும்போது எல்லா caller-களையும் மாற்ற வேண்டும். Agent crash ஆனால் traffic அங்கேயே போய் fail ஆகும். Scale பண்ண முடியாது.

இதுதான் Agent discovery பிரச்சனை. System-க்கு தெரிய வேண்டும்: **who is who, where are they, what can they do, are they healthy?**

## 2. Mental Model

Agent discovery என்பது ஒரு phonebook + health-check + capability registry.

ஒரு service mesh-ல போல்தான். ஒரு service இன்னொரு service-ஐ கண்டுபிடிக்க service registry-யை பார்க்கிறது. Agent discovery அதே வேலை, ஆனால் agents dynamic-ஆ வரும், போகும், capability evolve ஆகும்.

Mental model: **Agents themselves advertise themselves. Others query a central source of truth.**

## 3. How It Works

இரண்டு பேஸிக் பாட்டர்ன்கள் உள்ளன.

**a) Pull-based discovery**
Agent ஆரம்பிக்கும்போது registry-க்கு register செய்கிறது. Heartbeat அனுப்புகிறது. Orchestrator / other agents registry-யை query பண்ணி list எடுக்கிறது.
`agent -> register -> registry -> query -> caller`

**b) Push-based / gossip**
Agents ஒன்றுக்கொன்று peer-to-peer அறிமுகப்படுத்துகின்றன. Service mesh sidecar போல.

Practically, பெரும்பாலும் hybrid பயன்படுத்துவோம்:
* Registration with metadata: agent id, capabilities, version, endpoint, load, region
* Health check: liveness / readiness
* Lease / TTL: agent die ஆனால் auto remove
* Query API: `find agents where capability = "payment" AND region = "in"`

இது Consul, etcd, NATS discovery, Kubernetes endpoints போலவே வேலை செய்யும். Agent-specific metadata மட்டும் கூடுதல்.

## 4. Architectural Reasoning

எப்போது தேவை?

* Agents dynamically scale ஆகும்போது
* Capability-based routing தேவைப்படும்போது. எ.கா. `language=tamil` agent, `model=gpt-4` agent
* Fault tolerance தேவைப்படும்போது. Crash ஆன agent-க்கு request போகக்கூடாது
* Multi-tenant / multi-region deployment இருக்கும்போது

Alternatives:
* **Static config / hard-coded**: சிறிய prototype-க்கு OK. 3 agents வரை. அதுக்கு மேல் maintenance nightmare.
* **Central orchestrator knows all**: Simple ஆனால் orchestrator single point of failure, bottleneck.
* **Decentralized gossip**: Highly resilient, ஆனால் complex, eventual consistency.

Architect ஏன் choose பண்ணுவார்? 
System boundary தெளிவாக வைக்க, coupling குறைக்க. Caller agent-க்கு callee agent எங்கே இருக்கிறது என்று தெரிய வேண்டாம். Only capability தெரிந்தால் போதும்.

## 5. Trade-offs

**Central registry vs Decentralized**
Central registry simple ஆனால் availability risk. Decentralized resilient ஆனால் discovery latency அதிகம், consistency குறைவு.

**Strong consistency vs Availability**
Registry எப்போதும் up-to-date-ஆ இருக்க வேண்டுமா? Network partition-ல agents register ஆக முடியாமல் போகலாம். AP vs CP trade-off.

**Discovery freshness**
Heartbeat interval குறைவாக இருந்தால் stale entry குறைவு, ஆனால் network chatter அதிகம். Cost vs correctness.

**Security**
எவர் வேண்டுமானாலும் registry-ல register செய்துவிட்டால்? Impersonation. Mutual TLS, token-based authentication தேவை. Capability metadata trust எப்படி verify பண்ணுவது?

Failure mode: Registry itself down ஆனால் new agent join முடியாது, existing agents stale. அதனால் registry-யை highly available ஆக்க வேண்டும், or local cache + stale tolerance.

## 6. Practical Example

Enterprise order fulfillment system.

`OrderRouter agent` ஒரு order வாங்குகிறது. அதற்கு தேவை:
* Inventory check agent
* Payment agent
* Fraud check agent

Router registry-யை கேட்கிறது: `capability=inventory AND region=in AND load < 70`

Registry 3 healthy agents தருகிறது. Router load-based round robin பண்ணி ஒன்றை தேர்வு செய்கிறது.

Inventory agent crash ஆனால், heartbeat miss ஆகிறது. TTL expire ஆகி registry-ல இருந்து remove ஆகிறது. Router automatically next healthy agent-க்கு route செய்கிறது. No manual config change.

New Tamil support agent deploy ஆகும்போது, அது தானாக registry-ல register செய்துகொள்கிறது. Router உடனே அதை கண்டுபிடித்து route செய்கிறது.

## 7. Reasoning Challenge

உங்களிடம் 50 agents உள்ளன. ஒவ்வொன்றும் 5 விதமான capabilities expose செய்கிறது. Agents spot instances-ல run ஆகின்றன, எப்போது வேண்டுமானாலும் terminate ஆகலாம். 

Latency sensitive workflow, discovery call ஒவ்வொரு request-க்கும் செய்யக்கூடாது. 

இங்கே discovery design எப்படி இருக்கும்? Central registry-யை cache பண்ணுவீர்களா? TTL எவ்வளவு வைப்பீர்கள்? Stale agent-க்கு request போனால் என்ன recovery mechanism வைப்பீர்கள்?

## 8. Key Takeaways

* Agent discovery = dynamic phonebook + health + capability metadata
* Hard-coding breaks at scale. Registry decouples who from where
* Trade-off: consistency vs availability, freshness vs chatter, central vs decentralized
* Discovery failure is silent killer: stale entries lead to failed calls, retry storms
* Design for registration, heartbeat, TTL, secure authentication from day one

இதை புரிஞ்சா, Multi-Agent system-ஐ scale பண்ணுவது, failover பண்ணுவது, capability-based routing பண்ணுவது எல்லாம் reasoning-ஆக வரும்.
