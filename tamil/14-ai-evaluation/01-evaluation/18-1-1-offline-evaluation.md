# Offline evaluation

> **Learning Path:** AI Evaluation
> **Section:** 18.1.1 — Evaluation

## Offline Evaluation — AI Evaluation

### 1. Problem

உங்கள் LLM-based system production-ல் போய் விட்டது. User query வருகிறது, agent respond பண்ணுகிறது. ஒரு நாள் ஒரு மாதிரி output வருகிறது, மறுநாள் வேறு மாதிரி வருகிறது.

நீங்கள் deploy பண்ணும் முன் test செய்ய வேண்டும். ஆனால்:
* Live user-ஐ வைத்து experiment பண்ண முடியாது. Risk அதிகம்.
* Online metrics வர ஒரு வாரம் ஆகும். நீங்கள் ஒவ்வொரு change-க்கும் காத்திருக்க முடியாது.
* Model change, prompt change, retrieval change செய்தால் quality எப்படி மாறும் என்று உடனே தெரிய வேண்டும்.

இங்கே வரும் pain: **deploy பண்ணாமல், production data-யை பயன்படுத்தி, quality-யை repeatable-ஆக measure செய்ய வேண்டும்.** 

இதற்காகத் தான் Offline Evaluation வந்தது.

### 2. Mental Model

Offline Evaluation என்பது production-க்கு போகாமல், ஒரு fixed dataset மீது system-ஐ run செய்து score பண்ணுவது.

Think of it as unit test for AI system. Unit test-ல் input-output pair-க்கு expected output உண்டு. இங்கே expected output-க்கு பதில், quality signals உண்டு.

Key idea: **Production traffic-ஐ record பண்ணி, அதே traffic-ஐ offline sandbox-ல் replay செய்யுங்கள்.** அப்போது latency, cost, correctness எல்லாவற்றையும் பார்க்கலாம்.

### 3. How It Works

ஒரு offline eval loop பொதுவாக இப்படி இருக்கும்:

**Dataset** -> **System Under Test** -> **Metrics** -> **Decision**

1. **Golden Dataset**: Real user prompts, internal QA prompts, edge cases. Prompts + context + ground truth. RAG-க்கு relevant docs, expected answers. Agent-க்கு expected tool calls.
2. **Evaluation harness**: Same code path as production, but isolated. Model, prompt, retriever, embedding config எல்லாம் parameterized.
3. **Scoring**: Rule-based + LLM-as-judge. 
   * Rule-based: exact match, F1, tool call correctness, latency < 2s.
   * LLM-as-judge: helpfulness, factuality, style. Reference-based or reference-free.
4. **Reporting**: Per-metric score, regression detection, cost per query.

இதை CI/CD-ல் hook பண்ணினால், ஒவ்வொரு PR-க்கும் automatic regression check வரும்.

### 4. Architectural Reasoning

எப்போது offline eval useful?

* Model upgrade செய்யும்போது: GPT-4o mini -> GPT-4o. Quality improve ஆகிறதா? Cost increase justified ஆ?
* Prompt change: System prompt-ல் 2 line add பண்ணினால் hallucination குறையுமா?
* RAG pipeline change: New embedding model, new chunking strategy, new reranker.
* Agent tool change: New tool added, tool calling logic மாற்றம்.

Alternatives:
* **Online A/B testing**: Real users, real metrics. Gold standard but slow, risky, costly.
* **Manual QA**: Engineers sample outputs. Fast but not scalable, subjective.

Offline eval என்பது fast feedback loop. Architect-ஆக நீங்கள் decide பண்ணுவது: எந்த metrics-ஐ trust பண்ணலாம்? எந்த metrics online-ல் confirm பண்ண வேண்டும்?

Constraint: Offline dataset production distribution-ஐ represent செய்ய வேண்டும். Distribution shift ஆனால் offline score meaningless.

### 5. Trade-offs

**Speed vs Realism**: Offline fast, but user intent, multi-turn context, real retrieval noise capture பண்ண முடியாது.

**LLM-as-judge bias**: Judge model-க்கு own bias உண்டு. Judge model-ஐ மாற்றினால் scores மாறும். Inter-rater agreement check தேவை.

**Cost**: Large dataset-ல் eval செய்வது செலவு. 10k prompts x 3 variants = 30k LLM calls. Cache + sampling தேவை.

**Golden set maintenance**: Ground truth stale ஆகும். Production drift ஆனால் dataset புதுப்பிக்க வேண்டும். இல்லையெனில் false confidence.

Failure mode: Offline score improve ஆகிறது, online user satisfaction குறைகிறது. ஏனெனில் offline dataset-ல் easy queries அதிகம். அதனால் offline eval-க்கு stratified sampling தேவை: hard queries, edge cases, failure cases.

### 6. Practical Example

Enterprise support agent. Users ask about refund policy.

நீங்கள் offline dataset உருவாக்குகிறீர்கள்:
* 500 real anonymized queries from last month
* 100 manually crafted edge cases: ambiguous refund window, international orders
* Ground truth: expected answer summary + expected tool calls: `check_order_status`, `initiate_refund`

Current system: prompt v1 + embedding model A. Offline run:
* Factuality score 0.82, tool call accuracy 0.78, avg latency 1.4s, cost $0.012/query

Proposed change: prompt v2 with explicit instruction "never promise refund without order check". New embedding model B.

Offline run:
* Factuality 0.85, tool call accuracy 0.91, latency 1.6s, cost $0.013/query

Decision: Tool accuracy improve ஆகிறது, latency acceptable. Deploy to 5% canary for online validation.

Without offline eval, நீங்கள் production-ல் மாற்றம் செய்து, bad refunds create பண்ணி இருப்பீர்கள்.

### 7. Reasoning Challenge

உங்களிடம் customer-facing RAG system இருக்கிறது. Offline golden set-ல் 2,000 prompts உள்ளன. நீங்கள் retrieval model மாற்றுகிறீர்கள். Offline recall@10 0.71-ல் இருந்து 0.79-க்கு improve ஆகிறது. ஆனால் end-to-end answer quality score 0.74-ல் இருந்து 0.71-க்கு drop ஆகிறது.

இதை எப்படி reason பண்ணுவீர்கள்? Deploy பண்ணுவீர்களா? என்ன further check செய்வீர்கள்?

### 8. Key Takeaways

* Offline evaluation என்பது deploy-க்கு முன் fast, safe regression check. Online A/B-க்கு மாற்று அல்ல, complement.
* Good offline eval needs representative dataset, not just easy samples. Distribution matters.
* Metrics combination தேவை: rule-based correctness + LLM-as-judge quality + cost/latency.
* Offline score improve ஆனாலும், online validation தேவை. Every offline solution creates monitoring gap.
* Dataset-ஐ continuously refresh பண்ணுங்கள், இல்லையெனில் model உங்களை fool பண்ணும்.
