# Fine-tuning

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.3.5 — Model patterns

**Fine-tuning**

### 1. The problem

A base LLM is a generalist trained on public data. In production you need a specialist: consistent voice, internal terminology, product-specific reasoning, and low-latency answers without large prompts.

Prompt engineering and RAG can steer behavior, but they have limits:
* Prompts are fragile and expensive at inference time
* RAG adds latency, retrieval errors, and hallucination on gaps
* You cannot teach a base model your style, safety policies, or proprietary formats via prompts alone

Fine-tuning exists to bake knowledge and behavior into weights, not into context.

### 2. Mental model

Think of pre-training as learning language. Fine-tuning is steering.

You take a model with a broad distribution over responses and shift its weights toward a narrower distribution you care about: domain style, task format, tool use, tone.

It is not memorization. It is adjusting priors. The model keeps general capabilities but prefers your patterns.

### 3. How it works

You start from a base or instruction-tuned model and continue training on a curated dataset of examples: input → desired output.

Essential mechanism:
* **Data curation > algorithm.** Quality, coverage, and distribution match matter more than size. 1k-10k good examples beats 100k noisy ones.
* **Parameter-efficient methods.** Full fine-tuning is expensive. LoRA/QLoRA update low-rank adapters while freezing base weights, giving 90% of the effect for <1% of trainable params.
* **Evaluation loop.** You need task-specific evals: exact match, format adherence, style consistency, and safety. Train on one distribution, validate on a held-out set from real traffic.

```
flowchart LR
    Base[Base / Instruction Model] --> Prep[Curate task data]
    Prep --> Train[LoRA Fine-tune]
    Train --> Eval[Task eval + safety check]
    Eval -->|Pass| Deploy[Production model + version]
    Eval -->|Fail| Prep
    RAG[Retriever] -.optional.-> Deploy
```

Fine-tuning is complementary to RAG, not a replacement.

### 4. Architectural reasoning

When it helps:
* **Consistent style and tone** across thousands of responses, e.g., brand voice, regulatory phrasing
* **Proprietary formats** you want the model to emit reliably: JSON schemas, internal ticket structures, function calls
* **Low-latency, high-volume** tasks where prompt + retrieval cost is too high
* **Domain jargon and reasoning patterns** that are stable over time

When not to:
* **Frequently changing facts.** Use RAG. Fine-tuning is slow to update and risks stale knowledge.
* **Small, one-off customizations.** Prompting is cheaper.
* **Limited high-quality data.** Fine-tuning will overfit.

Decision rule: Fine-tune for *behavioral* invariants. Retrieve for *factual* volatility.

### 5. Trade-offs and failure modes

* **Data cost vs inference cost.** Fine-tuning costs up front, then inference is cheap and fast. Prompt + RAG costs every request.
* **Maintenance burden.** You now own a model artifact. You need versioning, regression testing, and retraining pipelines when data drifts.
* **Catastrophic forgetting and overfitting.** Model can lose general ability or memorize training examples. Needs careful learning rate, regularization, and eval.
* **Evaluation gap.** Benchmark scores don't equal production quality. You need golden sets from real user queries and A/B testing.
* **Security leakage.** Training data can be extracted. Redact PII, filter prompts, and test for memorization before release.

### 6. Example

Enterprise support assistant for a SaaS product.

Problem: Agents use internal ticket taxonomy, SLA language, and must never promise refunds without approval.

Approach:
* Base model + RAG for live KB articles
* LoRA fine-tune on 3k curated agent responses with desired tone, refusal patterns, and JSON output for ticket creation
* Eval set checks for correct taxonomy usage, no hallucinated refund promises, and schema validity

Result: 40% fewer prompt tokens, consistent outputs, and stable format for downstream automation. KB updates still via RAG; behavior stays via weights.

### 7. Reasoning challenge

You need to summarize earnings calls for internal investors. Data is private, style must be neutral and consistent, and new calls arrive weekly.

Do you fine-tune, use RAG, or both? What do you fine-tune on and what do you retrieve?

### 8. Key takeaway

* Fine-tuning shifts model priors to encode stable behavior, style, and formats; RAG provides volatile facts.
* Choose fine-tuning when behavior must be consistent, low-latency, and prompt engineering is insufficient.
* Data quality and evaluation design dominate success; fine-tuning is an ops problem, not just training.
* Plan for versioning, drift, and cost: fine-tuned models are assets that need lifecycle management.
