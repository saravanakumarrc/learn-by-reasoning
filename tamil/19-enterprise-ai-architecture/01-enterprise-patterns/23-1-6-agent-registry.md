# Agent registry

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.6 — Enterprise patterns

## 1. Problem

உங்க enterprise-ல 50+ AI agents ஓடுது. Customer support agent, billing agent, fraud detection agent, RAG agent, summarization agent...

ஒரு request வரும்போது "இந்த வேலையை யார் பண்ணுவா?" என்று எப்படி தீர்மானிக்கிறீங்க?

Agent-ஐ hard-code பண்ணி விட முடியாது. புது agent deploy ஆனா, பழைய agent retire ஆனா, version மாறினா, capability மாறினா?

இல்லாமல் என்ன ஆகும்?

- Routing logic எல்லா service-லயும் scatter ஆகும்
- ஒரு agent down ஆனால் கண்டுபிடிக்க முடியாது
- Capability discovery இல்லாமல் wrong agent-க்கு request போய் fail ஆகும்
- Observability, auth, rate-limit எல்லாம் per agent manage பண்ண முடியாது

இதை தான் Agent registry தீர்க்குது.

## 2. Mental Model

Agent registry என்பது **service registry + capability catalog** இரண்டின் கலவை.

Service registry மாதிரி: யார் alive, எங்கே ஓடுது, health என்ன?

Capability catalog மாதிரி: இந்த agent என்ன திறமை வைத்திருக்கிறது, எந்த input format எடுக்கும், latency எவ்வளவு, cost எவ்வளவு, SLA என்ன?

ஒரு central source of truth. Orchestrator அல்லது Router இதை பார்த்து "இந்த task-க்கு சரியான agent யார்" என்று முடிவு செய்யும்.

## 3. How It Works

ஒவ்வொரு agent start ஆகும் போது registry-ல register பண்ணும்:

- agent id, version, endpoint
- capabilities: skills, tools, domains e.g. `billing.read`, `lang:ta`, `model:gpt-4o`
- constraints: max concurrency, cost per token, latency SLO
- metadata: owner team, deployment region, auth requirements

Heartbeat வந்துகொண்டே இருக்கும். Health check fail ஆனால் auto deregister.

Request வரும்போது:

1. Intent classify ஆகும்
2. Registry query: `capability = X AND region = IN AND latency < 500ms`
3. Policy apply: load, cost, canary
4. Route to chosen agent instance

Registry itself highly available ஆக இருக்க வேண்டும். Read-heavy. Cache ஆகி இருக்கும்.

## 4. Architectural Reasoning

எப்போது தேவை?

- Multiple teams agents build பண்ணும்போது
- Dynamic routing வேண்டும்: load based, cost based, A/B test
- Agents ephemeral, auto-scale ஆகும் போது
- Compliance & audit: யார் எந்த request handle பண்ணினார் என்று தெரிய வேண்டும்

Alternative என்ன?

- Hard-coded routing table: small system-க்கு ok, scale ஆகாது
- Service mesh discovery: location தெரியும், capability தெரியாது
- Central orchestrator with config DB: manual sync, stale data

Registry ஏன் தேர்வு? Decoupling. Agent deploy/retire ஆனாலும் caller மாற வேண்டாம்.

## 5. Trade-offs

**Consistency vs Availability:** Registry data stale ஆனால் wrong agent-க்கு route ஆகும். Strong consistency கொடுத்தால் latency. பெரும்பாலும் eventual consistency + local cache + TTL.

**Central point of failure:** Registry down ஆனால் routing முடியாது. Read replicas, cache, fallback static routing வேண்டும்.

**Complexity:** Registration, heartbeats, schema evolution, versioning. Team discipline வேண்டும்.

**Security:** Registry poisoning ஆனால் malicious agent register ஆகி traffic hijack ஆகும். mTLS, signed registration, authZ critical.

## 6. Practical Example

Enterprise support platform.

`support-router` ஒரு request வாங்குகிறது: "எனது invoice தொகை தவறாக காட்டுகிறது".

Intent = `billing.dispute`. Registry query:

```
capability.includes('billing.dispute') 
AND language = 'ta' 
AND model_cost < $0.01/req
AND healthy = true
```

Registry returns 3 agents:
- billing-agent-v2 prod-us, 120ms, cost low
- billing-agent-v2 prod-in, 60ms, cost low
- billing-agent-v1 prod-in, 80ms

Policy: prefer same region, latency <100ms. Route to prod-in v2.

Agent down ஆனால் heartbeat stop, registry remove, next request automatically next healthy instance-க்கு போகும்.

Observability: registry-ல எந்த agent எத்தனை request எடுத்தது, error rate என்ன என்று தெரியும்.

## 7. Reasoning Challenge

உங்களிடம் 20 agents இருக்கு. எல்லாம் `document.summary` capability வைத்திருக்கு. ஆனால் சில agents high accuracy, high cost. சில agents fast, low cost.

Customer tier gold vs silver என்று வேறுபாடு உண்டு. Gold user-க்கு accuracy முக்கியம், silver-க்கு cost முக்கியம்.

இந்த routing decision-ஐ நீங்கள் எங்கே வைப்பீர்கள்? Agent registry-ல மட்டும் metadata வைத்து policy engine வேறு? Registry-ல query time-ல filter செய்யலாமா? ஏன்?

## 8. Key Takeaways

- Agent registry என்பது discovery + capability catalog + health, routing-க்கு தேவையான single source of truth
- Hard-coded routing scale ஆகாது, registry dynamic discovery-ஐ enable பண்ணும்
- Registry availability முக்கியம், stale data விட no data மோசமாக இருக்கலாம்
- Security, versioning, observability registry design-ல முதலில் வர வேண்டும்
