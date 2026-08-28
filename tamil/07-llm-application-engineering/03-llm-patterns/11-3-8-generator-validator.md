# Generator/validator

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.8 — LLM patterns

## 1. Problem

உங்க system-ல LLM ஒரு response generate பண்ணுது. அந்த response ஒரு structured JSON ஆக இருக்கணும், schema-க்கு match ஆகணும், factually correct ஆக இருக்கணும், policy-க்கு violate பண்ணக்கூடாது.

இப்போ LLM ஒரு shot-ல தப்பு பண்ணலாம். Hallucination வரும். JSON invalid ஆக வரும். Fields missing ஆகும். Business rule break ஆகும்.

இந்த output-ஐ நேரடியா user-க்கு அனுப்பினா என்ன ஆகும்? Downstream service crash ஆகும். Bad data database-ல போய் உட்காரும். Compliance breach ஆகும்.

இங்கே தேவை என்ன? **Generate பண்ணு, பிறகு validate பண்ணு, தப்புனா திரும்ப generate பண்ணு.** இது ஒரு loop.

## 2. Mental Model

Generator/validator pattern என்பது simple:

**Generator → Validator → Accept / Reject → Retry**

LLM என்பது Generator. அது creative, probabilistic. Validator என்பது deterministic checker. அது rules, schema, regex, code, external API call மூலம் check பண்ணும்.

Generator ஒரு முறை தப்பு பண்ணினாலும், validator catch பண்ணி திரும்ப சொல்லி திருத்த வைக்கலாம்.

இது ஒரு for-loop மாதிரி. நீங்கள் ஒரு junior developer-க்கு code review கொடுப்பது போல.

## 3. How It Works

Flow இப்படி:

1. Prompt + context → LLM → candidate output
2. Validator ஓடும்:
   - **Format validator:** JSON schema valid? Types correct? Required fields உள்ளதா?
   - **Logic validator:** Business rules follow ஆகிறதா? e.g., price > 0, date future-ல இல்லை
   - **Grounding validator:** Fact database/ API-ல cross-check பண்ணுதா?
   - **Policy validator:** Toxic, PII leak இல்லையா?
3. Pass ஆனால் output-ஐ return செய்
4. Fail ஆனால் error signal-ஐ திருப்பி generator-க்கு கொடு: "JSON invalid, missing field X" போன்ற feedback.
5. Max retries வரை loop.

இந்த feedback-ஐ சிலர் self-correction prompt-ல் கொடுக்கிறார்கள். சிலர் separate critic model-ஐ use பண்ணி validate பண்ணுகிறார்கள்.

## 4. Architectural Reasoning

எப்போது இது useful?

- Output format strict ஆக இருக்க வேண்டும்: API response, function calling schema, database record
- Hallucination cost high: finance, medical, legal
- Safety critical: policy violation கூடாது

Alternatives என்ன?

- **Better prompting only:** One-shot with examples. Cheap, but unreliable for strict schema.
- **Constrained decoding / Structured output:** LLM-ஐ token level-ல restrict பண்ணுது. Format guarantee ஆகும், ஆனால் content correctness guarantee இல்லை.
- **RAG + Grounding:** Fact correct ஆகும், ஆனால் format still risky.

Generator/validator என்பது இவற்றை combine பண்ணும். Format + logic + policy எல்லாவற்றையும் separate deterministic layer-ல் enforce பண்ணலாம்.

Architect க்கு இது முக்கியம், ஏனென்றால் LLM-ஐ black box ஆக நம்பாமல், system boundary-ல் safety net வைக்கிறோம்.

## 5. Trade-offs

**Latency vs Reliability:** ஒவ்வொரு retry-ம் LLM call + validator call. P95 latency increase ஆகும். Max retry limit வைக்க வேண்டும்.

**Cost:** LLM calls multiple times ஆகும். Token cost increase. Validator cheap ஆக இருக்க வேண்டும், இல்லை என்றால் cost explode ஆகும்.

**Correctness vs Creativity:** Validator strict ஆக இருந்தால் generator அதிகம் constrain ஆகும், output boring ஆகும். Too loose ஆனால் bug slip ஆகும்.

**Failure mode:** Validator itself wrong feedback கொடுத்தால் generator loop-ல் stuck ஆகும். Or infinite loop. Circuit breaker தேவை.

## 6. Practical Example

Enterprise support ticket classification agent.

Requirement: LLM ticket description-ஐ படித்து JSON return பண்ண வேண்டும்:
```json
{"category": "billing|tech|sales", "priority": "low|medium|high", "needs_escalation": true/false}
```

Generator/validator setup:

Generator prompt: Classify ticket, return JSON only.
Validator:
1. Schema check with Pydantic
2. Logic check: priority high ஆனால் needs_escalation false என்றால் reject
3. Category whitelist check

Fail ஆனால் feedback: "category value invalid, must be one of..." -> LLM-க்கு திருப்பி அனுப்பு.

இப்போது 95% valid structured output கிடைக்கிறது, manual correction தேவை இல்லை.

## 7. Reasoning Challenge

உங்களுக்கு RAG based product recommendation agent உள்ளது. LLM user query-க்கு 3 product IDs generate பண்ண வேண்டும். Requirements:
- IDs must exist in product catalog DB
- Price must be within user's budget filter
- No duplicate IDs

Generator alone செய்யும் போது 30% times invalid IDs வருகிறது. என்ன architecture போடுவீர்கள்? Validator எப்படி இருக்கும்? Retry எத்தனை முறை வரை செய்வீர்கள்?

## 8. Key Takeaways

- LLM என்பது generator, deterministic correctness-க்கு validator தேவை
- Generator/validator loop format, logic, policy compliance-ஐ enforce செய்யும்
- Trade-off என்பது latency மற்றும் cost vs reliability
- Validator-ஐ cheap, fast, deterministic ஆக வைத்து LLM retry-ஐ control பண்ணுங்கள்
