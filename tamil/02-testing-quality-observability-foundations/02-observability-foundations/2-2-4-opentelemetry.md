# OpenTelemetry

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.2.4 — Observability foundations

# OpenTelemetry — Observability-க்கு common language

## 1. Problem

ஒரு distributed system-ல் 30 microservices இருக்கு. User-ஒருத்தர் checkout பண்ணும்போது request 5-6 services-ஐ தொடும். Page load slow ஆகுது.

என்ன பண்ணுவீங்க?
Logs-ஐ எடுத்துப் பார்த்தால் ஒவ்வொரு service-லும் தனித்தனி log file. Request ID-வை வைத்து join பண்ண வேண்டும். Metrics இருக்கு, ஆனால் அது ஒரு service-ன் CPU, latency மட்டும் சொல்லும். யார் காரணம் என்று தெரியாது.

இன்னொரு பிரச்சினை: Team A Java-ல் Datadog SDK பயன்படுத்துகிறது. Team B Python-ல் New Relic SDK. Team C தனியாக Prometheus metrics எழுதுகிறது.

இப்போது vendor மாற வேண்டும் என்றால்? அல்லது self-host பண்ண வேண்டும் என்றால்? Instrumentation-ஐ முழுவதும் எழுத வேண்டும்.

**What goes wrong if we don't have this?** Observability data fragmented ஆகும், correlate பண்ண முடியாது, vendor lock-in வரும், each team தனியாக format வைத்துக்கொள்ளும்.

## 2. Mental Model

OpenTelemetry என்பது telemetry data-க்கான **standard + SDK + protocol**.

Think of it like this:
Instrumentation code என்பது service-க்குள் sensor. அது traces, metrics, logs என்ற மூன்று signal-ஐ generate பண்ணும்.

OpenTelemetry அந்த sensor-க்கு common wiring கொடுக்கிறது. எந்த language-ஆக இருந்தாலும், எந்த backend-க்கு அனுப்பினாலும் அதே format.

அதனால் நீங்கள் backend-ஐ மாற்றினாலும் instrumentation மாறாது. Standard-ஆக OTLP protocol-ல் data வெளியே போகும்.

## 3. How It Works

Basic flow மிகவும் simple:

`Application code -> OpenTelemetry SDK -> Span/Metric/Log -> Exporter -> Collector -> Backend`

**Trace** என்பது ஒரு user request-ன் end-to-end journey. Trace-ல் பல spans இருக்கும். ஒவ்வொரு service call ஒரு span.

**Metric** என்பது time series data. Request rate, latency p95, queue length போன்றவை.

**Log** என்பது structured event. OpenTelemetry-ல் logs-ஐ traces-டன் correlate பண்ணலாம்.

SDK instrumentation automatic ஆகவும், manual ஆகவும் செய்யலாம். Collector என்பது protocol translation, batching, sampling, filtering செய்யும் edge proxy. Backend என்பது Jaeger/Tempo, Prometheus, Loki போன்றவை.

```
User -> API Gateway -> Service A -> Service B -> Service C
               |          |          |          |
               +---span---+---span---+---span---+
                         trace_id same for all
```

## 4. Architectural Reasoning

OpenTelemetry useful ஆகும் போது:

* System distributed ஆகும்போது, request-ஐ end-to-end பார்க்க வேண்டும்.
* Multiple teams, multiple languages இருக்கும்போது.
* Vendor lock-in தவிர்க்க வேண்டும். இன்று Datadog, நாளை self-hosted. Instrumentation மாறக்கூடாது.
* Cost control வேண்டும். Sampling, filtering collector-ல் central ஆக செய்யலாம்.

Alternatives:
Proprietary SDK. வேகமாக start ஆகும், ஆனால் lock-in.
Homegrown JSON logging + grep. Small system-க்கு ஓகே, scale ஆகும்போது fail ஆகும்.

Architect ஆக நீங்கள் choose பண்ணுவது என்ன?
Observability-ஐ product decision ஆக பார்க்காமல், **platform capability** ஆக பார்க்க வேண்டும். Instrumentation once, backend many times.

## 5. Trade-offs

* **Instrumentation overhead.** Auto-instrumentation easy, ஆனால் span எண்ணிக்கை அதிகரிக்கும். High cardinality metrics cost அதிகரிக்கும். Sampling strategy தேவை.
* **Complexity shift.** Vendor SDK-ல் அவர்கள் handle பண்ணுவார்கள். OpenTelemetry-ல் நீங்கள் collector, storage, retention நீங்களே manage பண்ண வேண்டும்.
* **Consistency vs flexibility.** Standard format நல்லது, ஆனால் vendor-specific features கிடைக்காது.
* **Failure mode.** Collector down ஆனால் telemetry lost ஆகும். Buffer, retry, back-pressure design தேவை. Otherwise service performance-ஐயே பாதிக்கும்.

Every architectural solution creates another trade-off. OpenTelemetry lock-in குறைக்கும், ஆனால் operational ownership அதிகரிக்கும்.

## 6. Practical Example

E-commerce checkout flow.

`Checkout Service` -> `Payment Service` -> `Fraud Service` -> `Inventory Service`.

OpenTelemetry SDK அனைத்து service-லும் install செய்யப்பட்டது. API Gateway-ல் trace start ஆகிறது, trace_id propagate ஆகிறது.

User complaint: checkout slow. 

Trace backend-ல் பார்த்தால் 95% latency Payment Service-ல். அதன் span-ல் database call 800ms. Metric-ல் DB connection pool exhausted என்று தெரியும். Logs-ல் அதே trace_id-உடன் error pattern தெரியும்.

இங்கே traces, metrics, logs ஒன்றாக இணைந்து root cause கிடைக்கிறது. Backend Jaeger ஆக இருந்தாலும், Prometheus ஆக இருந்தாலும் SDK மாறாது.

## 7. Reasoning Challenge

உங்கள் system
