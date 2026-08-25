# Prompt versioning

> **Learning Path:** LLM Application Engineering
> **Section:** 7.1.6 — Prompt engineering

**Prompt versioning**

### 1. The problem

Prompts are production code, but they are treated like configuration.

When you ship a prompt change you change behavior without changing code. There is no compile step, no type check, and the output is non-deterministic. A small wording tweak can raise latency, cost, hallucination rate, or break downstream parsers.

Without versioning you get:
* No safe rollback when a prompt regresses
* No reproducibility for audits or incident post-mortems
* No controlled rollout or A/B test
* Silent drift between environments

You need the same guarantees you have for software: immutable artifacts, change history, and controlled promotion.

### 2. Mental model

Think of a prompt as a versioned API contract between your application and the model.

The contract is: inputs + versioned template + parameters -> expected behavior.

Versioning makes prompts discoverable, testable, and deployable like any other service artifact. The model is the runtime; the prompt version is the program.

### 3. How it works

A prompt version store holds immutable prompt artifacts:

```mermaid
flowchart LR
    Req[Request with context] --> Router[Prompt Router]
    Router --> Store[(Prompt Store)]
    Store --> V1[prompt@v1.3.0]
    Store --> V2[prompt@v2.0.0]
    Router --> LLM[LLM]
    LLM --> Resp[Response]
```

Each version contains:
* `template` - the text with placeholders
* `parameters` - temperature, max_tokens, tools, system role
* `metadata` - owner, change reason, tests passed, risk level
* `parent` - lineage for rollback

Routing is explicit. Requests are tagged with a version selector: pinned version, canary %, user segment, or model.

Promotion is a pipeline: draft -> test -> staging -> production. Once published, a version is immutable.

### 4. Architectural reasoning

When it helps:
* Multiple teams share prompts and need isolation
* You need A/B tests on wording, few-shot examples, or tool use
* Compliance requires reproducible outputs for the same input
* Cost/latency guardrails depend on prompt design

Alternatives:
* Hard-coded strings in code. Fast to start, impossible to govern at scale.
* Feature flags on prompts without versioning. You can toggle but you cannot audit or reproduce.
* No versioning. Works until first production incident.

Choose versioning when prompts become a reliability and business risk surface, not a one-off experiment.

### 5. Trade-offs and failure modes

* **Version explosion.** Every experiment creates a version. Without garbage collection and naming conventions, discovery fails. Mitigate with semantic versioning and lifecycle policies.
* **Routing complexity.** The router adds latency and a new failure mode. If the store is down, you need a fallback to last-known-good version.
* **Test gap.** Versioning without evaluation is just storage. You need automated prompt tests: golden outputs, unit tests on parsing, and metric gates on cost/latency/hallucination.
* **Model coupling.** A prompt version is only valid for a specific model and context. Changing the model without bumping the prompt version causes silent regressions. Store model_id with the version.
* **Observability cost.** You must log prompt_version_id with every inference to correlate issues. Otherwise you cannot roll back.

### 6. Example

Enterprise support chatbot.

V1.2.0 uses a concise extraction prompt for ticket classification. Support sees a 12% misclassification rate after adding a new product line.

Engineer creates v1.3.0 with updated few-shot examples. It is tested offline against a regression suite and promoted to 10% of traffic.

Metrics show lower misclassification and similar latency. Rollout completes to 100%. The old version remains for two weeks, then archived.

When a compliance audit asks “what prompt was used on 2026-01-12 for ticket #48291?”, the logged version_id returns the exact template and parameters.

### 7. Reasoning challenge

Your RAG summarizer prompt v2.1.0 reduces hallucination but increases tokens by 30%. You want to test it on premium users only, while keeping standard users on v2.0.0. Your prompt store supports version pinning per request, but your router currently selects by global default.

What is the minimal architectural change you need, and what metric would you gate promotion on?

### 8. Key takeaway

* Prompts are code. Version them immutably like code.
* Versioning enables safe rollout, rollback, and auditability for non-deterministic behavior.
* Pair versioning with automated evaluation and version-aware observability.
* Keep routing simple, store model coupling with the version, and delete old experiments.
