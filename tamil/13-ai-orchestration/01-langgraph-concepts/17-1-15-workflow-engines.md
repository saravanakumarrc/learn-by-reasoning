# Workflow engines

> **Learning Path:** AI Orchestration
> **Section:** 17.1.15 — LangGraph concepts

## 1. Problem

ஒரு LLM agent-ஐ build பண்ணும்போது ஒரே ஒரு LLM call மட்டும் போதாது. 

நீங்கள் ஒரு customer support agent பண்ணுகிறீர்கள். User query வந்ததும்:
1. Intent classify பண்ணனும்
2. Database-ல் order history தேடனும்
3. Retrieval பண்ணி relevant policy கண்டுபிடிக்கனும்
4. LLM-ல் answer generate பண்ணனும்
5. User-க்கு respond பண்ணனும்

இது ஒரு linear flow இல்லை. சில query-க்கு database தேவையே இல்லை. சில query-க்கு clarification தேவை. சில query fail ஆனால் retry பண்ணனும். ஒரு step error ஆனால் முழு workflow-ம் நிற்கக்கூடாது.

State இருக்கு, branching இருக்கு, loop இருக்கு, tool calls இருக்கு. இதை ad-hoc Python if-else-ல் எழுதினால் code ஒரு spaghetti ஆகிவிடும். மீண்டும் run பண்ண, debug பண்ண, test பண்ண கஷ்டம்.

**What problem became painful?** State + control flow + tools + retries + observability ஒன்றாக manage பண்ணுவது.

அதற்கு தேவை workflow engine.

## 2. Mental Model

LangGraph ஒரு graph-ஆக workflow-ஐ define பண்ண வைக்கிறது.

Nodes = steps. Eg: `classify`, `retrieve`, `generate`, `call_tool`
Edges = flow control. Eg: classify -> retrieve, classify -> generate

State என்பது graph-க்கு மத்தியில் flow ஆகும் shared data. ஒவ்வொரு node-ம் state-ஐ read பண்ணி update பண்ணும்.

Graph என்பது deterministic execution model. நீங்கள் ஒரு graph-ஐ build பண்ணினால், அதை run பண்ணலாம், replay பண்ணலாம், interrupt பண்ணலாம்.

Mental model: **Workflow = State Machine with nodes and edges, and LLM nodes inside it.**

## 3. How It Works

LangGraph-ல் மூன்று core concepts:

**StateGraph**: State-ஐ define பண்ணுவது. Pydantic model மாதிரி. `messages`, `user_id`, `order_id`, `retrieved_docs` இப்படி.

**Nodes**: Python functions. Input = state, Output = partial state update. Node-க்குள் LLM call, tool call எதுவும் இருக்கலாம்.

**Edges**: 
- Normal edge: A -> B
- Conditional edge: A -> B or C based on state. Eg: intent == 'refund' ? go to refund_flow : go to faq_flow
- Loop edge: generate -> check_quality -> if bad, regenerate

Graph compile ஆனதும் ஒரு runnable ஆகிறது. `graph.invoke(state)` என்றால் graph start from entry, state-ஐ propagate பண்ணி exit வரை run ஆகும்.

Checkpoints உள்ளன. ஒவ்வொரு step-க்கும் state save ஆகும். இதனால் human-in-the-loop, interrupt, resume possible. User-ஐக் கேட்டு clarification வாங்கி, அதே state-ல் தொடரலாம்.

## 4. Architectural Reasoning

LangGraph எப்போது useful?

* Multi-step agent flow தேவைப்படும் போது. Single LLM call-ல் முடியாது.
* State அடுத்த step-க்கு carry ஆக வேண்டும்.
* Branching, looping, retry logic தேவை.
* Observability + debugging தேவை. எந்த node fail ஆனது, state எப்படி மாறியது என்பது தெரிய வேண்டும்.

Alternative என்ன?
* Simple chain with LangChain. Linear மட்டும்.
* Manual orchestration with if-else. Small prototype-க்கு OK, scale ஆகாது.
* External workflow engines like Temporal, Prefect. Heavy, general purpose.

LangGraph choose பண்ணுவது ஏன்? AI specific. LLM nodes, tool calling, streaming, state management built-in. Pythonic API. Agent loop-ஐ natural-ஆக express பண்ண முடியும்.

## 5. Trade-offs

**Complexity vs Control**: Graph explicit ஆக இருக்கும். Flow clear. ஆனால் small task-க்கு overkill. 2 step flow-க்கு graph வேண்டாம்.

**State size**: State முழுவதும் memory-ல் / checkpoint store-ல் save ஆகும். Large `messages` history, big documents இருந்தால் checkpoint cost, latency increase ஆகும். State-ஐ prune பண்ண வேண்டும்.

**Determinism illusion**: Graph deterministic ஆக இருந்தாலும் LLM node non-deterministic. Same input, different output. அதனால் conditional edges flaky ஆகலாம். Guardrails தேவை.

**Operational complexity**: Local run சுலபம். Production-ல் checkpoint backend, persistence, concurrency handle பண்ணனும். Memory vs Postgres vs Redis trade-off.

Failure mode: Loop infinite. Conditional edge wrong condition -> dead end. State schema change -> old checkpoints incompatible.

## 6. Practical Example

Enterprise support agent:

State: `{messages, intent, order_id, retrieved_docs, answer}`

Nodes:
- `classify_intent` : LLM -> intent
- `fetch_order` : tool call if intent in [refund, status]
- `retrieve_policy` : vector DB search
- `generate_answer` : LLM with context
- `human_escalate` : if confidence low

Edges:
classify_intent -> conditional: intent == refund ? fetch_order : skip
fetch_order -> retrieve_policy -> generate_answer
generate_answer -> conditional: confidence < 0.6 ? human_escalate : end

Graph compile பண்ணி invoke பண்ணினால், ஒரு user query enter ஆகி, state முழுவதும் flow ஆகி, final answer வரும். Checkpoints இருப்பதால் user "wait, order id wrong" என்றால் state-ஐ update பண்ணி அதே graph-ஐ resume பண்ணலாம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG pipeline இருக்கு: retrieve -> rerank -> generate. Generate quality low என்றால் retrieve query-ஐ rewrite பண்ணி மீண்டும் retrieve பண்ணனும். ஆனால் மூன்று முறைக்கு மேல் retry பண்ணக்கூடாது. Max latency 2 sec.

இதற்கு LangGraph-ல் எப்படி graph design பண்ணுவீர்கள்? Nodes என்ன? Conditional edge எப்படி? Loop limit எப்படி enforce பண்ணுவீர்கள்?

## 8. Key Takeaways

* LangGraph = stateful workflow engine for LLM agents. Nodes + Edges + State.
* Problem solve பண்ணுவது: branching, looping, tool use, retries, human-in-the-loop.
* Graph explicit ஆக இருப்பதால் reasoning, testing, observability எளிது.
* Trade-off: small flows-க்கு overkill, state size மற்றும் LLM non-determinism கவனம் தேவை.
* Architecturally, workflow engine-ஐ தேர்வு செய்வது flow complexity + operability தேவைக்கு ஏற்ப.
