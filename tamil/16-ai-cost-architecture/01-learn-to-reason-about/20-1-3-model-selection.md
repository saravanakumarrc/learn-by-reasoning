# Model selection

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.3 — Learn to reason about

## 1. Problem

உங்க company-ல RAG agent இருக்கு. User query வருது. Simple FAQ-க்கு கூட அதே top-tier LLM-ஐ use பண்ணுறீங்க. 

பிறகு bill வருது. 

Token cost எதுக்கு இவ்வளவு? Latency 2-3 seconds. 80% queries-க்கு deep reasoning தேவையே இல்லை. ஆனா உங்க system எல்லாத்துக்கும் ஒரே model-ஐ பயன்படுத்துது.

இங்கே painful point என்ன? **Accuracy வேண்டும் என்ற பெயரில் cost, latency, throughput எல்லாத்தையும் கொடுத்துவிடுகிறோம்.**

Model selection என்பது model எது best என்பதை தேர்ந்தெடுப்பது அல்ல. System constraint-க்கு ஏற்ற model-ஐ எப்போது எங்கே பயன்படுத்துவது என்பதை reason பண்ணுவது.

## 2. Mental Model

ஒரு distributed system-ல tools choose பண்ணுவது போல. 

Heavy database job-க்கு Postgres, real-time stream-க்கு Kafka, cache-க்கு Redis. அதே மாதிரி AI system-ல:

* Classification, routing, summarization → cheap, fast model
* Complex reasoning, code generation → capable, expensive model
* Retrieval, embedding → specialized model

Model ஒரு resource. CPU / memory / network போல. **Right model for right workload.**

## 3. How It Works

Selection என்பது மூன்று dimensions-ல நடக்கும்:

**Capability:** Reasoning depth, context length, tool use, accuracy on domain.

**Cost:** Per token input/output, caching, batching.

**Latency & Throughput:** Time to first token, tokens per second, concurrency.

ஒரு request வரும்போது:

1. Intent ஐ classify பண்ணு
2. Constraint check பண்ணு: latency budget? cost budget? accuracy floor?
3. Routing decision: small model, medium model, large model or cascade

Cascade என்பது: cheap model-ல try பண்ணு, confidence low ஆனால் பெரிய model-க்கு escalate பண்ணு.

## 4. Architectural Reasoning

Model selection useful ஆகும் போது:

* Traffic volume high, cost dominant
* Latency SLO கடுமையானது
* Workload heterogeneous: simple vs complex queries mix
* Multi-tenant system with different SLAs

Alternatives:

* One-size-fits-all: எல்லாத்துக்கும் 405B model. Simple, operationally clean. Cost killer.
* Static tiering: query type-ஆல் fixed routing. Cheap to implement.
* Dynamic cascade + confidence gating: more complex, but cost efficient.
* Self-hosted open models vs API: control vs ops overhead.

Architect எப்போது choose பண்ணுவார்?

When cost per request matters more than absolute best accuracy, and when workload can be decomposed.

## 5. Trade-offs

**Accuracy vs Cost:** Bigger model = better quality, but 10-50x cost. Diminishing returns.

**Latency vs Capability:** Large models slow. User-facing chat-ல 800ms vs 3000ms difference conversion-ஐ மாற்றும்.

**Operational complexity vs Savings:** Routing logic, monitoring, fallback, A/B testing adds complexity. Team size small ஆனால் over-engineering ஆகிவிடும்.

**Consistency vs Flexibility:** One model = predictable behavior. Multiple models = evaluation, drift, prompt tuning per model.

Failure modes: Routing bug → cheap model-க்கு critical query போய் wrong answer. Cascade timeout → user wait double. Cost monitoring miss → bill spike.

## 6. Practical Example

Enterprise support RAG system.

Workload breakdown:
* 60% simple FAQ, entity extraction
* 30% multi-step reasoning, context synthesis
* 10% code/debugging help

Architecture:

Router service ஒரு tiny classifier model-ல query complexity-ஐ score பண்ணும்.

Score < 0.3 → 3B class model, cost $0.05 / 1M tokens, latency 200ms
Score 0.3-0.7 → 70B model, cost $2 / 1M tokens
Score > 0.7 → 405B model, cost $15 / 1M tokens

Cache layer: embeddings + response cache. Same query repeat ஆனால் model-க்கு போக வேண்டாம்.

Result: Average cost per query 70% குறைந்தது. P95 latency 40% குறைந்தது. Accuracy on critical queries same, because escalation path இருந்தது.

## 7. Reasoning Challenge

உங்களிடம் fintech chatbot உள்ளது. Two query types: balance check, transaction history. Simple. மற்றும் fraud explanation, dispute reasoning. Complex, regulated.

Latency budget 1.5 sec. Monthly query volume 10M. Cost budget $20k/month.

ஒரே 405B model-ஐ continue பண்ணுவீர்களா? இல்லை tiered routing பண்ணுவீர்களா? Routing செய்தால், எங்கே confidence threshold வைப்பீர்கள், எந்த failure mode-ஐ accept பண்ணுவீர்கள்?

## 8. Key Takeaways

* Model selection என்பது capability chase அல்ல, cost-latency-accuracy trade-off-ஐ manage செய்வது
* Workload-ஐ characterize பண்ணாமல் model தேர்வு செய்யாதே
* Cascade + routing + caching மூன்றும் சேர்ந்தால் தான் AI Cost Architecture வேலை செய்யும்
* Every routing decision creates new failure mode. Monitor it.
