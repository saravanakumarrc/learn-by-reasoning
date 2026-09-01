# Recovery

> **Learning Path:** Agentic AI
> **Section:** 15.3.4 — Agent state

## 1. Problem

ஒரு agent ஒரு multi-step task பண்ணிக்கிட்டு இருக்கு. உதாரணமா, ஒரு sales report generate பண்ணி, data fetch பண்ணி, analysis பண்ணி, email அனுப்பணும்.

Step 3-ல LLM call பண்ணும்போது timeout ஆகுது. அல்லது API rate limit hit ஆகுது. அல்லது service crash ஆகுது.

இப்போ என்ன ஆகும்? Agent முதல் step-ல இருந்து மறுபடியும் start பண்ணுமா? அப்படி பண்ணா time, cost, external side-effects எல்லாம் வீண்.

முக்கியமானது: **Agent state என்பது தற்காலிகம் அல்ல, அது ஒரு workflow-ன் memory.** அந்த memory தொலைஞ்சா, agent தன் identity-யை இழக்கும்.

> What goes wrong if we don't have recovery? Rework, inconsistent outputs, duplicate actions like double payment / double email.

## 2. Mental Model

Agent state = task progress + context + decisions + intermediate results.

Recovery = **நடுவில் நின்ற workflow-ஐ சரியான point-ல இருந்து தொடர வைக்கும் திறன்.**

Analogy: ஒரு long form fill பண்றீங்க. Browser crash ஆனாலும், autosave இருந்தால் நீங்கள் கடைசி field-ல இருந்து தொடரலாம். Agent-க்கு அதுதான் checkpoint.

## 3. How It Works

Agent state-ஐ நாம் persist பண்ணணும்.

Basic flow:
`Tool call → Result → Update state → Persist checkpoint → Next step`

Failure ஆனால்:
`Load last checkpoint → Replay from there → Skip already done side-effects`

முக்கியமான 3 விஷயங்கள்:

* **Checkpoint:** state-ன் snapshot. எந்த step முடிஞ்சது, என்ன context இருக்கு.
* **Idempotency:** ஒரு step-ஐ மறுபடி run பண்ணினாலும், side-effect ஒரு முறை மட்டும் நடக்கணும்.
* **Deterministic replay:** State இருந்தால், agent அதே reasoning path-ஐ தொடரலாம்.

## 4. Architectural Reasoning

எப்போது Recovery தேவை?

* Long-running agent workflows, multi-step planning
* External API calls உள்ள agent, latency / failure common
* Human-in-the-loop tasks, hours/days ஆகலாம்
* Cost sensitive LLM calls, rework செய்ய முடியாது

Alternatives:

* **Stateless restart:** எளிது, ஆனால் expensive & unsafe
* **In-memory state:** fast ஆனால் crash ஆனால் போச்சு
* **Persistent state + checkpoint:** சரியான balance

ஒரு architect ஏன் இதை தேர்வு செய்வார்? Reliability மற்றும் operability. Production-ல agent fail ஆகாமல் இருக்காது, recover ஆகணும்.

## 5. Trade-offs

* **Checkpoint frequency vs cost:** ஒவ்வொரு step-க்கும் persist பண்ணினால் durability அதிகம், latency & storage cost அதிகம்.
* **Consistency vs availability:** Strong consistency வேண்டுமா? அல்லது eventual recovery போதுமா? Distributed agent state-க்கு இது முக்கியம்.
* **Complexity:** State schema மாறினால், old checkpoints migrate பண்ண வேண்டும். Versioning தேவை.
* **Side-effect safety:** Duplicate email, duplicate DB write ஆகாமல் தடுக்க idempotency keys, outbox pattern தேவை.

Failure modes: checkpoint corrupt ஆனால், state drift ஆனால், partial write ஆனால் agent inconsistent decision எடுக்கும்.

## 6. Practical Example

Enterprise RAG agent: Customer support ticket-ஐ analyze பண்ணி, knowledge base search பண்ணி, draft reply create பண்ணி, human approvalக்கு அனுப்பணும்.

State contains: ticket id, retrieved docs, reasoning trace, draft reply.

Step 2-ல LLM timeout ஆகுது. Checkpoint இருந்தால், last successful state = docs retrieved. Agent அதை load பண்ணி, step 2-ல இருந்து தொடரும். Docs-ஐ மறுபடி fetch பண்ணாது.

Recovery இல்லாமல்: முதல் step-ல இருந்து தொடங்கும், அதே docs-ஐ மறுபடி fetch, cost double.

## 7. Reasoning Challenge

உங்கள் agent 10-step workflow பண்ணுது. Step 5-ல external payment API call பண்ணுது. Network timeout ஆகுது. Response வந்ததா இல்லையா தெரியல.

Recovery design பண்ணுங்க: checkpoint எப்போ வைப்பீங்க? Payment call-ஐ எப்படி idempotent ஆக்குவீங்க? Agent-ஐ எப்படி safe-ஆ restart பண்ணுவீங்க?

## 8. Key Takeaways

* Agent state என்பது progress memory, அதை persist செய்யாவிட்டால் recovery இல்லை
* Recovery = checkpoint + idempotency + deterministic replay
* Every recovery strategy introduces cost & complexity trade-off
* Production agent-க்கு recovery design என்பது core architectural decision, optional feature அல்ல
