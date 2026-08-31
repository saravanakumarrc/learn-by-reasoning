# Reasoning

> **Learning Path:** Agentic AI
> **Section:** 15.1.3 — Agent fundamentals

## 1. Problem

ஒரு LLM-க்கு நீங்கள் ஒரு task கொடுக்கிறீர்கள்: "எனக்கு user-ன் last 3 orders-ஐ எடுத்து, அவர் அதிகம் வாங்கும் category-ஐ கண்டுபிடித்து, அதற்கு ஒரு personalized offer generate பண்ணு."

LLM தனியாக என்ன செய்யும்? Prompt-ல் உள்ள data இல்லாமல் answer சொல்ல முடியாது. Order data எங்கே இருக்கு? Database-ல. Offer generate பண்ணணும்னா business rules தெரியணும்.

Simple chatbot போல "நான் தெரியாது" என்று சொல்லாமல், agent மாதிரி system ஒன்று தேவை: **சிந்தித்து, tools-ஐ use பண்ணி, படிப்படியாக task-ஐ முடிக்க**.

Problem என்ன? One-shot answer-ல் complex multi-step, multi-system task முடியாது. Context window limited, knowledge stale, மற்றும் external world-ல் action எடுக்க வேண்டும்.

## 2. Mental Model

Reasoning என்பது LLM-ன் output-ஐ **plan → execute → observe → revise** loop-க்குள் வைப்பது.

ஒரு experienced engineer போல் சிந்திக்கவும்:
> "என்ன தெரியும்? என்ன தெரியாது? என்ன tool தேவை? முதல் step என்ன? Result வந்ததும் அடுத்த step என்ன?"

Reasoning என்பது model-ஐ *generate text* பண்ண வைப்பதில்லை. Model-ஐ *internal chain-of-thought* உருவாக்கி, அதை action-ஆக மாற்ற வைப்பது.

Analogy: LLM என்பது ஒரு மிகவும் அறிவான ஆனால் blind intern. Agent framework என்பது intern-க்கு tools, memory, மற்றும் supervisor கொடுக்கிறது. Reasoning என்பது intern எப்படி plan போடுகிறான் என்பது.

## 3. How It Works

Agent fundamentals-ல் reasoning இப்படி work ஆகிறது:

**Thought:** Model current context-ஐ பார்த்து next logical step-ஐ infer பண்ணும். "எனக்கு user_id தேவை, ஆனால் இல்லை, முதலில் ask பண்ணணும்."

**Action:** Thought-ஐ tool call-ஆக மாற்றும். `get_user_orders(user_id)`, `search_product_catalog(category)`, `generate_offer(...)` போன்ற function.

**Observation:** Tool result திரும்ப வரும். Result success/fail, data.

**Loop:** Observation-ஐ திரும்ப context-ல் சேர்த்து அடுத்த Thought generate.

இது ReAct pattern: Reasoning + Acting. Model chain-of-thought-ஐ explicit-ஆக வெளியே கொண்டு வந்து, tool use-ஐ decision point-ஆக மாற்றும்.

Modern systems-ல் reasoning can be:
- **Chain-of-Thought prompting** - internal step-by-step
- **Tree-of-Thought** - multiple paths explore
- **Self-reflection** - answer-ஐ critique பண்ணி revise
- **Tool-augmented reasoning** - external data/tools-ஐ use பண்ணி reason

## 4. Architectural Reasoning

Reasoning தேவைப்படும் போது:

- Task multi-step and depends on external systems. DB query, API call, search, calculation தேவை.
- Output quality depends on fresh data, not static training knowledge.
- Error recovery தேவை. Tool fail ஆனால் retry or alternative path எடுக்க வேண்டும்.

Architect choose reasoning when:
- Simple RAG answer போதாது. User intent complex.
- Consistency முக்கியம். Same input-க்கு deterministic plan.
- Observability தேவை. Why agent இப்படி decide பண்ணியது என்பதை trace பண்ண வேண்டும்.

Alternative என்ன? Hard-coded workflow, orchestration. அது predictable ஆனால் brittle. New requirement வந்தால் code change தேவை. Reasoning-ஆல் model flexible ஆகும், ஆனால் non-deterministic.

Decision point: **Reasoning is for open-ended tasks, orchestration is for closed workflows.**

## 5. Trade-offs

**Latency vs Quality.** ஒவ்வொரு reasoning step-க்கும் LLM call + tool call. 3-5 steps = 3-5x latency. User experience-க்கு கேடு. ஆனால் quality improve ஆகும்.

**Correctness vs Hallucination.** Reasoning chain-ல் model wrong assumption எடுக்கலாம். "User last order என்பது 2024" என்று guess பண்ணி தவறான tool call. Guardrails, validation, structured output தேவை.

**Cost vs Capability.** Every thought = token. Agent with reasoning expensive. Production-ல் cost per request முக்கிய constraint.

**Control vs Autonomy.** More reasoning = more autonomy, ஆனால் auditability குறையும். Financial system-ல் agent தன்னிச்சையாக money transfer செய்யக்கூடாது. Human-in-the-loop தேவை.

Failure mode: Infinite loop. Agent தன்னைத்தானே circle-ல் reasoning பண்ணும். Max steps, timeout, and self-termination logic தேவை.

## 6. Practical Example

Enterprise support agent.

User: "எனது subscription-ஐ cancel பண்ணுங்க, ஆனால் முதலில் எனக்கு எவ்வளவு refund கிடைக்கும் என்று சொல்லுங்கள்."

Agent reasoning:
1. Thought: subscription_id தெரியாது. User identity verify செய்ய வேண்டும்.
2. Action: `verify_user(phone)`
3. Observation: user found, subscription_id = sub_123
4. Thought: refund policy தேவை, subscription start date, billing cycle தெரிய வேண்டும்.
5. Action: `get_subscription(sub_123)`, `get_refund_policy(plan)`
6. Observation: started 45 days ago, prorated refund = $27
7. Thought: user-க்கு confirm கேட்க வேண்டும்.
8. Action: ask user "Refund $27 confirm?"
9. Observation: user says yes
10. Action: `cancel_subscription(sub_123)`

Reasoning இல்லாமல் இது 10 separate prompts ஆகிவிடும். Reasoning-ஆல் flow automatic ஆகிறது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு agentic AI system இருக்கிறது. User asks: "எனது முந்தைய ஆர்டர்களைப் பார்த்து, எனக்கு பிடித்த பிராண்ட்-ஐ கண்டுபிடித்து, அதே பிராண்டின் புதிய product-ஐ suggest செய்."

Agent-க்கு database access உள்ளது, product catalog search tool உள்ளது.

இங்கே reasoning எப்படி fail ஆகலாம்? உதாரணமாக user-க்கு பல பிராண்டுகள் உள்ளன, அல்லது order history empty. Agent என்ன செய்ய வேண்டும்? Clarify செய்யுமா? அல்லது default assumption எடுக்குமா? நீங்கள் என்ன guardrail வைப்பீர்கள்?

## 8. Key Takeaways

- Reasoning என்பது LLM-ஐ plan செய்ய வைப்பது, முடிவுகளை tools மூலம் execute செய்வது.
- Problem → Constraints → Options → Reasoning → Decision என்ற loop agent-ஐ engineer போல் சிந்திக்க வைக்கிறது.
- More reasoning = more flexibility, ஆனால் latency, cost, hallucination risk அதிகரிக்கும்.
- Architect-ஆக நீங்கள் decide செய்ய வேண்டியது: எந்த task-க்கு autonomous reasoning தேவை, எதற்கு hard orchestration போதும்.
