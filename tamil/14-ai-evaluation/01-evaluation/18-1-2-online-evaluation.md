# Online evaluation

> **Learning Path:** AI Evaluation
> **Section:** 18.1.2 — Evaluation

## 1. Problem

உங்களிடம் ஒரு LLM-based service இருக்கு. Model-ஐ release பண்ணியாச்சு. Production-ல போனதும் users கேள்வி கேட்க ஆரம்பிச்சாங்க.

இப்போ கேள்வி: **இது சரியா வேலை செய்யுதா?**

Offline-ல நீங்க benchmark dataset-ல test பண்ணீங்க. அது pass ஆச்சு. ஆனால் real user prompt வேற மாதிரி இருக்கு. Prompt style மாறுது, language mix ஆகுது, context longer ஆகுது. Output quality drop ஆகுதா தெரியாது.

அதனால் வேணும்: production traffic-லயே, real user interaction-லயே evaluate பண்ணறது. அதுதான் **online evaluation**.

இல்லாம போனால் என்ன ஆகும்? Bad model version தொடர்ந்து serve ஆகும், regression catch ஆகாது, user trust போயிடும்.

## 2. Mental Model

Offline evaluation = lab test. Controlled dataset, static.

Online evaluation = real-world monitoring. Live traffic, live users, live metrics.

நீங்க ஒரு experiment-ஐ production-ல run பண்ணி, A/B test மாதிரி compare பண்ணுவீங்க. Model v1 vs Model v2, அல்லது prompt variant A vs B.

Mental model: **Shadow traffic + sampling + human / LLM judge + business metrics**.

## 3. How It Works

Core flow:

1. **Traffic capture**: Real user request வருது. அதை log பண்ணி, feature store-ல சேமிக்க.
2. **Routing**: Request-ஐ 100% production model-க்கு போக விடு. ஒரு fraction-ஐ candidate model-க்கு shadow அல்லது A/B route பண்ணு.
3. **Capture output**: Both outputs-ஐ store பண்ணு. User-க்கு மட்டும் control output தான் தெரியும்.
4. **Judge**: Output-ஐ evaluate பண்ணு. Options:
   - Human labelers
   - LLM-as-judge with rubric
   - Rule-based checks: latency, length, safety filter hit, format compliance
5. **Aggregate**: Metrics-ஐ real-time dashboard-ல பார். Statistical significance check பண்ணு.

Simple architecture:

`User -> API Gateway -> Router -> [Prod Model, Candidate Model] -> Response`
`           -> Event bus -> Evaluation pipeline -> Judge -> Metrics store -> Dashboard`

## 4. Architectural Reasoning

இது எப்போ useful?

* Model iteration speed அதிகமாகும் போது
* Prompt changes, retrieval strategy, RAG pipeline changes test பண்ணும்போது
* Business impact தெரிய வேணும் போது: conversion, retention, not just BLEU/ROUGE

Constraint it addresses: **Distribution shift**. Offline dataset production-ஐ represent பண்ணாது.

Alternatives:
* **Offline evaluation**: cheap, fast, safe. ஆனால் real user behavior miss ஆகும்.
* **Offline + human**: better quality, ஆனால் slow, expensive.
* **Online**: true signal, ஆனால் operational complexity அதிகம்.

Architect choose online evaluation when decision cost high. எ.கா., finance summarization model change பண்ணும்போது wrong output cost பெரியது.

## 5. Trade-offs

**Signal vs Safety**: Real traffic-ல test பண்ணுறது signal தரும், ஆனால் bad output user-க்கு போயிடும் risk உண்டு. அதனால் shadow mode + canary rollout முக்கியம்.

**Cost vs Coverage**: Full traffic-ஐ judge பண்ண முடியாது. Sampling தேவை. Sampling bias வரும். Stratified sampling by user segment, prompt type பண்ணனும்.

**Latency**: Judge pipeline async இருக்கணும். Synchronous judge பண்ணா user latency increase ஆகும்.

**Judge reliability**: LLM-as-judge cheap but inconsistent. Human judge accurate but slow. Hybrid: LLM filter → human review for disagreements.

Failure modes:
* Router bug → candidate traffic production-க்கு leak ஆகும்.
* Judge drift → metric improve ஆகுது போல தெரியும் ஆனால் actual quality drop.
* Feedback loop: model அதிகம் use ஆன data-க்கு bias ஆகும்.

## 6. Practical Example

Enterprise RAG chatbot.

Problem: New embedding model deploy பண்ணனும். Offline recall 3% improve ஆச்சு.

Online evaluation setup:
* 5% traffic-ஐ candidate RAG pipeline-க்கு shadow route பண்ணு.
* Prod output user-க்கு போகும். Candidate output internal-ல judge ஆகும்.
* Judge rubric: relevance, completeness, citation presence, latency.
* Metrics: LLM judge score, user follow-up question rate, conversation abandonment, thumbs down.

2 வாரம் run பண்ணியப்புறம் தெரிஞ்சது: relevance score improve ஆச்சு ஆனால் latency 400ms increase ஆச்சு. Mobile users-ல abandonment increase. Trade-off clear ஆச்சு. Decision: only desktop users-க்கு rollout.

## 7. Reasoning Challenge

உங்களிடம் customer support agent இருக்கு. Model v2 release பண்ண போறீங்க. Offline eval-ல quality +8% இருக்கு. ஆனால் v2 average response length 2x ஆகி இருக்கு.

Production-ல online evaluation பண்ண போறீங்க. 
* என்ன metrics track பண்ணுவீங்க?
* Shadow மட்டும் போதுமா, அல்லது 1% A/B கொடுக்கலாமா?
* Judge-ஐ எப்படி design பண்ணுவீங்க?

Reason பண்ணு: cost, risk, signal quality.

## 8. Key Takeaways

* Online evaluation = production reality check. Offline good start, online final truth.
* Shadow + sampled A/B + async judging = safe learning loop.
* Metrics must mix quality judges with business signals: latency, retention, user feedback.
* Every model change creates trade-off: quality vs latency vs cost vs safety. Online evaluation makes it visible before full rollout.
