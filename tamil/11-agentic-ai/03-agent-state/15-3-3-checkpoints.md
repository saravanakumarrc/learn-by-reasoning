# Checkpoints

> **Learning Path:** Agentic AI
> **Section:** 15.3.3 — Agent state

## 1. Problem

ஒரு agent ஒரு long-running task பண்ணுது. உதாரணமா, customer support ticket-ஐ analyze பண்ணி, database-ல இருந்து data எடுத்து, LLM-ஐ கூப்பிட்டு summary எழுதி, அதை approve-க்கு அனுப்புறது.

இதுல ஒரு step-ல network failure வந்துடுச்சு. அல்லது LLM timeout ஆயிடுச்சு. அல்லது container crash ஆயிடுச்சு.

இப்போ என்ன ஆகும்? Agent மறுபடி ஆரம்பத்தில் இருந்து start ஆகுமா?

ஆரம்பத்தில் இருந்து start பண்ணா:
- நேரம் waste
- costly API calls repeat
- user-க்கு inconsistent experience
- same step-ல மறுபடியும் fail ஆகலாம்

Agent-க்கு memory இருக்கு, state இருக்கு. அந்த state-ஐ எப்படி save பண்ணி, crash ஆனாலும் அதே இடத்தில் இருந்து தொடர முடியும்? அதுதான் checkpointing-ன் பிரச்சனை.

## 2. Mental Model

Checkpoint என்பது agent-ன் வேலை நிலையின் ஒரு snapshot.

ஒரு video game-ல save point மாதிரி.

Agent ஒரு step முடிச்சதும், அந்த step-ன் output + next step-ன் context-ஐ safe place-ல write பண்ணிடு. அப்புறம் failure வந்தாலும், கடைசி save point-ல இருந்து தொடரலாம்.

State-ல என்ன இருக்கும்?
- current step / workflow progress
- conversation history
- tool outputs
- intermediate results
- decisions made by agent
- pending tasks

## 3. How It Works

Agent ஒரு workflow-ல run ஆகுது. அதன் orchestrator ஒவ்வொரு meaningful boundary-ல checkpoint எடுக்கும்.

Simple flow:
`start → step1 → checkpoint1 → step2 → checkpoint2 → step3 → checkpoint3`

Checkpoint எப்போ எடுக்கறது?
- LLM call முடிஞ்சதும்
- Tool execution முடிஞ்சதும்
- Human approval கிடைச்சதும்
- Long-running task-ன் இடையில்

Checkpoint எங்க save ஆகும்?
- durable storage: database, object store, or agent state store
- key = run_id + step_id
- value = serialized state

Agent restart ஆனால்:
`load latest checkpoint → replay from next step`

Idempotency முக்கியம். ஏன்னா checkpoint-ல இருந்து தொடரும்போது, ஏற்கனவே செய்த step-ஐ மறுபடி செய்யக்கூடாது.

## 4. Architectural Reasoning

Checkpointing useful ஆகும் எப்போ?

- Long-running agent workflows, multi-step planning
- Non-deterministic steps உள்ளது, LLM calls, tool calls
- Failure-prone environment: network, rate limits, pod eviction
- Replay, audit, debugging தேவை
- Human-in-the-loop உள்ளது

Alternatives என்ன?

**No checkpointing**: Stateless restart. சின்ன tasks-க்கு ok. Long tasks-க்கு costly.

**Full replay**: ஆரம்பத்தில் இருந்து மறுபடி. Idempotent என்றால் பரவாயில்லை. ஆனால் latency மற்றும் cost அதிகம்.

**Event sourcing**: ஒவ்வொரு event-ஐயும் append-only log-ல வைத்து state reconstruct பண்ணுவது. Strong auditability தரும். ஆனால் complexity அதிகம்.

Architect ஏன் checkpoint-ஐ தேர்வு செய்வார்?
Failure-க்கு பிறகு recovery time குறைக்க, cost குறைக்க, user experience consistent ஆக்க.

Trade-off: consistency vs availability. Checkpoint save பண்ணும்போது sync write செய்தால் latency அதிகம். Async செய்தால் latest state lose ஆகலாம்.

## 5. Trade-offs

**Granularity**
Fine-grained checkpoint = frequent save, less rework. ஆனால் storage write அதிகம், I/O cost அதிகம்.
Coarse-grained = less overhead, ஆனால் failure-க்கு பிறகு அதிக rework.

**Storage cost vs compute cost**
Checkpoint store செய்வது cheap storage. ஆனால் state size பெரிதாகும். Conversation history, tool outputs எல்லாம் grow ஆகும். Retention policy தேவை.

**Consistency**
Checkpoint எப்போ commit ஆகும்? Step success ஆன பிறகா? அல்லது step start-க்கு முன்னாடியா? Wrong order-ல commit ஆனால் inconsistent state வரும்.

**Security & privacy**
Agent state-ல PII, sensitive tool outputs இருக்கலாம். Checkpoint storage encrypt பண்ணணும், access control வேணும்.

**Failure modes**
Checkpoint write itself fail ஆகலாம். அப்போ partial state. Duplicate checkpoint writes, race condition. Run idempotent அல்லாத tool calls மறுபடி execute ஆகலாம்.

## 6. Practical Example

Enterprise RAG agent, invoice processing.

Workflow:
1. PDF download from S3
2. Extract text via OCR tool
3. LLM call to extract fields
4. Validate against database
5. Human approval request
6. Update ERP

Step 3-ல LLM timeout. Container restart ஆகி, pod new node-ல schedule ஆகுது.

Checkpointing இல்லாமல்: மறுபடி PDF download, OCR, LLM call. 2 நிமிடம் waste, $0.02 API cost waste.

Checkpointing இருந்தால்:
- checkpoint2 save ஆகி இருக்கும்: PDF URL, OCR output
- Agent restart ஆனதும் latest checkpoint load பண்ணி step3-ல இருந்து தொடரும்
- Idempotent LLM call with same prompt, அல்லது cached result use பண்ணும்

State store-ல run_id = `invoice-12345`, step = `extract_fields`, data = `{ocr_text, pdf_hash}`

Operability improve ஆகும். Ops team audit பண்ணும்போது எந்த step-ல stuck ஆகியிருக்கு என்று தெரியும்.

## 7. Reasoning Challenge

உங்களிடம் multi-agent system இருக்கு. Agent A research பண்ணி, Agent B summary பண்ணி, Agent C action எடுக்கும்.

Agent B LLM call பண்ணும்போது rate limit hit ஆகுது. Retry பண்ண 5 நிமிடம் wait வேணும்.

இங்கே checkpoint-ஐ எங்கெங்க வைப்பீங்க? Fine-grained vs coarse-grained எது சரி? Checkpoint save செய்யும்போது synchronous write செய்யலாமா async செய்யலாமா? ஏன்?

## 8. Key Takeaways

* Checkpoint என்பது agent state-ன் durable save point. Failure-க்கு பிறகு அதே இடத்தில் தொடர உதவும்.
* Checkpoint granularity, storage durability, idempotency ஆகியவை architectural trade-off-கள்.
* Long-running, costly, failure-prone agent workflows-ல checkpointing cost மற்றும் latency-ஐ குறைக்கும்.
* Every checkpoint adds write overhead and state management complexity. ஆகவே, meaningful boundaries-ல மட்டும் checkpoint எடு.
