# Agent communication

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.12 — Learn

## 1. Problem

ஒரு multi-agent system-ல் 3-4 agents இருக்கு. Planner agent ஒன்று, Researcher agent இன்னொன்று, Executor agent மூன்றாவது.

Planner சொல்கிறது: "User-க்கு quarterly report தேவை, data fetch பண்ணு, summarize பண்ணு, email அனுப்பு".

இப்போது இந்த agents ஒன்றுக்கொன்று எப்படி பேசும்?

அவை ஒன்றோடு ஒன்று direct function call பண்ணுமா? Shared memory-ல write பண்ணுமா? Message queue-ல message போடுமா? Chat-like turn பண்ணுமா?

இதை தவறாக design பண்ணினால் என்ன ஆகும்?

Agent A தன் context-ஐ முழுவதுமாக Agent B-க்கு கொடுத்துவிட்டால் B-க்கு token budget explode ஆகும். Agent B தன் output-ஐ unclear format-ல் கொடுத்தால் Agent C அதை interpret பண்ண முடியாது. ஒரு agent fail ஆனால் மற்றவை எப்படி தெரிந்து கொள்ளும்? Retry எப்படி? Timeout? 

**Core problem:** Independent, autonomous agents need to coordinate without tight coupling, while preserving context, reliability, and observability.

## 2. Mental Model

Agent communication என்பது distributed system-ல் services பேசுவதை போன்றது, ஆனால் payload என்பது unstructured natural language + structured data கலவை.

நினைத்துக் கொள்ளுங்கள்: agents என்பது **loosely coupled workers** ஆகும். அவர்கள் ஒரு **protocol** மூலம் பேசுகிறார்கள்.

மூன்று layer உள்ளது:

1. **Transport** - message எப்படி அனுப்பப்படும்? Direct RPC, message queue, shared log, chat history?
2. **Format / Protocol** - message என்ன shape-ல் இருக்கும்? Free text, JSON schema, tool call, function calling?
3. **Coordination** - யார் முதலில் பேசுவார்? Who decides next step? Central orchestrator vs peer-to-peer.

## 3. How It Works

Practically, agent-to-agent communication mostly happens இப்படி:

**a. Message passing with explicit contract**
Agent A → sends structured message to Agent B
```
{
  "role": "request",
  "task_id": "t123",
  "intent": "fetch_sales_data",
  "parameters": {"quarter": "Q2", "region": "APAC"},
  "expected_schema": {"revenue": "number", "units": "number"}
}
```
B returns:
```
{
  "role": "response",
  "task_id": "t123",
  "status": "success|partial|error",
  "data": {...},
  "confidence": 0.92
}
```

**b. Shared context store**
All agents read/write to a common memory / task state. இது event sourcing போல் வேலை செய்யும். ஒவ்வொரு agent-ம் state change-ஐ பார்த்து react செய்யும்.

**c. Orchestrator mediated**
Central controller ஒன்று agents-ஐ schedule செய்கிறது, messages route செய்கிறது. Agents ஒன்றுக்கொன்று நேரடியாக பேசுவதில்லை.

Transport-ஆக:
- Synchronous: HTTP RPC / function calling - low latency, tight coupling
- Asynchronous: message queue like Kafka / Redis Streams - decoupled, durable
- Persistent log: event bus - replay possible

## 4. Architectural Reasoning

**When does this become useful?**

Single agent-க்கு மேல் task complex ஆகும்போது. Planner-Researcher-Executor பிரிப்பு, tool use, human-in-the-loop, long-running workflows.

**What constraint it addresses?**

Coupling, context bloat, failure isolation, observability.

**Options:**

1. **Direct Call / Orchestrator**
Simple, fast, easy to trace. ஆனால் orchestrator single point of failure, scaling bottleneck.

2. **Peer-to-peer with message bus**
Agents independent, can scale individually. ஆனால் coordination complex, message schema maintenance தேவை.

3. **Shared memory / blackboard**
Implicit communication. Easy to add agents. ஆனால் race condition, unclear ownership.

**Architect decision rule:**
Short, deterministic workflow → Orchestrator + direct calls.
Long-running, event-driven, many agents → Message bus + schema contract.
Need audit/replay → Event log + immutable messages.

## 5. Trade-offs

**Latency vs Decoupling**
Synchronous call fast but caller blocked. Async decoupled ஆனால் latency and eventual consistency வரும்.

**Schema strictness vs Flexibility**
Strict JSON schema / Pydantic models → agents reliable, validation easy. ஆனால் LLM output-ஐ force பண்ண கடினம். Free text flexible ஆனால் parsing errors அதிகம்.

**Centralized vs Distributed coordination**
Orchestrator easy to reason, debugging simple. Peer-to-peer resilient, ஆனால் deadlocks, loops வரும். E.g., Agent A waits for B, B waits for A.

**Context size vs Accuracy**
Full history forward பண்ணினால் context rich ஆனால் token cost, latency அதிகம். Summary only forward பண்ணினால் cheap ஆனால் information loss.

Failure modes முக்கியம்:
- Message lost / duplicate → idempotency தேவை
- Agent returns malformed output → schema validation + retry with clarification
- Agent hangs → timeout + circuit breaker
- Agent drifts → versioned protocol, backward compatibility

## 6. Practical Example

Enterprise support automation:

User → Intake Agent → Triage Agent → Specialist Agent → Executor Agent → User

Intake Agent user message-ஐ parse பண்ணி `ticket` create செய்யும். Message format:
```
{ task_id, user_id, intent: "billing_issue", raw_text, extracted_entities }
```

Message bus-ல publish செய்யும்.

Triage Agent subscribe செய்து priority assign பண்ணி Specialist Agent-க்கு forward செய்யும். Specialist Agent research tool use பண்ணி answer draft பண்ணி Executor Agent-க்கு அனுப்பும்.

All messages written to durable log. If Specialist Agent fails, message requeued with backoff. Each agent logs task_id, so trace complete.

இங்கே communication contract clear ஆக இருப்பதால் agents replace பண்ணலாம், scale பண்ணலாம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு customer research workflow உள்ளது. Planner agent research plan create பண்ணும். 5 Researcher agents parallel-ல் different sources-ல் data fetch பண்ணும். Aggregator agent அவை எல்லாவற்றையும் combine பண்ணி final report கொடுக்கும்.

Researcher agents different speed-ல் complete ஆகும். Aggregator எப்போது start பண்ண வேண்டும்? Researcher-கள் partial results intermediate-ல் publish பண்ண வேண்டுமா? இதற்கு synchronous RPC போதுமா, அல்லது event bus தேவையா? ஏன்?

## 8. Key Takeaways

- Agent communication என்பது coupling, context, reliability பற்றிய design decision. Protocol இல்லாமல் system fragile ஆகும்.
- Transport தேர்வு workflow nature-ஐ depend செய்கிறது: short deterministic → orchestrator, long async → message bus.
- Structured contract + validation + idempotency இல்லாமல் multi-agent system production ready ஆகாது.
- Every communication choice creates trade-off: latency vs decoupling, flexibility vs reliability, central control vs peer autonomy.
