# Model routing

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.8 — Learn to reason about

## 1. Problem

உங்க company-ல AI feature வந்துச்சு. ஆரம்பத்துல ஒரே ஒரு LLM தான் இருந்தது - say GPT-4o. அதுல எல்லா request-ம் போனது.

இப்போ பிரச்சனை வருது:

* Simple FAQ மாதிரி low-risk request-க்கு ஏன் expensive model use பண்ணணும்?
* Coding agent-க்கு reasoning heavy model தேவை, summary-க்கு சின்ன model போதும்.
* Peak load-ல latency spike ஆகுது, cost கூடுது.
* Compliance-க்கு data EU-க்குள்ள தான் இருக்கணும், ஆனா ஒரு global model தான் இருக்கு.
* ஒரு model down ஆனா முழு feature-மே down.

ஒரே model-க்கு எல்லாத்தையும் அனுப்புறது வேலை செய்யும் வரை சரி. Scale ஆனதும் cost, latency, reliability, quality எல்லாம் clash ஆகுது.

**Model routing என்பது எந்த request எந்த model-க்கு போகணும் என்று தீர்மானிக்கும் ஒரு decision layer.**

## 2. Mental Model

Model routing = smart traffic police for LLM calls.

Request வரும்போது, அதோட context, constraints, cost, latency budget-ஐ பார்த்து, available models-ல ஒன்றை தேர்வு செய்து அனுப்புது.

இது single model-ஐ replace பண்ணுவது இல்ல. இது முன்னால ஒரு thin layer வச்சு, பின்னால பல models-ஐ pool பண்ணி manage பண்ணுவது.

## 3. How It Works

Routing decision எப்போதும் இந்த inputs-ஐ பார்க்கும்:

* **Request features:** prompt length, task type - classification, summarization, coding, RAG, agent step
* **Policy:** cost cap per user, latency SLO, data residency, PII presence
* **Model capabilities:** context window, tool calling, reasoning, fine-tuned domain
* **Runtime health:** current latency, error rate, quota, cost per token

Flow simple:

```
Client → Router → {Model A / Model B / Model C}
          ↓
        Fallback, Retry, Cache check
```

Router தான் load balancing, failover, A/B testing, canary deployment எல்லாத்தையும் handle பண்ணும்.

அதிகம் வேண்டாம். Core ஐடியா: **decision is made per request, not per deployment.**

## 4. Architectural Reasoning

Model routing useful ஆகும் போது:

* **Cost control தேவைப்படும் போது.** 80% requests simple. Small cheap model-ல solve பண்ணலாம். 20% முக்கியமானது large model.
* **Quality vs latency trade-off** இருக்கும் போது. Real-time chat-க்கு fast model, batch analysis-க்கு slow but accurate model.
* **Multiple providers** use பண்ணும்போது. OpenAI, Anthropic, local open-weight model, fine-tuned model. Failover-க்கு தேவை.
* **Compliance / data residency** constraint இருக்கும் போது. EU data EU model-க்கு தான் போகணும்.

Alternatives:

* **Static mapping:** Route by endpoint. Simple ஆனா flexible இல்ல.
* **Client-side choice:** App logic decide. Router logic scattered ஆகும்.
* **No routing:** One model fits all. Scale-ல வேலை செய்யாது.

Architect choose பண்ணும் போது பார்ப்பது: Decision latency router-ல add ஆகுமா? Router single point of failure ஆகுமா? Observability எப்படி?

## 5. Trade-offs

* **Complexity vs savings.** Router logic grow ஆகும். Rules, ML-based classifier, feedback loop வேண்டி வரும். ஆனா cost 30-60% குறையலாம்.
* **Latency added.** Routing decision + possible queue. Decision <5ms இருக்கணும், இல்லனா SLO break ஆகும்.
* **Consistency risk.** Same prompt different model → different output. User experience non-deterministic ஆகும். Version pinning முக்கியம்.
* **Operational burden.** Model health, cost per request, token usage எல்லாத்தையும் monitor பண்ணணும். Router config drift ஆகும்.

Failure mode: Router bug ஆனா எல்லா traffic-மே தவறான model-க்கு போகும். அதனால router-ஐ simple, observable, feature-flagged வச்சுக்கணும்.

## 6. Practical Example

Enterprise support chatbot.

Request வருது:

* Tier 1: FAQ intent detection → small classifier model, < $0.001, <200ms
* Tier 2: Policy summarization → mid-size model with retrieval
* Tier 3: Escalation draft for human agent → large reasoning model, cost higher

Router logic:

```
if pii_detected == true → route to private on-prem model
elif prompt_tokens > 128k → route to long-context model
elif user_tier == "free" and latency_slo < 500ms → route to cheap fast model
elif task == "code_generation" → route to code fine-tuned model
else → default model
```

Peak load-ல router automatic failover பண்ணும்: primary model error rate >2% → secondary provider-க்கு switch.

Result: Cost per conversation குறைஞ்சது, latency P95 stable ஆனது.

## 7. Reasoning Challenge

உங்களிடம் 3 models இருக்கு:

* Model A: $0.01 /1k tokens, 800ms latency, high quality
* Model B: $0.002 /1k tokens, 400ms latency, medium quality
* Model C: self-hosted, $0.0005 /1k tokens, 1200ms latency, medium quality

Users: free tier - 10k requests/day, paid tier - 2k requests/day.

SLO: free tier latency <600ms, paid tier quality > threshold.

Peak traffic-ல Model A quota exhaust ஆகுது.

இந்த scenario-ல routing policy என்ன வைப்பீங்க? Free vs paid எப்படி route பண்ணுவீங்க? Failover எப்படி design பண்ணுவீங்க? ஏன்?

## 8. Key Takeaways

* Model routing என்பது cost, latency, quality, compliance constraints-க்கு ஏற்ப request-க்கு request model தேர்வு செய்யும் layer.
* One model fits all என்பது early stage-க்கு மட்டும் சரி. Scale-ல heterogeneous fleet தேவை.
* Router decision simple இருக்கணும், observable இருக்கணும், fail-safe இருக்கணும்.
* Every routing rule creates a new trade-off: savings vs complexity, consistency vs cost.

இதை புரிஞ்சுக்கிட்டா, AI cost architecture-ல model fleet-ஐ business constraints-க்கு ஏத்த மாதிரி run பண்ண முடியும்.
