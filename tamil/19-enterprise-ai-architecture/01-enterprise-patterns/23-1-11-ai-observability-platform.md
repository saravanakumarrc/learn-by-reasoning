# AI observability platform

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.11 — Enterprise patterns

## 1. Problem

உங்கள் team ஒரு production RAG system deploy பண்ணியிருக்கு. LLM + vector database + retrieval pipeline இருக்கு. 

ஒரு நாள் customer சொல்றார்: "இந்த answer ஏன் தப்பா வந்துச்சு?" 
நீங்கள் என்ன செய்வீங்க?

Log-ஐ பார்த்தால்: `query -> retrieval -> LLM call -> response`. மட்டும் தெரியும். எந்த document retrieve ஆச்சு, ஏன் அந்த document தேர்ந்தெடுக்கப்பட்டது, embedding similarity எவ்வளவு, prompt இறுதியா எப்படி இருந்தது, LLM token usage என்ன, latency எங்கே spike ஆச்சு — எதுவும் தெளிவா தெரியாது.

Traditional observability இருக்கு: service latency, error rate, CPU. ஆனால் AI system-ல failure mode வேறு. Hallucination, bad retrieval, prompt drift, data contamination, cost spike, slow reasoning — இவை எல்லாம் metrics-ல catch ஆகாது.

இங்கேதான் problem painful ஆகுது: **நீங்கள் output-ஐ trust பண்ண முடியாது, debug பண்ண முடியாது, improve பண்ண முடியாது.**

## 2. Mental Model

AI observability platform என்பது AI system-க்கான full-stack tracing + lineage + quality monitoring.

Traditional observability = **what happened to the system**.
AI observability = **what happened to the data, model, prompt, and reasoning, and why the output was that way.**

Mental model simple: ஒவ்வொரு request-உம் ஒரு trace ஆக capture பண்ணு. அந்த trace-ல்:

* Input: user query, context, metadata
* Retrieval: which chunks retrieved, similarity scores, reranker decision
* Prompt: final prompt sent to LLM, system prompt version
* LLM: model name, tokens in/out, latency, cost, raw output
* Post-processing: tool calls, agent steps, final answer

இதை time-series metrics + searchable logs + dashboards + alerts ஆக மாற்று.

## 3. How It Works

Core components:

**Instrumentation SDK** - உங்கள் service code-ல ஒரு wrapper. `tracer.start_span()` மாதிரி. இது automatically capture பண்ணும்: prompt, completion, retrieval results, embeddings.

**Trace collector** - high volume events வரும். Sampling + batching பண்ணி store செய்யும். Usually object storage + time-series DB.

**Evaluation & Quality Engine** - offline/online evaluation. LLM-as-judge, grounding check, faithfulness score, toxicity, PII leakage.

**Dashboard & Search** - ஒரு specific request-ஐ trace ID வச்சு பின் தொடரலாம். "இந்த user-க்கு ஏன் தவறான answer வந்தது?" என்று drill down.

**Alerting** - cost per query > threshold, latency p95 spike, retrieval recall drop, hallucination rate increase.

முக்கியமானது: **Data lineage**. Prompt version v1.2, embedding model v3, vector index built on 2024-09-01 data — இவை எல்லாம் trace-உடன் link ஆக இருக்கணும்.

## 4. Architectural Reasoning

When useful?

* Production AI system-ல் multiple components: retrieval, reranker, LLM, tools. Failure point தெரியாது.
* Prompt changes, model swaps, data refreshes நடக்கும். Regression detect பண்ண வேண்டும்.
* Compliance / audit வேண்டும்: "இந்த answer எந்த source-ல இருந்து வந்தது?"
* Cost control: LLM calls மிக அதிகமாகி விடுகிறதா?

Alternatives:
* DIY logging to Elasticsearch - வேலை செய்யும் ஆனால் schema, evaluation, lineage கிடையாது.
* APM tools like Datadog/New Relic - service health தெரியும், AI-specific semantics தெரியாது.

Architect choose பண்ணுவார் என்றால்: team size, data volume, need for custom evaluation.

## 5. Trade-offs

**Signal vs Overhead.** Full prompt capture செய்யலாம், ஆனால் PII leak ஆகும். Cost அதிகம். Sampling பண்ணினால் rare failure miss ஆகும்.

**Storage cost.** Every request trace ஆகும். 1M queries/day * 10KB = 10GB/day. Retention policy முக்கியம்.

**Evaluation latency.** LLM-as-judge ஒவ்வொரு request-க்கும் செய்ய முடியாது. Async batch evaluation பண்ணணும்.

**Consistency of metrics.** Hallucination score subjective. Different judges give different scores. Baseline வைத்து trend பார்க்கணும், absolute number-ஐ மட்டும் நம்பக்கூடாது.

Failure mode: observability itself becomes bottleneck. Tracer slow ஆனால் production latency increase ஆகும். Always make instrumentation non-blocking, drop if queue full.

## 6. Practical Example

Enterprise support chatbot.

Architecture: API Gateway -> Router -> Retrieval Service -> Reranker -> LLM Service -> Response.

Observability platform trace பார்க்கும்:

1. Query: "எனது insurance claim status என்ன?"
2. Retrieval: 3 chunks retrieved, top similarity 0.72, 0.61, 0.58. Chunk 1 outdated data from 2023.
3. Prompt version: system_prompt_v4, contains instruction "always use latest data".
4. LLM: GPT-4o, latency 1.8s, cost $0.004
5. Output: claims closed என்று சொல்லியுள்ளது.

Dashboard-ல alert: grounding score < 0.5 for last 100 requests. Drill down செய்தால் vector index last updated 3 months ago. Decision: trigger re-index.

இல்லாமல் இருந்தால், team எப்போதும் "LLM தப்பா பேசுது" என்று மட்டும் நினைத்திருப்பார்கள்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இல்லை, 20 LLM agents இருக்கு. ஒவ்வொரு agent-ம் tools use பண்ணும், multi-step reasoning பண்ணும். Cost per user request $0.10 முதல் $2 வரை மாறுகிறது. CEO கேட்கிறார்: "ஏன் கடந்த வாரம் cost 40% increase ஆனது?"

நீங்கள் AI observability இல்லாமல் என்ன பார்ப்பீர்கள்? Observability இருந்தால் எந்த 3 signals முதலில் பார்ப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* AI observability = request trace + data lineage + quality metrics. Service health மட்டும் போதாது.
* Problem இருக்கும் இடம்: retrieval quality, prompt drift, model behavior change, cost spike.
* Trade-off எப்போதும் overhead vs signal completeness. Sample, redact PII, async evaluation.
* Observability இல்லாமல் AI system-ஐ production-ல improve செய்ய முடியாது, trust பண்ண முடியாது.
