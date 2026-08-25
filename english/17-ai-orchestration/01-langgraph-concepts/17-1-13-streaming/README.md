# Streaming

> **Learning Path:** AI Orchestration
> **Section:** 13.1.13 — LangGraph concepts

**Streaming in LangGraph**

### 1. The problem

LLM calls are long and opaque. An agent may run multiple steps: retrieve, think, call a tool, generate. If you wait for the final output, the user sees nothing for seconds, you can't show progress, and failures are discovered late.

In AI Orchestration the constraint is not just latency, it's *visibility*. You need to surface partial results to the user, log intermediate agent decisions, and allow cancellation when a step goes wrong.

### 2. Mental model

Streaming is incremental delivery of work-in-progress instead of a single final response.

Think of a pipeline where the graph emits events as they happen. The client consumes a stream of those events and assembles the final answer on the fly. The graph keeps running, the client stays responsive.

```mermaid
flowchart LR
    User -->|stream()| Graph
    Graph -->|step start| Client
    Graph -->|LLM token| Client
    Graph -->|tool call| Client
    Graph -->|step complete| Client
    Client -->|render incrementally| User
```

### 3. How it works

LangGraph exposes streaming via `graph.stream()` which returns an async generator. The graph is executed node by node, and each mode decides what is emitted.

The essential modes:
* **values** - whole graph state after each step. Good for UI that needs consistent snapshots.
* **tokens** - raw LLM tokens as they arrive. Lowest latency for typing effect.
* **events** - fine-grained events per node/tool. Good for observability and debugging.
* **debug** - full trace.

Under the hood the graph is still deterministic. Streaming does not change execution, only what you surface and when. You can also stream updates from a single branch with `stream_mode` and control backpressure by how fast the client consumes.

A minimal pattern:

```python
for chunk in graph.stream(input, stream_mode="tokens"):
    # chunk arrives per token or per step depending on mode
    send_to_client(chunk)
```

### 4. Architectural reasoning

Use streaming when:

* **User perceived latency matters.** Token streaming makes a 4s generation feel interactive immediately.
* **Long-running agents.** Multi-step workflows with tools need progress signals so the user does not abandon.
* **Observability is required.** Operators need to see which node is running, which tool was called, and where it stalled.
* **Cancellation / early exit.** If the user stops the request, you can stop consuming the generator and abort downstream work.

Don't use streaming when you need a fully validated, atomic result before any external effect. Streaming is for delivery, not for transactional safety.

Alternatives: polling the final state, WebSocket push from a separate worker, or returning the full result once. Streaming wins on latency and coupling, loses on simplicity.

### 5. Trade-offs and failure modes

* **Complexity vs latency.** Streaming adds client assembly logic. You must handle partial, out-of-order chunks and reassembly. Simple request-response is easier to reason about.
* **State consistency.** With `values` mode you get consistent snapshots. With `tokens` you get fragments with no guarantees about downstream state. Mixing modes in one pipeline creates confusion.
* **Backpressure and disconnects.** Slow clients can cause memory buildup in the generator. Unwatched streams can leak LLM connections. Always bound stream lifetime and handle client disconnect.
* **Observability cost.** Fine-grained events are great for debugging but noisy in production. Log volume and cost grow with granularity.

Failure modes to design for: client disconnect mid-stream, token buffering causing UI jitter, tool calls interleaving with token streams leading to confusing ordering, and replaying a stream without idempotency.

### 6. Example

Customer support agent: classify intent -> retrieve KB -> call billing tool -> generate answer.

Without streaming: user waits 6s, sees spinner, then answer appears.

With streaming: first tokens appear in ~300ms while retrieval runs in parallel. When the billing tool is invoked, the UI shows `Checking account...`. The user can see progress and cancel if it stalls.

The architect chooses `stream_mode="values"` for the UI state machine and `stream_mode="tokens"` for the final answer renderer, using two subscriptions to the same run.

### 7. Reasoning challenge

You are building a financial advisory agent that must call a risk check tool before generating any advice. The tool is synchronous and may take 2-3 seconds. Should you stream LLM tokens before the tool completes, or block until the tool result is in state?

Think about user trust, regulatory safety, and what the user would see if you stream speculative text that later gets invalidated by the tool.

### 8. Key takeaway

* Streaming exists to reduce perceived latency and expose agent progress, not to make the graph faster.
* Choose the stream mode by what the consumer needs: tokens for UX, values for state, events for observability.
* Streaming trades simplicity for interactivity; design for backpressure, partial results, and clean cancellation.
* Always separate *what* is streamed from *when* the graph commits state changes.
