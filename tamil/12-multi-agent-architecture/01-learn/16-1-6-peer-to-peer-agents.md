# Peer-to-peer agents

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.6 — Learn

## 1. Problem

உங்களிடம் 10-20 agents இருக்கு. எல்லாம் LLM-based. ஒரு central orchestrator இருந்து "நீ task எடு, நீ result கொடு" என்று command பண்ணுகிறீர்கள்.

அது வேலை செய்யுமா? சிறிய scale-ல் செய்யும். ஆனால் scale ஆகும்போது என்ன பிரச்சனை வரும்?

Orchestrator ஒரு single point of failure ஆகிறது. ஒரு agent slow ஆனால் அனைத்து flow-ம் block ஆகிறது. Agents ஒன்றுக்கொன்று தேவையான context-ஐ தெரிந்துகொள்ள orchestrator வழியாகத்தான் போக வேண்டும். Latency அதிகரிக்கும். Cost அதிகரிக்கும்.

மேலும் real world-ல் agents எப்போதும் ஒரே மாதிரி இருப்பதில்லை. சில agents data access பண்ணும், சில reasoning பண்ணும், சில tools கொண்டிருக்கும். ஒவ்வொருவருக்கும் வேறு availability, rate limit, cost.

> "What problem became painful enough?" Central control doesn't scale, creates bottleneck, and hides local knowledge.

அதற்காக வருவது peer-to-peer agents.

## 2. Mental Model

Peer-to-peer agents என்பது ஒவ்வொரு agent-ம் சம peer. யாரும் மேலதிகாரி அல்ல.

ஒவ்வொரு agent-ம் தனக்கு தெரிந்த task-ஐ செய்யும், தனக்கு தெரியாததை தானே தேர்ந்தெடுத்த peer-க்கு delegate பண்ணும். Message பரிமாறிக்கொள்வது direct, orchestrator வழியாக அல்ல.

இது ஒரு distributed system-ல் nodes போல. ஒரு node down ஆனாலும் மற்றவை தொடரும்.

## 3. How It Works

ஒவ்வொரு agent-க்கும் 3 விஷயங்கள் தேவை:

**1. Identity & Capability Advertisement:** "நான் யார், என்ன செய்ய முடியும்" என்பதை broadcast செய்யும். Skill, tools, current load, latency.

**2. Peer Discovery:** தனக்கு தேவையான capability கொண்ட peer-ஐ கண்டுபிடிக்கும். இது gossip protocol, DHT, அல்லது shared registry மூலம் நடக்கலாம். ஆனால் routing decision local.

**3. Direct Communication:** Agent A -> Agent B என direct message, request-response அல்லது async event.

ஒரு task வரும்போது:
Agent A task-ஐ பார்க்கிறது → தன்னால் முடியுமா? → முடியாவிட்டால் capability match ஆகும் peer-ஐ தேடு → delegate → result-ஐ combine செய்.

No central scheduler. ஒவ்வொரு agent-மும் local reasoning மூலம் next step தீர்மானிக்கிறது.

## 4. Architectural Reasoning

Peer-to-peer எப்போது useful?

* **Heterogeneous agents:** வெவ்வேறு specialization உள்ள agents. ஒவ்வொருவரும் தங்களுக்கான domain knowledge வைத்திருக்கிறார்கள்.
* **High throughput, low latency requirement:** Central orchestrator queue-க்கு wait செய்ய வேண்டாம்.
* **Fault tolerance தேவை:** ஒரு agent fail ஆனாலும் system தொடர வேண்டும்.
* **Dynamic membership:** Agents அடிக்கடி join/leave ஆகின்றன. Auto-scale ஆக வேண்டும்.

Alternative என்ன? Central orchestrator / hub-and-spoke.

Hub-and-spoke simple, predictable, easy to debug. ஆனால் bottleneck, single point of failure, orchestrator complexity grows with agents.

Peer-to-peer trade-off: control குறைகிறது, coordination கடினம்.

## 5. Trade-offs

**Scalability vs Coordination Complexity:** Peer-to-peer horizontally scale ஆகும். ஆனால் "who does what" என்பதை coordinate செய்வது கடினம். Deadlock, circular delegation நடக்கலாம்.

**Fault tolerance vs Consistency:** Agent down ஆனாலும் மற்றவை தொடரும். ஆனால் global state consistent ஆக வைத்திருப்பது கடினம். Eventual consistency தேவை.

**Autonomy vs Observability:** ஒவ்வொரு agent-ம் தன்னிச்சையாக முடிவெடுக்கிறது. Debug பண்ணும்போது "ஏன் இந்த agent அதற்கு அனுப்பினது?" என்று trace கடினம்.

**Failure modes:** Message loss, peer unreachable, stale capability info, infinite delegation loop. Retry logic, timeout, idempotency மிக முக்கியம்.

## 6. Practical Example

Enterprise support automation.

Agent A: Ticket triage
Agent B: Knowledge base RAG
Agent C: Database query agent
Agent D: Escalation & human handoff

Central orchestrator இல்லை.

Customer query வருகிறது → Agent A receive செய்கிறது → intent extract → தனக்கு தெரியாத technical detail வேண்டும் என்றால் direct message-ல் Agent B-க்கு அனுப்புகிறது. Agent B vector DB-ல் search செய்து answer தருகிறது. Agent A result-ஐ summarize செய்து user-க்கு தருகிறது.

Database lookup தேவைப்பட்டால் Agent A direct-ஆக Agent C-க்கு delegate செய்கிறது. C returns data, A combines.

ஒரு agent overload ஆனால் அதன் capability advertisement-ல் load high என்று update செய்யும். மற்ற agents அதற்கு அனுப்பாமல் வேறு peer-ஐ தேர்வு செய்யும்.

## 7. Reasoning Challenge

உங்களிடம் 50 agents இருக்கு. சில agents data-sensitive, சில public. Peer-to-peer network-ல் எந்த agent எந்த peer-க்கு data அனுப்பலாம் என்பதை எப்படி control செய்வீர்கள்? Central policy இல்லாமல் privacy மற்றும் security எப்படி enforce செய்வது?

நீங்கள் என்ன mechanism வைப்பீர்கள்? Capability advertisement-ல் trust score, policy tag, அல்லது message routing-ல் encryption & access control?

## 8. Key Takeaways

* Peer-to-peer agents bottleneck-ஐ அகற்றுகிறது, ஆனால் coordination-ஐ agent-க்கு மாற்றுகிறது.
* ஒவ்வொரு agent-மும் தன்னுடைய capability, load, policy-ஐ advertise செய்து local decision எடுக்க வேண்டும்.
* Scale, fault tolerance கிடைக்கும். Observability, consistent global view கடினம்.
* Real architecture-ல் hybrid பொதுவானது: light coordinator for discovery + peer-to-peer for execution.
