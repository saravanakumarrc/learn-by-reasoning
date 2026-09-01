# AI service layer

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.3 — Enterprise patterns

## 1. Problem

உங்க company-ல LLM features வர ஆரம்பிச்சிருக்கு. 
Chatbot ஒன்னு, summarization ஒன்னு, classification ஒன்னு, RAG ஒன்னு.

எல்லாம் நேரடியா OpenAI API-க்கு, அல்லது ஒவ்வொரு team-ம் தனித்தனியா LLM call பண்ணுது.

என்ன ஆகுது?
* Prompt-கள் ஒவ்வொரு service-லும் copy-paste ஆகுது. One change = 10 repos.
* Cost எவ்வளவுன்னு தெரியல. Token usage, latency, error rate எல்லாம் scattered.
* Model பெயர் மாறணும், அல்லது temperature tweak பண்ணணும். எல்லா இடத்திலும் deploy பண்ண வேண்டி இருக்கு.
* PII data நேரடியா LLM-க்கு போகுது. Compliance team கேள்வி கேக்குது.
* One service slow ஆகும்போது அது மற்ற service-களை affect பண்ணுது.

இங்கே core problem: **AI logic business logic-ல கலந்து இருக்கு.** 
ஒரு LLM call ஒரு implementation detail ஆக இருக்க வேண்டியது, அது எல்லா இடத்திலும் leak ஆகி இருக்கு.

---

## 2. Mental Model

AI service layer என்பது LLM, embedding model, vector database, tools எல்லாத்தையும் **wrap பண்ணி ஒரு internal API** ஆக்குறது.

Business service -> AI service layer -> LLM / RAG / Agent infra

இது ஒரு abstraction boundary. உங்க app-க்கு தெரிய வேண்டியது: "எனக்கு summarization வேணும்". எந்த model, எந்த prompt template, எந்த retry policy, எந்த guardrail — அது AI service layer decide பண்ணும்.

Think of it like a database access layer. நீங்கள் SQL query எழுத மாட்டீங்க direct DB connection-ல. Connection pool, retry, monitoring எல்லாம் layer handle பண்ணும்.

---

## 3. How It Works

Layer-ல உள்ள core responsibilities:

* **Model routing & abstraction**: `summarize(text)` call வந்தால், layer decide பண்ணும் `gpt-4o-mini` vs `claude` vs local model. Cost, latency, quality அடிப்படையில்.
* **Prompt management**: Templates versioned ஆக இருக்கும். A/B test பண்ணலாம். Business code-ல hard-coded prompt இருக்காது.
* **RAG orchestration**: Retrieve from vector database, context build, call LLM, citations return — எல்லாம் layer-ல.
* **Guardrails & safety**: PII redaction, input validation, output filtering, toxicity check.
* **Observability**: Token usage, latency, cost per request, per team, per feature. Tracing to business request.
* **Retry, timeout, circuit breaker**: LLM flaky. Layer-ல standardized handling.
* **Tool calling**: Agents-க்கு tools expose பண்ணுறதும் இங்கே.

Implementation-ல இது பொதுவா ஒரு gRPC / REST service, அல்லது internal library with central config.

---

## 4. Architectural Reasoning

எப்போ தேவை?

* Multiple teams / products LLM use பண்ணும்போது.
* Cost control, compliance, audit trail வேணும்போது.
* Model switch, prompt iteration வேகமா வேணும்போது.
* Production reliability வேணும்போது.

Alternatives:
* **Direct calls**: வேகமா start பண்ணலாம். Small prototype-க்கு ok. Scale ஆகும்போது chaos.
* **Per-team wrapper library**: Reuse குறைவு. Config drift ஆகும்.
* **AI service layer**: Central control, but added latency & operational overhead.

Architect choose பண்ணுவது ஏன்? Because AI infra is a platform concern, not business logic concern.

---

## 5. Trade-offs

* **Latency**: Extra hop. 10-30ms network. Cache / async பண்ணி குறைக்கலாம். Trade-off for consistency.
* **Central bottleneck**: All AI traffic ஒரு layer வழியா போகும். Scale horizontally, rate limiting வேணும்.
* **Complexity**: New team, new service. Small use case-க்கு over-engineering ஆகலாம்.
* **Vendor lock-in vs abstraction**: Layer உங்களுக்கு model swap சுலபம் தரும். ஆனால் layer itself ஒரு dependency ஆகும்.
* **Failure mode**: Layer down ஆனால் எல்லா AI feature-ம் down. High availability, multi-region முக்கியம்.

---

## 6. Practical Example

Enterprise support system.

Customer support agent UI -> Support Service -> AI Service Layer -> LLM

User message வரும்போது:
1. AI Service Layer PII redact பண்ணும்.
2. Ticket context-க்கு vector database-ல retrieve பண்ணும்.
3. Prompt template `support_assist_v3` use பண்ணி LLM call.
4. Output-ல policy violation இருக்கா என check.
5. Response + citations + token cost log return.

இதே layer-ஐ sales team use பண்ணும்போது `sales_assist_v2` template use பண்ணும். Model routing வேற. Code change zero.

Cost dashboard-ல இப்போ தெரியும்: Support team per month $12k, avg latency 1.2s.

---

## 7. Reasoning Challenge

உங்களிடம் 3 products இருக்கு. எல்லாம் RAG பயன்படுத்துது. ஆனால் ஒவ்வொன்னுக்கும் தனித்தனி vector database இருக்கு. Compliance கேக்குது: ஒரே customer data தப்பா leak ஆகுதான்னு audit பண்ணணும்.

AI service layer வச்சா என்ன மாறும்? எந்த capability-ஐ முதலில் build பண்ணுவீங்க? Central logging, PII redaction, அல்லது model routing?

---

## 8. Key Takeaways

* AI service layer ஆனது LLM call-ஐ business logic-ல இருந்து separate பண்ணும் boundary.
* Prompt, model, guardrail, observability — எல்லாம் centralize ஆகும். Iteration வேகம் அதிகரிக்கும்.
* Cost, reliability, compliance control-க்கு இது must. Small prototype-க்கு overkill.
* Every abstraction adds latency and operational risk. அதை design-ல accept பண்ணி mitigate பண்ண வேண்டும்.

இதை புரிஞ்சா, AI feature add பண்ணுறது ஒரு API call மாதிரி ஆகும். Infra worry layer-ல இருக்கும்.
