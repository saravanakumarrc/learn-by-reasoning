# Distributed tracing

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.5 — Observability

## 1. Problem

உங்ககிட்ட 5-6 microservices இருக்கு. User login பண்ணினா, API Gateway -> Auth Service -> User Service -> Profile Service -> Notification Service னு call போகுது.

User login slow ஆகுது. 3 seconds ஆகுது. Problem எங்க இருக்கு?

Logs பார்த்தா ஒவ்வொரு service-லயும் தனித்தனி log இருக்கு. Request ID இல்லாம timestamp-ஆல மட்டும் match பண்ண முயற்சி பண்ணுறீங்க. Auth service-ல 50ms, User service-ல 2.8 seconds ஆகுது. அந்த 2.8 seconds எதுக்கு? DB query-வா? External call-வா? Lock-வா?

இதுதான் pain. Distributed system-ல ஒரு request பல service-கள் வழியா போகும். அதை end-to-end follow பண்ண முடியாம போகுது. Average latency பார்த்தாலும் போதாது. எந்த service slow ஆகுது, எந்த call தொங்குதுன்னு தெரியாது.

## 2. Mental Model

Distributed tracing என்பது ஒரு request-ன் lifecycle-ஐ ஒரே thread of identity-ஆல track பண்ணுறது.

ஒவ்வொரு request-க்கும் ஒரு Trace ID கொடு. அந்த Trace ID ஒவ்வொரு service-க்கும் pass ஆகும். ஒவ்வொரு service-க்குள்ளும் அந்த request செய்யும் காரியங்கள் Span-கள். ஒவ்வொரு span-க்கும் start time, end time, parent-child relationship இருக்கும்.

முடிவுல உங்களுக்கு ஒரு tree கிடைக்கும். Root span = incoming request. Children spans = downstream calls, DB query, external API call.

இது போல ஒரு request எப்படி பயணித்தது, எங்க நேரம் செலவானது, எங்க error ஆனது என்று பார்க்க முடியும்.

## 3. How It Works

Practically, 3 பகுதிகள் இருக்கும்.

**Instrumentation**: Service code-ல tracer client இருக்கும். OpenTelemetry, Jaeger client மாதிரி. ஒரு request வந்ததும் span create பண்ணி start பண்ணும்.

**Context propagation**: Request header-ல trace context போகும். `traceparent`, `trace_id`, `span_id`. Service A Service B-க்கு call பண்ணும்போது அதே trace ID-ஐ header-ல forward பண்ணும். Service B அதை parent span ஆக எடுத்துக்கும்.

**Collector & Storage**: Spans backend-க்கு அனுப்பப்படும். Collector அதை aggregate பண்ணி storage-ல போடும். Jaeger, Zipkin, Tempo, CloudWatch X-Ray, AWS X-Ray.

UI-ல trace ID search பண்ணினால், full waterfall timeline கிடைக்கும்.

## 4. Architectural Reasoning

இது useful ஆகும் எப்போ?

* Request path 3+ services cross பண்ணும்போது
* Latency p99 முக்கியமானதாக இருக்கும்போது
* Failure root cause தெரியாம debug பண்ணும்போது
* SLO/SLA track பண்ண வேண்டும் என்றால்

Alternatives என்ன?

* **Centralized logging with correlation ID**: Log-களை correlate பண்ணலாம். ஆனால் log search மெதுவு, timing தெரியாது, request flow visualization இல்லை.
* **Metrics only**: Latency, error rate பார்க்கலாம். ஆனால் *which* request, *which* path என்று தெரியாது.
* **APM tools**: New Relic, Datadog tracing கொடுக்கும். ஆனால் அதுவும் உள்ளே tracing-ஐயே use பண்ணும்.

Architect choose பண்ணுவார் எப்போ? System-ல service count அதிகமாகி, request flow complex ஆகும்போது. Monolith-ல tracing தேவையில்லை. Microservices + async message queue இருந்தால் கண்டிப்பாக தேவை.

## 5. Trade-offs

**Performance overhead**: ஒவ்வொரு span create, propagate, export என்பது CPU + network cost. High throughput service-ல sampling தேவைப்படும். 100% trace பண்ண முடியாது. 1% or 10% sample பண்ணுவது common.

**Data volume and cost**: ஒரு request 10 spans create பண்ணினால், 10k RPS-ல 100k spans/sec. Storage, retention cost அதிகம். Sampling, span filtering தேவை.

**Incomplete picture**: Async processing, message queue-ல correlation செய்ய கடினம். Trace context message-ல propagate ஆகாவிட்டால் gap வரும்.

**Observability vs Privacy**: Trace-ல PII data leak ஆகலாம். Header, URL, arguments log ஆகும். Redaction policy தேவை.

**Operational complexity**: Instrumentation maintain பண்ண வேண்டும். Library version upgrade, vendor lock-in.

Failure mode: Tracer client itself crash ஆகி service impact ஆகக்கூடாது. Tracer should be best-effort, fail-safe.

## 6. Practical Example

ஒரு e-commerce checkout flow: API Gateway -> Cart -> Inventory -> Payment -> Order.

User checkout 4.2 seconds எடுக்குது. Distributed tracing-ல trace ID-ஆல பார்த்தால்:

Root span 4.2s
- Cart service 80ms
- Inventory service 120ms
- Payment service 3.8s
   - Payment service -> Payment Gateway 3.7s
   - DB update 50ms

உடனே தெரியும் Payment Gateway தான் bottleneck. Inventory இல்ல. Cart இல்ல. அதை isolate பண்ணி fix பண்ணலாம்.

LLMOps / AI Observability context-ல: RAG pipeline-ல retrieval -> embedding call -> vector DB query -> LLM call -> post-processing. Distributed tracing-ல எந்த step latency கொடுக்குது, retrieval slow ஆகுதா, LLM call timeout ஆகுதா என்று தெரியும்.

## 7. Reasoning Challenge

உங்ககிட்ட 20 services இருக்கு. Peak traffic-ல 50k RPS. ஒவ்வொரு request-க்கும் full trace சேகரிக்க முடியாது. Sampling strategy என்ன வைப்பீங்க? Error requests-ஐ எப்படி 100% capture பண்ணுவீங்க? மேலும், async message queue-ல consumer process செய்யும் span-ஐ producer trace-உடன் எப்படி link பண்ணுவீங்க?

## 8. Key Takeaways

* Distributed tracing solves **request-level causality** in distributed systems, not just metrics or logs.
* Trace ID propagation is the core mechanism; instrumentation + context propagation + collector is the architecture.
* Use sampling for cost control, but always capture errors and slow traces.
* Tracing helps you decide *where* to optimize, not just *that* you need to optimize.
* Every architectural visibility solution adds overhead; design for fail-safe and cost.
