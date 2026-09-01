# Conditional routing

> **Learning Path:** AI Orchestration
> **Section:** 17.1.4 — LangGraph concepts

## 1. Problem

ஒரு AI agent-ஐ build பண்ணும்போது flow linear இருக்காது.

User query வந்தது. அதை **summarize** பண்ணணுமா? **search** பண்ணணுமா? **code generate** பண்ணணுமா? அல்லது **direct answer** கொடுக்கணுமா?

ஒரே workflow-க்குள்ள இதெல்லாம் மாறி மாறி வரும். Query type பார்த்து next step மாறணும்.

அப்படி இல்லாமல் எல்லாத்தையும் எப்போதும் run பண்ணினா என்ன ஆகும்?
* latency அதிகம்
* cost waste - search, tool call எல்லாம் தேவையில்லாமல்
* irrelevant output

நமக்கு தேவை: **state பார்த்து, condition check பண்ணி, next node-க்கு route பண்ண ஒரு வழி**.

அதுதான் conditional routing.

## 2. Mental Model

LangGraph-ல graph என்பது nodes + edges.

Normal edge = fixed. A -> B -> C

Conditional edge = A -> { condition } -> B / C / D

Node ஒன்று run ஆகி state-ஐ update பண்ணும். அடுத்து router function ஓடும். அது state-ஐ படிச்சு, ஒரு string return பண்ணும். அந்த string-ன் பேரில் next node select ஆகும்.

அதாவது flow-ஐ data driven ஆக்குறோம்.

> `should_route(state) -> "search" | "answer" | "clarify"`

## 3. How It Works

LangGraph-ல `add_conditional_edges` use பண்ணுவோம்.

```
graph.add_node("classifier", classify_query)
graph.add_node("search", search_tool)
graph.add_node("answer", generate_answer)

graph.add_edge(START, "classifier")

graph.add_conditional_edges(
    "classifier",
    route_decision, 
    {
        "search": "search",
        "answer": "answer",
        "clarify": "classifier"   # loop back
    }
)
```

`route_decision` என்பது simple python function:

```python
def route_decision(state):
    intent = state["intent"]
    needs_search = state["needs_search"]
    if intent == "clarification":
        return "clarify"
    if needs_search:
        return "search"
    return "answer"
```

State என்பது graph முழுவதும் pass ஆகும் dict. Classifier node output-ஐ state-ல set பண்ணும். Router அதை படிக்கும்.

இதே logic-ஐ loop-க்கும் use பண்ணலாம். Example: tool result sufficient இல்லைன்னா மீண்டும் search-க்கு திரும்பு.

## 4. Architectural Reasoning

Conditional routing useful ஆகும் போது:

* **Intent based branching**: Query type வேறு, path வேறு.
* **Guardrails**: Toxic / out-of-scope input-ஐ early reject பண்ணி short-circuit பண்ண.
* **Tool selection**: RAG தேவையா? Code executor தேவையா? Calculator தேவையா?
* **Retry / fallback logic**: Tool fail ஆனா alternative path எடு.
* **Human-in-the-loop**: Confidence low என்றால் human review node-க்கு route பண்ணு.

Alternatives என்ன?
* One big LLM prompt with all instructions: control இல்லை, cost அதிகம், reasoning opaque.
* Separate workflows per intent: duplication, maintenance கஷ்டம்.

Conditional routing ஏன் choose பண்ணுறோம்? Because **control + observability + cost control** ஒன்னா கிடைக்கும். Flow explicit ஆகும், test பண்ண எளிது.

## 5. Trade-offs

**Control vs Complexity**: Routing logic explicit ஆகும். ஆனால் graph கொஞ்சம் complex ஆகும். Too many branches = debugging கஷ்டம்.

**State size**: Router decision-க்கு தேவையான fields state-ல இருக்கணும். State big ஆனா serialization cost + memory cost.

**Latency vs Accuracy**: More checks = better decision, ஆனால் extra LLM call / classification cost.

**Failure modes**: Router function itself fail ஆனா graph stuck ஆகும். Default route வைக்கணும். Also non-deterministic LLM classifier -> inconsistent routing. அதனால் classifier output-ஐ validate பண்ணு, or use deterministic rules for critical paths.

## 6. Practical Example

Enterprise support agent.

Nodes:
`classify` -> `route` -> `faq_answer` / `rag_search` / `create_ticket`

User: "Order #12345 எப்போ வரும்?"

Classifier state-ல set பண்ணும்:
intent = "order_tracking", needs_search = True, sensitive = False

Router:
needs_search True -> `rag_search` node
rag_search returns answer + confidence = 0.92

Next conditional edge from `rag_search`:
confidence > 0.8 -> `answer`
confidence < 0.8 -> `create_ticket` for human

இப்படி routing பண்ணினா unnecessary ticket create ஆகாது. Cost குறையும். SLA improve ஆகும்.

Mermaid:
```mermaid
graph TD
    START --> classifier
    classifier --> route
    route -->|needs_search| rag_search
    route -->|no_search| faq_answer
    route -->|clarify| classifier
    rag_search --> check_confidence
    check_confidence -->|high| answer
    check_confidence -->|low| create_ticket
    faq_answer --> answer
    create_ticket --> end
```

## 7. Reasoning Challenge

உங்க RAG agent-ல 3 tools இருக்கு: vector_search, web_search, calculator.

Query வந்ததும் classifier ஒரு `intent` மற்றும் `needs_calculation` flag set பண்ணும்.

நீங்கள் conditional routing வைக்க விரும்புறீங்க.

* கேள்வி: vector_search முதலில் run பண்ணி, result relevance low என்றால் web_search-க்கு fallback பண்ண வேண்டும். calculator தேவையென்றால் மட்டும் run பண்ண வேண்டும்.

இதுக்கு எத்தனை conditional edges வேண்டும்? Router function எப்படி state-ஐ பார்க்கும்? Loop எங்கே வரும்? Trade-off என்ன?

இதை sketch பண்ணி பாருங்கள். முக்கியமாக state fields எவை முக்கியம்?

## 8. Key Takeaways

* Conditional routing = state-ஐ பார்த்து next node decide பண்ணுவது. Flow data driven ஆகும்.
* Problem solve பண்ணுவது: unnecessary tool calls, latency, cost waste, one-size-fits-all failure.
* Router என்பது small, deterministic function. LLM classification + rule based guardrails combine பண்ணு.
* Every branch உருவாக்கும் trade-off: control கிடைக்கும், ஆனால் complexity & observability burden உருவாகும்.
* Design principle: Route early, route explicitly, and always have a default safe path.
