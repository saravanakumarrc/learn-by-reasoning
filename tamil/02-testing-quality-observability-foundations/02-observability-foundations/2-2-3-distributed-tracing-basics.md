# Distributed tracing basics

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.2.3 — Observability foundations

# Distributed tracing basics

## 1. Problem

ஒரு user checkout பண்ணும்போது request 2 வினாடி ஆகுது. User complain பண்ணார். நீங்கள் logs பார்க்கிறீர்கள்.

API Gateway log-ல 120ms, Order Service log-ல 800ms, Payment Service log-ல timeout, Inventory Service log-ல success. ஆனால் எந்த request எந்த service-களை எப்போது hit பண்ணிச்சு, யார் யாரை wait பண்ணிச்சு என்று தெரியவில்லை.

Distributed system-ல ஒரு request 5-10 services-ஐ கடந்து போகும். ஒவ்வொரு service-க்கும் தனி log, தனி timestamp, தனி correlation இல்லை. Latency எங்கே உருவாகிறது, error எங்கே start ஆகிறது என்று கண்டுபிடிக்க 30 நிமிடம் தேட வேண்டும்.

இந்த pain தான் distributed tracing-ஐ கொண்டு வந்தது.

## 2. Mental Model

Trace = ஒரு user request-ன் முழு journey.

Span = journey-ல ஒரு service-ல நடக்கும் ஒரு unit of work.

Trace ID ஒன்று, அதுக்குள்ள parent-child spans.

உதாரணமாக ஒரு checkout request-க்கு ஒரு Trace ID கிடைக்கும். API Gateway ஒரு span, அது Order Service-ஐ call பண்ணும்போது child span உருவாகும். அதே மாதிரி Payment மற்றும் Inventory-க்கும் spans.

இப்போது ஒரே ID-ஐ வைத்து எல்லா service logs-ஐயும் join பண்ணி, request எப்படி பயணித்தது என்று timeline-ஆக பார்க்க முடியும்.

## 3. How It Works

Request start ஆகும் இடத்தில் Trace ID generate ஆகும். அது request header-ல propagate ஆகும்.

`traceparent` அல்லது `X-Request-ID` போன்ற header-ல Trace ID, Span ID, Parent Span ID போகும். ஒவ்வொரு service-ம் வந்த header-ஐ எடுத்து தன் span-ஐ start பண்ணும், தன் Span ID-ஐ child-களுக்கு கொடுக்கும்.

Span-ல start time, end time, service name, operation name, tags, logs இருக்கும். இது exporter மூலம் collector-க்கு அனுப்பப்படும். Jaeger, Zipkin, Tempo போன்ற tracing backend-கள் அதை store பண்ணி UI-ல visualize பண்ணும்.

Sampling முக்கியம். 100% traces capture பண்ணினால் overhead அதிகம். High traffic system-ல head sampling அல்லது tail-based sampling பயன்படுத்துவார்கள்.

```mermaid
graph TD
Client -->|Trace ID| API Gateway
API Gateway -->|same Trace ID| Order Service
Order Service -->|same Trace ID| Payment Service
Order Service -->|same Trace ID| Inventory Service
```

ஒரே Trace ID, வெவ்வேறு Spans.

## 4. Architectural Reasoning

இது useful ஆகும் போது:

* Request multiple services-ஐ கடக்கும் போது latency debug செய்ய.
* Error root cause கண்டுபிடிக்க. எந்த downstream call fail ஆனது என்பதை trace-ஆல் உடனே பார்க்கலாம்.
* Performance bottleneck identify பண்ண. எந்த span அதிக நேரம் எடுக்கிறது என்று தெரியும்.

Alternatives என்ன?

* Logs correlation மட்டும்: request ID வைத்து log aggregation பண்ணலாம். ஆனால் timing, dependency graph கிடைக்காது.
* Metrics மட்டும்: p95 latency தெரியும், ஆனால் ஏன் அப்படி என்று தெரியாது.

Architect தேர்வு: Observability 3 pillars = logs, metrics, traces. Logs என்ன நடந்தது, Metrics எவ்வளவு நடந்தது, Traces எப்படி நடந்தது.

## 5. Trade-offs

* **Overhead & Cost**: ஒவ்வொரு request-க்கும் span create பண்ணுவது CPU மற்றும் network overhead கொடுக்கும். High cardinality tags, high storage cost.
* **Sampling risk**: Sample செய்தால் rare errors miss ஆகலாம். Sample rate-ஐ traffic-க்கு ஏற்ப tune பண்ண வேண்டும்.
* **Privacy & Security**: Trace-ல user data, payload leak ஆகலாம். Tags-ஐ sanitize பண்ண வேண்டும்.
* **Observability gap**: Tracing code instrumentation தேவை. Library support இல்லாத legacy service-ல blind spot வரும்.

Failure mode: Trace context drop ஆனால் chain break ஆகும். Async message queue-ல correlation maintain பண்ணுவது கடினம்.

## 6. Practical Example

Enterprise e-commerce checkout:

API Gateway → Order Service → Payment Service, Inventory Service, Notification Service

User checkout slow என்று alert வந்தது. Tracing UI-ல trace திறந்தால்:
