# Infrastructure costs

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.13 — Learn to reason about

## 1. Problem

நீங்கள் ஒரு AI product-ஐ production-ல விட்டிருக்கீங்க. முதல் வாரம் எல்லாம் சுமார். இரண்டாவது வாரம் user traffic double ஆகுது. மூன்றாவது வாரம் ஒரு marketing campaign விட்டதும் traffic 5x ஆகுது.

அப்புறம் cloud bill வருது. GPU cost மட்டும் முன்னாடி விட 10x ஆகியிருக்கு. CTO கேட்குறார்: "எதுக்கு இவ்ளோ?"

இந்த கேள்விக்கு பதில் சொல்ல முடியலன்னா நீங்க architect இல்ல, cost victim.

Infrastructure costs ஒரு technical problem மட்டும் இல்ல. இது **architectural decision**-ன் direct consequence.

## 2. Mental Model

Infrastructure cost = **Resources × Time × Utilization Efficiency**

Resources = CPU, RAM, GPU, storage, bandwidth
Time = எவ்ளோ நேரம் ஓடுது
Utilization Efficiency = அந்த resource-ஐ நீங்க எவ்ளோ useful வேலைக்கு பயன்படுத்துறீங்க

AI systems-ல cost-ன் main driver GPU time. ஒரு inference request-க்கு நீங்க 80GB H100-ஐ 100ms-க்கு பயன்படுத்துறீங்கன்னா, அந்த 100ms-க்கு நீங்க cost pay பண்றீங்க. அதே request-ஐ batch பண்ணி, model smaller பண்ணி, cache பண்ணினா cost குறையும்.

Cost என்பது feature அல்ல. Cost என்பது **constraint**.

## 3. How It Works

Cloud pricing மூன்று முக்கிய models:

**On-demand:** உடனே வேணும். கூடுதல் விலை. Peak traffic-க்கு safe.

**Reserved / Savings Plans:** Long term commitment. 1-3 year. 30-70% saving. நீங்க usage predictable என்று நம்பும்போது மட்டும்.

**Spot / Preemptible:** Idle capacity. 60-90% cheaper. நிறுத்தப்படலாம். Training batch jobs-க்கு நல்லது.

AI-specific cost levers:

- **Model size vs latency trade-off:** 7B model ஒரு A10G-ல ஓடும். 70B model-க்கு 8x H100 தேவை. Latency same-ஆ வேணும் என்றால் cost skyrockets.
- **Batching:** 1 request per inference vs 32 requests batch-ஆ சேர்த்து inference. Throughput per GPU பெருகும். Latency கொஞ்சம் அதிகரிக்கும்.
- **Caching:** Same prompt/retrieval results மறுபடியும் compute பண்ண வேண்டாம். Embedding cache, response cache.
- **Quantization / Distillation:** FP16 → INT8/INT4. Accuracy கொஞ்சம் குறையலாம். Cost half ஆகும்.
- **Routing:** Simple query-க்கு small model, complex query-க்கு large model. Not all requests need GPT-4.

## 4. Architectural Reasoning

Cost-ஐ reason பண்ணும்போது கேள்வி இது:

> இந்த request-க்கு எவ்ளோ compute தேவை? அதை எப்படி குறைக்கலாம்?

அதுக்கு மூன்று layers இருக்கு:

**1. Workload shaping:** Peak-ஐ smooth பண்ணு. Async processing, queue. User-க்கு உடனே தேவையில்லாத work-ஐ off-peak-ல run பண்ணு.

**2. Architecture choice:** 
Monolith GPU service vs per-tenant isolated service vs serverless inference. Serverless startup latency high ஆனால் idle cost zero.

Event-driven vs request-driven. Streaming RAG pipeline-ல vector DB read + LLM call இரண்டையும் ஒரே time-ல செய்யாமல், pre-fetch பண்ணலாம்.

**3. Operational efficiency:** Auto-scaling policy எப்படி set பண்ணீங்க? Scale up slow, scale down fast. Idle pods waste. Right-sizing. GPU sharing via vLLM, TensorRT-LLM, continuous batching.

## 5. Trade-offs

**Latency vs Cost:** Lower latency = more idle capacity. Strict SLA வைக்கும்போது over-provisioning தேவை. Cost அதிகம்.

**Accuracy vs Cost:** Bigger model, more context, more tokens = better answer, higher cost. உங்க use case-க்கு really need 128k context? Maybe 8k enough.

**Consistency vs Cost:** Strong consistency க்கு more replicas, more writes. Eventual consistency-ல cost குறையும்.

**Operational simplicity vs Cost:** Managed service எளிது ஆனால் premium. Self-hosted Kubernetes + GPU node pool கட்டுப்பாடு அதிகம், team time cost அதிகம்.

**Failure mode:** Cost overrun தான் biggest failure. Unbounded autoscaling + prompt injection attack = bill $100k in hours. Rate limiting, budget alerts, quota per tenant must be architectural.

## 6. Practical Example

Enterprise RAG chatbot.

Initial design: Every user query → embedding → vector DB search → retrieve 20 chunks → build 20k token prompt → call GPT-4o → stream response.

Cost per query ~ $0.08. 100k queries/day = $8k/day.

Architectural reasoning:

- 60% queries repeat. Redis cache for query → response. Cost -40%
- Small model for query classification + routing. Simple FAQ → Llama 3 8B. Complex → GPT-4o. Cost -30%
- Retrieval reduced: Reranker + top 5 chunks instead of 20. Prompt size 8k. Cost -25%
- Batch embeddings offline. User uploads documents → async embedding pipeline with spot instances.

Final cost per query ~ $0.02. Same user experience for 80% queries.

இது model change இல்ல. Architecture change.

## 7. Reasoning Challenge

உங்களிடம் 2 products உள்ளது. Product A: Real-time fraud detection, 50ms SLA, 24/7 traffic. Product B: Weekly report generation for 10k users, can tolerate 4 hour delay.

இரண்டுக்கும் GPU inference தேவை. Same cloud account.

எப்படி infrastructure cost-ஐ reason பண்ணுவீங்க? On-demand, reserved, spot எதை எங்கே பயன்படுத்துவீங்க? Model serving architecture எப்படி வேறுபடும்?

## 8. Key Takeaways

- Cost is architectural constraint, not finance afterthought
- GPU time is the unit of cost in AI systems. Optimize batching, caching, routing, model size
- Match workload pattern to pricing model: steady → reserved, bursty → spot/on-demand, real-time → over-provision
- Every performance gain has cost consequence. Reason before you scale out

இதை புரிஞ்சா மட்டும் தான் bill-ஐ explain பண்ண முடியும்.
