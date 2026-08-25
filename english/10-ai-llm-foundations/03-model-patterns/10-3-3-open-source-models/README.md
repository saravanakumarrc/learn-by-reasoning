# Open-source models

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.3.3 — Model patterns

### 1. The problem

You need an LLM in production, not a demo. That means predictable cost, latency, data control, and the ability to change behavior without waiting for a vendor.

Closed APIs solve the first day: low ops burden, best-in-class performance, simple pricing. The constraints appear later:
* **Data residency and privacy:** You cannot send proprietary customer data, PII, or regulated data to a third-party API.
* **Cost at scale:** Token pricing is linear and non-negotiable. High-throughput workloads become a budget problem.
* **Latency and availability:** Network round-trip + vendor rate limits = unpredictable tail latency. No SLA you can control.
* **Customization:** You need domain style, tools, or safety policies baked in, not just prompt engineering.

Open-source models are a response to those constraints, not to ideology.

### 2. Mental model

Think of a model as software you can run, not just a service you call.

Closed model = SaaS. Open weights = source code for weights. You get the parameters, weights, and usually the architecture. You can host it, inspect it, fine-tune it, and modify the inference stack.

Open weights ≠ fully open source. Many models are open weights with restrictive licenses. The architectural capability you care about is: *can I run this in my VPC and change it?*

### 3. How it works

You download weights under a license, load them into an inference engine, and serve them.

```
mermaid
flowchart LR
    Client --> Router
    Router -->|public data, low sensitivity| ClosedAPI[Closed API]
    Router -->|private data, custom behavior| SelfHost[Self-hosted Open Weights]
    SelfHost --> GPUCluster[GPU Cluster / vLLM / TGI]
    GPUCluster --> Model[Open Weights Model]
```

Key pieces:
* **Inference stack:** vLLM, TGI, Ollama, or custom serving for throughput, quantization, and batching.
* **Fine-tuning / adaptation:** LoRA, QLoRA, or full fine-tune on proprietary data to change style, tools, and safety.
* **Guardrails and eval:** You own red-teaming, evaluation harnesses, and policy enforcement.

You trade vendor ops for your own ops.

### 4. Architectural reasoning

When it helps:
* Data cannot leave your perimeter. Healthcare, finance, government.
* You need deterministic latency and cost. Self-hosted cost is CapEx + fixed inference cost.
* You need custom behavior that prompt engineering cannot give. Fine-tuning on internal docs, codebases, or customer support history.
* You want to avoid lock-in and have an exit strategy for model changes.

Alternatives:
* Closed API: fastest to value, best raw capability, zero ops.
* Hybrid: closed API for general queries, open weights for sensitive or high-volume internal workloads.

Decision logic is not performance. It is control vs convenience.

### 5. Trade-offs and failure modes

* **Capability gap.** Leading open weights lag closed frontier models on raw reasoning and tool use. You close the gap with fine-tuning and RAG, not with weights alone.
* **Ops burden.** You now own GPUs, autoscaling, model updates, quantization, security patches, and monitoring. A model is not static software; it drifts and needs eval.
* **Security surface.** Open weights can be reverse-engineered. Model weights can leak prompts via side channels. You need prompt filtering, output validation, and strict access controls.
* **Licensing risk.** Commercial use restrictions, attribution, and redistribution clauses vary. Legal review is required before production.
* **Cost illusion.** Inference is cheap until you need 24/7 availability, redundancy, and A100/H100 capacity. Idle GPU cost dominates.

Failure mode to remember: teams self-host for privacy, then route all traffic through it without guardrails, quantization, or caching, and get latency spikes and cost overruns.

### 6. Example

Enterprise RAG for internal knowledge base with PII.

Closed API would require data masking and vendor DPA, still risky for HR and legal docs. 

Architecture chosen: Llama 3.1 70B open weights, quantized to 4-bit, served via vLLM on 2x8 H100s in private VPC. Retrieval from vector DB inside VPC. Fine-tune with LoRA on company tone and disallowed topics. Router sends public marketing queries to closed API, internal queries to self-hosted model.

Result: data never leaves network, latency P95 < 800ms, cost per 1M tokens predictable, and model can be updated quarterly with internal eval suite.

### 7. Reasoning challenge

You are architecting a customer-facing chatbot for a bank. It must handle general Q&A and process account-specific queries. Regulations require data residency in EU, and you expect 10M requests/day with bursty traffic.

Would you choose closed API, open weights self-hosted, or hybrid? What is the primary decision driver, and what is the first operational capability you would need to build before launch?

### 8. Key takeaway

* Open weights buy control, privacy, and cost predictability at the price of ops ownership.
* The decision is architectural, not about model quality alone. Data governance and latency requirements drive it.
* Self-hosting without eval, guardrails, and a rollout plan creates a reliability and security liability.
* Hybrid architectures are common: closed for capability, open for sensitive/high-volume workloads.
