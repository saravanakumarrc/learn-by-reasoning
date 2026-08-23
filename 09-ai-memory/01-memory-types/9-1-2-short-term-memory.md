# Short-term memory

> **Learning Path:** AI Memory
> **Section:** 9.1.2 — Memory types

### 1. The problem

An LLM has no memory between calls. Each request is stateless.

For a multi-turn task you need continuity: what the user just said, what tools were called, what the intermediate result was, what the user’s intent is *right now*.

If you only keep the current prompt, the model forgets the conversation. If you keep everything, you hit a hard limit: context window size, cost per token, and latency.

Short-term memory exists to give the model a working scratchpad for the current session without paying the cost and latency of full long-term retrieval every turn.

### 2. Mental model

Think RAM vs Disk.

**Short-term memory = RAM for the session.** Fast, ephemeral, bounded, in-process.
**Long-term memory = Disk.** Persistent, large, retrieved on demand.

Short-term holds: recent user messages, assistant replies, current task state, tool outputs from this turn chain, and a small summary of the session so far.

It is discarded when the session ends. It is not ground truth.

### 3. How it works

At a minimum it is the rolling conversation context you feed back into the model.

```
User -> Session Store -> Context Builder -> LLM
                ^                    |
                |--- tool outputs --|
```

The context builder assembles a working window:
* Session ID scoped buffer
* Last N messages or last N tokens
* Current turn state: active tool, pending clarification, etc.
* Optional short summary of earlier part of session to avoid pure truncation

Implementation is usually:
* In-memory cache / Redis for active sessions
* Sliding window with eviction policy
* Summarization/compression to keep important facts while dropping verbatim history

It is not retrieval from a vector DB. It is direct recall from the current working set.

### 4. Architectural reasoning

Use short-term memory when you need:

* **Coherence across turns.** The model must reference what was said 2 minutes ago without re-searching.
* **Low latency state.** Tool chaining within one request needs the prior tool result immediately.
* **Session continuity.** A user says “change that” and you need to know what “that” refers to.

Do not use it for:
* Facts that must survive session end
* Rarely accessed knowledge
* Cross-user personalization at scale

Alternatives:
* **Stateless + full retrieval each turn:** Accurate but expensive and slow. You retrieve everything relevant from long-term store each time.
* **Summarize aggressively:** Cheaper but loses nuance.
* **Pure context window:** Simple, but hits token limits and cost grows with conversation length.

Decision rule: keep what the model needs *now* in short-term, archive what it may need *later* in long-term.

### 5. Trade-offs and failure modes

**Bounded vs complete.** A fixed window guarantees latency and cost, but causes information loss. Larger window = better fidelity, higher cost.

**Recency bias.** The model overweights recent messages. Important facts from early in session get drowned out unless you compress/summarize.

**Context pollution.** Tool outputs, system prompts, and history compete for limited tokens. Noise reduces reasoning quality.

**Session bleed / leakage.** If session store is shared or not properly isolated, user A sees hints of user B’s context.

**Drift.** Without summarization, repeated re-injection of old text causes the model to hallucinate or contradict itself.

**Cost cliff.** Cost is linear with tokens in and out. Long sessions become expensive fast.

### 6. Example

Customer support agent for order changes.

Short-term memory holds:
* Session ID + user ID
* Current order ID from turn 3
* Last 4 messages
* Last tool output: `get_order_status`

Long-term memory holds:
* Product catalog, refund policy, user profile

Flow:
User: “Cancel my order”
Agent uses short-term to know which order. No vector search needed.
User: “Actually just change the address”
Short-term still contains order ID and prior intent. The model doesn’t need to re-retrieve.

When session ends, only a summary “User cancelled order #1234” is written to long-term.

### 7. Reasoning challenge

You have a 30 minute sales call transcribed into the LLM context. 12k tokens.

Options:
A. Keep full transcript in short-term memory for the whole session
B. Keep last 2k tokens + a 500 token summary of the earlier part
C. Drop transcript to long-term vector DB and retrieve only when needed

Which do you choose and what breaks if you choose wrong?

### 8. Key takeaway

* Short-term memory is session-scoped working RAM, not permanent knowledge.
* It solves the problem of continuity and low-latency state within a conversation, bounded by context window and cost.
* Keep only what is needed for the current reasoning step; archive the rest.
* Design for eviction, summarization, and session isolation, or you will get drift, cost blow-up, and leakage.
