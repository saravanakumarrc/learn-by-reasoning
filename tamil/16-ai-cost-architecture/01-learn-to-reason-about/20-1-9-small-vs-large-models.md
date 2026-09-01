# Small vs large models

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.9 — Learn to reason about

## 1. Problem

உங்க company-ல ஒரு AI feature இருக்கு. Chatbot, summarization, classification, RAG agent. Traffic வளர்ந்துகிட்டே போகுது. 

ஒரு request வந்தா, நீங்க அதை எப்போதும் GPT-4 class large model-க்கு அனுப்புறீங்க. Latency 2-3 seconds, cost per request $0.02. 1M requests per month = $20k. P95 latency உங்க SLA-வை தாண்டுது.

இப்போ வந்த request எல்லாம் ஒரே மாதிரி இல்ல. சிலது simple intent classification: "இது refund request-ஆ?". சிலது open-ended reasoning: "இந்த contract clause-ஐ விளக்கி, risk எழுது".

ஒரே hammer-ஆல எல்லாம் அடிச்சா என்ன ஆகும்? Cost explode ஆகும். Latency எல்லா user-க்கும் high ஆகும். Simple task-க்கு overkill ஆகும். 

**Problem என்ன?** Every request-க்கும் best accuracy வேணும்னு நினைக்கிறது, அது cost, latency, throughput-ல pain உருவாக்குது. 

அதனால தான் small vs large model என்ற reasoning தேவைப்படுது.

## 2. Mental Model

Model size ஒரு spectrum. 

Small model = 1B - 7B parameters. Fast, cheap, fits on CPU / small GPU, lower quality on complex reasoning.

Large model = 70B+ அல்லது frontier models. Slow, expensive, needs high-end GPU, better reasoning, longer context, better nuance.

Think of it as **specialized worker vs generalist expert**.

Small model = line worker. Routine, repetitive, well-defined input-output. Fast and cheap.

Large model = senior architect. Complex, ambiguous, needs deep reasoning. Slow and costly.

நீங்க எல்லா வேலையும் senior-க்கு கொடுக்க மாட்டீங்க. அப்படி கொடுத்தா burn rate ஏறும்.

## 3. How It Works

Difference வருவது மூன்று இடத்தில்:

**Capacity:** Large model-க்கு more parameters, so it can learn richer patterns, handle ambiguity, do multi-step reasoning.

**Latency & Throughput:** Small model inference milliseconds-ல் முடியும். Large model seconds எடுக்கும். Same hardware-ல small model-ஐ 10x அதிக instances ஓட்றலாம்.

**Cost:** Inference cost roughly proportional to parameters * tokens. Small model per token cost 5-10x குறைவு.

ஒரு typical architecture: Router service incoming prompt-ஐ பார்க்கும். Prompt length, complexity, confidence threshold பார்த்து small model-க்கு அனுப்புமா, large model-க்கு அனுப்புமா decide பண்ணும். Failure-ல fallback இருக்கும்.

## 4. Architectural Reasoning

எப்போ small model use பண்ணுவீங்க?

* High volume, low complexity tasks: intent classification, entity extraction, spam detection, routing, moderation pre-filter.
* Latency sensitive path: autocomplete, real-time chatbot first response.
* Edge / on-device: privacy, offline.

எப்போ large model use பண்ணுவீங்க?

* Ambiguous, open-ended generation, long context reasoning, code synthesis, multi-step planning.
* Where quality error cost high: legal summary, financial advice, customer escalation.

Decision flow பொதுவா:

Problem pain -> Constraints: latency budget, cost per 1k requests, accuracy requirement -> Options: small only, large only, hybrid router -> Decision.

Hybrid தான் பெரும்பாலும் winning pattern. Small model first, if confidence low -> escalate to large. அல்லது small model for fast draft, large model for refine.

## 5. Trade-offs

**Accuracy vs Cost:** Large model wins accuracy, but cost 5-20x. Small model 80-90% accuracy போதுமானது என்றால் அது enough.

**Latency vs Quality:** Small model <100ms possible. Large model 1-3s. User experience-க்கு அது முக்கியம்.

**Operational complexity:** Two models = routing logic, monitoring, fallback. Complexity ஏறும். But cost saving justify பண்ணும்.

**Failure mode:** Small model overconfident wrong answer கொடுக்கும். Large model hallucinate பண்ணும், but less frequently. Router itself தப்பா route பண்ணினால் quality drop ஆகும்.

Every architectural solution creates trade-off. Small+large = savings, but now you have routing error, model drift, evaluation overhead.

## 6. Practical Example

Enterprise support chatbot.

Request வருது. 

Router: prompt-ஐ small classifier-க்கு அனுப்பு. "password reset" மாதிரி FAQ pattern-னா small model-ல தீர்வு கொடு. 80ms, $0.0002.

Confidence <0.8 அல்லது query contains "billing dispute", "legal" keywords என்றால் large model-க்கு escalate பண்ணு. RAG with vector database, then large model generate.

Result: 70% requests small model-ல settle. Cost per month $20k -> $6k. P95 latency 800ms -> 250ms. Customer satisfaction same because simple queries fast.

Monitoring: small model accuracy weekly evaluate. Drift ஆனா retrain.

## 7. Reasoning Challenge

உங்களிடம் RAG chatbot இருக்கு. 500k queries/day. 60% queries are simple FAQ retrieval. 30% need synthesis. 10% need deep reasoning with 32k context.

Latency SLA 600ms. Cost budget $10k/month.

நீங்கள் ஒரே large model use பண்ணினால் cost என்ன ஆகும்? Latency SLA meet ஆகுமா?

இப்போ hybrid router + small model for FAQ classification + large model for synthesis என்று design பண்ணினால், எந்த metrics-ஐ monitor பண்ணுவீங்க router decision சரியாக இருக்கிறதா என்று உறுதி பண்ண? 

ஏன் small model-ஐ first pass-ஆ போடுவது cost architecture-க்கு முக்கியம்?

## 8. Key Takeaways

* Model size ஒரு cost-latency-quality knob. எல்லாம் large model-க்கு அனுப்புவது architectural waste.
* High volume simple tasks = small model. Complex ambiguous tasks = large model. Hybrid routing தான் practical.
* Decision ஆதாரம்: accuracy requirement, latency budget, cost per request, error cost.
* Router தவறு, monitoring gap, fallback இல்லாமை என்பது hybrid architecture-ன் முக்கிய failure modes.
