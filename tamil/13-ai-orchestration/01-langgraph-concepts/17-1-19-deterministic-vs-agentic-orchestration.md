# Deterministic vs agentic orchestration

> **Learning Path:** AI Orchestration
> **Section:** 17.1.19 — LangGraph concepts

## 1. Problem

உங்களிடம் ஒரு AI workflow இருக்கு. User-க்கு loan application summary தயார் பண்ணனும்.

Step 1: Application form-ஐ read பண்ணு.
Step 2: Credit score fetch பண்ணு.
Step 3: Documents verify பண்ணு.
Step 4: Risk model-ஆல் score பண்ணு.
Step 5: Final summary generate பண்ணு.

இந்த steps எப்போதும் same order-ல், same tools-ஐ use பண்ணி, same output format-ல் வர வேண்டும். 

இப்போதான் requirement மாறுது. บาง customer-க்கு documents missing. அப்போ alternative path-க்கு போகணும். சில cases-ல் risk score high-னா extra human review node-க்கு போகணும். User follow-up question கேட்டால் conversation history-ஐ பார்த்து next step decide பண்ணணும்.

இங்கே என்ன problem வரும்? Fixed pipeline போட்டால் flexibility இல்லை. Fully free agent-ஆ விட்டால் control, audit, cost எல்லாம் கட்டுக்குள் வராது.

இந்த tension-தான் deterministic vs agentic orchestration.

## 2. Mental Model

Deterministic orchestration = **flow chart-ஐ முன்கூட்டியே வரைந்து விடுவது**.

நீங்கள் graph-ல் nodes-ஐ போட்டு, edges-ஐ hard-code பண்ணி விடுவீர்கள். LangGraph-ல் இது `StateGraph` with explicit `add_edge` / `add_conditional_edge`. ஒவ்வொரு run-மும் same path-ஐ follow பண்ணும்.

Agentic orchestration = **agent தான் next step decide பண்ணும்**.

Agent-க்கு goal, tools, memory கொடுத்து விட்டு, "இதை செய்" என்று சொல்லி விடுவீர்கள். அது தான் என்ன tool use பண்ண வேண்டும், எப்போது stop பண்ண வேண்டும் என்று reason பண்ணும். LangGraph-ல் இது `Agent` node + `LLM as router` pattern.

ஒன்று blueprint. மற்றொன்று self-driving.

## 3. How It Works

LangGraph-ல் இரண்டும் same primitive-களால் கட்டப்படுகிறது: nodes, edges, state.

Deterministic flow-ல்:
State ஒரு dict. Node A output -> State update -> Edge condition check -> Node B.
Conditional edge-ல் கூட decision function deterministic-ஆக இருக்கும். உதாரணமாக `if risk_score > 0.8: go_to human_review else go_to approve`. Logic நீங்கள் எழுதியது.

Agentic flow-ல்:
Node A ஒரு ReAct agent. Agent-க்கு tools list கொடுக்கப்பட்டிருக்கும். LLM தான் current state-ஐ பார்த்து, next action-ஐ choose பண்ணும். `Thought -> Action -> Observation` loop நடக்கும். Graph-ல் loop back edge இருக்கும்.

முக்கிய வித்தியாசம்: **Who decides the next node?** You vs Model.

## 4. Architectural Reasoning

Deterministic orchestration choose பண்ணுங்கள் when:

* Compliance, audit, reproducibility முக்கியம். Financial, healthcare, legal workflows.
* Steps fixed, exception cases limited and known.
* Latency மற்றும் cost predictable வேண்டும். No open-ended LLM reasoning loops.
* Same input => same output வேண்டும்.

Agentic orchestration choose பண்ணுங்கள் when:

* User intent ambiguous, conversation dynamic.
* Task decomposition முன்னதாக தெரியாது. Research, coding help, multi-step planning.
* Tools set large, and which tool needed depends on context.
* You want system to discover new paths.

Hybrid தான் real world. Deterministic skeleton + agentic node inside.

LangGraph-ல் common pattern: Outer graph deterministic, inner node agentic. உதாரணமாக, `extract -> classify -> agent_resolve -> finalize`. Classify deterministic, resolve agentic.

## 5. Trade-offs

**Control vs Flexibility**
Deterministic = full control, testable, observable. Agentic = flexible, but non-deterministic.

**Cost & Latency**
Deterministic = predictable token usage, fixed number of LLM calls. Agentic = loop வரைக்கும் run ஆகும். Hallucination-ஆல் extra tool calls.

**Debugging & Ops**
Deterministic = graph trace easy. Same state, same path. Agentic = need LLM reasoning logs, guardrails, max iterations.

**Failure modes**
Deterministic: missing edge case -> hard failure. You need to pre-model all.
Agentic: infinite loop, tool misuse, goal drift. Need `max_steps`, `interrupt` handling.

**Maintainability**
Deterministic: code changes for new path. Agentic: prompt changes may suffice, but behaviour harder to pin down.

## 6. Practical Example

Loan summary workflow.

Deterministic version:
`parse_form -> fetch_credit -> verify_docs -> risk_score -> generate_summary`

Conditional edge: `verify_docs` output `missing_docs` -> `request_docs` node.

இது production-க்கு safe. Audit log clean.

Agentic version:
`triage_agent` node gets whole application. Agent decides: credit fetch வேண்டுமா? Document verification எந்த tool-ஆல்? Risk model எந்த version? User follow-up கேட்டால் context-ஐ பார்த்து தான் next action decide.

Hybrid:
Outer graph deterministic: `intake -> triage -> processing -> output`.
`processing` node உள்ளே agentic loop இருக்கும். Processing-ல் agent தான் sub-steps decide பண்ணும், ஆனால் outer graph-ல் timeout, human review, compliance check fixed.

இது cost கட்டுக்குள் வைத்து flexibility கொடுக்கும்.

## 7. Reasoning Challenge

உங்களிடம் customer support agent இருக்கு. 80% queries FAQ-ஆல் resolve ஆகும். 20% escalate ஆகும். Queries increasing, new product features weekly add ஆகிறது.

Option A: Fully deterministic LangGraph with router node for each product feature.
Option B: One agentic node with tools: knowledge base search, ticket create, refund API.

நீங்கள் எதை தேர்வு செய்வீர்கள்? எப்போது hybrid-க்கு மாறுவீர்கள்? Cost, accuracy, ops complexity எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Deterministic orchestration = you control the path, predictable, auditable.
* Agentic orchestration = model controls the path, flexible, harder to guarantee.
* Real systems use deterministic skeleton with agentic nodes inside.
* Decision driver: how much uncertainty is acceptable vs how much control you need.
* Always design for failure: max steps, interrupts, human handoff.
