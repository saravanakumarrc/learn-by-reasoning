# Hallucination

> **Learning Path:** RAG Architecture
> **Section:** 8.3.8 — RAG failure modes

**Hallucination in RAG: Why retrieval does not equal truth**

### 1. The problem

You add retrieval to an LLM to ground answers in your own data. The user asks a factual question, the system retrieves relevant documents, and the model generates a confident answer.

The problem: the answer can still be false, and the model will be confident about it.

RAG reduces hallucination, it does not eliminate it. The model is a next-token predictor trained to be fluent and coherent, not to be faithful to a specific source. When the retrieved context is incomplete, ambiguous, or contradictory, the model fills the gaps with parametric knowledge and hallucinates.

This matters architecturally because users trust RAG systems as authoritative. A plausible false statement in a support bot, contract summarizer, or medical assistant is worse than no answer.

### 2. Mental model

Think of the LLM as a skilled writer with a library access pass.

Retrieval gives the writer a few books. The writer can:
* Quote correctly
* Paraphrase correctly
* Misread a passage
* Combine two passages that were never meant together
* Ignore the books and write from memory when the books are unhelpful

Hallucination is the writer making up a citation, a detail, or a logical link that is not in the books, while still sounding correct.

### 3. How it works in RAG

```mermaid
flowchart LR
    Q[User Query] --> R[Retriever]
    R --> D[Top-k Chunks]
    D --> LLM[LLM + Context]
    LLM --> A[Answer]
    D -. incomplete/ambiguous .-> LLM
    LLM -. parametric memory .-> A
```

Failure points:
* **Retrieval gap:** The right information is not retrieved, or is retrieved but truncated. The model hallucinates to complete the answer.
* **Context overload:** Too many chunks, noisy chunks, or conflicting chunks. The model attends to the wrong part.
* **Reasoning over generation:** The model needs to infer a conclusion not explicitly stated. It generates a plausible bridge that is not grounded.
* **Instruction following drift:** The model prioritizes fluency and user satisfaction over strict grounding.

These are not bugs. They are the expected behavior of a system built from a generative model + retrieval.

### 4. Architectural reasoning

You use RAG to trade parametric knowledge for controllable knowledge.

When it helps: domain-specific facts, up-to-date data, proprietary documents, compliance requirements.

Alternatives:
* Pure parametric LLM: cheaper, faster, but ungrounded and stale.
* RAG with strict grounding: slower, more complex, but auditable.
* Retrieval + verification pipeline: generate then verify against source.

The decision is not "add RAG and be safe". The decision is how much faithfulness you need and what cost you will pay for it.

### 5. Trade-offs and failure modes

* **Faithfulness vs coverage.** Tight prompts like "only use provided context" reduce hallucination but increase refusals and incomplete answers. Loose prompts improve coverage but increase hallucination.
* **Latency vs verification.** Adding a second pass to check citations or use a smaller verifier model improves safety, adds latency and cost.
* **Chunking strategy.** Smaller chunks improve precision but lose context. Larger chunks preserve context but introduce noise. Both increase hallucination risk.
* **Retrieval quality is the bottleneck.** A hallucination rate of 5% with perfect retrieval can become 30% with bad retrieval. The model cannot ground what it never saw.

Key failure mode to remember: *confident fabrication*. The model will not signal uncertainty unless you explicitly design for it.

### 6. Example

Enterprise support RAG for an SaaS product.

Query: "How do I enable SSO for enterprise plan?"

Retriever returns a page about SSO setup and a page about enterprise billing.

The model hallucinates: "Enable SSO in Billing > Enterprise Settings > SSO toggle". That UI path does not exist. The billing page mentions a toggle for invoicing, not SSO.

The answer is plausible, internally consistent, and cites no source. The user follows it, fails, and loses trust.

Architectural fix is not better prompting alone. It is retrieval quality + grounding enforcement: return chunk IDs, force citation, and reject answers where claims cannot be mapped to a chunk.

### 7. Reasoning challenge

You are designing a RAG system for legal contract clause extraction. The requirement is high precision, low hallucination, but queries are long and retrieval is expensive.

Do you:
A. Use a single large context window and let the model reason over the whole contract.
B. Retrieve top-k chunks, generate with citations, and add a verifier model that checks each claim against its cited chunk.

What do you choose and what trade-off are you accepting?

### 8. Key takeaway

* Hallucination is a system property, not a model bug. It emerges from the interaction of retrieval quality, context design, and generative priors.
* RAG reduces hallucination but shifts the risk to retrieval gaps and grounding enforcement.
* Architect for verifiability: citations, claim-to-chunk mapping, and explicit uncertainty signals are more reliable than "better prompts".
* The critical trade-off is faithfulness vs completeness vs latency/cost. Choose consciously per use case.
