# Model calls

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.8 — Observability

## 1. Problem

நீங்கள் production-ல் ஒரு LLM-powered service ஓட விட்டிருக்கீங்க. User query வருது, அது உங்கள் API வழியா போய், model call ஆகுது, response வருது.

இப்போ user சொல்றார்: "Response slow ஆ இருக்கு" அல்லது "Response quality மோசமா இருக்கு" அல்லது "Cost எகிறிடுச்சு".

உங்களுக்கு தெரியுமா?

* எந்த model call எப்போ எடுக்கப்பட்டது?
* எவ்வளவு latency வந்தது? Network-ஆ? Model inference-ஆ?
* Prompt எப்படி இருந்தது, output என்ன வந்தது?
* Token usage எவ்வளவு? Cost எவ்வளவு?
* Same prompt-க்கு வேற output வருதா? Non-deterministic ஆக இருக்கா?
* Error வந்தா, எந்த step-ல fail ஆச்சு? Retry ஆச்சா?

Traditional observability-ல் logs, metrics, traces இருக்கு. ஆனால் model call ஒன்று என்பது முழுக்க black box ஆக இருக்கும். Input, output, latency, cost, quality எல்லாம் தெரியாமல் debug பண்ணுவது கிட்டத்தட்ட blind flight.

இதுதான் model calls-க்கான observability தேவையை உருவாக்கியது.

## 2. Mental Model

Model call என்பது ஒரு external dependency call போலத்தான், ஆனால் அது deterministic இல்லை.

ஒரு database call-க்கு நீங்கள் SQL query பார்த்தால் போதும். Model call-க்கு prompt, system message, temperature, max tokens, tools, context window, embedding, RAG retrieval quality எல்லாம் input-ஆகும்.

Observability என்பது இதை 3 விஷயங்களாக பார்ப்பது:

* **Metrics**: Model calls எத்தனை? Latency எவ்வளவு? Error rate? Token usage? Cost per request?
* **Logs**: Prompt என்ன, response என்ன, model version என்ன, parameters என்ன?
* **Traces**: User request -> API -> RAG retrieval -> embedding call -> vector DB -> model call -> post-processing. இந்த flow-ல் எங்கே time போகுது?

ஒரு model call என்பது ஒரு distributed transaction-க்குள் ஒரு span.

## 3. How It Works

Practical-ல் நீங்கள் ஒவ்வொரு model call-ஐயும் ஒரு structured event-ஆக capture பண்ணுவீங்க.

அந்த event-ல் கட்டாயம் இருக்க வேண்டியவை:

* request_id / trace_id
* model name + version
* prompt tokens, completion tokens, total tokens
* latency: time_to_first_token, total latency
* cost estimate
* input: prompt, system prompt, tools used
* output: raw response, finish reason
* metadata: temperature, top_p, user_id, session_id

இதை நீங்கள் OpenTelemetry span-ஆக emit பண்ணலாம். அல்லது custom telemetry pipeline-க்கு போடலாம்.

Observability stack-ல் இந்த data போனதும் நீங்கள்:

* Dashboard-ல் latency p95, error rate பார்க்கலாம்
* Log search-ல் ஒரு specific user query-க்கு என்ன prompt போய், என்ன output வந்தது என்று பார்க்கலாம்
* Alert set பண்ணலாம்: latency > 5s, cost per request > $0.10, error rate > 1%

## 4. Architectural Reasoning

Model calls observability எப்போது critical ஆகும்?

* Production LLM service ஓடும் போது
* Cost control தேவைப்படும் போது
* Quality regression கண்டுபிடிக்க வேண்டும் போது
* Multiple models, routing, fallback logic இருக்கும் போது

ஏன் இது முக்கியம்? ஒரு model call fail ஆனால் அது உங்கள் business logic-ஐயும் fail ஆக்கும். Timeout ஆனால் user experience கெட்டுப்போகும். Prompt drift ஆனால் quality drop ஆகும்.

Alternatives:

* Just logs மட்டும்: searchable ஆனால் aggregated view இல்லை
* Just metrics: aggregated ஆனால் root cause தெரியாது
* Full recording of all prompts/responses: compliance risk, storage cost

அதனால் architect-கள் பொதுவாக sampling + redaction பயன்படுத்துவார்கள். PII உள்ள data-ஐ mask பண்ணி, high-value requests மட்டும் full capture.

## 5. Trade-offs

**Observability vs Privacy / Cost**

ஒவ்வொரு prompt/response-ஐயும் store பண்ணினால் observability நல்லா இருக்கும், ஆனால் storage cost அதிகரிக்கும், PII leak risk வரும். GDPR compliance-க்கு problem.

**Granularity vs Overhead**

ஒவ்வொரு token level-ல் log பண்ணினால் overhead அதிகம். அதனால் key fields மட்டும் capture பண்ணுவது practical.

**Real-time vs Batch**

Real-time alerting வேண்டுமா? அதற்கு streaming pipeline தேவை. அது complexity அதிகரிக்கும்.

**Failure modes**

Model provider rate limit hit ஆனால் உங்களுக்கு தெரிய வேண்டும். Model version change ஆனால் latency change ஆகலாம். Prompt injection வந்தால் அதை detect பண்ண வேண்டும்.

## 6. Practical Example

உங்களிடம் ஒரு customer support chatbot இருக்கு. RAG + LLM.

User query -> API Gateway -> Auth -> Intent classifier -> Vector DB retrieval -> Context assembly -> Model call -> Response.

இங்கே observability இல்லாமல் user சொல்றார் "answer wrong".

உங்களுக்கு trace_id இருந்தால் நீங்கள் பார்க்கலாம்:

* Retrieval step-ல் 3 docs மட்டும் தான் வந்தது, relevance score குறைவு
* Model call latency 4.2s, time_to_first_token 1.8s
* Prompt tokens 3200, context window near limit
* Cost $0.08 per request

இதிலிருந்து தெரியும்: retrieval quality தான் பிரச்சனை, model அல்ல. அல்லது context window overflow ஆகுது.

இல்லாமல் நீங்கள் blind-ஆக model-ஐ மாற்றி பார்ப்பீங்க.

## 7. Reasoning Challenge

உங்களிடம் 1000 requests/minute வரும். ஒவ்வொரு request-க்கும் full prompt/response store பண்ணினால் மாதம் 500 GB data வரும். Compliance team PII redact செய்ய சொல்றார். Cost team budget control செய்ய சொல்றார்.

நீங்கள் என்ன observability strategy தேர்வு செய்வீர்கள்? Sampling rate என்ன? எந்த fields-ஐ முழுசா store பண்ணுவீங்க, எதை summarize பண்ணுவீங்க? ஏன்?

## 8. Key Takeaways

* Model call என்பது external dependency. அதற்கு metrics, logs, traces மூன்றும் தேவை.
* Input prompt, output response, tokens, latency, cost, model version இவை core observability signals.
* Observability என்பது debug-க்கு மட்டும் அல்ல, cost control மற்றும் quality regression கண்டுபிடிக்கவும்.
* Privacy மற்றும் storage cost-க்காக sampling, redaction, retention policy முக்கியம்.
* ஒரு trace-ல் model call ஒரு span-ஆக இருந்தால் முழு request flow-ஐ புரிந்துகொள்ள முடியும்.
