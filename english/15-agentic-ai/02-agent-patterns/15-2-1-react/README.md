# ReAct

> **Learning Path:** Agentic AI
> **Section:** 11.2.1 — Agent patterns

**ReAct**

### The problem

A language model is a closed world. It has static knowledge, no reliable way to know what it doesn't know, and no way to execute actions in the real world.

Chain-of-Thought helps the model reason internally, but it stays internal. The model can still hallucinate facts, invent tool outputs, or call a tool with the wrong arguments because there is no feedback loop.

Pure tool use with a single function call is brittle. The model has to get everything right on the first try: identify the needed information, choose the correct tool, format arguments correctly. In practice it mis-routes, over-calls, or assumes data it hasn't retrieved.

You need a pattern where reasoning and action are interleaved so the model can test a hypothesis, observe the result, and revise.

### Mental model

ReAct = **Reasoning and Acting**.

The agent thinks out loud, decides on one action, executes it, reads the observation, and thinks again. It is a tight loop: Thought → Action → Observation → Thought.

Analogy: a junior analyst with access to a database and APIs. You don't give them the full plan up front. You let them state what they believe, ask for one piece of data, read it, and adjust their reasoning.

### How it works

The model generates a reasoning trace, then emits a structured action. The environment returns an observation, which is fed back as context.

```
flowchart LR
    LLM[LLM] --> Thought[Thought: What do I know? What do I need?]
    Thought --> Action[Action: call_tool(args)]
    Action --> Tool[Tool / Environment]
    Tool --> Obs[Observation: result]
    Obs --> LLM
```

The loop repeats until the model emits a final answer. The reasoning trace is not just for show; it conditions the next action. The observation grounds the next thought, reducing hallucination.

This is typically implemented with a system prompt that enforces the format, a parser for Action blocks, and a router that maps actions to real tools. No new model training is required.

### Architectural reasoning

Use ReAct when you need grounded, multi-step problem solving with tools, and the correct tool sequence is not known in advance.

It helps when:
* The task requires retrieval, computation, or external state: order lookup, live pricing, code execution, web search
* The information needed depends on previous results: you need an ID before you can fetch details
* You want interpretability: the Thought trace shows why an action was taken

Alternatives:
* **Plan-then-Act**: generate a full plan first, then execute. Faster and cheaper, but brittle if the plan is wrong or the environment changes.
* **Pure CoT + RAG**: good for knowledge questions, no actions.
* **Tool calling with fixed schema**: good for single-step, well-defined tasks.

Choose ReAct when the cost of a wrong action is high and the task has branching dependencies.

### Trade-offs and failure modes

* **Latency and cost**: each loop is a model call + tool call. Token usage grows with reasoning verbosity. You pay for thinking.
* **Loop stability**: the model can loop, repeat actions, or drift in reasoning. You need max steps, action deduplication, and a stop condition.
* **Reasoning quality vs control**: verbose thoughts improve accuracy but increase prompt size and can leak into outputs. You may need to separate internal chain from final answer.
* **Observation overload**: returning too much raw tool output drowns the context window. Summarize or filter observations.
* **Action hallucination**: the model invents tools or arguments. Strict parsing and a whitelist of allowed actions are required.

### Example

Customer support agent: "Can I get a refund for order 48291?"

1. Thought: I need order status and refund policy for this order.
2. Action: get_order_status(order_id=48291)
3. Observation: status=delivered, delivered_date=2025-10-01, refund_window=30 days
4. Thought: Delivered within window, refund allowed. Need customer ID to process.
5. Action: get_customer(order_id=48291)
6. Observation: customer_id= C9921, tier=gold
7. Thought: Gold tier gets expedited refund. I can now answer.

Without the loop the model would likely hallucinate status or assume policy.

### Reasoning challenge

You are building an agent that books travel. It can call `search_flights`, `check_visa_requirements`, and `book_ticket`. A user asks: "Book me the cheapest flight to Tokyo next week, but I need a visa."

Do you want ReAct here, or a single plan-then-act? What guardrails would you add to prevent the agent from booking before checking visa eligibility?

### Key takeaway

* ReAct interleaves explicit reasoning with grounded actions to reduce hallucination and enable tool use.
* It trades latency and cost for correctness in multi-step, information-dependent tasks.
* Control the loop with max steps, allowed actions, and filtered observations.
* Choose it over plan-then-act when the task has unknown dependencies and feedback matters.
