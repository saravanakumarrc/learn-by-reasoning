# AI observability platform

> **Learning Path:** Enterprise AI Architecture
> **Section:** 19.1.11 — Enterprise patterns

### The problem

Traditional observability works for deterministic services: request in, request out, latency, error rate, trace the call chain. 

AI systems break that model. The same prompt can produce different answers. Failure is not a 500 error, it is a hallucination, a bad retrieval, a drifted embedding, a toxic output, or a $12,000 surprise bill. The root cause lives across three domains that never meet in normal telemetry: **input data and context**, **model and prompt logic**, and **non-deterministic execution**.

When a customer support agent gives a wrong refund policy, you need more than latency. You need: what user message arrived, what conversation history was fed, which documents were retrieved and with what scores, what prompt template and system instructions were used, which model version was called, what tools were invoked and with what arguments, what the raw output was, and how it was evaluated. Without that lineage, you cannot reproduce, fix, or prove compliance.

### Mental model

Think of AI observability as distributed tracing for reasoning, not just requests.

A trace is a conversation execution. A span is a step: ingestion, retrieval, prompt construction, LLM call, tool call, post-processing, evaluation. Each span carries data lineage, not just timing: inputs, parameters, embeddings, token counts, cost, and outcome signals.

The platform’s job is to capture that lineage reliably, make it queryable, and attach evaluations to it so you can reason about quality, not just uptime.

### How it works

Capture is done at the agent/LLM gateway, not inside the model.

```
flowchart LR
    User --> API[API Gateway]
    API --> Agent[Agent Orchestrator]
    Agent --> Retriever[RAG / Vector DB]
    Agent --> LLM[LLM Provider]
    Agent --> Tool[Tools / APIs]
    Agent --> Eval[Evaluator]
    Agent --> Collector[Observability Collector]
    Collector --> Store[(Trace Store)]
    Collector --> Warehouse[(Data Lake / Warehouse)]
    Store --> UI[Analytics & Alerts]
```

The collector records:
* **Request context**: user id, session, prompt template id, system instructions, conversation history, metadata.
* **Data lineage**: retrieved documents with ids, scores, sources; feature inputs.
* **Execution**: model name, version, temperature, tokens in/out, latency, cost, tool calls with args/results.
* **Output & evaluation**: final response, guardrail decisions, automated metrics like faithfulness, relevance, toxicity, and human labels.

Storage is tiered. Hot traces for recent sessions in a purpose-built store, raw payloads in object storage, aggregated metrics in warehouse. Sampling is essential: capture 100% for errors/low confidence, sample high-volume healthy traffic.

### Architectural reasoning

You need this when AI moves from prototype to production with real users, cost, and risk.

It helps when:
* Multiple models, prompts, and retrievers change independently. You need to attribute regressions to a specific change.
* Agents compose tools. You need causal tracing across LLM + external systems.
* Compliance and safety require auditability: what was shown to whom, with what source.

Alternatives are ad-hoc logging and manual replay. That works for a demo, fails at scale because prompts are large, data is PII-sensitive, and you cannot reproduce non-determinism without frozen context.

Decision point: centralize observability at the gateway. A thin SDK or proxy intercepts every LLM/tool call, enriches with trace context, and emits a structured event. This decouples application code from observability and guarantees consistent capture.

### Trade-offs and failure modes

* **Fidelity vs cost and privacy.** Full payload capture enables debugging but explodes storage and creates PII risk. You need redaction, PII masking, and retention policies per data class. Mask before storage, keep a reference hash for correlation.
* **Real-time vs analysis.** Real-time alerts on latency/cost are cheap. Deep quality analysis needs batch evaluation and human review. Don’t force both into one pipeline.
* **Centralized control vs team autonomy.** A single platform enforces standards, but teams want local dashboards. Provide a common ingestion schema and let teams build views on top.
* **Evaluation drift.** Automated evaluators are themselves models. If you optimize to the metric, you optimize to the evaluator. Always keep a human-labeled holdout set and monitor evaluator agreement.

Common failure: logging only the final response. You lose retrieval quality and prompt version, so you can’t explain why an answer changed.

### Example

Enterprise customer support agent with RAG over internal KB.

A ticket spikes for incorrect pricing. With AI observability you query traces where `intent=pricing` and `evaluator.fact_check < 0.5` in last 24h. You find traces where retriever returned a stale doc version `kb-v3` instead of `kb-v5`, and the prompt template `support-v2` truncates context at 2k tokens. The trace shows token cost jumped after a model upgrade to `gpt-4o-mini` with higher temperature. You roll back retriever config and pin prompt version, then alert on retrieval score <0.7 for pricing intents.

Without lineage you would be guessing between model, data, and prompt.

### Reasoning challenge

You are launching an internal code-assistant agent. Traffic is 50k requests/day, 30% contain code snippets that may be proprietary. Leadership wants full prompt capture for debugging; security wants zero code stored.

What do you capture, where, and how do you still enable root-cause analysis? What trade-off are you making?

### Key takeaway

* AI observability is lineage + evaluation for non-deterministic reasoning, not just latency and errors.
* Capture at a central gateway with structured spans for prompt, retrieval, model, tools, and evaluation.
* Sample aggressively, redact PII early, tier storage, and separate real-time signals from deep analysis.
* Use it to attribute quality and cost changes to specific data, prompt, model, or tool decisions.
