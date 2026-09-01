# Quality degradation

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.7 — AI-specific monitoring

## 1. Problem

உங்கள் RAG system production-ல் நல்லா run ஆகுது. ஒரு வாரம் முன்னாடி user satisfaction நல்லா இருந்தது. இப்போ complaints வருது: "answers irrelevant", "hallucination அதிகம்", "slow".

Logs-ல் errors இல்லை. Latency சராசரி 1.2s, p95 2s. Service up. Database healthy. GPU utilization normal.

என்ன நடந்தது? Traditional monitoring சொல்லாது.

AI system-ல் quality degrade ஆகும் போது, metrics green-ஆ இருந்தாலும் user experience கெட்டுபோகும். Quality degradation என்பது silent failure.

**ஏன் இது painful?** ஏனெனில், LLM output non-deterministic, data drift ஆகும், embedding model stale ஆகும், retrieval quality குறையும், prompt drift ஆகும். இதை CPU, memory, error rate-ஆல் catch பண்ண முடியாது.

## 2. Mental Model

Quality degradation = **Expected behavior vs Observed behavior gap** growing over time.

Traditional system-ல் "working" என்பது request succeed ஆனது. AI system-ல் "working" என்பது request succeed ஆனதோடு, answer relevant, factual, safe, on-brand, helpful என்பதும்.

நீங்கள் ஒரு service-ஐ monitor பண்ணுவது போல, AI system-ஐ monitor பண்ணுவது output quality-ஐ monitor பண்ணுவது.

## 3. How It Works

AI-specific monitoring என்பது three signals-ஐ track பண்ணும்:

**1. Input signal**
User query distribution எப்படி மாறுது? New intents வருதா? Prompt injection அதிகமா? 
Topic drift, language mix, length change.

**2. Processing signal**
Retrieval quality: query → vector search → retrieved chunks. 
Precision@k, recall, retrieval latency, context relevance score.
LLM generation: prompt version, temperature, model version, token usage.

**3. Output signal**
Answer quality: relevance, factuality, safety, style adherence, latency-to-first-token.
User feedback: thumbs up/down, follow-up query rate, conversation abandonment.

இதை தொடர்ந்து measure பண்ணி, baseline-உடன் compare பண்ணணும். Drift detect ஆனால் alert.

## 4. Architectural Reasoning

இது எப்போ useful?

* Production LLM app, RAG, agent உள்ள system
* Model or data pipeline மாறும்
* User behavior மாறும்
* Compliance / safety தேவை

Alternatives:
* Only business metrics: conversion, churn. Too late, root cause தெரியாது.
* Only LLM logs: you see output but not why quality fell.
* Only manual QA sampling: slow, not scalable.

Architect choice: **Online + Offline evaluation loop**.

Online: production traffic-ல் lightweight proxies run பண்ணி, sampled responses-ஐ score பண்ணு.
Offline: golden dataset, synthetic queries, regression test suite weekly run பண்ணு.

## 5. Trade-offs

**1. Evaluation cost vs coverage**
Real human rating accurate ஆனா expensive. LLM-as-a-judge cheap ஆனா bias உண்டு. உண்மையில் hybrid: high-value traffic-ல் human review, rest-ல் automated judge.

**2. Latency vs observability**
Production-ல் every request-ஐ evaluate பண்ணுவது cost அதிகம். Sampling, shadow evaluation தேவை. Trade-off: faster detection vs cost.

**3. Granularity vs noise**
Too many metrics → alert fatigue. முக்கியமான 4-6 quality signals தேர்வு பண்ணு: retrieval relevance, answer relevance, factuality, safety violation rate, user satisfaction.

**4. Stability vs sensitivity**
Threshold too tight → false alarms. Too loose → degradation miss ஆகும். Baseline மாறும் user pattern-ஐ consider பண்ணி adaptive threshold வை.

Failure modes: 
* Golden dataset stale ஆகி, actual user need-ஐ capture பண்ணாது.
* Judge model bias: உங்கள் own LLM judge ஆனது உங்கள் model-ஐ over-score பண்ணும்.
* Data drift detection slow, quality already degraded for days.

## 6. Practical Example

Enterprise support RAG.

Architecture: user query → retriever → vector DB → LLM → answer.

Monitoring:
* Retrieval: top-3 chunks relevance score < 0.6 ஆனால் alert. Query embedding drift detect via clustering.
* Generation: answer contains source citation? citation present ஆனா source-ல் இல்லாத claim உண்டா? Factuality check via NLI model.
* User signal: thumbs down rate > 5% for 30 min window. Follow-up query within 1 min rate increase.

ஒரு நாள், retrieval relevance drop ஆனது. Investigation-ல் vector DB-ல் நேற்று நடந்த product update chunks index ஆகவில்லை. Pipeline lag.

Traditional monitoring: all green. AI observability: quality degrade catch.

## 7. Reasoning Challenge

உங்கள் customer-facing chatbot-ல் monthly model upgrade பண்ணீங்க. Latency same, error rate zero. ஆனால் user thumbs down 3% இருந்து 8% ஆக உயர்ந்துள்ளது.

Retrieval metrics stable. Prompt same. என்ன investigate பண்ணுவீங்க? Quality degrade-ன் possible root cause என்ன என்ன? Which signal நீங்கள் first check பண்ணுவீங்க, ஏன்?

## 8. Key Takeaways

* AI system health = uptime அல்ல, output quality consistency.
* Quality degradation-ஐ catch பண்ண input drift, retrieval quality, generation quality, user feedback signals வேண்டும்.
* Monitoring without baseline and automated evaluation = blind.
* Every architectural change — model, prompt, retriever, data — creates quality risk. Measure before and after.

இதை புரிஞ்சா, நீங்கள் AI system-ஐ architect பண்ணும்போது reliability-ஐ availability-ல மட்டும் அளக்காம, quality-ஆயும் அளப்பீங்க.
