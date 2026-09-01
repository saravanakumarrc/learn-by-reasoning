# Nodes

> **Learning Path:** AI Orchestration
> **Section:** 17.1.2 — LangGraph concepts

## 1. Problem

உங்களுக்கு ஒரு AI agent build பண்ணணும். User query வந்தா, அதை analyze பண்ணணும், database-ல தேடணும், RAG செய்யணும், ஒரு tool call பண்ணணும், பிறகு answer generate பண்ணணும். 

இதை ஒரே LLM call-ல பண்ண முடியுமா? இல்லை. ஒவ்வொரு step-க்கும் வெவ்வேறு logic, வெவ்வேறு input/output தேவை. ஒரு linear chain-ல எழுதினால், ஒரு step fail ஆனால் எல்லாம் break ஆகும். Loop போடணும், condition பார்க்கணும், state maintain பண்ணணும்.

இங்கே பிரச்சனை என்ன? **Control flow**. ஒரு workflow-ல எந்த step அடுத்து run ஆகும், எப்போ stop ஆகும், state எப்படி carry ஆகும் என்பதை manage பண்ணணும்.

LangGraph-ல இதற்கு பதில் தருவது **Nodes**.

## 2. Mental Model

Node என்பது ஒரு **pure function / work unit**.

Input: state
Processing: ஒரு defined task
Output: updated state

ஒரு kitchen-ல ஒரு chef. Chef-க்கு plate வரும், அவர் cut பண்ணுவார், plate திரும்ப போகும். அவருக்கு தெரியாது அடுத்து எந்த chef-க்கு போகும். அவர் வேலை மட்டும் செய்வார்.

அதே மாதிரி Node-க்கு தெரியாது அடுத்த node எது. அது தன்னுடைய job மட்டும் செய்து state-ஐ update செய்யும். Graph-ல edges decide பண்ணும் யார் அடுத்து.

> Node = What to do. Edge = When to do next.

## 3. How It Works

LangGraph-ல ஒரு Node என்பது simple Python function.

```python
def retrieve_node(state):
    query = state["query"]
    docs = vector_db.search(query)
    return {"documents": docs, "query": query}
```

State என்பது dict மாதிரி. ஒரு Node run ஆனதும், அது state-ஐ return செய்யும். அந்த updated state அடுத்த Node-க்கு போகும்.

Key points:

* Node stateless இருக்க முயற்சி செய்யலாம். All context state-ல வரும்.
* Node-ல side effects இருக்கலாம்: DB call, API call, LLM call.
* Node-க்கு input type என்ன, output type என்ன என்பது clear ஆக இருக்கணும்.

Graph construction:

```python
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_edge("retrieve", "generate")
```

இப்போ workflow deterministic ஆகிறது.

## 4. Architectural Reasoning

Node ஏன் தேவை?

**Separation of concerns.** ஒவ்வொரு business logic-ஐயும் isolated unit-ல வைக்கிறோம். Test பண்ண எளிது, reuse பண்ண எளிது.

**Composability.** Simple nodes-ஐ combine பண்ணி complex agent flow build பண்ணலாம். Retrieve node, summarize node, tool node எல்லாம் interchangeable.

**State management.** LangGraph state machine போல work செய்யும். Node-களுக்கு இடையில் state carry ஆகும். இது conversation memory, intermediate results எல்லாம் handle பண்ண உதவும்.

எப்போ Node use பண்ணணும்?

* ஒரு step-ல clear input-output இருக்கும் போது.
* LLM call + tool call + post-processing வேறு வேறு ஆக இருக்கும் போது.
* Reusable logic தேவைப்படும் போது.

Alternatives: One giant LLM prompt with all logic inside. அது quick ஆகும் ஆனால் debug கஷ்டம், non-deterministic, tool control இல்லை.

## 5. Trade-offs

**Granularity.** Node-களை மிக சிறியதாக பிரித்தால், graph complex ஆகும், overhead அதிகம். மிக பெரியதாக வைத்தால், reuse குறையும். Sweet spot: one business step per node.

**State size.** ஒவ்வொரு Node-க்கும் full state copy போகும். State பெரிதாக இருந்தால் latency, memory cost வரும். Selective state update செய்யணும்.

**Error handling.** ஒரு Node fail ஆனால் whole graph fail ஆகுமா? Retry logic, fallback node எங்கே வைக்கிறீர்கள் என்பது முக்கியம்.

**Operability.** Node-கள் independent ஆக இருந்தால் observability எளிது. ஒவ்வொரு node-க்கும் tracing, latency, error rate பார்க்கலாம். ஆனால் graph-ல 50 nodes ஆனால் mental model கடினம்.

## 6. Practical Example

Enterprise support agent.

Nodes:

1. `classify_intent` - User query-ஐ classify செய்யும். billing / technical / refund.
2. `retrieve_policy` - Intent பார்த்து knowledge base-ல relevant policy docs தேடும்.
3. `call_tool` - Billing என்றால் billing API-க்கு call, Technical என்றால் ticket create.
4. `generate_answer` - RAG + tool output combine பண்ணி final answer generate.

State:
```python
{
  "query": "...",
  "intent": None,
  "documents": [],
  "tool_output": None,
  "answer": None
}
```

Flow: classify_intent -> retrieve_policy -> call_tool -> generate_answer

ஒரு Node-ல LLM call, மற்ற Node-ல DB call. எதுவும் ஒன்றோடு ஒன்று mix ஆகவில்லை. Testing எளிது. ஒரு நாள் policy retrieval மாறினால், retrieve_policy node மட்டும் மாற்றினால் போதும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு agent இருக்கு. User query வந்ததும்:

1. `summarize` node
2. `retrieve` node
3. `generate` node

`generate` node output quality மோசமாக இருக்கிறது. Log பார்த்தால் `retrieve` node 0 documents return செய்கிறது, சில queries-க்கு மட்டும்.

நீங்கள் இந்த flow-ல ஒரு node சேர்க்கலாம். என்ன node சேர்ப்பீர்கள்? எங்கே வைப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Node = isolated work unit. What to do, not when to do.
* State is the contract between nodes. Clear input/output design is architecture.
* Nodes allow reasoning-first design: problem -> steps -> units.
* Too fine-grained nodes increase operational complexity. Choose business meaningful boundaries.
* Design nodes for testability and observability, not just functionality.
