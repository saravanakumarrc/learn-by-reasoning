# Top-p

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.1.11 — Understand

**Top-p**

### 1. The problem

Generating text with an LLM is sampling from a huge distribution over the next token. You need two conflicting properties:

* **Coherence** - stay on topic, use high-probability tokens
* **Diversity** - avoid deterministic, repetitive output

Temperature scales the whole distribution, making it sharper or flatter. It does not solve the core issue: *how much of the tail should you allow?*

With greedy decoding you get repetition. With pure sampling you get garbage from the 0.0001% tail. You need a way to say "only sample from the plausible set" without fixing a hard rank limit.

### 2. Mental model

Top-p, nucleus sampling, is a dynamic vocabulary cut.

Instead of "take the top K tokens", you take the *smallest set of tokens whose cumulative probability mass reaches p*.

Think of a probability budget. You keep adding the most likely tokens until you have spent, say, 90% of the probability mass. Then you sample only inside that nucleus and renormalize.

High p = large nucleus, more tail, more creativity. Low p = small nucleus, only the obvious tokens.

### 3. How it works

1. Model outputs logits -> softmax -> probability distribution over vocab
2. Sort tokens descending by probability
3. Compute cumulative sum
4. Keep the prefix where cumulative sum <= p
5. Renormalize probabilities inside that prefix to sum to 1
6. Sample from it

```
flowchart LR
    A[Logits → probs] --> B[Sort descending]
    B --> C[Cumulative sum]
    C --> D{p ≥ p?}
    D -->|No| E[Add next token]
    E --> C
    D -->|Yes| F[Renormalize set]
    F --> G[Sample]
```

The size of the set adapts to the model confidence. When the model is sure, the nucleus may be 2 tokens. When uncertain, it may be 2000 tokens.

### 4. Architectural reasoning

Top-p solves the rank vs probability problem.

* **Top-k** uses a fixed rank cut. K=40 is too restrictive when the model is uncertain and too permissive when the model is confident.
* **Top-p** uses a probability mass cut. It automatically expands in uncertain contexts and contracts in confident ones.

When it helps:
* Production chat where you want consistent tone but not robotic repetition
* Creative tasks where you want diversity without nonsense
* Any system where quality must be stable across prompts of varying ambiguity

Alternatives:
* Temperature only: controls sharpness but not tail inclusion
* Top-k: simpler, but brittle across domains
* Typical sampling: adds entropy filter, more complex

Decision: Use top-p as the primary diversity knob for user-facing generation, and pair it with temperature for fine-tuning sharpness.

### 5. Trade-offs and failure modes

* **Diversity vs coherence.** Lower p = safer, more deterministic. Higher p = more creative, more risk of drift and hallucination.
* **Interaction with temperature.** Temperature reshapes the distribution *before* top-p cuts it. High temperature + high p = very noisy. Low temperature + low p = near greedy, can loop.
* **No quality guarantee.** Top-p controls *where* you sample, not *how good* the sample is. It cannot fix a bad prompt or a misaligned model.
* **Operability.** The same p feels different per model, per task, per language. You will need per-use-case tuning. Monitoring repetition rate and semantic drift is more useful than a single p value.

Failure mode to watch: p too low with low temperature creates a tiny nucleus that repeats the same few tokens. p too high with high temperature pulls in low-probability tail tokens that are syntactically valid but semantically wrong.

### 6. Example

Enterprise support assistant vs brainstorming tool.

Support assistant: p = 0.85-0.92, temperature = 0.6-0.8. Small nucleus keeps answers on policy and factual, reduces hallucinated steps.

Brainstorming tool: p = 0.95-0.98, temperature = 0.9-1.1. Larger nucleus allows unusual combinations while still discarding the long tail of gibberish.

Same model, different sampling policy = different product behavior. This is an architectural choice, not a model change.

### 7. Reasoning challenge

You are shipping a summarization API for internal documents. Users complain summaries are either too generic or occasionally hallucinate facts.

Current config: temperature 1.0, top-p 0.99.

What do you change first and why? What metric would you track to validate the change?

### 8. Key takeaway

* Top-p is a probability mass budget, not a rank limit. It dynamically sizes the sampling set.
* Use it to control diversity while keeping the tail out. Temperature controls sharpness, top-p controls breadth.
* Lower p for safety and consistency, higher p for creativity. Tune per use case, not globally.
* The real architectural decision is pairing sampling parameters with task risk: factual tasks need small nucleus, open-ended tasks need larger nucleus.

You should be able to reason: *given a quality vs diversity requirement and a failure cost, what nucleus size and temperature give the right operating point?*
