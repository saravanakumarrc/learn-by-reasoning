# OpenTelemetry

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.4 — Observability

## 1. Problem

உங்க system-ல 50 microservices இருக்கு. API gateway → auth service → order service → payment service → inventory service. ஒரு user-க்கு order place பண்ணும்போது latency 4.2 seconds வருது. யார் காரணம்?

Logs-ல பார்த்தா order service-ல timeout error இருக்கு. payment service logs-ல success இருக்கு. APM tool-ல எந்த trace-ம் இல்லை. அதனால service A எப்போ call பண்ணுது, எவ்வளவு நேரம் எடுத்துது, எந்த request-ல fail ஆகுதுன்னு connect பண்ண முடியல.

LLM call பண்ணும் ஒரு RAG service இருக்கு. Prompt token 1200, latency 2.1s. இது model-ல slow-வா, retrieval-ல slow-வா, vector DB slow-வா? மூணு system வெவ்வேறு teams maintain பண்றாங்க. அவங்க எல்லாரும் வெவ்வேறு tool use பண்றாங்க.

இங்கே வலி என்ன? **Observability data fragmented**. Metrics எங்கேயோ, logs எங்கேயோ, traces எங்கேயோ. Correlation இல்ல. AI pipeline-ல LLM call, embedding call, retrieval call எல்லாம் ஒரே request-ல நடக்குது. அதை ஒரே view-ல பார்க்க முடியல.

## 2. Mental Model

OpenTelemetry என்பது observability data-க்கான **common language**.

Metrics, logs, traces-க்கு ஒரே instrumentation model, ஒரே format, ஒரே export protocol. Application code-ல ஒரே முறை instrument பண்ணினால், அது எந்த backend-க்கும் போகும்.

நினைச்சுக்கோ: ஒரு service-க்கு மூன்று wires இருக்கு. ஒன்னு metrics, ஒன்னு traces, ஒன்னு logs. OpenTelemetry அந்த மூணு wires-க்கும் ஒரே plug standard கொடுக்குது. Collector ஒன்னு அதை receive பண்ணி, Prometheus, Jaeger, Grafana Cloud, Datadog, ELK எங்கே வேணும்னாலும் forward பண்ணும்.

## 3. How It Works

Instrumentation library உன் code-ல install ஆகும். Python, Java, Go, Node எல்லாம் இருக்கு.

நீ context propagate பண்ணுற. ஒரு request வந்தா trace_id create ஆகும். அது downstream service-க்கு HTTP header-ல போகும். அதனால end-to-end trace ஒன்னா தெரியும்.

இங்கே மூன்று signals:

* **Traces**: Request flow. Span = ஒரு work unit. `order.create` span-க்குள்ள `payment.call` child span.
* **Metrics**: Time series. request latency, LLM token usage, error rate. Counter, histogram, gauge.
* **Logs**: Event level details. Error message, prompt, tool call.

எல்லாம் OpenTelemetry SDK generate பண்ணி, local exporter அல்லது OTLP exporter மூலம் OpenTelemetry Collector-க்கு அனுப்பும். Collector process, batch, filter, route பண்ணி backend-க்கு அனுப்பும்.

LLMOps-க்கு முக்கியம்: OpenTelemetry semantic conventions for GenAI இருக்கு. `gen_ai.request`, `gen_ai.token.usage`, `gen_ai.operation.name` போன்ற attributes standard ஆக define ஆகியிருக்கு. அதனால model, provider, prompt, completion எல்லாம் consistent-ஆ measure பண்ண முடியும்.

## 4. Architectural Reasoning

எப்போ OpenTelemetry தேவை?

* Service count > 5 மற்றும் request crosses service boundary.
* LLM/agent pipeline இருக்கு, அங்கே latency பிரிக்கணும்: retrieval vs embedding vs LLM.
* Multi-team, multi-tool environment. Standardize instrumentation.
* Vendor lock-in தவிர்க்கணும்.

Alternatives என்ன?

* Vendor-specific SDK: Datadog APM, New Relic. Easy start, but migration costly.
* Custom logging + metrics. Cheap initially, ஆனால் correlation கிடைக்காது.
* Zipkin/Jaeger only for traces. Metrics/logs கவர் ஆகாது.

ஏன் OpenTelemetry choose பண்ணுவோம்?

* Instrumentation once, backend anytime. Cost control.
* Open standard, CNCF graduated.
* AI observability conventions ready.

Decision trade-off: உனக்கு கூடுதல் operational complexity வரும். Collector deploy, cardinality manage, sampling policy set பண்ணனும். Team-க்கு learning curve இருக்கு.

## 5. Trade-offs

* **Signal completeness vs cost**: Full tracing 100% sampling = storage cost high. Production-ல head sampling + tail sampling use பண்ணுவாங்க. LLM token metrics high cardinality ஆகும், அதை aggregate பண்ணணும்.
* **Standardization vs flexibility**: Semantic conventions follow பண்ணினா cross-tool compatible. ஆனால் custom business attributes வேணும்னா extra schema maintain பண்ணணும்.
* **Instrumentation overhead**: SDK overhead 1-3% typically. Hot path-ல excessive span creation latency add பண்ணும். Span naming முக்கியம்.
* **Observability vs privacy**: LLM prompts, user PII trace-ல capture ஆகும். Redaction, sampling, retention policy முக்கியம்.

Failure modes: Collector down ஆனா telemetry loss. Buffer fill ஆனா backpressure. Wrong trace_id propagation ஆனா trace broken.

## 6. Practical Example

Enterprise RAG chatbot.

Flow: API → Gateway → Orchestrator Agent → Retrieval Service → Vector DB → LLM Service.

OpenTelemetry SDK எல்லா service-லும். Orchestrator span start ஆகும். அதுக்குள்ள retrieval span, vector DB span, LLM span child ஆகும்.

Semantic conventions: `gen_ai.system=openai`, `gen_ai.request.model=gpt-4o`, `gen_ai.usage.input_tokens=1200`, `gen_ai.usage.output_tokens=300`. Latency per span தெரியும்.

இப்போ பார்த்தால் LLM span 1800ms, retrieval 400ms. ஆனால் token cost spike ஆகுது. Trace-ல பார்த்தா prompt size அதிகம். அதனால prompt compression செய்யலாம்.

ஒரே dashboard-ல traces + metrics + logs correlate ஆகும். Error rate increase ஆனால் எந்த model version, எந்த user segment என்று filter பண்ண முடியும்.

## 7. Reasoning Challenge

உங்க AI agent pipeline-ல 20 tools இருக்கு. ஒவ்வொரு tool call-க்கும் latency vary ஆகுது. Cost per request track பண்ணணும். Team-கள் Python, Go, Java mix ஆக இருக்கு. Observability backend-ஐ 6 மாசம் கழித்து மாற்ற வாய்ப்பு இருக்கு.

இங்கே OpenTelemetry use பண்ணுவீங்களா? Instrumentation எப்படி design பண்ணுவீங்க? Sampling எப்படி set பண்ணுவீங்க? PII prompts-ஐ எப்படி handle பண்ணுவீங்க?

## 8. Key Takeaways

* OpenTelemetry என்பது observability data-க்கான standard, tool அல்ல.
* Traces connect distributed request, metrics show health, logs give context. மூணும் correlate ஆகணும்.
* LLMOps-ல GenAI semantic conventions use பண்ணினால் model, token, latency compare பண்ண எளிது.
* Instrument once, export anywhere என்பது vendor lock-in-ஐ குறைக்கும், ஆனால் collector ops overhead தரும்.
* Sampling, cardinality, PII redaction ஆகியவை production design-ல முக்கியம்.
