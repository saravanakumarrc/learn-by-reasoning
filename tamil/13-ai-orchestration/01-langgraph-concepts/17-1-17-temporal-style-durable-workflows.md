# Temporal-style durable workflows

> **Learning Path:** AI Orchestration
> **Section:** 17.1.17 — LangGraph concepts

## 1. Problem

உங்களிடம் ஒரு AI agent workflow இருக்கு. Steps: `validate_input -> call LLM -> call vector DB -> call external API -> write to database -> send notification`.

இது ஒரு request-ல நடக்குது. 2 நிமிஷம் எடுக்குது.

இப்போ என்ன ஆகும்?
* Worker pod crash ஆனால்? Workflow நடுவுல நின்னுடும்.
* LLM call timeout ஆனால்? Retry செய்ய வேண்டும், ஆனால் எத்தனை முறை?
* External API 5 நிமிஷம் slow ஆ இருக்கு. Request timeout ஆகும்.
* Step 3 வரை செய்து முடித்து, step 4-ல fail ஆனால் மறுபடி தொடக்கத்தில் இருந்து தொடங்க வேண்டுமா?

Long-running, multi-step, external calls உள்ள workflow-களில் **state, retry, timeout, crash recovery** எல்லாம் manual ஆக handle பண்ணினால் code குப்பையாகும்.

> What problem became painful? Business logic + reliability concerns ஒன்றாக mix ஆகி, workflow-ஐ maintain பண்ண முடியாமல் போகிறது.

## 2. Mental Model

Temporal-style durable workflow என்பது **உங்கள் business logic-ஐ ஒரு reliable state machine ஆக run செய்யும் engine**.

நீங்கள் steps-ஐ எழுதுவது போல sequential ஆக எழுதுங்கள். Engine அதை durable ஆக persist செய்து, crash ஆனாலும் அதே இடத்தில் தொடரும்.

Analogy: ஒரு recipe book. Chef கையில் இருந்து spoon விழுந்தால், recipe நின்று விடாது. Cookbook-ல எந்த step-ல இருந்தீர்கள் என்பது record ஆக இருக்கும். Chef வந்ததும் அதே step-ல தொடரலாம்.

## 3. How It Works

Workflow code உங்களுடையது, ஆனால் அது **deterministic** ஆக இருக்க வேண்டும்.

Engine என்ன செய்கிறது:
* Workflow execution-ஐ event sourcing மூலம் persist செய்கிறது. ஒவ்வொரு step completion-ம் event ஆக save ஆகும்.
* Workflow worker crash ஆனாலும், replay செய்து அடுத்த step-ல தொடரும்.
* Activities என்று external calls-ஐ isolate செய்யும். Activity timeout, retry, heartbeat எல்லாம் engine கையாளும்.
* Signals, timers, cancellation எல்லாம் first-class concepts.

நீங்கள் எழுதுவது:

```
workflow runOrder(orderId):
  validate(orderId)
  payment = callPaymentActivity(orderId) // retry with backoff
  if payment.failed: compensate()
  inventory = callInventoryActivity(orderId)
  notifyUser(orderId)
```

Engine அதை `workflow execution` ஆக track செய்கிறது. Activity failure வந்தால், engine automatic retry செய்யும், அல்லது workflow-க்கு signal அனுப்பும்.

## 4. Architectural Reasoning

**எப்போது useful?**
* Multi-step business process > few seconds
* External service calls உள்ளது, network failure சாத்தியம்
* Human-in-the-loop, approval steps தேவை
* Replay / audit தேவை
* Long-running saga / compensation logic

**Constraint it addresses:** Reliability + operability. Developer reliability concerns-ஐ framework-க்கு delegate செய்வது.

**Alternatives:**
* In-process state machine + DB + manual retry → complex, bug-prone
* Message queue + saga pattern → works, ஆனால் workflow state reconstruct செய்ய கடினம்
* Cron + checkpoint → partial, visibility குறைவு

Architect ஏன் Temporal style-ஐ choose பண்ணுவார்? Because business logic readable ஆக இருக்கும், reliability operational concerns engine handle செய்யும். Team size பெரிதாகும்போது, everyone writes same retry logic தேவையில்லை.

## 5. Trade-offs

* **Determinism constraint:** Workflow code side-effects கொண்டிருக்கக்கூடாது. Random, time, external call எல்லாம் activities-க்குள் மட்டும். இது learning curve.
* **Latency vs Durability:** Every step persisted. Low latency வேண்டும் எனில் overhead தெரியும்.
* **Operational complexity:** New system - workflow service, worker fleet, visibility UI maintain பண்ண வேண்டும்.
* **Vendor lock-in:** Workflow definition engine-specific. Port செய்வது கடினம்.

Failure modes: Worker version upgrade செய்யும்போது non-deterministic change வந்தால் replay fail ஆகும். Workflow stuck ஆகலாம். Idempotency activities-ல் முக்கியம்.

## 6. Practical Example

AI Orchestration scenario: `RAG Agent Workflow`

1. `ingest_query`
2. `retrieve_context` from vector DB
3. `generate_answer` via LLM
4. `validate_answer` via second LLM call
5. `write_to_knowledge_base` if new info
6. `notify_user`

Query 30 seconds எடுக்கும். LLM provider தற்காலிகமாக down ஆனால் workflow 3-ல நின்னு 5 min கழித்து resume செய்யும். User-க்கு timeout ஆனாலும் workflow background-ல continue செய்யும்.

Engine heartbeat மூலம் long LLM call-ஐ track செய்யும். Activity retry with exponential backoff. Workflow history மூலம் ஏன் fail ஆனது என audit செய்யலாம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு payment reconciliation workflow இருக்கு. ஒரு நாளைக்கு 10,000 runs. ஒவ்வொரு run-ம் 20 steps, average 2 நிமிஷம்.

Requirement: Step fail ஆனால் மறுபடி அதே step-ல தொடர வேண்டும். Team different language-ல microservices எழுதுகிறது.

இதை நீங்கள் Temporal-style durable workflow-ல implement செய்வீர்களா? இல்லை message queue + idempotent workers + DB checkpoint செய்வீர்களா? ஏன்?

## 8. Key Takeaways

* Durable workflow = business logic-ஐ reliable execution engine-க்கு delegate செய்வது
* State persistence + deterministic replay = crash recovery சாத்தியம்
* Activities-ல external calls isolate செய்து retry, timeout, heartbeat கையாளுங்கள்
* Trade-off: simplicity of code vs determinism constraint + operational overhead
