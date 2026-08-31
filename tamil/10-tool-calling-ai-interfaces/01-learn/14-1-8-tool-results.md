# Tool results

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.8 — Learn

## 1. Problem

உங்கள் AI agent ஒரு tool-ஐ call பண்ணுது. உதாரணமா `get_weather(city)` அல்லது `fetch_user_orders(user_id)`.

Call பண்ணியாச்சு. இப்போ result வந்துடுச்சு.

அந்த result-ஐ agent எப்படி பயன்படுத்தும்? அதை எப்படி புரிஞ்சுக்கும்?

Real problem இங்கே தான் start ஆகுது.

Tool result ஒரு raw JSON, list of numbers, error message, empty response, partial data. Agent-க்கு அதை context-ல correct interpretation பண்ண தெரியணும்.

இல்லைன்னா agent hallucinates பண்ணும், wrong decision எடுக்கும், அல்லது "I don't know"ன்னு சொல்லிடும்.

> What goes wrong if we don't handle tool results well?

Agent calls tool, gets data, but அதை reasoning chain-ல integrate பண்ண முடியாமல் போகுது. User-க்கு wrong answer.

## 2. Mental Model

Tool result என்பது agent-க்கு வரும் external observation.

Agent-க்கு இரண்டு விஷயங்கள் தேவை:

1. **What did the tool return?** - structured data, error, empty
2. **What does it mean for the current task?** - அந்த data task-ஐ முன்னோக்கி நகர்த்துதா? இல்லை தடுக்குதா?

Mental model: Tool call = question. Tool result = answer. Agent = reader who must verify answer-ஐ புரிஞ்சுக்கணும், trust பண்ணணும், அடுத்த step decide பண்ணணும்.

## 3. How It Works

ஒரு typical flow:

`User request -> Agent reasoning -> Tool call decision -> Tool execution -> Tool result -> Agent interprets result -> Next reasoning step`

Tool result பொதுவாக 3 வகையாக வரும்:

* **Success with data**: `{"orders": [...]}`. Agent அதை parse பண்ணி task-ல use பண்ணணும்.
* **Success with empty**: `{"orders": []}`. இது success தான், ஆனால் meaning வேற. No data found.
* **Failure/Error**: Timeout, 500, invalid params. Agent retry பண்ணுமா? Alternative tool use பண்ணுமா? User-க்கு சொல்லுமா?

அதனால் agent-க்கு result-ஐ normalize பண்ண ஒரு schema தேவை. Structured output, tool result contract.

Good practice: Tool definition-ல output schema கொடு. Agent அதை expect பண்ணும். Result வந்ததும் agent அதை validate பண்ணி, missing fields இருந்தா handle பண்ணும்.

## 4. Architectural Reasoning

Tool result handling ஏன் architectural decision ஆகும்?

Because it affects reliability, latency, and correctness.

**When this becomes useful:**
Agent multiple tools chain பண்ணும் போது. உதாரணமா search -> fetch details -> summarize.

**Constraint it addresses:**
Agent should not assume tool always succeeds and returns perfect data. Real world messy.

**Alternatives:**
1. *Naive pass-through*: Result-ஐ directly user-க்கு கொடு. Fast, but agent learning zero.
2. *Strict schema validation*: Result match schema இல்லைன்னா reject. Safe, but brittle.
3. *Graceful degradation*: Partial result-ஐ use பண்ணி best effort answer கொடு. Flexible, but risk hallucination.

Architect choose பண்ணுவது depends on risk. Financial transaction tool result-ல error handle strict ஆக வேணும். Search result-ல partial ok.

## 5. Trade-offs

**Correctness vs Latency**
Result-ஐ validate, cross-check பண்ணினால் correctness improve ஆகும், ஆனால் latency increase ஆகும். Real-time agent-க்கு trade-off.

**Strictness vs Resilience**
Schema strict ஆக இருந்தா agent predictable ஆக இருக்கும். ஆனால் tool change ஆனால் break ஆகும். Loose handling resilient, ஆனால் agent misinterpret பண்ண risk.

**Statefulness**
Tool result-ஐ conversation history-ல keep பண்ணணுமா? Long context cost increase ஆகும். ஆனால் multi-step task-க்கு தேவை.

**Failure modes:**
* Tool returns stale data. Agent outdated info use பண்ணும்.
* Tool returns partial data due to pagination. Agent incomplete conclusion எடுக்கும்.
* Tool error but agent thinks success. Silent failure.

## 6. Practical Example

Enterprise support agent.

User: "என்னோட last 3 orders status என்ன?"

Agent `fetch_user_orders(user_id)` call பண்ணுது.

Tool result வருது:

```json
{
  "orders": [
    {"id":"O123","status":"shipped","eta":"2025-08-01"},
    {"id":"O124","status":"processing","eta":null}
  ],
  "total": 5,
  "page":1,
  "page_size":2
}
```

Agent-க்கு புரியணும்: இது partial result. Total 5, but got 2. User asked last 3 orders. Agent next call பண்ணி page 2 fetch பண்ணணும் அல்லது summary give பண்ணணும்.

இங்கே tool result interpretation தான் next action-ஐ decide பண்ணுது.

If agent just says "உங்களுக்கு 2 orders இருக்கு" அது wrong.

Correct handling: Recognize pagination, fetch next page, then summarize.

## 7. Reasoning Challenge

உங்களிடம் `check_inventory(product_id)` tool இருக்கு. அது 2 வினாடிக்கு மேல் எடுத்தால் timeout ஆகும். Agent ஒரு cart checkout flow-ல இதை call பண்ணுது.

Result வருது: timeout error.

இப்போ agent என்ன பண்ணும்?

Options:
A. Directly user-க்கு "inventory check failed"ன்னு சொல்லிடு
B. Retry once with backoff
C. Assume in-stock and proceed, later reconcile

உங்கள் system constraints: checkout latency SLA 3 sec, inventory accuracy critical for oversell prevention.

நீங்கள் எந்த decision எடுப்பீர்கள்? ஏன்? Tool result handling-ல என்ன guardrail வைப்பீர்கள்?

## 8. Key Takeaways

* Tool result என்பது raw data அல்ல, agent-க்கு observation. Interpretation தான் முக்கியம்.
* Success, empty, error ஆகிய மூன்றையும் தனித்தனியாக handle பண்ணு.
* Tool result contract / schema வைத்தால் agent predictable ஆக இருக்கும்.
* Partial data, pagination, staleness போன்ற real-world issues-க்கு agent reasoning chain-ல explicit handling தேவை.
* Every tool result handling decision creates trade-off between correctness, latency, and resilience.
