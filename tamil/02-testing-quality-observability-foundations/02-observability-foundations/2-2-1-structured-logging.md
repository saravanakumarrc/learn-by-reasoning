# Structured logging

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.2.1 — Observability foundations

## 1. Problem

Production-ல ஒரு order fail ஆகுது. 3 service-கள் இருக்கு: API Gateway, Order Service, Payment Service.

Unstructured log-ல நீங்கள் பார்ப்பது:

`2024-10-01 12:01:02 INFO order placed for user 123`
`2024-10-01 12:01:03 ERROR payment failed for order 456`

இப்போது கேள்வி: இந்த error எந்த user-க்கு? எந்த request-க்கு? எத்தனை முறை நடந்தது? எந்த service-ல இருந்து வந்தது? எவ்வளவு latency?

Grep, regex, eyeballing-ல தேடினால் நேரம் போகும். Log message format ஒவ்வொரு developer-க்கும் வேறுபடும். `user id` சில இடத்தில் `user_id`, சில இடத்தில் `uid` என்று இருக்கும்.

Incident-ல நிமிடத்துக்கு முக்கியம். அப்போது உங்களுக்கு தேவை என்ன? **Search, filter, correlate, aggregate பண்ண முடியும்** ஒரு log.

இந்த வலி தான் structured logging வந்த காரணம்.

## 2. Mental Model

Unstructured log = free-form text sentence.
Structured log = event with fixed fields.

ஒரு log என்பது ஒரு key-value map. `timestamp`, `level`, `message` போன்ற standard fields + உங்கள் business context fields.

Mental model: **Log ஒரு document, message ஒரு field மட்டுமே.**

JSON இல் பார்த்தால்:

```json
{
  "timestamp": "2024-10-01T12:01:03Z",
  "level": "error",
  "service": "payment-service",
  "request_id": "req_abc123",
  "user_id": "u_123",
  "order_id": "o_456",
  "message": "payment failed",
  "latency_ms": 342
}
```

இப்போது `request_id` மூலம் எல்லா service-களின் log-களையும் join செய்யலாம். `level=error` மற்றும் `service=payment-service` என்று filter செய்யலாம்.

## 3. How It Works

Application code log அனுப்பும்போது field-களை explicitly set செய்யுங்கள்.

Python-ல் json logger உதாரணம்:

```python
logger.info("order placed", extra={
  "order_id": "o_456",
  "user_id": "u_123",
  "request_id": "req_abc123"
})
```

Output என்பது parseable JSON. Log collector Loki, Elasticsearch, CloudWatch Logs Insights போன்றவை இதை index செய்து query செய்யும்.

Request flow-ல correlation செய்ய:

```mermaid
graph LR
    Client --> API[API Gateway]
    API --> Order[Order Service]
    Order --> Payment[Payment Service]
    API -. request_id ..> Order
    Order -. request_id ..> Payment
    Order --> Log[(Structured Logs)]
    Payment --> Log
```

ஒரே `request_id` எல்லா service-லும் propagate ஆகும். அதனால் distributed trace இல்லாமலேயே log correlation செய்ய முடியும்.

## 4. Architectural Reasoning

இது useful ஆகும் போது:

* Multiple service-கள் இருக்கும் போது, incident correlation தேவை.
* Log-களை programmatically analyze செய்ய வேண்டும்: error rate, latency p95, user impact.
* Alerting, dashboard, SLO monitoring க்கு log-களை source ஆக பயன்படுத்த வேண்டும்.

Constraint it addresses: **observability with low overhead.** Metrics கொடுக்கும் aggregate, traces கொடுக்கும் request path, logs கொடுக்கும் context.

Alternatives:
* Unstructured text logs + grep
* Centralized logging but unstructured
* Only metrics/tracing

ஏன் structured? Search cost குறையும். `user_id = 'u_123'` என்று exact filter செய்யலாம். Field names standard ஆனால் தான் team-முழுவதும் ஒரே query work ஆகும்.

## 5. Trade-offs

**Performance vs richness**: JSON serialization cost உண்டு. High throughput service-ல async logging, sampling பயன்படுத்த வேண்டும்.

**Schema evolution**: Field names மாறினால் dashboards break ஆகும். `order_id` vs `orderId` confusion வரும். Convention + schema registry போன்றது தேவை.

**Cost**: Structured logs அதிக volume ஆகும். Indexing செய்தால் storage cost அதிகம். Retention policy, sampling, field whitelist தேவை.

**Security**: Log-ல PII, token, password வந்துவிடக்கூடாது. Structured என்பதால் field level masking செய்ய எளிது, ஆனால் developer தவறாக field add செய்தால் leak ஆகும்.

Failure mode: Log flood. Exception loop-ல ஒரே error ஆயிரம் முறை log ஆனால் cost & noise அதிகம். Rate limiting, error grouping தேவை.

## 6. Practical Example

E-commerce order flow.

நீங்கள் எல்லா log-லும் இந்த fields-ஐ mandatory ஆக்குங்கள்:

`timestamp`, `level`, `service`, `request_id`, `user_id`, `trace_id`, `environment`

Business fields: `order_id`, `payment_method`, `latency_ms`, `status`

Incident: Payment failure rate 5% ஆக உ
