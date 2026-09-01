# Metrics

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.2 — Observability

## 1. Problem

உங்க LLM agent production-ல இருக்கு. Users சொல்றாங்க "response slow", "sometimes wrong". உங்க team சொல்றாங்க "எங்களுக்கு தெரியல".

Logs பார்த்தால் எதுவும் தெரியல. ஒரு request எவ்ளோ நேரம் எடுத்தது? எத்தனை requests fail ஆச்சு? LLM call எத்தனை முறை retry ஆச்சு? RAG retrieval latency எப்படி இருக்கு?

Logs என்பது **what happened** சொல்லும். ஆனால் **how healthy is the system** என்பதை சொல்லாது.

Metrics தேவைப்படுவதற்கு காரணம் இதுதான்: நீங்கள் ஒரு system-ஐ real-time-ல முடிவு எடுக்க வேண்டும், அதற்கு numbers வேண்டும். Not stories.

## 2. Mental Model

Metrics என்பது system-ன் vital signs.

ஒரு நபருக்கு body temperature, heart rate, blood pressure பார்த்தால் ஆரோக்கியம் தெரியும். System-க்கு request rate, latency, error rate, saturation பார்த்தால் ஆரோக்கியம் தெரியும்.

Metrics = time series numbers, aggregated continuously.

Logs = events. Traces = requests.

Observability = Metrics + Logs + Traces.

LLMOps / AI Observability-ல Metrics முதல் layer.

## 3. How It Works

ஒவ்வொரு service, LLM call, vector DB query, API gateway என்று எல்லா component-லும் instrumentation இருக்கும்.

அங்கே நீங்கள் counters, gauges, histograms expose பண்ணுவீர்கள்.

Prometheus போன்ற metrics collector அவற்றை scrape பண்ணும். Pull model. அல்லது OpenTelemetry exporter push பண்ணும்.

அந்த numbers-க்கு time dimension இருக்கும். அதை store செய்து query செய்யலாம். Grafana-ல dashboard பார்க்கலாம்.

இதுதான் core loop: instrument → collect → store → visualize → alert.

## 4. Architectural Reasoning

**எப்போது Metrics தேவை?**

System behavior-ஐ quantify செய்ய வேண்டும். Capacity plan செய்ய, SLO define செய்ய, incident-ஐ catch செய்ய.

**LLMOps-ல என்ன metrics?**

Application level: request_rate, request_latency p50/p95/p99, error_rate, token_usage_per_request.

LLM specific: prompt_tokens, completion_tokens, cost_per_request, LLM latency, retry_count, timeout_rate.

RAG specific: retrieval_latency, retrieved_chunks_count, reranker_score distribution, cache_hit_rate.

Infrastructure: CPU, memory, GPU utilization, queue length.

**ஏன் இதை தேர்வு செய்ய வேண்டும்?**

Metrics cheap, fast, aggregate ஆகும். Real-time alerting-க்கு சரியானது.

Logs-ஐ கொண்டு alert பண்ணினால் noise அதிகம். Traces expensive, sampling தேவை.

Metrics-ஐ பார்த்தால் தான் trend தெரியும். "Latency spike ஆரம்பித்த 10 நிமிடத்திற்கு முன் request rate double ஆகியிருக்கு" என்று reason பண்ண முடியும்.

## 5. Trade-offs

**Granularity vs Cost.** High cardinality metrics, உதாரணமாக user_id அல்லது request_id-ன் மீது label போட்டால் cardinality explode ஆகும். Prometheus storage cost அதிகரிக்கும். Cardinailty control செய்ய வேண்டும்.

**Aggregation loss.** Metrics aggregate ஆகிறது. ஒரு specific failure-ன் root cause கண்டுபிடிக்க logs/traces தேவை. Metrics tell you *something is wrong*, not *why*.

**Sampling bias.** LLM cost மாறும். Token usage distribution skewed ஆக இருக்கும். Average பார்த்தால் மோசடி ஆகும். p95/p99 முக்கியம்.

**Alert fatigue.** Too many alerts = ignored alerts. SLI/SLO define செய்து error budget-based alerting பண்ண வேண்டும்.

Failure mode: Metric gap. ஒரு critical path-ல instrumentation இல்லை என்றால், அங்கு blind spot. Incident-க்கு பிறகு தான் தெரியும்.

## 6. Practical Example

Enterprise RAG agent.

நீங்கள் dashboard-ல இவற்றை track செய்கிறீர்கள்:

- `rag_request_rate`: 120 req/min
- `llm_latency_p95`: 4.2s
- `retrieval_latency_p95`: 600ms
- `vector_db_error_rate`: 0.8%
- `cache_hit_rate`: 62%
- `cost_per_request`: $0.018

ஒரு நாள் `llm_latency_p95` 4.2s இலிருந்து 9s ஆகிறது. `retry_count` உயருகிறது. `cost_per_request` உயருகிறது.

Metrics-ஐ பார்த்தால்: latency spike + retry + cost up = LLM provider throttling அல்லது timeout.

Logs பார்த்தால்: `timeout after 10s` errors.

Decision: timeout reduce செய்யாமல், retry with exponential backoff + fallback model use செய்ய. அல்லது rate limit செய்ய.

இது தான் Metrics → reasoning → decision.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. Same LLM agent. ஒவ்வொரு consumer-க்கும் latency SLO வேறுபடுகிறது. Free tier-க்கு p95 < 5s, Enterprise tier-க்கு p95 < 2s.

நீங்கள் ஒரே metric name `llm_latency_seconds` வைத்திருக்கிறீர்கள்.

இப்போது dashboard-ல p95 4s காட்டுகிறது. Enterprise customers complain செய்கிறார்கள்.

Metrics-ஐ எப்படி design செய்வீர்கள்? எந்த label add செய்வீர்கள்? அதன் trade-off என்ன?

## 8. Key Takeaways

- Metrics என்பது system health-ன் numbers, not stories.
- LLMOps-ல Metrics = request rate, latency, error rate, token usage, cost, retrieval latency.
- Metrics quick மற்றும் cheap, ஆனால் why என்பதை சொல்லாது. Logs + Traces தேவை.
- High cardinality கவனம். Label design என்பது architectural decision.
- SLO define செய்து error budget-ல alert செய்யுங்கள், அல்லது alert fatigue வரும்.
