# Validation

> **Learning Path:** LLM Application Engineering
> **Section:** 11.2.4 — Structured outputs

## 1. Problem

LLM-ஐ பயன்படுத்தி ஒரு real application பண்ணும்போது நீங்கள் கண்டிப்பாக சந்திக்கும் பிரச்சனை:

Model output ஒரு free-form text. நீங்கள் அதை downstream service-க்கு கொடுக்க வேண்டும். அந்த service JSON expect பண்ணும். ஆனால் LLM சில நேரம் JSON கொடுக்கும், சில நேரம் தப்பான field name கொடுக்கும், சில நேரம் extra explanation கொடுக்கும், சில நேரம் hallucinate பண்ணும்.

இப்போது உங்கள் agent workflow உடைந்துவிடும். Parser error வரும். Database insert fail ஆகும். User-க்கு weird output போகும்.

> What goes wrong if we don't have validation? Model-இன் creativity உங்கள் pipeline-ஐ break செய்யும்.

Structured output என்பது இந்த பிரச்சனைக்கு தீர்வு.

## 2. Mental Model

LLM ஒரு creative writer. நீங்கள் அதை ஒரு strict data producer ஆக மாற்ற வேண்டும்.

Structured output என்பது: Model output-ஐ ஒரு predefined schema-க்கு கட்டுப்படுத்துவது. Schema = shape, types, required fields, enums.

உங்களுக்கு தேவை: **predictable shape** மற்றும் **machine-readable** output.

Analogy: Model-க்கு ஒரு form கொடுப்பது. Free text essay எழுத சொல்லாமல், name, age, city என்ற fields fill பண்ண சொல்வது.

## 3. How It Works

இரண்டு layer உள்ளது.

**Generation layer:** Prompting + model constraints
* Output format-ஐ specify பண்ணுங்கள்: "Return only valid JSON matching this schema"
* JSON Schema / Pydantic model-ஐ system prompt-ல் கொடுங்கள்
* Modern models-ல் guided decoding உள்ளது: JSON schema-வை model generation-க்கு கொடுத்தால் token level-லேயே invalid structure வராமல் தடுக்கும்

**Validation layer:** Post-generation check
* Generated text-ஐ parse பண்ணுங்கள்
* Schema validation செய்யுங்கள்: field exists? type correct? enum match?
* Fail ஆனால் retry / fallback / repair

Good architecture-ல் இரண்டும் சேர்ந்து இருக்கும். Generation-ஐ குறைக்க, validation-ஐ catch செய்ய.

## 4. Architectural Reasoning

எப்போது இது தேவை?

* LLM output நேரடியாக database, API call, tool call-க்கு போகும்போது
* Multi-step agent workflow-ல் step output next step-ன் input ஆகும்போது
* RAG system-ல் extracted entities, citations, classification labels தேவைப்படும்போது

Constraint அது address பண்ணுவது: **reliability and contract**.

Alternatives:
* **Free text + regex parsing**: cheap but brittle. Schema மாறினால் உடையும்
* **LLM self-correct**: "Check if valid JSON" என்று மீண்டும் கேட்பது. Latency அதிகம், cost அதிகம்
* **Structured output with schema enforcement**: upfront cost குறைவு, reliability அதிகம்

Architect choose பண்ணும் காரணம்: Downstream system-க்கு contract தேவை. Human reading-க்கு மட்டும் என்றால் structured தேவையில்லை. Machine consumption-க்கு தேவை.

## 5. Trade-offs

**Reliability vs Flexibility**
Schema strict ஆக இருந்தால் model refuse பண்ணலாம் அல்லது hallucinate குறையும். ஆனால் unexpected but valid info-வை capture பண்ண முடியாது.

**Latency vs Safety**
Guided decoding + validation சேர்த்தால் latency +10-30% increase ஆகலாம். ஆனால் retry குறையும்.

**Prompt complexity vs Code complexity**
Schema-வை prompt-ல் விவரமாக எழுதலாம். அல்லது Pydantic model + tool calling use பண்ணலாம். Code maintainability better ஆகும்.

**Failure modes**
* Model schema-வை புரிந்துகொள்ளாமல் invalid output கொடுக்கும்
* Valid JSON ஆனால் semantically wrong data
* Schema drift: Model fine-tuned old schema-க்கு

Validation-ஐ pass ஆனாலும் business rule validation தனியாக தேவை.

## 6. Practical Example

Enterprise support ticket classification system.

Requirement: User message-ஐ படித்து structured output தர வேண்டும்:
```json
{
  "intent": "billing | technical | refund",
  "priority": "low | medium | high",
  "entities": [{"type":"order_id","value":"..."}],
  "summary": "short sentence"
}
```

Architecture:
1. User message → LLM with JSON schema
2. Output parse → Pydantic model validation
3. Fail ஆனால்: auto-repair prompt with error message → one retry
4. Success ஆனால்: downstream router service-க்கு pass

இப்படி செய்தால் routing logic deterministic ஆகும். Dashboard metrics reliable ஆகும். மற்றும் model output-ஐ log பண்ணி audit செய்ய முடியும்.

## 7. Reasoning Challenge

உங்களிடம் LLM agent உள்ளது. அது product catalog-ல் இருந்து items-ஐ extract பண்ணி `items: [{sku, quantity, price}]` என்ற schema-ல் தர வேண்டும்.

Production-ல் சில நேரம் model price field-ஐ string "19.99 USD" என்று தருகிறது, சில நேரம் number 19.99 என்று தருகிறது. Quantity சில நேரம் missing.

இங்கே உங்கள் validation strategy என்னவாக இருக்கும்? Generation-ஐ எப்படி கட்டுப்படுத்துவீர்கள், validation-ஐ எப்படி செய்வீர்கள், fail ஆனால் என்ன செய்வீர்கள்?

## 8. Key Takeaways

* Structured output என்பது creativity-க்கு கட்டுப்பாடு, not limitation
* Generation time-ல் schema guide பண்ணுங்கள், generation அப்புறம் validate பண்ணுங்கள்
* Model-ஐ trust பண்ணாதீர்கள். Always validate before machine consumption
* Schema என்பது architectural contract. அதை change பண்ணும்போது version பண்ணுங்கள்
