# Small language models

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.3.2 — Model patterns

### 1. The problem

Large language models are powerful, but they create architectural constraints. 
A 70B+ model in the cloud means: high latency per request, $0.001-$0.01 per token cost at scale, data leaving your perimeter, and you are rate limited and offline-unavailable.

That matters when the requirement is low latency, high volume, privacy, or offline operation. A chatbot that must respond in <100ms on a factory floor, a co-pilot that cannot send code to the internet, or a support bot handling 10M queries a month — the economics and operability of a large model break.

The problem is not capability alone. It is capability per constraint: latency budget, cost budget, data residency, and hardware budget.

### 2. Mental model

A Small Language Model is not a worse LLM. It is a capacity-for-constraint trade.

Think of it as a specialist vs a generalist. An SLM is 1B-8B parameters, often distilled and quantized, designed to be good enough at a narrow task and cheap enough to run where a large model cannot.

It moves intelligence closer to the data and the user.

### 3. How it works

SLMs get usable quality through three levers, not just size:

* **Distillation.** A small model is trained to mimic the outputs of a larger teacher, preserving reasoning patterns while shrinking parameters.
* **Efficient architecture and training.** Techniques like GQA, RoPE, and short-context pretraining keep inference fast on limited hardware.
* **Quantization and compilation.** INT4/INT8 quantization and kernels for ARM/NPU/Apple Silicon make a 3B model runnable on a phone or laptop at ~2-4GB RAM.

The result is a model that can run locally on CPU/NPU with tens to hundreds of ms latency and near-zero marginal cost per token.

### 4. Architectural reasoning

When it helps:
* **Latency-sensitive interactions.** On-device autocomplete, voice assistants, real-time agents.
* **Privacy and data residency.** PII, healthcare, finance data that cannot leave the device or VPC.
* **High-volume, low-complexity tasks.** Classification, entity extraction, simple RAG retrieval, routing.
* **Offline / unreliable networks.** Field devices, retail POS, aircraft.

Alternatives:
* Cloud LLM only. Best accuracy, worst cost/latency/privacy.
* Hybrid. SLM as first line, large model as fallback.

Decision rule: Use SLM when the task is bounded and the constraints are non-negotiable.

```
flowchart LR
    User[Client] --> SLM[On-device SLM 3B]
    SLM -->|Confidence high| Resp[Response]
    SLM -->|Uncertain / Complex| Router[Router]
    Router --> LLM[Cloud LLM]
    LLM --> Resp
```

This is the classic SLM + router pattern. The SLM handles 70-90% of queries locally. Only hard cases escalate.

### 5. Trade-offs and failure modes

* **Accuracy and reasoning depth.** SLMs hallucinate more and struggle with multi-step reasoning, long context, and rare knowledge. Fine-tuning on domain data helps, but does not close the gap with large models.
* **Context window.** Smaller models often have 4k-8k context vs 128k+ for large models. RAG must be tighter.
* **Prompt sensitivity.** They are less robust to ambiguous prompts. You need better system prompts and guardrails.
* **Operational cost shifts.** Inference cost drops, but you pay in engineering: quantization, evaluation, fine-tuning, and on-device updates.

Failure mode to watch: over-trust. Deploying an SLM for a task that needs high factual reliability without validation creates silent errors. Always pair with confidence scoring and fallback.

### 6. Example

Enterprise helpdesk for a bank. 

Requirement: internal agents must get instant answers to policy questions from a 200 page PDF, no customer data can leave the network, and 10k queries/day.

Architecture: 3B SLM quantized to INT4 runs on an on-prem inference box. Knowledge is embedded via RAG over the policy docs. The SLM does retrieval + short answer generation in <150ms. A router checks confidence and citation presence. If confidence <0.7 or no citation found, request escalates to a larger cloud LLM in a private VPC for final answer.

Result: 85% of queries answered locally, zero data exfiltration, cost per query ~$0.00001, latency acceptable for agents.

### 7. Reasoning challenge

You are designing a medical triage chatbot for a clinic. It must run offline on a tablet in exam rooms. It needs to extract symptoms from patient speech and draft a summary for the doctor. Accuracy is critical, but latency and privacy are non-negotiable.

Would you use an SLM alone, a large model alone, or a hybrid? What is your fallback for low confidence, and what would you measure to decide if the SLM is good enough?

### 8. Key takeaway

* SLMs exist to satisfy constraints — latency, cost, privacy, offline — not to maximize benchmark scores.
* They enable edge and private architectures by moving inference closer to data.
* Use them for bounded tasks with guardrails, and route hard cases to larger models.
* The architect's job is to define the confidence threshold and failure mode, not just pick a model size.
