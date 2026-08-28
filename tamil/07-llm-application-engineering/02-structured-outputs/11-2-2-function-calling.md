# Function calling

> **Learning Path:** LLM Application Engineering
> **Section:** 11.2.2 — Structured outputs

## 1. Problem

LLM-ஐ நேரடியாக use பண்ணும்போது ஒரு பெரிய பிரச்சனை வரும்: output unpredictable.

நீங்கள் ஒரு agent-க்கு சொல்கிறீர்கள்: "user-க்கு order status கொடு". LLM சில நேரம் சரியாக status-ஐ extract பண்ணி தரும், சில நேரம் கதை மாதிரி எழுதும், சில நேரம் தவறான JSON தரும்.

நீங்கள் பின்னால் அந்த text-ஐ parse பண்ணி உங்கள் service-க்கு கொடுக்க வேண்டும். அது fragile.

**What goes wrong if we don't have this?**
- Hallucinated fields
- Wrong types: "price: free" instead of number
- Unstructured text, manual parsing fails
- Retry logic முடியாது
- Downstream service crash

Function calling என்பது இந்த பிரச்சனைக்கு பிறந்தது: LLM-ஐ சரியான structured output-ஐ கொடுக்க வைக்க, மற்றும் tool-ஐ call பண்ண வைக்க.

## 2. Mental Model

Function calling என்பது LLM-க்கு ஒரு schema கொடுப்பது.

> நீ கொடுக்கும் data இப்படி இருக்கணும். இந்த fields மட்டும் இருக்கணும். இதுக்கு மேல் இல்ல.

ஒரு contract போல. LLM அதை follow பண்ண முயற்சிக்கும்.

இரண்டு வடிவங்கள் உள்ளன:
1. **Structured Output:** LLM-ஐ திருப்பி JSON / schema-க்கு கட்டுப்படுத்துதல்.
2. **Tool Use / Function Calling:** LLM ஒரு function-ஐ identify பண்ணி, arguments-ஐ fill பண்ணி call செய்யச் சொல்லுதல்.

இரண்டும் ஒன்றாக வேலை செய்கிறது.

## 3. How It Works

நீங்கள் LLM-க்கு கொடுப்பது:

- System prompt
- User query
- Function definition: name, description, parameters with JSON Schema, required fields, types

LLM இதை பார்த்து:
1. இந்த query-க்கு function தேவையா என்று decide பண்ணும்
2. தேவைப்பட்டால் arguments-ஐ generate பண்ணும்
3. Structured JSON-ல் output தரும்

Provider side-ல் இது JSON Schema validation, guided decoding மூலம் enforce ஆகும்.

Simple flow:

User: "order 12345 status என்ன?"
LLM → detect need for `get_order_status`
LLM → arguments: {"order_id": "12345"}
Your code → call real service → return result
LLM → use result to generate final answer

## 4. Architectural Reasoning

Function calling எப்போது useful?

- LLM output downstream code-க்கு input ஆகிறது
- Multiple steps தேவை, tool use தேவை
- Reliability, type safety முக்கியம்
- RAG + agent workflow

Constraints it addresses:
- **Predictability:** Output schema fixed
- **Safety:** LLM arbitrary text generate பண்ண முடியாது
- **Composability:** Service-ஐ modular ஆக call பண்ணலாம்

Alternatives:
- Regex / post-processing: brittle, fail silently
- Prompt-only: "JSON return pannu" - works 80% time, production-ல் போதாது
- Strict output parsers: validation after generation, but LLM-க்கு retry செலவு

ஏன் architect choose பண்ணுவார்? Because business logic-ஐ LLM-ல் கொடுக்காமல், LLM-ஐ orchestrator ஆக use பண்ணி, actual data access, payment, DB operations எல்லாம் real functions-ல் வைக்க முடியும்.

## 5. Trade-offs

**1. Schema rigidity vs Flexibility**
Schema strict ஆக இருந்தால் LLM-க்கு hallucination குறையும், ஆனால் complex reasoning கட்டுப்படுத்தப்படும். Over-specify பண்ணாதீர்கள்.

**2. Latency & Cost**
Function call = multiple LLM round trips. Tool result-ஐ மீண்டும் LLM-க்கு feed பண்ண வேண்டும். Latency அதிகரிக்கும். Token cost அதிகரிக்கும்.

**3. Error handling**
Function definition தவறாக இருந்தால் LLM wrong arguments தரும். Parameter description unclear ஆனால் LLM guess பண்ணும். Validation layer தேவை.

**4. Operational complexity**
Function catalog maintain பண்ண வேண்டும். Versioning, deprecation, access control எல்லாம் வரும். LLM-க்கு தேவையான function-ஐ choose பண்ண சரியான description தர வேண்டும்.

Failure mode: LLM function-ஐ தேவையில்லாமல் call பண்ணும், அல்லது required param missing. Always validate arguments before calling real service.

## 6. Practical Example

Enterprise support chatbot.

User: "என் last order-க்கு refund வேண்டும்"

இதை LLM மட்டும் handle பண்ண முடியாது. Steps தேவை:
1. user identity verify
2. last order fetch
3. refund eligibility check
4. refund create

Function definitions:
- `get_user_by_email` parameters: email string
- `get_last_order` parameters: user_id string
- `check_refund_policy` parameters: order_id string, reason string
- `create_refund` parameters: order_id string, amount number

LLM user query-ஐ read பண்ணி step by step functions-ஐ call பண்ணும். Each output structured JSON. No free-form parsing.

இதனால் audit trail கிடைக்கும், business logic LLM-ல் இல்லை.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG system உள்ளது. User question-க்கு relevant chunks retrieve பண்ணி answer generate பண்ண வேண்டும்.

இரண்டு வழிகள் உள்ளன:
A. LLM-க்கு chunks கொடுத்து, பின்னர் answer generate பண்ணச் சொல்லி, structured JSON output enforce பண்ணுவது
B. LLM-க்கு `search_knowledge_base` function கொடுத்து, LLM தேவையான query-ஐ தானே generate பண்ணி call செய்ய வைப்பது

உங்கள் data 10M documents, latency SLA 2 sec. எந்த approach எடுப்பீர்கள்? ஏன்? என்ன trade-off?

## 8. Key Takeaways

- Function calling என்பது LLM-க்கு contract கொடுத்து structured, reliable output-ஐ enforce செய்வது
- Tool use மூலம் LLM-ஐ orchestrator ஆக்கி, real services-ஐ safely call செய்யலாம்
- Schema clarity முக்கியம்; bad description = bad arguments
- Every function call adds latency and cost, use it only where predictability தேவை
- Validation layer எப்போதும் வைக்கவும்; LLM-ஐ trust பண்ணாதீர்கள்
