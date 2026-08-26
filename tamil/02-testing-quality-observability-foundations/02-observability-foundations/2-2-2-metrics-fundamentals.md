# Metrics fundamentals

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.2.2 — Observability foundations

## 1. Problem

உங்கள் service production-ல இருக்கு. பகல் 2 மணிக்கு customers "checkout slow" என்று complain பண்ண ஆரம்பிக்கிறார்கள். 

Logs-ஐ பார்த்தால் error இல்லை. Traces இருந்தால் ஒரு request எங்கே தாமதமாகிறது என்று தெரியும். ஆனால் trace எடுக்கும் முன்பே உங்களுக்கு தெரிய வேண்டும்: இது திடீர் spike-ஆ? எப்போதும் இருக்கிறதா? எந்த service-ல இருந்து வருகிறது?

Logs and traces react to an incident. Metrics உங்களுக்கு pattern-ஐ முன்கூட்டியே காட்டும்.

> Metrics இல்லாமல் நீங்கள் குருட்டாய் debug பண்ணுவீர்கள். System healthy ஆ? எப்போது unhealthy ஆகிறது? என்று உங்களுக்கு number-ல தெரியாது.

## 2. Mental Model

Metrics என்பது **நேரத்தோடு மாறும் எண்கள்**. 

ஒரு counter, gauge, histogram போன்ற வகைகள் உண்டு. ஆனால் core idea ஒன்றுதான்: நீங்கள் ஒரு system property-ஐ எண்ணாக அளவிட்டு, அதை time series-ஆ சேமித்து, trend, threshold, anomaly பார்க்கிறீர்கள்.

Analogy: Car dashboard. Speedometer, fuel gauge, engine temperature எல்லாம் real-time numbers. Engine open பண்ணி பார்க்காமலேயே நீங்கள் புரிந்து கொள்ளலாம்.

அதேபோல service dashboard-ல latency, error rate, throughput இருந்தால் போதும் system-ன் health புரிந்துவிடும்.

## 3. How It Works

Service-ல metrics expose பண்ணப்படும். Prometheus style-ல `/metrics` endpoint-ல ஒரு text format-ல counters/gauges வரும்.

```
http_requests_total{method="POST",status="200"} 12345
http_request_duration_seconds_bucket{le="0.5"} 9800
```

Exporter, client library அல்லது sidecar இதை scrape செய்யும். Scrape interval 15s to 60s.

Scraped data time series database-ல சேமிக்கப்படும். Query பண்ணி graph பார்க்கலாம், alert rule set பண்ணலாம்.

Push vs Pull இரண்டும் உண்டு. Cloud-native-ல pull தான் common.

## 4. Architectural Reasoning

Metrics எப்போது தேவை?

* **Availability & performance monitor பண்ண**: request rate, error rate, latency.
* **Capacity planning**: CPU, memory, disk, connection pool usage trend பார்க்க.
* **SLO tracking**: 99th percentile latency < 500ms, error rate < 0.1% போன்ற target-ஐ measure பண்ண.
* **Fast triage**: alert வந்த உடனே எந்த service, எந்த dimension-ல problem என்று குறுகல் செய்ய.

Alternatives என்ன? Logs, traces. 
Logs = what happened, traces = how request flowed. Metrics = how much, how fast, how full.

ஒரு architect இதை தேர்வு செய்வது ஏனெனில் metrics cheap, aggregated, real-time, alert செய்ய ஏற்றது. Every request-ஐ log பண்ணுவது costly. Trace 100% செய்ய முடியாது.

## 5. Trade-offs

**Cardinality explosion.** Label-களை அதிகமாக போட்டால் time series எண்ணிக்கை அதிகரிக்கும். `user_id` or `request_id` ஐ label-ஆ போடாதீர்கள். உங்கள் TSDB memory and cost-ஐ blow up செய்யும்.

**Aggregation vs detail.** Metrics aggregated. எந்த specific request fail ஆனது என்று தெரியாது. அதற்கு logs/traces தேவை.

**Sampling & resolution.** High scrape frequency = better resolution, but more load. 15s interval போதும். Business metric-களுக்கு 1 min கூட போதும்.

**Alert fatigue.** Threshold set பண்ணும்போது noise வரும். Good practice: rate of change, not absolute value. Error rate > 1% for 5 minutes.

**Meaningful naming.** `http_requests_total` போல counter suffix `_total`, gauge suffix `_bytes` என்ற convention. Team இல்லாமல் dashboard-ல confusion ஆகும்.

## 6. Practical Example

E-commerce checkout service.

Four Golden Signals-ஐ monitor பண்ணுங்கள்:

* **Latency**: `http_request_duration_seconds` histogram. p95, p99 பார்க்க.
* **Traffic**: `http_requests_total` counter. RPS trend.
* **Errors**: `http_requests_total` by status code. Error rate = 5xx / total.
* **Saturation**: `process_cpu_seconds_total`, `container_memory_working_set_bytes`, DB connection pool usage gauge.

Production-ல traffic 2x ஆனது. Latency p99 200ms -> 1200ms ஆனது. CPU saturation 85% தொடுகிறது. Error rate மாறவில்லை.

இது capacity problem, not bug. Auto-scaling trigger ஆகிறது அல்லது cache hit ratio குறைந்ததா என்று பார்க்க வேண்டும்.

இதே metrics-ஐ SLO க்கு பயன்படுத்தலாம்: `availability = successful requests / total requests` over 30 days.

## 7. Reasoning Challenge

உங்களிடம் 20 microservices உள்ளது. ஒவ்வொரு service-ம் `http_request_duration_seconds` histogram-ஐ expose செய்கிறது. Labels: `service`, `endpoint`, `status`, `region`, `tenant_id`.

Dashboard ஆரம்பத்தில் நல்லா இருந்தது. 3 மாதம் கழித்து Prometheus OOM ஆகிறது, query slow ஆகிறது.

இங்கே என்ன problem? எந்த label-ஐ remove அல்லது redesign செய்வீர்கள்? High cardinality-ன் consequence என்ன?

சிந்தியுங்கள். Metrics-ன் purpose அளவிடுவது, ஒவ்வொரு request-ஐயும் track பண்ணுவது அல்ல.

## 8. Key Takeaways

* Metrics = numbers over time
