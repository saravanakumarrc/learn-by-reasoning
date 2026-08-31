# Persistence

> **Learning Path:** Agentic AI
> **Section:** 15.3.2 — Agent state

## 1. Problem

ஒரு agent-ஐ run பண்ணும்போது என்ன நடக்கும்?

User query வரும். Agent think பண்ணும். Tools-ஐ call பண்ணும். Context-ஐ build பண்ணும். பல steps-ல முடிவு எடுக்கும்.

இப்போ user connection cut ஆனால் என்ன ஆகும்? Server restart ஆனால்? New request வந்தால் அது முந்தைய conversation-ஐ எப்படி தெரிஞ்சுக்கும்?

Stateless LLM call மட்டும் போதாது. Agent-க்கு memory வேணும். அந்த memory எங்கே இருக்கும்? Process memory-ல வச்சா pod restart ஆனதும் போயிடும்.

**Problem:** Agent-ன் current state, past interactions, in-progress tasks, intermediate results, tool outputs எல்லாம் survive செய்யணும். Failures, scale-out, new session எல்லாத்துக்கும்.

Persistence இல்லாமல் agent என்பது amnesiac bot. ஒவ்வொரு request-ம first request மாதிரி.

## 2. Mental Model

Agent state = ஒரு living document.

அதில் இருக்கும்:

* **Conversation history** - user messages, agent messages
* **Working memory** - current task, sub-tasks, plan
* **Tool state** - last API call results, pending calls
* **Session metadata** - user id, session id, created at, last active

இதை நாம் தற்காலிகமாக in-memory வைக்கலாம். ஆனால் production-ல agent என்பது long-running, multi-turn, multi-service.

ஆக state-ஐ externalize பண்ணணும். External store-ல persist பண்ணணும்.

Mental model: Agent என்பது stateless compute + externalized state store.

## 3. How It Works

Basic loop:

1. Request வரும் → session id வைத்து state store-ல் read பண்ணு
2. State + new user input → LLM-க்கு கொடு → reasoning
3. Plan update ஆனால் → state-ல write பண்ணு
4. Tool call வந்தால் → execute → result-ஐ state-ல append பண்ணு
5. Response return → next request-க்கு state ready

Persistence layer என்பது:

* **Session store** - key value store. Redis, DynamoDB
* **Document store** - conversation as JSON document. Postgres JSONB, MongoDB
* **Event log** - immutable append-only log. Kafka, EventStore

சிறிய agent-க்கு simple document store போதும். Long-running autonomous agent-க்கு event sourcing தேவைப்படும்.

State snapshot + event log கொண்டு agent-ஐ rebuild பண்ணலாம்.

## 4. Architectural Reasoning

Persistence எப்போது useful?

* Multi-turn conversation தேவைப்படும்போது
* Agent பல steps-ல task செய்யும்போது
* Failure recovery தேவைப்படும்போது
* Multiple workers / horizontal scale தேவைப்படும்போது
* Audit, compliance, replay தேவைப்படும்போது

Alternatives:

* **In-memory only** - fastest, cheapest. ஆனால் restart-ல் loss, scale out impossible
* **Database per session** - Postgres row per session. Strong consistency, SQL queries possible. Write latency அதிகம்
* **Cache + DB** - Redis hot state, Postgres durable. Common pattern
* **Event log** - full history, replay possible. Complexity அதிகம்

Architect choose பண்ணுவது:

Latency sensitive chatbot → Redis + periodic flush to DB
Financial agent with audit → Postgres + immutable event log
Autonomous agent with long horizon → Event store + snapshot

## 5. Trade-offs

**Consistency vs Availability:** Strong consistency கொடுத்தால் state write slow ஆகும். Agent next turn wait பண்ணும். Eventual consistency வைத்தால் duplicate writes, lost updates வரலாம்.

**Granularity:** Fine-grained state updates = more accurate, more I/O. Coarse snapshot = less I/O, but conflict அதிகம்.

**Cost vs Durability:** Redis fast ஆனால் memory cost high. Disk store cheap ஆனால் latency high.

**Failure modes:** Network partition-ல் state read stale ஆகும். Agent wrong decision எடுக்கும். Write failure-ல் state diverge ஆகும். Idempotency key, version number வைத்து conflict resolve பண்ணணும்.

State size grow ஆகும். Conversation history நீண்டால் LLM context window overflow. ஆக summarization, pruning தேவை.

## 6. Practical Example

Enterprise support agent.

User: "என் order #12345 எங்கே இருக்கு? நேத்து தான் cancel பண்ணினேன்."

Agent-க்கு state store-ல இருந்து பழைய conversation தேவை.

Flow:

* session_id வைத்து Redis-ல state read. Last state: user cancelled order yesterday, refund initiated.
* Current query + history → LLM
* Agent decides: order service API call பண்ணு
* Result: refund processed, amount credited
* State update: append tool result, update last task status = completed
* Write back to Redis + async flush to Postgres for audit

Pod crash ஆனாலும் next request-ல state restore ஆகும். Another pod agent-ஐ continue பண்ணும்.

இங்கே persistence இல்லாமல் agent "நேத்து cancel பண்ணினேன்" என்பதை forget பண்ணும். ஒவ்வொரு முறையும் user-ஐ repeat செய்ய சொல்லும்.

## 7. Reasoning Challenge

உங்களிடம் autonomous research agent உள்ளது. ஒரு task 30 mins எடுக்கும், 10 steps. 5 workers parallel-ல run ஆகிறது. Worker crash ஆனால் task continue ஆக வேண்டும். Full audit trail வேண்டும்.

இங்கே state-ஐ எப்படி persist பண்ணுவீர்கள்? Redis மட்டும் போதுமா? Event log தேவையா? Snapshot எப்போது எடுப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Agent without persistence = stateless chatbot. Real agent-க்கு external state store must
* State = conversation + working memory + tool results. இதை durable + recoverable ஆக்கு
* Simple sessions → DB / Cache. Long-running autonomous → Event log + snapshot
* Every persistence choice = latency, consistency, cost, operability trade-off
* Design for failure: versioning, idempotency, replay. Restart-க்கு பிறகும் agent continue ஆக வேண்டும்
