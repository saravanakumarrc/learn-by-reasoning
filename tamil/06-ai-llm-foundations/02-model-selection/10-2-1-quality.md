# Quality

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.1 — Model selection

### 1. Problem

நீங்கள் ஒரு RAG system-க்கு LLM வாங்க போறீங்க. Options எல்லாம் இருக்கு: GPT-4o, GPT-4.1 mini, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1 70B, Mistral Small, open source 8B models.

Budget limit இருக்கு, latency SLA இருக்கு, accuracy தேவைப்படுது. எல்லா model-உம் "good" என்று சொல்லும். 

What goes wrong if you just pick the biggest model? Cost per 1M tokens 30x ஆகும். p95 latency 2 sec ஆகும். 10k requests/day-க்கு bill மாதம் $15k ஆகும். 

What goes wrong if you pick the cheapest model? Hallucination அதிகம், tool calling fail ஆகும், user trust போகும்.

Model selection-ன் பிரச்சனை: **Best model இல்லை, best fit for constraints இருக்கு.**

### 2. Mental Model

Model selection என்பது **trade-off space-ல் ஒரு point-ஐ தேர்வு செய்வது**.

அந்த space-ன் axes:

* **Quality / Capability** - reasoning, instruction following, tool use, long context
* **Latency** - time to first token, time to completion
* **Cost** - per token input/output
* **Throughput / Scale** - how many requests per second you can serve
* **Control / Privacy** - on-prem vs API, data retention, fine-tuning
* **Operability** - observability, rate limits, reliability

நீங்கள் ஒரு புள்ளியை தேர்வு செய்கிறீர்கள், அது உங்கள் constraints-ஐ satisfy பண்ணனும்.

### 3. How It Works

Practical-ல model selection ஒரு process மாதிரி run ஆகும்:

**1. Define use case constraints.** Not "we need good LLM". Define: max latency 800ms, cost per request < $0.02, accuracy > 90% on internal benchmark, context length 32k.

**2. Create evaluation set.** Real user prompts, not generic. உங்கள் domain-ன் 200-500 examples. Include edge cases: tool calling, long context, multilingual Tamil/English mix, reasoning.

**3. Candidate shortlist.** 3-5 models max. Mix: one premium, one mid, one small/open.

**4. Measure.** Latency, cost, quality. Quality-க்கு human eval + automated metrics: pass rate, hallucination rate, tool call correctness.

**5. Decision with guardrails.** Choose model, but set fallback: if latency > threshold, degrade to smaller model. If confidence low, escalate to bigger model.

Model selection is not one-time. It is continuous. Traffic pattern, cost, new model release மாறும்.

### 4. Architectural Reasoning

When does model selection matter?

* **Chatbot / Customer support:** Latency matters, cost matters a lot. Small model + good RAG often enough.
* **Agent with tool use:** Instruction following முக்கியம். Cheapest model fail ஆகும். Here mid-size model needed.
* **Code generation / Reasoning heavy:** Premium model needed, but can be async.
* **High volume, low margin:** You must go small or open source + self-host.

Alternatives:

* **One big model for everything** - simple, but wasteful and slow.
* **Model routing** - simple queries -> small model, hard queries -> big model. Best cost/quality balance.
* **Cascade / fallback** - try small first, if fails, retry with big.
* **Fine-tune small model** - domain specific performance improve ஆகும், but operational overhead உண்டு.

Architect choose ஏன்? Because model is a component with SLA. Like choosing database. You wouldn't pick Postgres for everything blindly.

### 5. Trade-offs

**Quality vs Cost:** 70B class model 3-5x better on reasoning but 10-30x cost. Is that worth it for your use case?

**Latency vs Quality:** Larger models, longer context = higher latency. For synchronous user chat, 1.5 sec vs 4 sec = churn.

**Control vs Convenience:** Open source model self-host பண்ணினால் data privacy control கிடைக்கும், but you own ops, GPU cost, reliability. API model = zero ops, but vendor lock-in.

**Throughput vs Capability:** One A100 can serve ~100 req/s with 8B model, but only ~20 req/s with 70B. Scale cost changes.

Failure modes: You pick model based on benchmark, but production data distribution different. Hallucination increases. Rate limits hit during peak. Context length exceed ஆகி truncation ஆகும்.

### 6. Practical Example

Enterprise support RAG system.

Constraints: 5k chats/day, p95 latency < 1.2s, cost < $0.015 per chat, Tamil+English mix.

Evaluation:

* GPT-4o: 92% pass, 1.1s latency, $0.028 per chat → cost fail
* GPT-4o mini: 78% pass, 0.6s latency, $0.004 per chat → quality fail
* Claude 3.5 Haiku: 85% pass, 0.7s latency, $0.006 per chat → ok
* Llama 3.1 8B self-hosted: 82% pass, 0.5s latency, $0.002 per chat → ops overhead

Decision: Start with Claude 3.5 Haiku for API simplicity. Add routing: simple FAQ -> Llama 8B self-hosted to cut cost 40%. Hard reasoning queries -> escalate to GPT-4o.

Result: Average cost $0.008, p95 latency 0.9s, pass rate 87%.

### 7. Reasoning Challenge

உங்களிடம் ஒரு code review agent இருக்கு. Daily 2k PRs. ஒவ்வொரு PR-க்கும் 500 tokens context. Need high accuracy on logic bugs, latency not critical because async.

Options: GPT-4o mini $0.15/1M, 80% bug detection. GPT-4o $2.5/1M, 94% detection. Llama 70B self-host, ~$0.6/1M equivalent GPU cost, 90% detection.

எந்த architecture தேர்வு செய்வீர்கள்? Cost, quality, ops complexity எப்படி balance பண்ணுவீர்கள்? Routing வேண்டுமா?

### 8. Key Takeaways

* Model selection என்பது capability-ஐ தேர்வு செய்வது அல்ல, constraints-ஐ satisfy செய்யும் trade-off-ஐ தேர்வு செய்வது.
* Quality, latency, cost, control ஆகியவை ஒன்றுக்கொன்று முரண்படும். One metric optimize பண்ணினால் மற்றது degrade ஆகும்.
* Production evaluation set உங்கள் domain data-ல் இருந்து வர வேண்டும். Generic benchmarks mislead ஆகும்.
* Model routing / cascade பெரும்பாலும் best ROI கொடுக்கும். Not one model for all.

**One mental model to leave with:** Model is not a feature, it's an infrastructure component with cost and SLA. Choose it like you choose a database.
