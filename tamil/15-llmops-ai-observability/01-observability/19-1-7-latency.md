# Latency

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.7 — Observability

## 1. Problem

ஒரு LLM-powered chatbot இருக்கு. User ஒரு question கேட்டதும், response வர 8 seconds ஆகுது. User முதல் 2 seconds-லேயே கைவிட்டுடுறான்.

LLMOps-ல இது ஒரு business problem மட்டுமல்ல. Observability-ல இது ஒரு root cause தேடும் problem.

Latency ஏன் முக்கியம்? ஏனெனில் ஒரு AI system-ல user experience, cost, reliability எல்லாம் latency-ஆலயே decide ஆகும். ஒரு RAG pipeline-ல retrieval slow ஆனால் LLM wait பண்ணும். LLM token generation slow ஆனால் user experience மோசமாகும். முழு system-ம் ஒரு chain of services. ஒவ்வொன்றும் தனக்கு வரும் request-க்கு எவ்வளவு நேரம் எடுக்குது என்பது தெரியாமல், எங்கே bottleneck இருக்குன்னு கண்டுபிடிக்க முடியாது.

> What goes wrong if we don't have this? Bottleneck invisible ஆக இருக்கும். Slow component-ஐ optimize பண்ண முடியாது. User drop-off increase ஆகும். Cost per request அதிகமாகும்.

## 2. Mental Model

Latency என்பது **ஒரு request ஆரம்பிச்சு, முழு response கிடைக்க எடுக்கும் நேரம்**.

ஒரு distributed system-ல இது sum of waits அல்ல. இது chain reaction.

`User → API Gateway → Auth → Router → Retriever → Vector DB → LLM Service → Post-processor → Response`

ஒவ்வொரு service-ம் தனக்கு முன்னால் வரும் request-ஐ process பண்ணி அடுத்த service-க்கு forward பண்ணும். ஒவ்வொரு hop-லும் network latency, queue wait, processing time சேரும்.

Mental model: Latency = **Time to First Token + Time to Complete**. AI system-ல TTFB முக்கியம். User-க்கு "typing..." feel வேணும்.

## 3. How It Works

Observability-ல latency-ஐ நாம் மூன்று விதத்தில் பார்க்கிறோம்.

**1. End-to-End Latency:** User request to final response. இது business SLA define பண்ணும் metric.

**2. Service Latency:** ஒவ்வொரு service/service call-க்கும் எவ்வளவு நேரம் எடுக்குது. API gateway logs, distributed tracing spans-ல இது கிடைக்கும்.

**3. Component Latency:** Retrieval latency, embedding latency, LLM inference latency, token generation per second.

Tracing tools like OpenTelemetry, Jaeger, Datadog இந்த spans-ஐ collect பண்ணி, ஒரு request எங்கே நின்னுச்சு என்பதை visualize பண்ணும்.

ஒரு LLM call-ல 3000ms எடுத்தா, அதில் 200ms network, 800ms retrieval, 2000ms LLM generation என்பது தெரிந்தால்தான் action எடுக்க முடியும்.

## 4. Architectural Reasoning

Latency ஏன் observability-ல core metric ஆக இருக்கு?

LLMOps-ல system unpredictable. LLM inference time input length, model size, load-அனுசாரம் மாறும். RAG-ல vector DB query slow ஆகலாம். Cache miss ஆனால் latency spike ஆகும்.

Constraint இருக்கு: User tolerates max 2-3 seconds for conversational AI. Beyond that abandonment.

Options:

* **Measure only end-to-end:** Simple, but debug கஷ்டம்.
* **Distributed tracing per hop:** More overhead, but precise root cause.

Architect choose பண்ணுவது: Critical path services-க்கு tracing enable பண்ணி, latency histograms track பண்ணுவது. P50, P95, P99 எல்லாம் பார்க்கணும். Average மட்டும் பார்த்தால் slow tail users தெரியாது.

LLM service-ல streaming enable பண்ணி TTFB reduce பண்ணலாம். Retrieval-ல cache போடலாம். Vector DB-ஐ optimize பண்ணலாம்.

## 5. Trade-offs

**Latency vs Cost:** Latency குறைக்க, larger model, more replicas, faster GPU வேணும். Cost increase ஆகும். Smaller model + caching = cheaper but quality trade-off.

**Latency vs Consistency / Accuracy:** Retrieval-ல more sources check பண்ணினால் accuracy increase ஆகும், latency increase ஆகும். Trade-off.

**Latency vs Throughput:** System-ஐ scale up பண்ணி throughput increase பண்ணும்போது per request latency அதிகரிக்கலாம் if queue builds up.

**Observability overhead:** Tracing, metrics collection itself adds small latency and cost. Sampling use பண்ணி balance பண்ணணும்.

Failure mode: Latency spike invisible ஆக இருந்தால், autoscaling trigger ஆகாது. User experience degrade ஆகும், but dashboard green-ஆக காட்டும்.

## 6. Practical Example

Enterprise RAG assistant for internal docs.

End-to-end latency P95 = 4.2 seconds. SLA = 2.5 seconds.

Tracing-ல பார்த்தால்: API Gateway 30ms, Auth 40ms, Router 20ms, Retriever 1800ms, Vector DB 1200ms, LLM inference 1300ms.

Retriever slow ஆனது காரணம்: top-k=20, reranking enabled. Vector DB latency spike during peak hours.

Decision: Retriever-ல cache for frequent queries, top-k reduce to 10, async reranking for non-critical path. Result P95 drops to 2.4 seconds.

Cost? Cache adds Redis cost. Acceptable.

## 7. Reasoning Challenge

உங்க RAG system-ல P99 latency 6 seconds. P50 latency 1.2 seconds.

Tracing-ல பார்த்தால், 90% requests-ல retrieval 200ms, LLM 800ms. ஆனால் 1% requests-ல retrieval 4 seconds ஆகுது.

என்ன ஆராய்வீர்கள்? அது cold start ஆ? Vector DB shard imbalance ஆ? Query complexity variation ஆ? எந்த metric முதலில் பார்ப்பீர்கள்?

## 8. Key Takeaways

* Latency என்பது user experience-ன் direct proxy. AI system-ல TTFB முக்கியம்.
* End-to-end latency மட்டும் போதாது. Service level latency மற்றும் component latency தெரிந்தால்தான் root cause கிடைக்கும்.
* P50 கிடையாது, P95/P99 தான் architectural decision-க்கு guide பண்ணும்.
* Every latency optimization is a trade-off with cost, accuracy, and complexity.
