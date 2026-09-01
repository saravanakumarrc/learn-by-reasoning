# Persistence

> **Learning Path:** AI Orchestration
> **Section:** 17.1.6 — LangGraph concepts

### 1. Problem

LangGraph-ல ஒரு agent workflow ஓடிக்கிட்டு இருக்கு. 5 steps: retrieve → think → call tool → decide → respond.

நடுவுல step 3-ல் tool call பண்ணும்போது service down ஆகிடுச்சு. அல்லது user session close ஆகிடுச்சு. அல்லது pod restart ஆகிடுச்சு.

அடுத்த request வந்தா, workflow முதல்ல இருந்து மறுபடியும் start ஆகுதா? முந்தைய state எல்லாம் போயிடுச்சா?

இதுதான் painful point. Stateful multi-step execution-ஐ in-memory வச்சுக்கிட்டா, process die ஆனால் எல்லாம் lost.

AI Orchestration-ல agent என்பது long-running, non-deterministic, branching ஆக இருக்கும். நீங்கள் ஒரு conversation-ஐ, tool results-ஐ, intermediate decisions-ஐ மறக்கக்கூடாது.

**Problem:** How to survive restarts, enable resume, support human-in-the-loop, and replay/debug?

அதற்குத்தான் Persistence.

### 2. Mental Model

Persistence என்பது LangGraph-க்கு ஒரு external memory.

Graph execution என்பது state machine. State = nodes completed, inputs, outputs, messages, metadata.

In-memory runner என்பது RAM-ல state வச்சுக்கும். Process kill ஆனா முடிஞ்சது.

Persistent runner என்பது ஒவ்வொரு step முடிந்ததும் state-ஐ checkpoint-க்கு save பண்ணும். ஒரு thread மீண்டும் resume பண்ணும்போது அந்த checkpoint-ல இருந்து தொடரும்.

Analogy: ஒரு பெரிய ஆவணத்தை எழுதும்போது auto-save. Power cut வந்தாலும் last saved version-ல இருந்து தொடரலாம்.

### 3. How It Works

LangGraph-ல `checkpointer` interface இருக்கு.

Workflow ஒரு `thread_id` கொடுத்து ஓடும். Checkpointer அந்த thread-க்கு state-ஐ store/retrieve பண்ணும்.

Flow:
`invoke / stream` → node execute → state update → checkpointer.put(checkpoint) → next tick.

Resume பண்ணும்போது `checkpointer.get(thread_id, checkpoint)` → last state load → continue from next node.

LangGraph built-in checkpointer types:
* `MemorySaver` - dev/test க்கு. In-memory, restart ஆனா போயிடும்.
* `SqliteSaver`, `PostgresSaver`, `RedisSaver` - production.

State என்ன save ஆகும்? Graph state, node inputs/outputs, channel values, human interrupt points.

Human-in-the-loop க்கு `interrupt_before` / `interrupt_after` use பண்ணி, state-ஐ pause பண்ணி store பண்ணி, later resume பண்ணலாம்.

### 4. Architectural Reasoning

Persistence எப்போ useful?

* Long-running agent workflows > few seconds, multiple tool calls
* Need fault tolerance: pod crash, node restart, autoscaling
* Need audit / replay / debugging
* Need human approval steps
* Multi-turn conversations where context accumulate ஆகணும்

என்ன constraint address பண்ணுது?
Reliability and operability. Stateless HTTP request model work ஆகாது multi-step orchestration-க்கு.

Alternatives:
* Client side state: client ஒவ்வொரு step result-ஐ வச்சுக்கும். Fragile, trust issue.
* In-memory: fast but volatile.
* External DB manual: possible but you need to manage serialization, versioning, consistency yourself.

LangGraph checkpointer என்பது convention + serialization கொடுக்கும். You focus on graph logic, not storage plumbing.

### 5. Trade-offs

**Latency vs Durability.** Every step-க்கு write செய்யணும். Async write, batch, or write-after-node செய்யலாம். Too frequent write = slow. Too rare = data loss window.

**Storage size vs Replay fidelity.** Full state snapshot எடுத்தால் storage பெருசாகும். Delta checkpoint பண்ணினால் reconstruct செய்ய complexity அதிகம்.

**Consistency vs Availability.** Postgres checkpointer strong consistency தரும். Redis fast but eventual. Architect choose based on need.

**Versioning risk.** Graph schema மாறினால் old checkpoints deserialize ஆகாது. Migration தேவைப்படும். State schema version பண்ணி keep backward compatibility.

Failure mode: checkpointer itself down ஆனால் whole graph stuck. So checkpointer needs HA, backup.

### 6. Practical Example

Enterprise support agent.

User: "என் order #12345-ன் refund status என்ன?"

Graph: retrieve_order → check_policy → call_refund_api → summarize → respond

Step 2-ல policy check பண்ணும்போது human reviewer க்கு interrupt விடு.

Checkpointer = PostgresSaver.

Thread id = user session id.

First run: retrieve_order done, check_policy done, interrupt triggered. State saved in DB with `needs_approval: true`.

Reviewer later approves via dashboard. Same thread_id கொடுத்து resume() call. Graph picks up from checkpoint, skips retrieve, directly call_refund_api.

Pod restart ஆனாலும் conversation continue ஆகும். Audit trail கிடைக்கும்.

### 7. Reasoning Challenge

உங்களிடம் 10k concurrent agent threads இருக்கு. ஒவ்வொரு thread-ம் average 20 steps, ஒவ்வொரு step-க்கு state size ~200KB.

Persistence-க்கு Postgres vs Redis எது தேர்வு செய்வீர்கள்? Write latency, durability, cost, replay need ஆகியவற்றை எப்படி balance பண்ணுவீர்கள்? Checkpoint frequency என்ன வைப்பீர்கள்?

### 8. Key Takeaways

* Persistence என்பது LangGraph-க்கு external memory. Process die ஆனாலும் workflow survive ஆகும்.
* Checkpointer தேர்வு = durability, latency, cost trade-off. Dev-க்கு MemorySaver, prod-க்கு Postgres/Redis.
* State save செய்வது fault tolerance, resume, human-in-the-loop, audit ஆகியவற்றை enable பண்ணும்.
* ஒவ்வொரு architectural solution-ம் trade-off create பண்ணும். Persistence add செய்யும் latency, storage, versioning complexity.
