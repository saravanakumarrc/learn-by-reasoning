# Hosted models

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.3.4 — Model patterns

**Hosted models**

### 1. The problem

You need LLM capabilities in production, but you don't want to own the model stack.

Training and even fine-tuning are one problem. Serving a foundation model at production quality is another: GPUs, autoscaling, model sharding, quantization, request batching, safety filters, canary rollouts, monitoring, and 24/7 ops.

The constraint is not just cost. It's people and time. A team can ship a product with an API call in days. Standing up reliable inference takes a dedicated ML platform team and weeks to months.

Hosted models exist to buy out that operational burden.

### 2. Mental model

Think rent vs own for compute + weights.

With a hosted model you rent inference capacity and a model artifact from a provider. You own the prompt, the application logic, and the data in flight. The provider owns the hardware, the serving stack, the scaling, and the model weights.

You trade control for velocity and operational simplicity.

### 3. How it works

Your app sends a request to a managed inference endpoint. The provider routes, batches, and serves on GPU infra you never see.

```mermaid
flowchart LR
    App[Your App / API Gateway] --> Req[Prompt + Context]
    Req --> Provider[Hosted Model API]
    Provider --> Infra[(Managed GPU, autoscaling, routing)]
    Infra --> Model[(Foundation Model vX)]
    Model --> Resp[Tokens + usage]
    Resp --> App
```

You get a stable contract: input schema, latency SLOs, rate limits, and model versioning. Under the hood the provider can swap hardware, patch models, and scale without you changing code.

### 4. Architectural reasoning

Hosted helps when:

* Time to value matters more than fine-grained control. MVP, internal tools, or features with variable demand.
* Load is spiky and unpredictable. You pay per token and scale to zero without provisioning clusters.
* You lack ML platform expertise. No need to manage Triton, vLLM, or custom serving.

Self-hosted or hybrid makes sense when:

* Data residency, compliance, or PII constraints forbid third-party processing.
* You need deterministic latency, cost predictability at high volume, or custom model modifications.
* You must control model versioning, safety filters, and auditability end-to-end.

Alternatives on the spectrum: fully managed API, managed endpoint for your own weights on cloud GPUs, and on-prem inference. Hosted is the first stop on that spectrum.

Decision rule: start hosted to learn the workload, then move pieces inward only when a concrete constraint forces it.

### 5. Trade-offs and failure modes

* **Vendor lock-in and API surface.** Prompts, tools, and streaming semantics differ across providers. Abstraction helps but never fully removes it.
* **Data and privacy.** Prompts leave your perimeter. Even with data processing agreements, you lose full control over retention and training use. For regulated data, this is a hard no.
* **Cost model.** Per-token pricing is great at low volume, punishing at scale. A self-hosted cluster has high fixed cost but lower marginal cost.
* **Latency and reliability.** You inherit the provider's SLOs, rate limits, and outages. Noisy neighbors and regional failures are yours to handle with retries, backoff, and fallbacks.
* **Model governance.** You cannot inspect weights, reproduce results exactly, or guarantee version pinning forever. Providers deprecate models.

Common failures: cost spikes from prompt bloat and unthrottled retries; silent model drift when a provider updates a model; leaking secrets in prompts because the boundary feels “internal”.

### 6. Example

Enterprise customer support bot.

App layer owns conversation state, retrieval from private KB, and PII redaction. LLM call is delegated to a hosted model via a thin abstraction. Traffic is bursty, team has no ML ops, and compliance requires prompts to be logged and redacted before leaving the VPC.

Architecture: App -> API Gateway -> Redaction service -> Hosted Model API -> Response -> Logging.

If support volume grows 10x, you scale the app, not GPUs. If a compliance audit demands on-prem processing for EU customers, you add a self-hosted replica for that region and route by geo.

### 7. Reasoning challenge

You are building a real-time risk scoring API for a bank. Latency p95 must be <200ms, prompts contain unredacted PII, and expected QPS is 5k sustained with 20k peaks. The product must launch in 6 weeks.

Hosted model or self-hosted? Which constraints dominate the decision, and what mitigations would you need if you choose hosted?

### 8. Key takeaway

* Hosted models buy out inference operations at the cost of control and data boundary.
* Choose hosted for speed, variable load, and lack of ML platform resources; choose self-hosted for compliance, cost at scale, and latency control.
* Abstract the provider behind a thin gateway early to preserve optionality.
* Design for provider failures: retries with backoff, rate limiting, cost guards, and prompt hygiene.
