# Traces

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.3 — Observability

## 1. Problem

உங்கள் system-ல 10 services இருக்கு. User ஒரு request அனுப்புகிறார். API Gateway → Auth Service → Order Service → Payment Service → Inventory Service → Notification Service.

Request slow ஆகிறது. யார் தாமதப்படுத்துகிறார்கள்? எந்த service-ல timeout ஆகிறது? எந்த database call slow?

Logs மட்டும் இருந்தால் ஒவ்வொரு service-ன் log-ஐ தனித்தனியாக தேட வேண்டும். Request ID வைத்து join பண்ணினாலும் timeline புரியாது. Correlation இல்லை.

ஒரு request எப்படி பயணிக்கிறது, எங்கே நேரம் செலவாகிறது, எங்கே fail ஆகிறது என்பதை பார்க்க முடியாமல் போகிறது.

**Pain:** Distributed system-ல request-ன் end-to-end journey invisible ஆகிறது. Debugging ஆகிறது guesswork.

## 2. Mental Model

Trace என்பது ஒரு request-ன் life story.

ஒரு request ஒரு trace ஆகிறது. அந்த trace-ன் உள்ளே ஒவ்வொரு service call ஒரு span.

Trace = request journey. Span = one unit of work.

எல்லா span-களும் parent-child relationship-ல இணைக்கப்படுகின்றன. இதனால் ஒரு tree கிடைக்கிறது.

Analogy: Flight itinerary. Trace என்பது ஒரு passenger-ன் முழு trip. Span என்பது ஒவ்வொரு flight leg, layover, immigration.

## 3. How It Works

ஒரு request வரும்போது root span create ஆகிறது. அதற்கு Trace ID generate ஆகிறது.

அந்த Trace ID + Span ID ஐ context-ல propagate பண்ண வேண்டும். HTTP header-ல `traceparent`, gRPC metadata-ல, message queue-ல.

Service A service B-ஐ call பண்ணும்போது, incoming context-ல இருந்து Trace ID எடுத்து, புதிய child span create பண்ணுகிறது.

ஒவ்வொரு span-ம் start time, end time, duration, service name, operation name, tags, logs கொண்டிருக்கும்.

இவை collector-க்கு அனுப்பப்படுகின்றன. Collector அவற்றை storage-ல சேர்த்து, UI-ல trace tree-யாக காட்டுகிறது.

OpenTelemetry standard இப்போது common ஆகிவிட்டது. Instrumentation SDK-கள் auto-instrumentation கொடுக்கின்றன.

## 4. Architectural Reasoning

Trace எப்போது useful?

* Request latency புரிய வேண்டும். எந்த hop slow என்பதை pinpoint பண்ண.
* Error root cause கண்டுபிடிக்க. எந்த service fail ஆனது, அதற்கு முன் என்ன நடந்தது.
* Dependency map பார்க்க. உங்கள் service யார் யாரை அழைக்கிறது.
* SLO / SLA measure பண்ண. P95 latency எங்கே break ஆகிறது.

Alternatives?

* Logs only: correlation கஷ்டம், timeline இல்லை.
* Metrics only: average latency தெரியும், ஆனால் ஒரு specific request எங்கே தாமதம் ஆனது தெரியாது.

Trace choose பண்ணும் போது நீங்கள் கேட்க வேண்டியது: Request flow visibility தேவையா? Distributed context தேவையா?

## 5. Trade-offs

**Sampling.** 100% tracing செய்தால் cost அதிகம். High traffic system-ல 10k RPS என்றால் spans பில்லியன்-கள். Sampling பண்ணி 1% அல்லது adaptive sampling use பண்ணுவார்கள். Trade-off: Rare errors miss ஆகலாம்.

**Cardinality & Storage.** Span tags-ல high cardinality data வைத்தால் storage explode ஆகும். User ID, request payload எல்லாம் tag பண்ணக்கூடாது.

**Propagation overhead.** Header propagate பண்ணுவது, span create பண்ணுவது சிறிய overhead. Hot path-ல excessive instrumentation performance impact கொடுக்கும்.

**Observability blind spots.** Async work, message queue, background jobs-ல context propagate பண்ணாமல் trace break ஆகும். Trace அப்படியே பாதியில் நிற்கும்.

**Security & PII.** Trace-ல sensitive data leak ஆகலாம். Tag sanitization தேவை.

## 6. Practical Example

Enterprise order flow.

User checkout செய்கிறார். Trace ID = `4bf92f3577b34da6a3e...`

UI → API Gateway span 120ms
API Gateway → Auth Service span 45ms
API Gateway → Order Service span 210ms
Order Service → Payment Service span 180ms [slow]
Order Service → Inventory Service span 30ms
Payment Service → DB span 150ms [slow]

UI-ல total latency 380ms. Trace tree-ல தெரிகிறது Payment Service தான் bottleneck. அதன் DB span slow. அதை drill down பண்ணினால் lock contention தெரிகிறது.

இல்லாமல் இருந்தால் "system slow" என்று மட்டும் தெரிந்திருக்கும்.

AI system-ல: User query → Router → Retriever → LLM call → Reranker → Response. Trace-ல எந்த stage-ல latency அதிகம், LLM call fail ஆனதா, retrieval empty ஆனதா என்பதை பார்க்க முடியும்.

## 7. Reasoning Challenge

உங்களிடம் RAG pipeline இருக்கு. User query வந்தால்: Embedder → Vector DB → LLM → Post-process.

Vector DB latency சில நேரம் spike ஆகிறது. Metrics-ல P95 80ms-ல இருந்து 400ms ஆகிறது.

Traces enable பண்ணுவதால் என்ன தெரிந்து கொள்ள முடியும்? Sampling strategy என்ன வைப்பீர்கள்? Trace-ல எந்த tag வைக்க மாட்டீர்கள்?

## 8. Key Takeaways

* Trace என்பது request-ன் end-to-end story. Span என்பது ஒரு unit of work. Parent-child link தான் distributed context.
* Traces பிரச்சனைக்கு தேவைப்படுவது correlation + timeline + dependency map. Logs and metrics இதை முழுவதுமாக கொடுக்காது.
* 100% tracing cost செலவு. Sampling, retention, tag hygiene முக்கியம்.
* Trace data உடன் logs மற்றும் metrics இணைத்தால் தான் full observability கிடைக்கும்.
