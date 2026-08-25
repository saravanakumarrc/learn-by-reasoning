# Input vs output tokens

> **Learning Path:** AI Cost Architecture
> **Section:** 16.1.2 — Learn to reason about

### The problem

You ship an AI feature. First month usage is fine. Month two, traffic 3x and the LLM bill is 10x. Why?

Because you priced the feature on requests, but the provider prices on tokens. And token cost is not symmetric. Input tokens are cheap to process; output tokens are expensive to generate.

The problem is cost predictability and control. An architect needs to reason about where tokens are spent, not just how many calls you make. A single long prompt can be cheap, a single short answer can be expensive.

### Mental model

Think of a model as a reader and writer.

**Input tokens = reading.** The model ingests your prompt, context, system instructions, tools, retrieved docs. Reading is parallelizable and cheap.

**Output tokens = writing.** The model generates token by token, autoregressively, with sampling and verification. Writing is sequential and compute-intensive.

Pricing reflects that: input is typically $0.10-$1 per 1M tokens, output is $0.40-$10 per 1M tokens, often 3-10x higher. Some models also charge more for output with reasoning.

```
User --> Prompt[Input tokens: cheap to read] --> Model
Model --> Response[Output tokens: expensive to write] --> User
```

Cost = `input_tokens * input_price + output_tokens * output_price`. Output dominates.

### How it works

Tokenization converts text to model-specific units. ~4 chars ≈ 1 token for English. Pricing is per token, not per character.

The asymmetry comes from architecture: input is processed once in parallel via attention over the whole context. Output is generated step by step, each new token attends to all previous tokens, so cost grows quadratically with output length.

Two modifiers matter for architects:
* **Context window cost.** Longer input = more KV-cache memory and compute per output token. You pay input once, but you pay for it on every generated token.
* **Caching.** Many providers cache repeated input prefixes. A cached hit can drop input cost by ~90%. That changes the economics of system prompts and RAG chunks.

### Architectural reasoning

Input vs output pricing creates design pressure.

**When it helps to think about it:**
* High-volume chat, summarization, code generation. Output length varies wildly with user input.
* RAG systems where you retrieve long documents. You can spend a lot on input to save a little on output, or vice versa.

**Design levers:**
* **Shrink output, not just input.** Ask for structured output, concise answers, or a summary instead of full prose. Output tokens are the lever.
* **Move work out of the model.** Use tools, function calling, retrieval to provide facts instead of making the model hallucinate long explanations. Cheaper output = shorter output.
* **Control input bloat.** System prompts, few-shot examples, and retrieved chunks are input tokens. Reuse them via caching. Chunk retrieval carefully: send relevant passages, not the whole corpus.
* **Tier prompts by intent.** Simple classification = tiny output. Complex reasoning = allow longer output but gate it behind user tier.

Alternatives: smaller models for first pass, then larger model only when needed. Streaming to allow early termination. Prompt compression.

### Trade-offs and failure modes

* **Cost vs quality.** Shorter outputs save money but may reduce completeness. The optimal length is not minimal, it's the point where marginal value < marginal token cost.
* **Input bloat hides cost.** A 32k context RAG prompt feels fine in dev, but each query costs input tokens for all retrieved docs *plus* output tokens. At scale, input dominates.
* **Latency coupling.** Output tokens = latency. Cutting output saves both cost and latency.
* **Cache invalidation.** Caching helps only if prefixes are stable. Dynamic user data in the prompt kills cache hit rate.
* **Token estimation drift.** Different models tokenize differently. Counting characters is a rough estimate. Budgeting without measurement drifts.

Failure mode: designing a summarizer that asks the model to return the full document plus a summary. You pay input for the doc and output for the doc again.

### Example

Enterprise support bot.

Bad design: Send full ticket history + all previous chat + 5 page KB article per turn. Prompt = 8k input tokens. Output = 600 tokens verbose answer. Cost per turn ~ $0.008 input + $0.012 output.

Better design: System prompt cached. Retrieve top 2 relevant KB chunks ~ 800 tokens. Summarize ticket history to 200 tokens. Prompt = 1k input. Output = 200 tokens concise answer with citations. Cost per turn ~ $0.001 input + $0.004 output.

Same user experience, ~60% cost reduction, faster latency. The win came from shrinking both input and especially output.

### Reasoning challenge

You have a daily report generator. Users paste ~10k tokens of raw logs and ask for analysis. Output is currently ~2k tokens per report, 5k reports/day.

Option A: Keep model, add instruction "be concise, max 400 tokens".
Option B: Pre-process logs with a cheap model to extract key events, send ~1k tokens to main model.
Option C: Move to a cheaper model for all reports.

Which do you choose and what metric do you monitor to know if it worked?

### Key takeaway

* Output tokens drive cost, not request count. Design for output first.
* Input is cheap to read but expensive to carry through generation. Long context increases per-output-token cost.
* Caching stable prefixes and trimming retrieved context are high-leverage cost controls.
* Measure tokens per user intent, not just tokens per request. Budget by output length distribution.

You should be able to reason: *If I change this prompt or architecture, how does input and output token count change, and what is the cost impact at scale?*
