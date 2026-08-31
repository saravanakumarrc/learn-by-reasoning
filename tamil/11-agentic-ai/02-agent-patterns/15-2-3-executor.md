# Executor

> **Learning Path:** Agentic AI
> **Section:** 15.2.3 — Agent patterns

## 1. Problem

உங்க agent ஒரு plan பண்ணுது. "User-க்கு quarterly sales report generate பண்ணு"ன்னா agent யோசிக்கும்: 1. DB-ல data fetch பண்ணு, 2. aggregate பண்ணு, 3. chart create பண்ணு, 4. PDF generate பண்ணு, 5. email அனுப்பு.

Plan பண்ணினது ஒன்னு. அதை execute பண்ணுறது வேற. Agent-க்கு எல்லா tools-மும் தெரியும், ஆனா அதை எப்படி call பண்ணனும், input-output எப்படி map பண்ணனும், error வந்தா retry பண்ணனுமா, partial failure-ல என்ன பண்ணனும் — இதெல்லாம் confusing ஆகுது.

Plan-ஐ generate பண்ணும் brain மற்றும் action-ஐ செய்யும் hands-ஐ ஒன்னா வச்சா, LLM-ம் hallucinate பண்ணும், tool call syntax தப்பிக்கும், state மறக்கும்.

இந்த வலி வரும்போது தான் Executor pattern தேவைப்படுது.

## 2. Mental Model

Executor என்பது **Planner-ன் plan-ஐ ஒரு deterministic engine மூலம் run பண்ணும் worker**.

Planner = strategy
Executor = execution loop

ஒரு kitchen-ல Chef menu plan பண்ணுவார். Executor அதை step-by-step follow பண்ணி, ingredients ready இருக்கானு check பண்ணி, stove-ஐ switch on பண்ணி, timer set பண்ணி, failed dish-ஐ retry பண்ணுவார்.

Agent-ல, Executor கிட்ட plan வரும். அது ஒவ்வொரு step-ஐயும் validate பண்ணி, tool-ஐ call பண்ணி, result-ஐ capture பண்ணி, next step-க்கு context pass பண்ணும்.

## 3. How It Works

Typical loop:

1. **Plan intake**: Planner-ல இருந்து structured plan வாங்கும். Steps = [tool_name, inputs, expected output]
2. **State tracking**: Current step index, history of tool calls, intermediate results.
3. **Execution**: Step-ஐ run பண்ணு → tool-ஐ call பண்ணு → output-ஐ schema-வோட validate பண்ணு
4. **Decision**: Success? → next step. Failure? → retry / fallback / ask Planner to replan
5. **Termination**: All steps done or unrecoverable error.

Executor LLM-ஐ use பண்ணலாம், ஆனா அதன் job reasoning அல்ல. Orchestration. பல implementation-ல Executor என்பது simple loop + state machine. LLM-ஐ மீண்டும் reasoning-க்கு call பண்ணாமல் tool call-ஐ execute பண்ணும்.

## 4. Architectural Reasoning

இது எப்போ useful?

* Multi-step workflows இருக்கும்போது
* Tool calls deterministic ஆக இருக்கும் போது
* Error handling, retry, timeout, idempotency தேவைப்படும் போது

Planner-ஐ pure reasoning-க்கு மட்டும் வச்சு, Executor-ஐ execution-க்கு மட்டும் வச்சால்:

* Planner simpler ஆகும், less hallucination
* Execution observable ஆகும், logs, metrics எளிது
* Same plan-ஐ different Executor-களால் run பண்ணலாம்

Alternatives:
* **Monolithic Agent**: Planner + Executor ஒன்னா. Simple ஆனா fragile.
* **ReAct loop**: LLM தான் next action decide பண்ணும். Flexible ஆனா costly, non-deterministic.

Architect தேர்வு: Control முக்கியமா? Audit trail வேணுமா? Cost முக்கியமா? ReAct cheap workflow-க்கு நல்லது. Executor enterprise workflow-க்கு நல்லது.

## 5. Trade-offs

* **Determinism vs Flexibility**: Executor strict step follow பண்ணும். Plan தப்பா இருந்தா stuck ஆகும். ReAct dynamic ஆக adapt பண்ணும்.
* **Observability vs Complexity**: Executor-ல each step traceable. Extra component maintain பண்ணனும்.
* **Latency**: Every step synchronous wait. Parallel execution கைமுறையா design பண்ணனும்.
* **Failure modes**: Tool timeout, partial success, schema mismatch. Executor-ல retry with exponential backoff, circuit breaker வச்சு handle பண்ணனும். இல்லனா whole plan fail ஆகும்.

## 6. Practical Example

Enterprise support agent.

User: "Last month-ல failed payments-ஐ refund பண்ணு"

Planner generates plan:
1. fetch_failed_payments(month=last)
2. validate_refund_eligibility(payment_id)
3. create_refund(payment_id)
4. notify_user(payment_id)

Executor receives this plan. It maintains state in memory/DB.

Step1 success → 120 payment_ids
Step2 loop: 120 items. 5 items ineligible → mark skip
Step3: API call to payment service. 2 calls timeout → retry with idempotency key. Success.
Step4: send email via notification service.

Executor logs each step, emits events to observability. If step3 fails after 3 retries, Executor pauses and asks Planner for alternative plan, e.g., batch refund.

Without Executor, LLM would try to remember all 120 ids in context, hallucinate API payloads.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG agent இருக்கு. Plan: retrieve → rerank → summarize → cite. Retrieve step 2 sec எடுக்குது, rerank 1 sec, summarize 3 sec. Executor ஒரு step-ஐ முடிச்சு தான் அடுத்த step-ஐ start பண்ணுது.

User experience slow ஆகுது. எந்த architectural மாற்றம் பண்ணுவீங்க? Executor-ஐ modify பண்ணுவீங்களா, அல்லது plan-ஐ மாற்றுவீங்களா? ஏன்?

## 8. Key Takeaways

* Executor = plan-ஐ run பண்ணும் deterministic engine, reasoning இல்லை.
* Planner-ஐ reasoning-க்கு, Executor-ஐ execution & reliability-க்கு பிரிப்பது observability, retry, idempotency-ஐ எளிதாக்கும்.
* Every architectural solution creates trade-off: determinism vs flexibility, control vs cost.
* Agent design-ல separation of concerns தான் scalability க்கு முக்கியம்.
