# Output constraints

> **Learning Path:** LLM Application Engineering
> **Section:** 7.1.8 — Prompt engineering

### 7.1.8 — Prompt Engineering

**The problem**
LLMs are not deterministic functions. Same intent expressed differently yields different outputs, and the model has no built-in contract for your domain logic. You need reliable, repeatable behavior from a system whose inputs are natural language and whose outputs are sampled from a distribution.

For an architect this is an interface problem. You are designing an API boundary where the protocol is text, the runtime is non-deterministic, and failure modes are subtle: hallucination, instruction drift, prompt leakage, and cost blow-up from token use.

Prompt engineering is the discipline of shaping that interface to make the model reliably do a bounded task under operational constraints.

**Mental model**
Think of a prompt as a runtime specification for an untrusted worker. You cannot change its code, you can only change the context it sees at inference time.

The core levers are:
* **Instruction** - what to do and what constraints to obey
* **Context** - data the model must use, not hallucinate
* **Format** - how the output must be structured so you can parse it reliably
* **Examples** - showing the desired input-output mapping

A good prompt is not clever wording. It is a minimal specification that reduces ambiguity and makes the desired behavior the highest probability completion.

```mermaid
flowchart LR
    User[Business Intent] --> Template[Prompt Template + Variables]
    Template --> LLM[LLM with System/User Roles]
    LLM --> Output[Structured Output]
    Output --> Validator[Schema / Guardrail]
    Validator -->|Pass| Use
    Validator -->|Fail| Retry/ Fallback
```

**How it works**
The model conditions on the entire prompt in its context window. System role sets stable persona and rules. User role carries task + data. The prompt template is code; the variables are data.

Essential patterns, used sparingly:
* **Clear role + objective.** One task per call. "You are a classifier. Classify the ticket into one of..."
* **Output contract.** Force a machine-readable schema: JSON with fixed keys, enum values. This moves validation left.
* **Few-shot.** 1-3 examples anchor format and style. More examples cost tokens and can dilute the instruction.
* **Delimiters and separation.** Explicitly separate instruction from data with XML tags or markdown to avoid the model mixing them.
* **Self-consistency.** Ask for reasoning then final answer, or require the model to check its own output against constraints.

Prompt engineering is iterative: hypothesize failure, add a constraint, measure.

**Architectural reasoning**
Use prompt engineering when you need behavior change without retraining, with low latency, and with a task that fits in context.

Choose it over fine-tuning when:
* Requirements change weekly
* You need per-tenant customization
* Data is sensitive and cannot leave your environment for training

Choose it with RAG when the task needs current or private knowledge. Prompt + retrieval = grounded generation. The prompt controls how retrieved chunks are used.

Choose tool use / function calling when the task requires reliable external actions. Prompts steer; tools execute.

The architectural decision is where to place control: in the prompt, in retrieval, in validation, or in fine-tuning. Most production systems use all four, with prompts as the first line of control.

**Trade-offs and failure modes**
* **Brittleness.** Small wording changes change results. Prompts need tests like code.
* **Token cost and latency.** Longer prompts = higher cost and latency. Few-shot and chain-of-thought increase both.
* **Leakage.** Putting secrets or internal policy in prompts risks exposure in logs and model outputs. Treat prompts as untrusted surface.
* **Distribution shift.** Prompts degrade as data drifts. No compiler catches it. You need evals and monitoring.
* **False confidence.** Structured output looks correct but can be hallucinated. Always validate schema and business rules downstream.

**Example**
Enterprise support triage. Inbound tickets must be classified, prioritized, and routed.

Bad: "Read this ticket and tell me what to do."
Good architecture:
* System prompt defines role, allowed categories, priority rules, and JSON schema.
* User prompt injects ticket text + recent KB summary from RAG.
* Output schema: `{category: enum, priority: 1-3, reason: string, needs_human: bool}`
* Validator rejects outputs with invalid enums or missing fields; retries once with error feedback.

The prompt is versioned in Git, tested against a golden set, and A/B tested in production. Cost is capped by max tokens and input truncation.

**Reasoning challenge**
Your compliance policy changes monthly and is 2,000 words long. You can fit it in context but it adds 800 tokens per request. Do you embed the full policy in the system prompt, retrieve only relevant sections via RAG, or fine-tune a model on the policy?

What failure mode worries you most and how would you measure it?

**Key takeaway**
* Prompts are interface contracts, not magic words. Design them for reliability, not eloquence.
* Control output with explicit schema and validation; never trust raw text.
* Prompt engineering trades flexibility for brittleness. Pair it with retrieval, tools, and guardrails for production.
* Treat prompts as code: version, test, monitor, and limit blast radius.
