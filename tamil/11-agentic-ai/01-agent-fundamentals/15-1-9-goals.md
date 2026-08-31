# Goals

> **Learning Path:** Agentic AI
> **Section:** 15.1.9 — Agent fundamentals

## 1. Problem

ஒரு LLM-ஐ நீங்கள் chatbot-ஆக போட்டுவிட்டீர்கள். User கேள்வி கேட்டால், அது அழகாக பதில் சொல்கிறது. ஆனால் user சொன்னது: "எனது கடந்த 3 மாத ஆர்டர்களை எடுத்து, total spend-ஐ கணக்கிட்டு, அதற்கு ஏற்ற discount coupon-ஐ apply பண்ணி, எனக்கு email அனுப்பு."

இங்கே என்ன நடக்கும்? LLM தனியாக database-ஐ query பண்ண முடியாது. Email அனுப்ப முடியாது. Logic-ஐ ஒழுங்காக step-by-step run பண்ண முடியாது. ஒரே response-ல் hallucination ஆனது.

**Problem என்ன?** LLM என்பது ஒரு language model. அது world-ஐ access பண்ணும் power இல்லாதது. Tool use, memory, planning இல்லாதது.

அதனால் தான் *agent* தேவைப்பட்டது.

## 2. Mental Model

Agent என்பது: **LLM + Tools + Memory + Planning loop**.

எளிமையாக சொன்னால், LLM ஒரு brain. அதற்கு கைகள் தேவை. Tools அந்த கைகள். Database query, API call, search, email send, calculator — இவை tools.

ஒரு agent என்பது goal-oriented. "என்ன செய்யணும்" என்பதை புரிந்து கொண்டு, அதை சிறு steps-ஆக பிரித்து, tools-ஐ use பண்ணி, result-ஐ பார்த்து திரும்ப plan பண்ணும்.

நீங்கள் ஒரு junior developer-க்கு task கொடுப்பது போல. "இதை செய். இந்த tools உனக்கு கிடைக்கும். செய்யும்போது என்ன கிடைக்குதுன்னு பார்த்து முடிவு எடு."

## 3. How It Works

Core loop மிகவும் simple:

**Observe → Think → Act → Observe**

1. **Observe**: User goal, context, previous tool results, memory
2. **Think**: LLM தனது reasoning-ஐ use பண்ணி next action-ஐ தீர்மானிக்கிறது. இது ReAct pattern: Reason + Act
3. **Act**: Tool-ஐ call பண்ணுகிறது. உதாரணமாக `get_orders(user_id, last_90_days)`
4. **Observe**: Tool result திரும்ப வரும். அதை பார்த்து தொடரும்.

இது loop ஆகிறது until goal complete.

Memory இங்கே முக்கியம். Short-term memory = conversation history. Long-term memory = vector database / user profile / past actions. இல்லாமல் agent திரும்ப திரும்ப ஒன்றை கேட்கும்.

Planning level: Simple agent ஒரு step முன்னால் தான் பார்க்கும். Advanced agent multi-step plan தீட்டி, dependencies பார்த்து, rollback பண்ணும்.

## 4. Architectural Reasoning

Agent எப்போது useful?

* User request என்பது single answer அல்ல, multi-step workflow.
* External systems-ஐ access செய்ய வேண்டும்.
* Context time-sensitive / dynamic.

Alternatives:
* **Static RAG**: User query → retrieve docs → answer. Tools இல்லை, loop இல்லை.
* **Hardcoded workflow**: Business logic code-ல் hardcode செய்யப்பட்டது. Flexible இல்லை.
* **Human-in-the-loop**: எல்லாம் manual.

Agent choose பண்ணும் போது architect யோசிக்க வேண்டியது:
* Tool reliability எப்படி? Tool fail ஆனால் retry / fallback என்ன?
* Planning deterministic ஆக வேண்டுமா? Financial transaction-க்கு strict.
* Latency எவ்வளவு acceptable? Loop ஒவ்வொன்றும் LLM call = cost + latency.

## 5. Trade-offs

**1. Autonomy vs Control**
Agent-க்கு அதிக freedom கொடுத்தால், unexpected tool calls வரும். Guardrails, allow-listed tools, validation layer தேவை. Control கொடுத்தால் flexibility குறையும்.

**2. Cost vs Capability**
Every loop = LLM inference + tool call. 5-step task = 5x cost. Small model + few-shot கொண்டு குறைக்கலாம், ஆனால் reasoning quality குறையும்.

**3. Hallucination and tool misuse**
LLM தவறான tool parameter generate பண்ணும். Type validation, schema enforcement, tool result verification தேவை. இல்லாவிட்டால் data corruption.

**4. Observability**
Traditional API-க்கு request/response இருக்கும். Agent-க்கு non-deterministic plan இருக்கும். Debugging கடினம். Tracer, tool call logs, decision audit trail முக்கியம்.

Failure modes: Infinite loop, tool looping, context overflow, sensitive data leakage via tool output.

## 6. Practical Example

Enterprise support agent.

User: "எனது account-ல் last invoice-ஐ ஏன் dispute பண்ண முடியலை?"

Agent steps:
1. `get_user_from_email` tool → user_id
2. `get_invoices(user_id, limit=1)` → invoice_id, status
3. Status = `pending_payment`. Dispute allowed only for `paid` invoices.
4. `check_payment_methods(user_id)` → card expired
5. Agent reason: user can pay now, then dispute window open.
6. `send_email` tool with explanation + payment link.

இங்கே agent மட்டும் இல்லை, business policy-யை follow பண்ணும். Tool outputs-ஐ synthesize பண்ணி human-readable answer கொடுக்கும்.

## 7. Reasoning Challenge

உங்களிடம் 20,000 users-க்கு monthly report generate பண்ணும் agent உள்ளது. ஒவ்வொருவருக்கும் database query, PDF generation, email send என 3 steps. Agent per user 4 LLM calls எடுக்கிறது.

இங்கே என்ன architectural problem வரும்? Cost, latency, reliability எப்படி handle பண்ணுவீர்கள்? Agent-ஐ fully autonomous-ஆ விடுவீர்களா, அல்லது workflow orchestration + LLM for decision only என மாற்றுவீர்களா? ஏன்?

## 8. Key Takeaways

* Agent என்பது LLM மட்டும் அல்ல. LLM + Tools + Memory + Planning loop.
* Agent-ஐ design பண்ணும்போது முதலில் tools, failure modes, observability பாருங்கள்.
* Every step = cost + latency. Autonomy-க்கு விலை உண்டு.
* Agent என்பது architectural decision. Simple RAG போதும் என்றால் agent-ஐ விரிவுபடுத்தாதீர்கள்.
