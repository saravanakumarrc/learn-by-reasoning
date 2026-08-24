# Foundation models

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.1.2 — Understand

### 1. The problem

Building AI used to mean: collect labeled data for one task, train a model from scratch for that task, deploy, repeat.

That creates three architectural constraints:
* **Data cost per task.** Labeling is expensive and domain-specific. You can't label for every possible use case.
* **Training cost per task.** Training a large model from scratch costs millions in compute and weeks of time.
* **Fragmentation.** Each task gets its own model, its own pipeline, its own maintenance.

You need a way to amortize the massive upfront cost of learning general patterns, then cheaply specialize it.

### 2. Mental model

A foundation model is a pre-trained general-purpose representation learned from massive, diverse data.

Think of it as an operating system for intelligence: expensive to build once, cheap to run many applications on top of. You don't train a new OS for each app; you build on it.

The value is transfer: the model already knows syntax, semantics, reasoning patterns, and world knowledge. You only need to steer it.

```mermaid
flowchart LR
    A[Massive unlabeled data] --> B[Self-supervised pre-training]
    B --> C[Foundation Model: general representations]
    C --> D[Adaptation: Prompting / Fine-tune / LoRA]
    D --> E[Downstream tasks]
```

### 3. How it works

Pre-training is self-supervised on broad corpora. The objective is simple: predict next token, masked token, or similar. At scale this forces the model to learn reusable representations of language, code, images, or multimodal data.

Capabilities emerge from scale and breadth, not explicit programming.

Adaptation is cheap compared to pre-training:
* **Prompting / in-context learning:** steer behavior at inference with examples.
* **Lightweight adaptation:** LoRA/adapters, fine-tuning on small labeled sets.
* **RAG:** keep knowledge external and ground outputs with retrieval.

You pay once for pre-training, many times for cheap adaptation.

### 4. Architectural reasoning

When it helps:
* Many downstream tasks share a common domain and you have limited labeled data per task.
* You need generalization to unseen inputs, not just classification of a fixed set.
* Time-to-value matters more than absolute control.

Alternatives:
* **Train from scratch:** only makes sense if you have a massive private dataset that must never leave your environment and the task is narrow and stable.
* **Smaller task-specific models:** better latency, cost, and control, but require more labeled data and fail on distribution shift.
* **Retrieval-only systems:** good for factual lookup, poor for synthesis and reasoning.

Decision driver is economics of reuse. If you can amortize pre-training across >1 task, foundation model wins.

### 5. Trade-offs and failure modes

* **Cost shifts from training to inference.** Pre-training is amortized, but inference is continuous and expensive. Latency and throughput become architectural constraints.
* **Generalization vs control.** More general means more hallucination, prompt injection risk, and non-determinism. You trade precision for flexibility.
* **Data privacy and leakage.** Pre-training on public data means potential memorization. Private data should not be used for prompt-only systems without isolation.
* **Operational brittleness.** Small prompt changes cause large behavior changes. Versioning, evaluation, and guardrails are required.
* **Vendor lock-in and alignment drift.** Behavior depends on provider updates. Your product can change without code changes.

Failure modes architects see: over-reliance on zero-shot for high-stakes decisions, no grounding, and treating the model as a reliable database.

### 6. Example

Enterprise customer support.

Problem: thousands of intents, new products weekly, limited labeled conversations.

Architecture:
* Foundation LLM as base capability for understanding and generation.
* Retrieval layer over knowledge base, policies, and tickets for grounding.
* Lightweight fine-tune or LoRA on approved responses for tone and compliance.
* Evaluation harness for factuality and safety before production.

Result: one model supports many intents, new products are covered by retrieval not retraining, and adaptation cost is hours not weeks.

### 7. Reasoning challenge

You are architecting a real-time fraud detection system that must decide in <100ms and explain decisions for auditors. You have 10 years of private labeled transactions you cannot share externally.

Do you build on a foundation model, a smaller task-specific model, or a hybrid? What constraints drive your choice?

### 8. Key takeaway

* Foundation models exist to amortize massive pre-training cost across many tasks via cheap adaptation.
* They trade training cost and data needs for inference cost, non-determinism, and operational complexity.
* Choose them when you need broad generalization and reuse; avoid them when you need hard real-time guarantees, full data control, or provable determinism.
* Architect around them with grounding, evaluation, and guardrails, not as drop-in replacements for databases or business logic.
