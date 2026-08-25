# Attention — conceptual understanding

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.1.7 — Understand

### 1. The problem

Recurrent models process a sequence one token at a time. To relate token 1 and token 512 the signal must pass through 511 steps of recurrence.

That creates three architectural constraints:
* **Sequential bottleneck.** Computation cannot be parallelized across positions.
* **Vanishing signal.** Gradients decay over long distances, so distant dependencies are hard to learn.
* **Fixed capacity.** Hidden state is a single vector that must compress the entire past.

For language, code, and multimodal data, meaning depends on long-range relationships: a pronoun refers to a noun 200 tokens earlier, a function definition constrains a call much later. You need a mechanism that can directly access any prior position without walking the whole chain.

### 2. Mental model

Attention is content-addressable retrieval over a sequence.

Instead of a compressed summary, keep the whole sequence in memory as values. For each position, form a query. Compare the query to keys from all positions. The comparison yields a relevance weight. Use those weights to form a weighted sum of values.

Analogy: reading a document with a highlighter. You don't re-read from the start for each new sentence. You scan the whole document once, and for each new query you instantly find the most relevant passages.

### 3. How it works

Scaled dot-product self-attention on one head:

`Attention(Q,K,V) = softmax( Q K^T / sqrt(d_k) ) V`

* Q, K, V are linear projections of the same input embeddings.
* `Q K^T` is a similarity score between every pair of positions.
* Softmax turns scores into a probability distribution over the sequence.
* The distribution weights the values.

Multi-head attention runs several such mechanisms in parallel with different projections, allowing the model to attend to different types of relationships: syntax, coreference, position, etc.

The result is permutation-agnostic by itself, so positional encodings are added to give order information.

```mermaid
flowchart LR
    X[Input sequence] --> Proj[Linear Proj]
    Proj --> Q[Query]
    Proj --> K[Key]
    Proj --> V[Value]
    Q --> Score[Q·K^T / sqrt(d)]
    K --> Score
    Score --> Softmax[Softmax weights]
    Softmax --> Weighted[Weighted sum of V]
    V --> Weighted
    Weighted --> Out[Contextual output]
```

### 4. Architectural reasoning

**When it helps**
* Long-range dependencies matter more than local patterns.
* You need parallel training and fast GPU utilization.
* You want the model to learn what to attend to, not hand-craft receptive fields.

**Alternatives**
* RNN/LSTM: O(n) sequential, O(1) memory per step, struggles beyond ~200 tokens.
* CNN with dilated kernels: parallel, local, needs deep stacks for long range.
* Attention: O(n²) compute and memory, but direct access to any position.

The decision is a trade-off between expressiveness and cost. Attention won for LLMs because training throughput and long-context modeling outweighed the quadratic cost at typical sequence lengths, and hardware favored large matrix multiplies.

In transformers attention is used twice:
* **Self-attention:** the model attends to itself within a sequence.
* **Cross-attention:** decoder attends to encoder representations, enabling conditional generation in translation, RAG, and vision-language models.

### 5. Trade-offs and failure modes

* **Quadratic cost.** Time and memory grow ~n² with sequence length. A 32k context needs ~1B pairwise scores. This drives sparse, sliding-window, and linear attention variants for long contexts.
* **No built-in recurrence.** Attention has no state; it cannot naturally stream. You must re-compute over the full window or cache KV pairs. Cache blow-up is a real ops problem.
* **Positional blindness.** Without strong positional encodings, order is lost. Rotating embeddings and relative position biases are architectural choices with real accuracy impact.
* **Attention is not reasoning.** High attention weights correlate with relevance but do not guarantee causal correctness. Over-reliance on attention maps for interpretability is a common failure.

### 6. Example

RAG retrieval-augmented generation.

User query is embedded. Top-k documents are retrieved. The LLM decoder uses cross-attention to attend over the concatenated retrieved chunks while generating the answer.

Self-attention lets the model fuse information across documents, resolve contradictions, and cite specific passages without scanning sequentially. The architectural choice is justified because the relevant fact may be in chunk 7 of 10, and the model needs direct access rather than a compressed summary.

### 7. Reasoning challenge

You are designing a real-time speech-to-text system with a 10 second latency budget and a 30 second sliding context window. Full self-attention over 30s ~ 30k frames is infeasible.

Would you use full attention, sliding-window attention, or a recurrent state with attention? What do you lose and gain with each choice?

### 8. Key takeaway

* Attention solves the sequential bottleneck by enabling direct, content-based access to any prior position.
* It trades O(n²) compute/memory for parallelizable training and long-range expressiveness.
* Architectural choice depends on sequence length, latency, and hardware: full attention for training and offline, sparse/streaming variants for long or real-time contexts.
* Attention is a retrieval primitive, not a reasoning guarantee; design around its costs and failure modes.
