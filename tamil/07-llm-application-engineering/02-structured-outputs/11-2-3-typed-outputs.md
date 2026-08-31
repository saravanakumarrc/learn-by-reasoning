# Typed outputs

> **Learning Path:** LLM Application Engineering
> **Section:** 11.2.3 — Structured outputs

### 1. Problem

நீங்கள் ஒரு LLM-ஐ உங்கள் application-ல் integrate பண்ணியிருக்கீங்க. Service கேட்கிறது: "இந்த user message-ஐ analyze பண்ணி, JSON திருப்பிக் கொடு: `{intent, entities, confidence}`".

பிரச்சனை என்ன? LLM நல்ல English-ல பதில் சொல்லும், ஆனா output format எப்போதும் மாறும்.

ஒரு முறை சரியான JSON, அடுத்த முறை JSON-க்குள் explanation, அடுத்த முறை field names தப்பா, அடுத்த முறை quotes missing. உங்கள் code `json.loads` பண்ணும்போது crash.

பெரிய scale-ல இது painful ஆகிறது. Parser எழுதி, retry பண்ணி, regex வைத்து fix பண்ணுவது brittle. Production-ல reliability போய்விடும்.

**What problem became painful?** LLM is a probabilistic text generator. Application needs deterministic, typed data.

### 2. Mental Model

Structured outputs = LLM-ஐ பேச்சிலிருந்து data generation-க்கு மாற்றுவது.

நீங்கள் model-க்கு schema கொடுக்கிறீர்கள். Model அந்த schema-வுக்கு conforming output மட்டுமே தர வேண்டும். இது மொழி உற்பத்தி அல்ல, typed data உற்பத்தி.

மனதில் வைக்கவும்: `prompt + schema -> constrained decoding -> valid JSON/object`.

### 3. How It Works

இரண்டு அடுக்கு உள்ளது.

**1. Prompt-level steering**
System prompt-ல JSON schema, example, rules கொடுக்கிறீர்கள். Model-ஐ "இது மாதிரி output கொடு" என train செய்கிறீர்கள். இது cheap, ஆனா guarantee இல்லை.

**2. Decoding-level enforcement**
Modern providers `response_format: json_schema` அல்லது `tools` function calling மூலம் output-ஐ constrain பண்ணுகிறார்கள். Token generation நேரத்தில் parser வைத்து invalid token-ஐ block செய்கிறார்கள். Result: model-க்கு சரியான JSON மட்டுமே generate பண்ண முடியும்.

Simple flow:
`user input -> LLM with schema -> constrained decoder -> validated JSON -> your code`

Structured output என்பது LLM output-ஐ typed contract-ஆக மாற்றுவது.

### 4. Architectural Reasoning

எப்போது தேவை?

* LLM output-ஐ அடுத்த service / database / UI-க்கு pass பண்ணும்போது
* Classification, extraction, routing போன்ற tasks
* RAG pipeline-ல structured facts extract பண்ணும்போது
* Agent workflow-ல tool calls, plan steps define பண்ணும்போது

எப்போது தேவையில்லை?

Free-form summarization, creative writing, chat reply மாதிரி human-readable text மட்டும் தேவைப்படும்போது.

Alternatives:
* Regex + post-processing: cheap, brittle, maintenance nightmare
* LLM -> text -> second LLM to fix JSON: latency + cost
* Structured outputs: upfront schema, reliable downstream

Architect choose பண்ணும் போது கேட்க வேண்டியது: Downstream system type-safe data expect செய்கிறதா? ஆம் எனில் structured output தேவை.

### 5. Trade-offs

**Reliability vs Flexibility**
Schema strict ஆக இருந்தால் valid data கிடைக்கும், ஆனால் model creative reasoning-ஐ கட்டுப்படுத்தும். Schema too loose ஆனால் benefit குறையும்.

**Cost & Latency**
Constrained decoding சில provider-ல சற்று expensive / slower. ஆனால் retry + parser logic save பண்ணும்.

**Schema complexity**
Nested objects, arrays, enums support பண்ணும். மிகவும் complex schema model-ஐ confuse பண்ணும். Keep schema minimal for the task.

**Failure modes**
Schema mismatch, hallucinated enum values, missing required fields. Always validate output with JSON Schema validator in code, don't trust blindly. Version your schema.

### 6. Practical Example

Enterprise support ticket classifier.

Requirement: User message -> `{intent: "billing|technical|refund", priority: "low|medium|high", entities: [{type, value}], confidence: 0-1}`

Without structured output:
You get free text, parser fails 5-10% of time.

With structured output:
System prompt + JSON schema enforce செய்யவும். Model output always parse-able.

Downstream routing service directly use `intent` to route to team, `priority` to SLA queue. No brittle regex.

If new intent வருகிறது, schema-வை update பண்ணி deploy செய்யவும். Old clients break ஆகாமல் backward compatibility maintain பண்ண schema version பண்ணவும்.

### 7. Reasoning Challenge

உங்களுக்கு ஒரு LLM agent உள்ளது. Agent ஒரு task plan தயாரிக்க வேண்டும். Plan format: `{steps: [{id, action, input, output}], estimated_time}`

உங்களிடம் 2 options உள்ளது:
A. Prompt-ல example கொடுத்து, output-ஐ regex-ல parse பண்ணுவது
B. JSON Schema enforced structured output use பண்ணுவது, ஆனால் schema change அடிக்கடி தேவைப்படும்

Production reliability முக்கியம், ஆனால் product team schema-வை விரைவாக iterate செய்ய விரும்புகிறார்கள்.

நீங்கள் என்ன தேர்வு செய்வீர்கள்? ஏன்? Schema evolve ஆகும் போது எப்படி handle பண்ணுவீர்கள்?

### 8. Key Takeaways

* Structured outputs LLM-ஐ unreliable text generator-லிருந்து reliable data producer-ஆக மாற்றுகிறது
* Prompt steering + decoding enforcement இரண்டும் சேர்ந்தால் தான் production-grade reliability வரும்
* Schema என்பது contract. It defines system boundary between LLM and code
* Always validate output in code, version schema, and monitor parse failure rate
