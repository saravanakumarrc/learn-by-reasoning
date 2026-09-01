# Cost changes

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.6 — AI-specific monitoring

### 1. Problem

நீங்கள் ஒரு RAG service ஐ production-ல் ஓட விட்டிருக்கிறீர்கள். LLM call cost per request $0.02 இருந்தது. ஒரு வாரத்தில் bill $800 இருந்து $3,200 ஆகி விட்டது.

என்ன நடந்தது? 

Prompt length அதிகமாகி விட்டதா? Users திடீரென்று 10x queries அனுப்புகிறார்களா? ஒரு buggy agent loop ஓடி ஒரே user query-க்கு 50 LLM calls பண்ணுகிறதா? Vector DB search தவறாக கonfigure ஆகி, ஒவ்வொரு query-க்கும் 2000 tokens context fetch ஆகிறதா?

Traditional monitoring சொல்லும்: latency up, error rate up. Cost change-ஐ சொல்லாது. Cost change என்பது AI-specific monitoring-ன் முதல் red flag. இது performance இல்லை, இது business impact.

**What goes wrong if we don't have this?** Bill shock, மற்றும் silent degradation. நீங்கள் cost அதிகரிப்பை தெரிந்து கொள்ளும்போது, root cause already 3 நாள் முன்பு ஆரம்பித்திருக்கும்.

### 2. Mental Model

Cost change monitoring என்பது resource usage monitoring அல்ல. 

இது **per-unit economics** monitoring ஆகும்.

`Cost per successful user request` = `(LLM input tokens + output tokens + embedding calls + vector DB reads + tool calls) / successful requests`

இந்த metric ஒரு baseline-ல் இருந்து deviate ஆனால், அது ஒரு signal ஆகும். அது system behavior மாறியிருக்கிறது என்று அர்த்தம்.

Latency அதிகரித்தால் user கவனிக்கிறார். Cost அதிகரித்தால் CFO கவனிக்கிறார்.

### 3. How It Works

ஒவ்வொரு AI operation-க்கும் நீங்கள் இதை track செய்ய வேண்டும்:

1. **Token accounting**: Prompt tokens, completion tokens, cached tokens. Model per-token price வைத்து cost calculate பண்ணுங்கள்.
2. **Call pattern**: Calls per user request, calls per session, retries count.
3. **Context size**: RAG-ல் retrieved chunks count, average context tokens per request.
4. **Tool usage**: Agent tool calls எத்தனை, எந்த tool அதிகம் use ஆகிறது.
5. **Success outcome**: Did the user get a good answer? Did it require retry? Cost per successful completion.

இதை ஒரு observability pipeline-ல் கொண்டு போங்கள்:

`LLM call -> trace span with metadata: model, input_tokens, output_tokens, tools_used -> cost calculated at span level -> aggregate by user, by feature flag, by prompt version -> alert on deviation`

OpenTelemetry span attributes-ல் `llm.model`, `llm.input_tokens`, `llm.cost_usd` போன்றவற்றை வைத்தால், உங்கள் existing tracing system-ல் cost view ஆகும்.

### 4. Architectural Reasoning

Cost change எப்போது useful ஆகிறது?

* Prompt version rollout செய்யும்போது. புதிய prompt 15% longer context use செய்தால், உடனே தெரிய வேண்டும்.
* New agent workflow deploy செய்யும்போது. Loop detection இல்லாமல் agent infinite reasoning செய்யலாம்.
* Traffic spike வரும்போது. Organic growth vs bug-induced growth-ஐ differentiate செய்ய.
* Model swap செய்யும்போது. Cheaper model-க்கு மாறியும் cost per request குறையவில்லை என்றால், usage pattern மாறி இருக்கிறது.

Alternatives? Simple cloud billing dashboard பார்ப்பது. அது daily aggregate மட்டும் கொடுக்கும். Root cause சொல்லாது. உங்களுக்கு per-request attribution தேவை.

### 5. Trade-offs

**Granularity vs Overhead**: Token level logging cost அதிகம். Sampling செய்யலாம், ஆனால் sudden spike-ஐ miss பண்ணலாம்.

**Cost attribution vs Privacy**: User-level cost tracking வேண்டும், ஆனால் PII log செய்ய கூடாது. Hash user id.

**Real-time alert vs Noise**: Per-minute cost change alert அதிக false positive தரும். Baseline compare with moving average, 20% deviation over 30 min window.

**Centralized cost collector**: Single point of failure. Cost metadata-ஐ async pipeline-ல் அனுப்புங்கள், main request path-ஐ block செய்யாதீர்கள்.

Failure mode: Cost calculation logic bug. Model pricing update ஆனதும் code-ல் hard-coded price இருந்தால், நீங்கள் wrong alert-ஐ trust பண்ணுவீர்கள். Pricing config-ஐ externalize செய்யுங்கள்.

### 6. Practical Example

Enterprise support chatbot. 

Baseline: Cost per resolved ticket = $0.18

Day 3-ல்: Cost per resolved ticket = $0.41

AI-specific dashboard காட்டுகிறது:

* `average_context_tokens` 800 -> 2100
* `calls_per_request` 1.2 -> 3.4
* `tool_calls per request` 0.1 -> 1.8

Reasoning: New prompt version ல் system instruction "Always retrieve 10 documents before answering". Old version 3 documents. அதனால் vector DB cost + LLM input cost increase.

இதை தெரிந்து கொண்டதும், prompt version rollback செய்து, cost 2 மணி நேரத்தில் normalize ஆகிறது. Traditional latency/error monitoring இதை catch செய்யாது. Latency 400ms -> 650ms மட்டும் increase, user கவனிக்க மாட்டார்.

### 7. Reasoning Challenge

உங்கள் RAG agent-க்கு cost per user session இரண்டு மடங்காகியுள்ளது. Latency மாறவில்லை, error rate மாறவில்லை. Success rate குறைந்துள்ளது.

உங்கள் observability data காட்டுகிறது:

* `input_tokens per request` stable
* `output_tokens per request` stable
* `calls_per_request` 2.1 -> 2.1 stable
* `tool_calls per request` 0.5 -> 2.3

இதற்கு என்ன possible root causes இருக்கும்? எந்த metric-ஐ முதலில் deep dive செய்வீர்கள்? Cost change-ஐ reduce செய்ய architectural decision என்னவாக இருக்கும்?

### 8. Key Takeaways

* Cost per successful request தான் AI system-ன் primary economic health metric.
* Cost change என்பது performance regression-க்கு முன் வரும் signal.
* Token, call pattern, context size, tool usage ஆகியவற்றை trace span attributes-ல் capture செய்யுங்கள்.
* Alert on deviation from baseline, not absolute value.
* Every cost saving decision creates a trade-off with quality/latency — reason it explicitly.
