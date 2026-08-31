# Function calling

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.1 — Learn

## 1. Problem

உங்களிடம் ஒரு LLM இருக்கு. அது text generate பண்ணுறது நல்லா. ஆனா user கேட்கிறான்: "என் last 3 orders-ஐ காட்டு" அல்லது "இன்னைக்கு USD to INR rate என்ன?".

LLM-க்கு உண்மையான data தெரியாது. அது hallucinate பண்ணி ஒரு rate சொல்லிடும். Wrong.

இன்னொரு option: நீங்களே prompt-ல எல்லா data-யும் hardcode பண்ணி கொடுக்க முடியாது. Real-time data வேணும். Business logic வேணும்.

இங்கே problem என்ன? LLM ஒரு brain மாதிரி, ஆனா அதுக்கு hands இல்ல. Action எடுக்க முடியாது.

அதனால் தான் **function calling** தேவைப்பட்டது.

## 2. Mental Model

Function calling என்பது LLM-க்கு ஒரு toolbox கொடுப்பது.

நீங்கள் LLM-க்கு சொல்கிறீர்கள்: "இதோ available tools இருக்கு. function A, function B. அவற்றின் parameters என்ன என்ன."

User query வந்ததும் LLM புரிஞ்சுக்கும்: இது எனக்கு தெரிஞ்சதில்ல, இது ஒரு tool call தேவை.

LLM output ஒரு structured call ஆக மாறும்: `get_orders(user_id="123", limit=3)`. உங்கள் system அதை execute பண்ணி result திருப்பி கொடுக்கும். LLM அந்த result-ஐ பயன்படுத்தி final answer-ஐ generate பண்ணும்.

அதாவது: LLM → decide tool → call → get data → reason → answer.

## 3. How It Works

Function calling ஒரு loop.

1. **Tool Definition**: நீங்கள் JSON schema-ல function definition கொடுக்கிறீர்கள். `name`, `description`, `parameters` with types.
   `description` மிக முக்கியம். LLM அதை பார்த்து தான் சரியான function-ஐ தேர்வு செய்யும்.

2. **Model Inference**: User prompt + tool definitions → LLM. Output இரண்டு வகை: direct answer அல்லது function call request.

3. **Execution**: உங்கள் application layer அந்த call-ஐ validate பண்ணி real service-க்கு அனுப்பும். Database query, API call, calculation.

4. **Result Injection**: Function output-ஐ மீண்டும் LLM-க்கு கொடுக்கிறீர்கள் as tool result. LLM அதை read பண்ணி natural language answer-ஐ உருவாக்கும்.

Multiple rounds நடக்கலாம். ஒரு call-ன் result பார்த்து அடுத்த function-ஐ decide பண்ணும்.

Important point: LLM function-ஐ execute பண்ணாது. அது மட்டும் decide பண்ணும். Execution உங்கள் code தான்.

## 4. Architectural Reasoning

Function calling எப்போ useful?

* **Grounding**: Real-time data தேவை. DB, API, pricing, inventory.
* **Action**: உண்மையான side effect வேண்டும். Payment create, ticket raise, email send.
* **Determinism**: LLM hallucinate பண்ணக்கூடாத இடங்களில் business logic-ஐ code-ல வைக்க.

Constraint அது address பண்ணும்: LLM-ன் knowledge cutoff, hallucination, lack of action.

Alternatives என்ன?
* **RAG only**: Data retrieve பண்ணி context-ல கொடுக்கலாம். ஆனா action இல்ல.
* **Prompt engineering with rules**: Static. Dynamic இல்ல.
* **Agent with code interpreter**: Powerful ஆனா slow, risky.

Architect ஏன் choose பண்ணுவார்? Control தேவை. LLM decide பண்ணும், நீங்கள் guardrails வைக்கலாம். Validation, auth, rate limiting எல்லாம் உங்கள் layer-ல.

## 5. Trade-offs

**Latency**: Every function call = network hop + LLM round trip. User experience slow ஆகும். Parallel calls செய்யலாம், ஆனா complexity ஏறும்.

**Correctness vs Flexibility**: LLM சரியான function-ஐ தேர்வு செய்யுமா? Description தெளிவாக இல்லை என்றால் wrong tool call. Overly generic schema = ambiguity.

**Error handling**: Function fail ஆனால் என்ன? Timeout, 500 error. LLM-க்கு error-ஐ திருப்பி கொடுத்து graceful fallback செய்ய வேண்டும். இல்லை என்றால் weird answer.

**Security**: LLM external tool-ஐ call பண்ணும். Parameter injection risk. User prompt-ல malicious input வந்து function parameter-ல தப்பாக map ஆகலாம். Validate, sanitize, auth check mandatory.

**Cost**: More tokens per turn. Tool definition + result injection = token increase.

## 6. Practical Example

Enterprise support chatbot.

User: "என் order #4521 delay ஆகுது, status என்ன?"

Flow:
1. LLM sees tools: `get_order_status(order_id)`, `create_support_ticket(user_id, order_id, issue)`
2. LLM decides `get_order_status` call needed.
3. System calls internal order service, gets: `status: shipped, ETA: 2 days`
4. LLM returns: "Order #4521 shipped ஆகிடுச்சு, 2 days-ல வந்துடும்."
5. User: "இல்ல, எனக்கு urgent வேணும்."
6. LLM decides `create_support_ticket` call.

இங்கே LLM ஒரு router மாதிரி வேலை செய்யுது. Business logic code-ல இருக்கு. LLM மட்டும் natural language bridge.

## 7. Reasoning Challenge

உங்களிடம் ஒரு finance agent இருக்கு. Tools: `get_stock_price(symbol)`, `convert_currency(amount, from, to)`, `get_portfolio_value(user_id)`.

User கேட்கிறான்: "என் portfolio இன்னைக்கு USD-ல எவ்வளவு?"

இதை handle பண்ண எத்தனை function calls தேவை? Sequence என்ன? முதலில் எந்த tool? எதையெல்லாம் assume பண்ணக்கூடாது? Portfolio value INR-ல வந்தால் என்ன செய்வீர்கள்?

## 8. Key Takeaways

* Function calling என்பது LLM-க்கு action capability கொடுக்கும் bridge. LLM decide பண்ணும், code execute பண்ணும்.
* Good tool description + strict schema = correct routing. இது architecture quality-ஐ decide பண்ணும்.
* Every call adds latency, cost, failure surface. Use only when real data/action தேவை.
* Validate, auth, error handle பண்ணாமல் function expose பண்ணாதீர்கள். LLM ஒரு untrusted client தான்.
