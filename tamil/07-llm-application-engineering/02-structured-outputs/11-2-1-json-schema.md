# JSON schema

> **Learning Path:** LLM Application Engineering
> **Section:** 11.2.1 — Structured outputs

## 1. Problem

LLM Application Engineering-ல நீங்கள் ஒரு LLM-ஐ business logic-உடன் connect பண்ணும்போது, output என்ன வேண்டும் என்று தெளிவாக சொல்லணும்.

உதாரணமாக, user கேட்கிறார்: "இந்த invoice-இல் என்ன items இருக்கு?" 
LLM respond பண்ணும்: "Item 1: Laptop, qty 2..." அல்லது JSON வடிவத்தில் வேண்டும் என்றால்: `[{"item":"Laptop","qty":2}]`

Problem என்ன? LLM free text தரும். Format மாறும். Key names மாறும். Extra field வரும். Missing field வரும். Type தவறாக வரும். 

இப்போது உங்கள் downstream service அந்த text-ஐ parse பண்ணி database-க்கு செலுத்த முயற்சிக்கும். Parser fail ஆகும். Retry பண்ணணும். Manual fix வரும். 

அப்படி என்ன கஷ்டம்? 
* **Non-deterministic output**: ஒரே prompt-க்கு வெவ்வேறு shape.
* **Contract break**: API consumer எதிர்பார்த்த schema வராது.
* **Validation cost**: எல்லா output-உம் பார்த்து சரி பார்க்க வேண்டும்.

What goes wrong if we don't have this? Production-ல உங்கள் agent தரும் output-ஐ நம்பி database write, payment, order creation நடக்கும். ஒரு முறை field name `price` vs `amount` ஆக மாறினால் போதும், data corrupt ஆகும்.

## 2. Mental Model

JSON Schema என்பது output-க்கான contract.

நீங்கள் LLM-க்கு சொல்கிறீர்கள்: "Output இப்படி இருக்க வேண்டும், இந்த fields கட்டாயம், இந்த type, இந்த range." Schema என்பது அந்த rulebook.

Mental model: LLM ஒரு smart but sloppy writer. JSON Schema என்பது editor-in-chief. Writer எழுதும் போதே editor format-ஐ enforce பண்ணுவது. Structured outputs என்பது LLM-ஐ schema-க்கு conform ஆக தள்ளுவது.

## 3. How It Works

LLM Application Engineering-ல இரண்டு வழிகள் உண்டு.

**1. Prompt-based constraint**: Prompt-ல JSON schema-ஐ describe பண்ணி, "Return only valid JSON matching this schema" என்று சொல்லுங்கள். LLM பெரும்பாலும் follow பண்ணும். ஆனால் guarantee இல்லை.

**2. Structured output with schema enforcement**: Modern providers ஆன OpenAI, Anthropic, Gemini இப்போது JSON Schema அல்லது Pydantic model-ஐ API parameter-ஆக எடுத்து, generation-ஐ constrain பண்ணுகிறார்கள். Token generation போது schema valid JSON மட்டுமே produce ஆகும் என்று decoder-ஐ guide பண்ணுவார்கள்.

Flow:
Prompt + System instruction → JSON Schema → LLM generation with constrained decoding → Valid JSON object → Schema validation → Downstream service.

RAG / Agent workflow-ல இது முக்கியம். Retrieval result-ஐ LLM summarize பண்ணி, அதை structured data-ஆக மாற்றி vector database-க்கு திருப்பி செலுத்தும்போது schema தேவை.

## 4. Architectural Reasoning

எப்போது JSON Schema useful?

* LLM output-ஐ நேரடியாக code, database, API call-க்கு feed பண்ணும்போது.
* Agent tool calling-ல arguments validate பண்ணும்போது.
* Data extraction pipeline-ல: invoice, receipt, form fields-ஐ structured JSON-ஆக extract.
* Multi-step reasoning-ல intermediate state-ஐ consistent shape-ல keep பண்ண.

Constraint it addresses: **Output reliability and contract stability**.

Alternatives:
* Regex post-processing. Fragile, maintenance hell.
* LLM output-ஐ மறுபடியும் LLM-க்கு கொடுத்து "fix this JSON" என்று ask. Latency + cost அதிகம்.
* Manual validation in code with try-catch. Fail rate அதிகம்.

ஏன் schema choose பண்ணுறோம்? Because it moves validation left. Generation time-லேயே shape enforce ஆகும். Downstream system-க்கு trust அதிகரிக்கும்.

## 5. Trade-offs

* **Rigidity vs flexibility**: Schema strict ஆக இருந்தால் LLM hallucinate பண்ண முடியாது, ஆனால் unexpected but valid information-ஐ reject பண்ணும். Overly strict schema creative extraction-ஐ கெடுக்கும்.
* **Schema complexity vs prompt cost**: Complex nested schema, enum, conditional logic கொடுத்தால் LLM-க்கு harder to follow, generation slow ஆகலாம்.
* **Provider lock-in**: Structured output feature implementation provider-க்கு provider வேறுபடும். Pure JSON Schema standard என்றாலும், extra features vary.
* **Failure mode**: Schema invalid ஆனால் LLM stuck ஆகி incomplete JSON தரும். அப்போது fallback strategy வேண்டும்: schema simplify, retry with relaxed constraints, or human review queue.

## 6. Practical Example

Enterprise support ticket triage agent.

User message: "My app crashes when I upload file, error code 503"

நீங்கள் LLM-ஐ structured output தர சொல்ல வேண்டும்:

```json
{
  "intent": "bug_report",
  "priority": "high" | "medium" | "low",
  "category": "upload" | "login" | "billing",
  "extracted_entities": {
    "error_code": "503",
    "component": "app"
  },
  "summary": "string <= 200 chars"
}
```

Schema-ஐ define பண்ணி API call-ல pass பண்ணுங்கள். LLM output எப்போதும் இந்த shape-ல வரும். உங்கள் router service இதை நேரடியாக take பண்ணி JIRA ticket create பண்ணும்.

இல்லாமல் free text வந்திருந்தால், entity extraction மீண்டும் ஒரு model run தேவைப்படும்.

## 7. Reasoning Challenge

உங்களிடம் RAG pipeline இருக்கிறது. Document chunk-ஐ LLM படித்து structured metadata தர வேண்டும்: `title`, `topic`, `entities[]`, `summary`.

Schema-ல `entities` என்பது array of strings. சில documents-ல entities 50+ இருக்கும். Schema strict ஆக இருக்கும்.

Production-ல latency முக்கியம், cost குறைவாக வேண்டும். இங்கே schema strict ஆக வைக்கலாமா? அல்லது entities-ஐ optional ஆக்கி, max items limit போடலாமா? ஏன்?

## 8. Key Takeaways

* JSON Schema என்பது LLM output-க்கான contract, documentation அல்ல.
* Structured outputs என்பது generation-ஐ constrain பண்ணுவது, post-hoc parsing-ஐ குறைப்பது.
* Schema design = architecture decision. Too strict = brittle, too loose = useless.
* Always validate output even with structured mode, and have fallback for schema mismatch.
* Schema clarity reduces downstream integration cost and increases system reliability.

இது புரிந்தால், LLM-ஐ safe-ஆக production system-உடன் கனெக்ட பண்ண முடியும்.
