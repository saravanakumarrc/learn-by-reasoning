# Output parsing

> **Learning Path:** LLM Application Engineering
> **Section:** 11.2.6 — Structured outputs

## 1. Problem

நீங்கள் ஒரு LLM-ஐ உங்கள் service-க்குள் பயன்படுத்துகிறீர்கள். LLM-க்கு prompt கொடுத்து, response வருகிறது. அந்த response-ஐ உங்கள் backend code எடுத்து அடுத்த step-க்கு போக வேண்டும்.

இங்கே என்ன வரும்? Free-form text.

நீங்கள் வேண்டியது structured data. உதாரணமாக:
`{ "intent": "book_flight", "origin": "Chennai", "destination": "Delhi", "date": "2025-12-01" }`

ஆனால் LLM தருவது:
"சரி, Chennai-ல இருந்து Delhi-க்கு 1 Dec-க்கு flight book பண்ணலாம். Intent book_flight."

இது human-க்கு புரியும். Code-க்கு புரியாது.

Output parsing என்பது இந்த gap-ஐ close பண்ணுவது. LLM output-ஐ reliable JSON / schema-க்கு மாற்றுவது.

**What goes wrong if we don't have this?**
Parsing fail ஆகும், fields missing ஆகும், type mismatch ஆகும், hallucination வரும். Retry logic, error handling எல்லாம் messy ஆகும். Production-ல இது silent bug ஆக மாறும்.

## 2. Mental Model

LLM என்பது probabilistic text generator. அதற்கு schema என்பது constraint அல்ல.

Output parsing = **LLM output-ஐ உங்கள் system boundary-க்கு சரியாக fit ஆக்கும் adapter**.

இது 3 layer-ல நடக்கும்:
1. **Generation constraint**: LLM-ஐ structured output தர சொல்லி கட்டுப்படுத்துவது
2. **Validation**: வந்த output schema-க்கு match ஆகிறதா என்று check செய்வது
3. **Repair / Fallback**: match இல்லை என்றால் fix பண்ணுவது அல்லது safe default-க்கு போவது

## 3. How It Works

**Option A: Prompt engineering only**
"Output valid JSON only, keys: intent, origin...". இது cheap ஆனால் unreliable. Model size குறையும் போது, format drift ஆகும்.

**Option B: Schema-guided generation**
Modern models support `response_format: json_schema` அல்லது structured outputs. Model decoder-ஐயே schema-க்கு constrain பண்ணும். Token generation-லயே invalid JSON வராமல் தடுக்கும்.

**Option C: Output parser in code**
LLM output-ஐ பெற்ற பிறகு Pydantic / Zod model-க்கு parse முயற்சி. Fail ஆனால்:
- Re-prompt with error message
- Use regex / LLM-as-parser for extraction
- Return partial result

**Option D: Two-step parsing**
First pass: raw text -> LLM extracts structured fields via a small, deterministic parser prompt.
Second pass: Validate against schema.

Practical-ல நீங்கள் பெரும்பாலும் B + C கலந்து பயன்படுத்துவீர்கள்.

## 4. Architectural Reasoning

**When this becomes useful?**
LLM output நேரடியாக database-க்கு போகும் போது, API response ஆகும் போது, அல்லது downstream service-க்கு input ஆகும் போது.

**What constraint it addresses?**
Reliability and contract. உங்கள் system-க்கு deterministic interface வேண்டும். LLM nondeterministic.

**Alternatives?**
*Post-processing with regex*: Quick but brittle. Schema மாறினால் உடைந்து விடும்.
*Human-in-the-loop*: Correctness உறுதி ஆனால் latency, cost அதிகம்.
*No structure, just RAG*: Chatbot-க்கு மட்டும் போதும். Automation-க்கு போதாது.

Architect choose schema-guided generation when correctness > creativity. Choose parser+validation when you need backward compatibility and observability.

## 5. Trade-offs

**Schema strictness vs flexibility**
Strict JSON schema = fewer hallucinations, but model may refuse or truncate. Loose schema = more outputs but more validation failures.

**Latency vs reliability**
Structured output generation சற்று slow ஆகும். Re-prompt + repair cycle latency-ஐ 2-3x ஆக்கும். ஆனால் error rate குறையும்.

**Cost vs accuracy**
Validation fail ஆனால் re-prompt பண்ணினால் token cost double. Better to invest in good schema + few-shot examples upfront.

**Failure modes**
- Model returns valid JSON but semantically wrong. Parser catch செய்யாது. Need semantic validation.
- Partial output: JSON truncated due to max_tokens. Parser crash.
- Type coercion: `"price": "twenty"` instead of number. Schema validation fail.

## 6. Practical Example

Enterprise support ticket triage agent.

Input: user message in Tamil/English mixed.
Need output:
```json
{
  "category": "billing|technical|refund",
  "priority": "low|medium|high",
  "needs_human": boolean,
  "extracted_entities": { "order_id": "...", "amount": number }
}
```

Architecture:
1. LLM call with `response_format: json_schema` defining above schema + examples.
2. Response comes back. Pydantic model validate செய்கிறது.
3. If validation error -> log to observability, trigger repair prompt with error message.
4. If valid but `needs_human=true` -> route to human queue. Else auto action.

இங்கே output parsing இல்லாமல், நீங்கள் free text-ஐ மறுபடியும் LLM-க்கு கொடுத்து parse செய்ய வேண்டும். அது fragile மற்றும் expensive.

## 7. Reasoning Challenge

உங்கள் RAG agent ஒரு product catalog-ல இருந்து 3 products recommend செய்ய வேண்டும். Output schema: array of objects with `product_id`, `price`, `reason`. 

Production-ல 2% cases-ல LLM array-ஐ return பண்ணாமல் bullet list தருகிறது. Schema-guided generation use பண்ணினாலும் model சில நேரம் `reason` field-ஐ miss பண்ணுகிறது.

நீங்கள் என்ன design செய்வீர்கள்? Re-prompt செய்யலாமா? Fallback parser எழுதலாமா? இரண்டுக்கும் trade-off என்ன?

## 8. Key Takeaways

* Output parsing என்பது LLM-ஐ deterministic system-ஆக்கும் bridge.
* Schema-guided generation + code validation இரண்டும் சேர்த்தே production ready ஆகும்.
* Parser fail ஆனால் repair strategy தயாராக இருக்க வேண்டும், silent failure அனுமதிக்க கூடாது.
* Every parsing decision is a trade-off between strictness, latency, cost, and reliability.
