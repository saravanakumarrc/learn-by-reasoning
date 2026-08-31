# State modeling

> **Learning Path:** Agentic AI
> **Section:** 15.3.1 — Agent state

### 1. Problem

ஒரு agent-க்கு task கொடுக்கிறோம். "User-க்கு last 3 months-ல் வந்த invoices-ஐ summarize பண்ணி, அதுல high-value items எது என்று கண்டுபிடித்து, email அனுப்பு."

Agent start ஆகும். Tool call பண்ணும். Database-ல் query பண்ணும். Result வரும். Next step என்ன? Agent-க்கு தான் எங்கே இருக்கிறோம் என்று தெரிய வேண்டும்.

Session-ல் பல steps. Tool outputs வரும். Context window limited. Network failure வந்தால்? Agent restart ஆனால்? User conversation-ல் மத்தியில் context மாறும்.

இல்லாமல் என்ன ஆகும்? Agent தான் என்ன செய்தோம், என்ன செய்ய வேண்டும், என்ன data already collect ஆயிற்று என்று மறந்து விடும். Loop-ல் மாட்டிக்கொள்ளும். அதே tool-ஐ மீண்டும் call பண்ணும். Incomplete task.

State modeling என்பது agent-க்கு memory + progress + context-ஐ ஒழுங்காக வைத்திருக்கும் system.

### 2. Mental Model

Agent state என்பது ஒரு working memory file. இது மூன்று விஷயங்களை வைத்திருக்கும்:

* **What it knows:** task, user intent, collected facts, tool outputs
* **Where it is:** current step, next step, history of actions
* **How it should behave:** mode, constraints, guardrails

LLM-ன் context window என்பது short-term memory. Agent state என்பது durable, structured memory.

அனலாகி: Software engineer-க்கு whiteboard. அவர் பிரச்சனையை solve பண்ணும்போது, யோசித்ததை எழுதி வைக்கிறார். நீங்கள் mid-meeting-ல் வந்தாலும் அவருக்கு தெரியும் எங்கே நின்றோம்.

### 3. How It Works

Agent ஒரு step run ஆகும்போது:

1. **Read State**: current state-ஐ load பண்ணு. Task, history, facts.
2. **Reason**: LLM decide செய்யும். Next action என்ன?
3. **Act**: Tool call / user message.
4. **Update State**: Result-ஐ state-ல் merge பண்ணு. History append. Facts update.

State-ஐ store பண்ணுவது எங்கே?

* **In-memory**: fast, session முடிந்தால் மறையும்.
* **Database / KV store**: session restore ஆகும், persistence கிடைக்கும்.
* **External state store**: Redis, Postgres, DynamoDB.

State representation பொதுவாக JSON / structured schema.

```
{
  "task_id": "...",
  "user_goal": "...",
  "current_step": "fetch_invoices",
  "history": [{"action":"query_db","result":"..."}],
  "facts": {"invoices_found": 12, "period":"last_3_months"},
  "next_intent": "summarize"
}
```

Agent framework-கள் state-ஐ explicit ஆக manage பண்ணும். LangGraph, AutoGen போன்றவை state machine ஆக மாற்றுகின்றன.

### 4. Architectural Reasoning

State modeling எப்போது தேவை?

* Multi-step task > 3 steps
* Tool calls multiple, dependencies உள்ளன
* Long-running task, minutes/hours
* Need for replay / audit / debugging
* Need for human-in-the-loop

Constraints:

* **Latency**: state read/write overhead
* **Consistency**: concurrent updates, race condition
* **Size**: state கனமாகும். LLM context limit hit ஆகும்
* **Privacy**: sensitive data state-ல் store ஆகும்

Alternatives:

* Pure context passing: simple, but brittle, no persistence
* Stateless agent per turn: cheap, but no memory across steps
* Full state modeling: robust, but complexity அதிகம்

Architect choose பண்ணும்போது கேட்க வேண்டியது: Task deterministic ஆ? Reproducible ஆ? Failure-க்கு recover வேண்டுமா?

### 5. Trade-offs

**Persistence vs Speed**: DB-ல் save பண்ணினால் durable, ஆனால் latency வரும். In-memory fast, ஆனால் crash ஆனால் மறையும்.

**Granularity vs Complexity**: Fine-grained state, every fact track பண்ணினால் reasoning better, ஆனால் schema maintain பண்ண கஷ்டம். Coarse state simple, ஆனால் information loss.

**Centralized vs Distributed**: Single state store simple. But agent parallel steps run பண்ணும்போது contention வரும்.

Failure modes:

* State corruption: partial write. Agent confused.
* Stale state: tool result outdated ஆகும், agent wrong decision.
* State bloat: history அதிகமாகும், LLM hallucinate செய்யும்.

Security: State-ல் PII இருக்கும். Encryption, access control தேவை.

### 6. Practical Example

Enterprise support agent. User: "என் last order status என்ன?"

Agent state start:
`{current_step: "identify_user", facts: {}, history: []}`

Step1: identify user via email. State update `facts.user_id = 123`.
Step2: query orders. State update `facts.orders = [...]`, `current_step = "find_latest"`.
Step3: summarize. State update `facts.summary = "..."`.

User இடையில்: "Wait, wrong account". Agent state-ஐ read பண்ணி, current facts-ஐ invalidate பண்ணி, step reset பண்ணும்.

Without state modeling, agent மீண்டும் user email கேட்கும். With state, agent knows context and can ask clarification only.

RAG agent-ல் state = query, retrieved docs, previous reasoning, final answer. Replay செய்ய audit-க்கு உதவும்.

### 7. Reasoning Challenge

உங்களிடம் multi-agent system இருக்கு. Planner agent task decompose பண்ணும். Executor agents tools call பண்ணும். Task 30 mins நடக்கும். Executor crash ஆனால் task continue ஆக வேண்டும்.

State-ஐ எங்கே வைப்பீர்கள்? In-memory per agent? Shared DB? State schema எப்படி design பண்ணுவீர்கள்? Consistency எப்படி handle பண்ணுவீர்கள்?

### 8. Key Takeaways

* Agent state என்பது progress + memory + context-ன் structured representation. LLM context அல்ல.
* State modeling இல்லாமல் multi-step task reliable ஆக இயங்காது.
* Design state for persistence, observability, and recovery. Trade-off between speed and durability.
* Every architectural solution creates another trade-off: state gives memory but adds complexity, consistency, and cost.
