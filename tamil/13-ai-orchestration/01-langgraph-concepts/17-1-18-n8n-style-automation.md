# n8n-style automation

> **Learning Path:** AI Orchestration
> **Section:** 17.1.18 — LangGraph concepts

## 1. Problem

நீங்கள் ஒரு AI agent-ஐ build பண்ணறீங்க. Agent ஒரு task-ஐ step by step பண்ணணும்.

முதல் step: user query-ஐ understand பண்ணணும்.
இரண்டாவது: database-ல data fetch பண்ணணும்.
மூன்றாவது: LLM-ல summarize பண்ணணும்.
நாலாவது: result-ஐ user-க்கு திருப்பி அனுப்பணும்.

Simple workflow போல தெரியுது. ஆனா real world-ல:

* User திருத்தம் கேட்கலாம், அப்போ மீண்டும் step 3-க்கு போகணும்.
* Database timeout ஆனா retry பண்ணி, fail ஆனா fallback-க்கு போகணும்.
* LLM hallucinate பண்ணா human review-க்கு அனுப்பணும்.
* State-ஐ track பண்ணணும், எந்த step-ல இருக்கோ அதை தெரிஞ்சுக்கணும்.

இப்போ code-ல if-else chain ஆகிடும். 10 step-க்கு மேல் போனா debugging கஷ்டம், test பண்ண கஷ்டம், new branch add பண்ண கஷ்டம்.

n8n-style automation-ல நீங்க nodes-ஐ connect பண்ணுவீங்க. LangGraph-ல அதே idea, ஆனா code-ல, stateful, deterministic control flow-உம் LLM-உம் கலந்த workflow.

**Problem என்ன?** Linear script-ல போதாது. Graph-ல think பண்ணணும்.

## 2. Mental Model

LangGraph = stateful graph of nodes.

Node = ஒரு function. `LLM call`, `tool call`, `condition check`, `human input` எல்லாம் node.
Edge = next node எது என்பதை decide பண்ணும் logic.

நீங்கள் ஒரு state object-ஐ வைத்திருக்கீங்க. அது workflow-ல் பயணிக்கிறது. ஒவ்வொரு node-ம் state-ஐ read பண்ணும், modify பண்ணும், அடுத்த node-க்கு pass பண்ணும்.

n8n-ல visual nodes. LangGraph-ல code nodes. Core idea same: **data flows, control flows**.

## 3. How It Works

மூன்று core concepts மட்டும் போதும்.

**State:** Graph-க்கு shared memory. `{messages, user_id, db_result, summary}` மாதிரி. State schema define பண்ணுவீங்க.

**Nodes:** Pure functions. `state -> state`. Side effect இருக்கலாம், ஆனா output-ல state update ஆகணும்.

**Edges:** Conditional edges. `if state.needs_more_info: go to ask_user else: go to summarize`. Also simple edges.

Graph-ஐ compile பண்ணி, ஒரு `Runnable` மாதிரி run பண்ணுவீங்க. LangGraph checkpointer வைத்து, ஒரு execution-ஐ pause பண்ணி, resume பண்ணலாம். அதனால human-in-the-loop easy.

## 4. Architectural Reasoning

எப்போ LangGraph தேவை?

* Multi-step agent workflow வேண்டும்.
* Branches, loops, retries தேவை.
* State-ஐ persist பண்ணி, mid-workflow resume வேண்டும்.
* Observability வேண்டும்: எந்த node-ல fail ஆச்சு என்பதை தெரிஞ்சுக்க.

Alternatives என்ன?

* Simple chain with LangChain: `LLM -> Tool -> LLM`. Linear. Branch கிடையாது.
* n8n / Zapier style visual automation: Non-technical, great for ops. ஆனா custom logic, complex state, tight LLM integration கஷ்டம்.
* Raw Python orchestration: Full control, ஆனா boilerplate அதிகம், failure handling நீங்களே எழுதணும்.

Architect ஏன் LangGraph choose பண்ணுவார்? 
Because you need **code-level control + visual graph mental model + persistence**. AI Orchestration-ல இது common.

## 5. Trade-offs

**State management complexity.** State schema grow ஆனா, versioning கஷ்டம். எல்லா node-மும் state-ஐ touch பண்ணலாம். Careful design தேவை.

**Operational complexity.** Graph compile, checkpointer DB, streaming. n8n-க்கு UI இருக்கு. LangGraph-க்கு devOps நீங்களே பார்க்கணும்.

**Latency & cost.** Loop இருந்தால் LLM call அதிகம் ஆகும். Retry logic, re-prompting cost add ஆகும்.

**Failure modes.** Node crash ஆனா whole graph stop ஆகும். Idempotency, timeout, retry policy தேவை. Checkpointer corrupt ஆனால் state lose ஆகும்.

## 6. Practical Example

Customer support agent.

Flow:

`Start -> Intent Classify -> Fetch Ticket -> Generate Draft Reply -> Quality Check -> Route`

Quality Check node ஒரு condition: `confidence < 0.8` என்றால் `Human Review` node-க்கு போகும். Reviewer approve செய்தால் மீண்டும் `Generate Draft Reply`-க்கு போகாது, `Send Reply`-க்கு போகும்.

State contains: `user_query, ticket_data, draft, confidence, reviewer_note`.

Checkpointer SQLite-ல save பண்ணும். User "இன்னும் கொஞ்சம் formal-ஆ எழுது" என்றால், graph-ஐ அதே state-ல resume பண்ணி `Generate Draft Reply` node-க்கு போகும்.

n8n-style thinking இருக்கு, ஆனா code-ல type-safe.

```
graph
A[Start] --> B[Classify]
B --> C[Fetch Ticket]
C --> D[Generate Draft]
D --> E[Quality Check]
E -->|high| F[Send]
E -->|low| G[Human Review]
G --> F
```

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG agent இருக்கு. Retrieve -> Generate -> Evaluate -> If answer unsatisfactory, re-retrieve with different query.

User chat ongoing. Conversation history grow ஆகுது. ஒவ்வொரு turn-லும் full graph run பண்ணினால் cost அதிகம். 

இங்கே state-ஐ எப்படி design பண்ணுவீங்க? Re-retrieve loop-ஐ எப்படி limit பண்ணுவீங்க? Human fallback எப்போ trigger பண்ணுவீங்க?

## 8. Key Takeaways

* LangGraph = n8n-style workflow, ஆனா code-first, stateful, LLM-friendly.
* Graph design = problem definition. Nodes small, state explicit.
* Every branch/loop adds operational cost and failure surface. Limit it.
* Checkpointer வைத்தால் மட்டுமே production agent ஆகும். Stateless chain போதாது.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியுமா?
