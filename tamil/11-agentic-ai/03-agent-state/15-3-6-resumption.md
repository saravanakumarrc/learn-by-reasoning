# Resumption

> **Learning Path:** Agentic AI
> **Section:** 15.3.6 — Agent state

## 1. Problem

ஒரு agent ஒரு long-running task-ஐ handle பண்ணிக்கிட்டு இருக்கு. உதாரணமா, ஒரு customer support agent பல steps-ல ஒரு refund request-ஐ investigate பண்ணுது: order fetch பண்ணு → payment verify பண்ணு → fraud check பண்ணு → approval கேளு → confirmation அனுப்பு.

இடையில் agent process crash ஆகுது, அல்லது container restart ஆகுது, அல்லது user session disconnect ஆகுது. இப்போ என்ன ஆகும்?

Task-ஐ முதல்ல இருந்து தொடங்குமா? முந்தைய steps எல்லாம் repeat ஆகுமா? User-க்கு context இழக்குமா?

இதுதான் painful problem. Agent-க்கு memory இருந்தாலும், அது volatile. State இல்லாமல் agent stateless ஆகிவிடும். ஒவ்வொரு run-உம் clean slate.

Resumption என்பது: **interrupt ஆன ஒரு agent-ஐ, அதே context-உடன், அதே point-ல இருந்து தொடர வைப்பது.**

## 2. Mental Model

Agent-ஐ ஒரு human worker மாதிரி நினைச்சுக்கோ.

Worker ஒரு file-ல தன் progress-ஐ note எடுத்துக்கிறார். "Step 3 முடிந்தது, next step 4". அவர் lunch-க்கு போனாலும், திரும்ப வந்து note பார்த்து தொடர்வார்.

Agent state = அந்த note pad. Resumption = note pad-ஐ பார்த்து எங்கே நின்றோமோ அங்கே தொடர்வது.

State என்பது இரண்டு விஷயம்:
* **Conversation history / working memory**: என்ன பேசினோம், என்ன decide பண்ணோம்
* **Task progress / execution state**: எந்த step-ல இருக்கோம், என்ன tools use பண்ணோம், என்ன intermediate results save பண்ணியிருக்கோம்

Resumption இல்லாமல் agent ஒரு short-lived chatbot மட்டுமே. Resumption இருந்தால் agent ஒரு reliable worker.

## 3. How It Works

Resumption-க்கு மூன்று core pieces தேவை.

**1. Persistent state store**
Agent state-ஐ memory-ல மட்டும் வைக்கக்கூடாது. Database, key-value store, or durable log-ல save பண்ணணும். Session ID அல்லது task ID key ஆக இருக்கும்.

**2. Checkpointing**
ஒவ்வொரு meaningful step முடிந்ததும் state-ஐ snapshot எடு. Tool call result, decision, next action intention எல்லாம் persist ஆகும்.

**3. Recovery logic**
Agent restart ஆன போது, current task ID-ஐ load பண்ணி, last checkpoint-ல இருந்து resume பண்ணு. Incomplete steps-ஐ re-execute செய்யாமல் skip பண்ணு, அல்லது idempotent ஆக re-run செய்யு.

Simple flow:

```
User request → Task created with task_id → Step 1 → checkpoint → Step 2 → checkpoint → crash → restart → load state from task_id → resume from Step 3
```

## 4. Architectural Reasoning

Resumption எப்போ useful?

* Long-running workflows: research, multi-step booking, code generation + test + deploy
* Human-in-the-loop: agent waits for user approval, hours/days later resume
* Fault tolerance: service crash, pod eviction, deployment rollout
* Cost control: expensive LLM calls-ஐ repeat பண்ணக்கூடாது

Options:

* **In-memory state**: fast, but crash ஆனால் lost. Prototype-க்கு மட்டும்.
* **External durable store**: Postgres / Redis / DynamoDB. Production default.
* **Event sourcing**: ஒவ்வொரு action-உம் immutable event ஆக append. Replay பண்ணி state reconstruct பண்ணலாம். Full audit trail கிடைக்கும்.

Architect எப்போ choose பண்ணுவார்?
Task duration > seconds, failure cost > retry cost, user expects continuity. அப்போ resumption must.

## 5. Trade-offs

**Consistency vs Availability**
State-ஐ எப்போ save பண்ணுறது? Every step-ல save பண்ணினால் consistency high, latency & cost high. Batch save பண்ணினால் crash-ல data loss ஆகும்.

**State size vs Performance**
Full conversation history-ஐ store பண்ணினால் context rich, but load time & token cost அதிகம். Summarization / pruning தேவை.

**Durability vs Complexity**
Event sourcing gives perfect replay, ஆனால் implementation complexity அதிகம். Simple checkpointing எளிது, ஆனால் partial failure handle பண்ண கஷ்டம்.

**Failure mode**
State store itself down ஆனால் agent completely stuck. So state store needs HA, backup.

## 6. Practical Example

RAG-based research agent.

User: "Competitor X-ன் Q2 pricing strategy பத்தி report தயாரி".

Agent:
1. Search web
2. Fetch PDFs
3. Summarize
4. Create draft report
5. Ask user for feedback

Step 3-ல 10 mins LLM processing ஆகுது. அப்போ Kubernetes node evict ஆகுது.

Resumption இல்லாமல்: Agent முதல்ல இருந்து தொடங்கும். User frustrated.

Resumption உடன்: task_id = `research-abc123`. Last checkpoint = step 3 completed, summaries saved in state store. Restart ஆனதும் agent state load பண்ணி step 4-ல இருந்து தொடரும். User-க்கு தெரியாது crash ஆனது.

State store-ல இருக்கும்: conversation, tool outputs, intermediate summaries, next_action.

## 7. Reasoning Challenge

உங்க agent 20 concurrent users-க்கு multi-step form filling பண்ணுது. ஒரு user 2 நாள் கழித்து திரும்ப வரணும். Agent process எப்போவும் restart ஆகலாம். State-ஐ எப்படி design பண்ணுவீங்க? In-memory, DB, அல்லது event log? Checkpoint எப்போ எடுப்பீங்க? State size grow ஆகும்போது என்ன செய்வீங்க?

## 8. Key Takeaways

* Resumption இல்லாமல் agent reliable worker ஆக முடியாது.
* State = conversation + task progress. இதை durable store-ல checkpoint பண்ணு.
* Crash ஆனாலும் agent last point-ல இருந்து தொடர வேண்டும், முதல்ல இருந்து அல்ல.
* Every architectural solution creates trade-off: durability vs latency, completeness vs cost.
