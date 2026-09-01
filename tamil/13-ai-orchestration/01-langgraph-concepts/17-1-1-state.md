# State

> **Learning Path:** AI Orchestration
> **Section:** 17.1.1 — LangGraph concepts

## 1. Problem

ஒரு LLM agent-ஐ நீங்கள் multiple steps-ல run பண்றீங்க. Step 1: user query-ஐ understand பண்ணி plan போடு. Step 2: tool-ஐ call பண்ணி data fetch பண்ணு. Step 3: அந்த data-வை வைத்து answer generate பண்ணு.

பிரச்சனை என்ன? ஒவ்வொரு step-மும் ஒரு node. ஒவ்வொரு node-க்கும் context தேவை. User message, previous tool output, conversation history, intermediate decisions எல்லாம் pass ஆகணும்.

இதை நீங்கள் எப்படி manage பண்ணுவீங்க? Global variable-ல வைக்கலாம்? Function arguments-ல pass பண்ணலாம்? Graph-ல 10 nodes ஆனதும் arguments signature மாறும். ஒரு node-க்கு தேவையில்லாத data-யும் கொடுக்கணும்.

State இல்லாமல், graph ஒரு stateless function chain ஆகிவிடும். ஒவ்வொரு hop-லும் முந்தைய context காணாமல் போகும். Agent மறந்துவிடும், hallucinate ஆகும், loop-ல சிக்கும்.

**What problem became painful?** Multi-step reasoning-ல context carry பண்ணுவது painful ஆகிவிட்டது.

## 2. Mental Model

LangGraph-ல **State** என்பது graph-ன் shared memory.

ஒரு application state ஒரு single object. அது graph-ல் உள்ள எல்லா nodes-க்கும் common. ஒரு node run ஆகும்போது அது state-ஐ read பண்ணும், மாற்றும், திருப்பி கொடுக்கும்.

அனலாஜி: ஒரு construction site-ல blueprint + site log book. ஒவ்வொரு worker வந்து log book-ஐ பார்க்கிறார், தனக்கு தேவையான part-ஐ update பண்ணி, திருப்பி வைக்கிறார். யார் என்ன செய்தார் என்பது பின்னால் வருபவருக்கு தெரியும்.

State = {messages: [...], user_id: ..., plan: ..., tools_output: ..., current_step: ...}

Node-கள் pure functions: `State -> State`. Side effect இல்லை, just state transform.

## 3. How It Works

LangGraph-ல State இரண்டு வகை.

**Typed State:** Python TypedDict or Pydantic model. Field-கள் define பண்ணி, type safety வைக்கலாம்.

```python
class AgentState(TypedDict):
    messages: list[Message]
    query: str
    plan: list[str]
    retrieved_docs: list[dict]
```

**Channel-based State:** LangGraph internal channels. Different update semantics உள்ளன: `Value`, `Topic`, `Aggregator`. நீங்கள் state-ஐ எப்படி merge பண்ண வேண்டும் என்பதை control பண்ணலாம்.

Flow:
`input -> node1 reads state -> node1 returns partial update -> LangGraph merge -> node2 gets updated state`

Node ஒரு field-ஐ மட்டும் update பண்ணலாம். மற்ற field-கள் untouched-ஆக இருக்கும். Immutable update போல.

Checkpointing: State ஒவ்வொரு step-க்கும் save ஆகும். அதனால் graph-ஐ resume, rewind, debug பண்ண முடியும்.

## 4. Architectural Reasoning

State எப்போது useful?

நீங்கள் orchestration பண்ணும் போது workflow multi-step, branching, looping இருக்கும் போது. Agent-க்கு memory வேண்டும். Tool results accumulate ஆக வேண்டும்.

Alternatives என்ன?

* Stateless chain: LangChain RunnableSequence. Simple, but context lose ஆகும். Long conversation-க்கு முடியாது.
* External DB: ஒவ்வொரு node-ம் DB-ல read/write பண்ணும். Slow, error prone, consistency கஷ்டம்.
* In-memory dict passed manually: Code messy ஆகும். Node signature explode ஆகும்.

LangGraph State ஏன் choose பண்ணுவது?
Because graph-ல control flow முக்கியம். Conditional edges, loops, parallel branches இருக்கும். State-ஐ centralize பண்ணினால் nodes clean-ஆக இருக்கும், reasoning explicit ஆகும்.

Trade-off: State size grow ஆகும். Messages list நீளும். Serialization cost வரும். Checkpoint store-ல DB cost வரும்.

## 5. Trade-offs

**Consistency vs Flexibility:** Typed State strict. Field missing என்றால் error. Flexible dict easy ஆனால் bug கண்டுபிடிக்க கஷ்டம்.

**Memory vs Performance:** பெரிய state-ஐ ஒவ்வொரு node-க்கும் pass பண்ணுவது latency கொடுக்கும். ஆனால் small incremental updates possible.

**Immutability vs Mutation:** LangGraph prefers immutable partial updates. Reasoning easy. ஆனால் developer-க்கு ஆரம்பத்தில் counter-intuitive.

**Failure mode:** State schema மாற்றினால் old checkpoints incompatible ஆகும். Versioning தேவை. Partial update-ல overwrite பண்ணி முக்கிய data-ஐ இழக்கும் risk.

**Observability:** State-ஐ log பண்ணினால் sensitive data leak ஆகும். PII, tool outputs. Redaction தேவை.

## 6. Practical Example

Enterprise support agent.

Workflow: `classify -> retrieve -> reason -> respond`

State:
```
messages: [user query]
intent: null
retrieved_tickets: []
summary: null
final_answer: null
```

Node 1 - classify: messages-ஐ பார்த்து intent set பண்ணும். `state["intent"] = "billing"`
Node 2 - retrieve: intent-ஐ வைத்து vector DB-ல search பண்ணி `retrieved_tickets` append பண்ணும்.
Node 3 - reason: messages + retrieved_tickets-ஐ வைத்து summary create பண்ணும்.
Node 4 - respond: summary-ஐ வைத்து final_answer generate பண்ணும்.

User follows up பண்ணினால், graph-ஐ restart பண்ணாமல் same state-ஐ continue பண்ணலாம். Checkpointing-ல user_id-வை key-ஆக வைத்து conversation resume பண்ணலாம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG agent இருக்கு. 3 rounds retrieve-reason loop வைத்திருக்கிறீர்கள். ஒவ்வொரு round-லும் messages list-க்கு 2k tokens add ஆகிறது. State-ல messages-ஐ முழுவதுமாக வைத்தால் 6k tokens ஆகும். LLM context window limit 8k.

இங்கே state-ஐ எப்படி design செய்வீர்கள்? Messages-ஐ முழுவதுமாக keep பண்ணுவீர்களா? Summarize பண்ணி truncate பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* State என்பது LangGraph-ன் shared memory. Nodes pure transform functions.
* Multi-step orchestration-க்கு context carry பண்ணுவதற்கு State தேவை. இல்லாவிட்டால் agent forget ஆகும்.
* Typed State-ஐ define பண்ணுங்கள். Schema explicit ஆக இருந்தால் architectural decisions clear ஆகும்.
* State size, checkpoint cost, schema evolution ஆகியவை real trade-offs. Every solution creates a new trade-off.
