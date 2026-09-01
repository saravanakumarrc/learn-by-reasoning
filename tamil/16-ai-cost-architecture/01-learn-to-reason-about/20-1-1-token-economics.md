# Token economics

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.1 — Learn to reason about

## 1. Problem

உங்கள் AI product production-ல launch ஆனது. First week-ல cost $200. Second week-ல $4,000. Traffic double ஆகல. User prompts length increase ஆயிடுச்சு.

என்ன நடந்தது?

LLM call-க்கு நீங்கள் pay பண்ணுவது tokens-க்கு. Input tokens, output tokens, caching, reasoning tokens எல்லாம் வெவ்வேறு price. ஒரு user ஒரு simple query-க்கு 500 tokens input கொடுத்து 800 tokens output வாங்குறார். ஆனால் அடுத்த user அதே query-ஐ context-உடன் 4,000 tokens input-ல் அனுப்புறார்.

Token economics இல்லாமல் architect பண்ணினால், latency improve ஆகும். Cost explode ஆகும். Rate limit-ல் hit ஆகும். Budget predict பண்ண முடியாது.

**What goes wrong if we don't have this?** Cost unpredictable, margin கரைகிறது, scaling impossible.

## 2. Mental Model

Token = LLM-க்கு unit of work.

ஒரு distributed system-ல் CPU cycles, network bytes மாதிரி. ஆனால் token cost nonlinear.

Key idea: **Cost = f(input tokens, output tokens, model tier, caching hit, latency budget)**

நீங்கள் architect ஆக design பண்ணும்போது, tokens-ஐ resource மாதிரி treat பண்ணணும். Database query cost, bandwidth cost மாதிரி.

Mental model: Every user request has a token budget. Every service has a token budget per minute.

## 3. How It Works

LLM provider pricing generally:

* Input tokens cheaper than output tokens
* Cached input tokens cheaper than fresh input
* Reasoning models: input cheaper, output expensive
* Longer context window = more tokens per request

ஒரு request flow:

User prompt → tokenizer → input tokens → LLM inference → output tokens → response

Architectural levers உங்களுக்கு:

* Prompt length control
* Context window trimming
* Summarization before sending
* Cache hits via prompt caching / semantic cache
* Model routing: cheap model for simple query, expensive for complex
* Output length control via max_tokens, stop sequences
* Batching and streaming

## 4. Architectural Reasoning

Token economics useful ஆகும்போது:

* High QPS, high concurrency API
* RAG pipeline-ல் retrieval results-ஐ context-ல் stuff பண்ணும்போது
* Agent workflows-ல் multiple LLM calls chain ஆகும்போது
* Chat product-ல் conversation history grow ஆகும்போது

Constraint it addresses: cost, latency, throughput

Alternatives:

* Always use cheapest model → quality drop
* Always use best model → cost blow up
* No context management → token waste

Architect choose பண்ணும்போது:

Latency sensitive path-ல் small context + fast model
Cost sensitive bulk job-ல் cheap model + batch
Quality critical path-ல் larger context + reasoning model

## 5. Trade-offs

**Input tokens vs Output tokens**
Input increase செய்வது cheap ஆக தோன்றும். ஆனால் larger context = slower inference, higher input cost, and often more output tokens. Trade-off: completeness vs cost.

**Caching vs Freshness**
Prompt caching cost குறைக்கும். ஆனால் cache invalidation logic, stale context risk. Trade-off: cost vs correctness.

**Model quality vs Token price**
Bigger model = better output, but 5-10x price. Routing logic add complexity. Trade-off: user experience vs margin.

**Context window utilization vs Token waste**
RAG-ல் top-k documents அனுப்புவது easy. ஆனால் irrelevant chunks tokens waste. Need reranking, compression. Trade-off: recall vs token budget.

Failure modes: Token exhaustion leads to 429 errors. Unbounded conversation history leads to cost spike. Retry without idempotency leads to double cost.

## 6. Practical Example

Enterprise support chatbot with RAG.

User query: "Last month invoice status"

Naive design: Fetch last 20 conversations + last 10 invoices + full KB = 12k input tokens per request. Model gpt-4o output ~400 tokens. Cost per request ~ $0.02. 1M requests/month = $20k.

Architected design:

1. Conversation history summarize to 800 tokens
2. Retrieve top 3 relevant invoices only, not 10
3. Use prompt caching for system prompt
4. Route simple FAQ to small model, complex to large model
5. Cap output to 250 tokens

Now input ~2.5k tokens, cost per request ~ $0.004. 1M requests = $4k. 5x saving.

Same user experience, different token economics.

## 7. Reasoning Challenge

உங்களிடம் RAG agent இருக்கு. ஒரு user request-க்கு 3 tool calls ஆகும். ஒவ்வொரு tool output-ஐயும் context-ல் சேர்த்து next LLM call-க்கு அனுப்புறீங்க.

Traffic 10x grow ஆகிறது. Cost 15x grow ஆகிறது. ஏன்?

நீங்கள் என்ன metrics track பண்ணுவீங்க, என்ன architectural change பண்ணுவீங்க? Token budget per request, per user, per session எப்படி set பண்ணுவீங்க?

## 8. Key Takeaways

* Tokens are a first-class resource in AI architecture, like CPU and bandwidth
* Cost driven by input length, output length, model tier, and cache hit rate
* Control tokens via context trimming, summarization, routing, and caching
* Every architectural decision creates a new trade-off between quality, latency, and cost
