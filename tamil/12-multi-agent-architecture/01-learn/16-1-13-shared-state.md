# Shared state

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.13 — Learn

## 1. Problem

Multi-Agent Architecture-ல ஒவ்வொரு agent-ம் தனித்தனியாக வேலை பார்க்கிறது. ஒரு agent தகவலை தேடுகிறது, இன்னொரு agent அதை பயன்படுத்தி decision எடுக்கிறது, மூன்றாவது agent result-ஐ update செய்கிறது.

இப்போது கேள்வி: இந்த agents எல்லாம் ஒரே தகவலை எப்படி பார்க்கும்? ஒரு agent பார்த்த memory-ஐ இன்னொரு agent பார்க்க முடியுமா?

Shared state இல்லாமல் என்ன ஆகும்?
- Agent A ஒரு user profile-ஐ update செய்தது, Agent B இன்னும் பழைய copy-ஐ வைத்து decision எடுக்கும்.
- Duplicate work ஆகும். ஒரே task-ஐ இரண்டு agents ஒரே நேரத்தில் எடுத்துக்கொள்வார்கள்.
- Conversation context தொலையும். Agent சேர்ந்து ஒரு flow-ஐ build செய்ய முடியாது.

Shared state என்பது agents இடையே common ground உருவாக்குவதற்கான வழி.

## 2. Mental Model

Shared state என்பது agents-க்கான common whiteboard.

ஒவ்வொரு agent-ம் read/write செய்யக்கூடிய ஒரு central place. அங்கே facts, intermediate results, decisions, locks எல்லாம் வைக்கலாம்.

இது distributed system-ல shared database போலவே இருக்கிறது, ஆனால் agent context-க்கு optimize செய்யப்பட்டது.

## 3. How It Works

Agent ஒன்று ஒரு task-ஐ எடுக்கும்போது:
1. Shared state-ல இந்த task already taken-ஆ என்று check செய்யும்.
2. State-ல write செய்யும்: `task_id -> agent_id, status = in_progress`.
3. Work செய்த பிறகு result-ஐ state-ல update செய்யும்.
4. மற்ற agents அதே state-ஐ read செய்து current picture பார்க்கும்.

Implementation options:
- **Central store**: Postgres, Redis, DynamoDB. Simple, strong consistency கிடைக்கும்.
- **Event log**: Kafka / Event store. State என்பது events-இன் projection. Replay செய்யலாம்.
- **Agent memory bus**: Redis pub/sub, message queue. Real-time sync.

## 4. Architectural Reasoning

Shared state எப்போது தேவை?

- **Coordination தேவைப்படும்போது**: Agents தனித்தனியாக run ஆகும்போது duplicate work தடுக்க.
- **Multi-step workflow**: Agent 1 research செய்யும், Agent 2 summarize செய்யும். இடையில் state persist ஆக வேண்டும்.
- **Long-running context**: User session cross agent தொடர வேண்டும்.

Alternatives:
- **Stateless agents + external API call per request**: Simple, but no memory across agents.
- **Message passing only**: Agents message exchange செய்யும், ஆனால் global view இல்லை. Order மற்றும் consistency கஷ்டம்.
- **Shared state**: More coupling, but coordination easy.

ஏன் choose பண்ணுவீர்கள்? Agent system scale ஆகும்போது implicit coordination fail ஆகும். Explicit shared state வைத்தால் reasoning தெளிவாகும்.

## 5. Trade-offs

**Consistency vs Availability**
Shared state strong consistency வைத்தால் agents slow ஆகும், write contention வரும். Eventual consistency வைத்தால் stale read வரும். Agent decision தவறாகும்.

**Coupling vs Coordination**
State shared ஆனால் agents tightly coupled ஆகும். One store down ஆனால் எல்லா agents-ம் stuck ஆகும். Decentralized state less fragile ஆனால் coordination complex.

**Freshness vs Cost**
Real-time sync cost அதிகம். Polling செய்தால் latency வரும். Cache செய்தால் stale data.

**Failure modes**
- Race condition: இரண்டு agents ஒரே task-ஐ pick செய்யும். Need distributed lock / atomic compare-and-set.
- Partial update: Agent crash ஆனால் state inconsistent ஆகும். Heartbeat + lease timeout தேவை.
- Schema drift: Agents different version-ல state interpret செய்யும். Versioning தேவை.

## 6. Practical Example

Enterprise support agent system.

`TicketRouter` agent ticket-ஐ classify செய்கிறது. `ResearchAgent` knowledge base-ல தேடுகிறது. `ResponderAgent` reply draft செய்கிறது.

Shared state = Redis hash: `ticket:{id}`

```
status: routed | researching | drafting | done
assigned_agent: research-3
context: {customer_history, past_tickets}
research_result: ...
draft: ...
```

Router ticket-ஐ create செய்து state-ல `status=routed` set செய்கிறது. ResearchAgent state-ஐ poll செய்து `status=routed` இருக்கும் ticket-ஐ atomic-ஆக claim செய்கிறது. Result-ஐ write செய்கிறது. ResponderAgent அதை read செய்து draft செய்கிறது.

இல்லாமல் இருந்தால் ஒவ்வொரு agent-ம் தனியாக DB-ல query செய்து stale data வைத்து வேலை செய்யும்.

## 7. Reasoning Challenge

உங்களிடம் 3 agents உள்ளன: Planner, Executor, Evaluator. ஒரே user request-க்கு அவர்கள் sequence-ல வேலை செய்ய வேண்டும். Shared state-ஐ Redis-ல வைக்கிறீர்கள்.

Executor crash ஆன பிறகு state `in_progress` இல் stuck ஆகிறது. Planner மற்றொரு Executor-ஐ assign செய்ய வேண்டுமா? இதற்கு என்ன mechanism வேண்டும்? Trade-off என்ன?

## 8. Key Takeaways

- Shared state என்பது agents-க்கு common ground கொடுக்கிறது, coordination-க்கு தேவை.
- State design என்பது consistency, availability, cost இடையே trade-off.
- Race condition, stale read, partial failure முக்கிய failure modes.
- Every shared state decision creates coupling and operational complexity.
