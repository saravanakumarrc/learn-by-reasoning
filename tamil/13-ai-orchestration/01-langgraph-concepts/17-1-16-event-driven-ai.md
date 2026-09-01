# Event-driven AI

> **Learning Path:** AI Orchestration
> **Section:** 17.1.16 — LangGraph concepts

## 1. Problem

உங்களுக்கு ஒரு AI agent வேண்டும். அது ஒரு user query வாங்கி, ஆவணங்களை search பண்ணும், RAG லிருந்து context எடுக்கும், ஒரு tool call பண்ணும், மறுபடியும் LLM க்கு அனுப்பும், பிறகு summary generate பண்ணும்.

இது ஒரு முறை அல்ல. இது ஒரு loop.

இப்போது code ல இதை எப்படி handle பண்ணுவீர்கள்? `while` loop ல states ஐ நீங்களே track பண்ணி, if-else கொண்டு next step decide பண்ணுவீர்கள்.

பிரச்சனை என்ன?
* Flow மாறினால் code முழுவதும் மாறும்.
* Error ஆனால் எங்கே retry பண்ணுவது தெரியாது.
* Same flow ஐ multiple agents பகிர்ந்து கொள்ள முடியாது.
* Testing, observability, persistence எல்லாம் நீங்களே build பண்ண வேண்டும்.

அப்படி இருக்கும்போது, **workflow ஐ explicit graph ஆக மாடல் பண்ணினால் என்ன நடக்கும்?** Nodes = steps, Edges = transitions.

அதுதான் LangGraph கேள்வி.

## 2. Mental Model

LangGraph என்பது **stateful, cyclical graphs for LLM applications**.

சிம்பிள் mental model:
* **State** = ஒரு dictionary போல. `messages`, `documents`, `user_id`, `tool_output` போன்றவை இங்கே இருக்கும்.
* **Node** = ஒரு function. LLM call, tool call, classification, RAG retrieval போன்றவை.
* **Edge** = Node A முடிந்ததும், next என்ன node என்பதை தீர்மானிக்கும் logic.

இது LangChain ன் chain + agent ஐ விட ஒரு படி மேலே. ஏனெனில் இங்கே flow ஐ நீங்கள் **graph ஆக வரையலாம்**, மற்றும் அது state ஐ carry பண்ணும்.

அனாலஜி: ஒரு manufacturing line. ஒவ்வொரு station ஒரு node. Product வரும், process ஆகும், next station க்கு போகும். ஒரு station தோல்வி அடைந்தால், product திரும்பும். LangGraph அதே concept ஆனால் AI steps க்கு.

## 3. How It Works

Core concepts:

**StateGraph**
நீங்கள் state schema வரையறுக்கிறீர்கள். Pydantic model போல.

```python
class AgentState(TypedDict):
    messages: list
    context: list
    needs_search: bool
```

**Nodes**
ஒவ்வொரு node ஒரு function ஆக இருக்கும், `state` ஐ input ஆக வாங்கி, மாற்றிய `state` ஐ திருப்பி தரும்.

**Conditional Edges**
நீங்கள் `add_conditional_edges` வைக்கிறீர்கள். உதாரணம்: LLM output ல `needs_tool = true` என்றால் tool node க்கு போ, இல்லை என்றால் end.

**Checkpointer**
இதுதான் LangGraph ஐ special ஆக்கும். ஒவ்வொரு step ன் state ஐ persist பண்ணும். Database, memory, Redis என்று வைக்கலாம்.

இதனால்:
* Agent முன்னேற்றத்தை மீண்டும் தொடங்கலாம். `thread_id` கொடுத்தால் முந்தைய state இருந்து தொடரும்.
* Human-in-the-loop பண்ணலாம். Graph pause பண்ணி, human input க்காக காத்திருக்கும்.
* Replay/debug செய்யலாம்.

**Graph compile**
Graph வரையப்பட்ட பிறகு `graph.compile(checkpointer=...)` செய்தால், அது ஒரு runnable ஆக மாறும். `.invoke()` அல்லது `.stream()` மூலம் run பண்ணலாம்.

## 4. Architectural Reasoning

எப்போது LangGraph useful?

* Multi-step reasoning தேவைப்படும் போது. RAG → Tool → Summarize → Validate போன்ற loop.
* Flow branching தேவைப்படும் போது. Classification based routing.
* Long-running workflow தேவைப்படும் போது. Human approval, async tool results.
* State க்கு strong consistency தேவைப்படும் போது.

Alternative என்ன?
* Simple LangChain Chain: Linear flow க்கு நல்லது. ஆனால் branching, loop கஷ்டம்.
* Custom orchestrator with state machine: முழுவதும் நீங்கள் build பண்ண வேண்டும்.
* Workflow engines like Temporal, Step Functions: Heavy, generic. LLM specific features இல்லை.

Architect ஆக நீங்கள் LangGraph ஐ தேர்வு செய்யும்போது, நீங்கள் கொடுப்பது: **declarative flow control + persistence**.

## 5. Trade-offs

**State management overhead**
State ஐ நீங்கள் explicit ஆக define பண்ண வேண்டும். அது நல்லது, ஆனால் initial boilerplate அதிகம். State schema மாறினால் migration தேவை.

**Complexity vs flexibility**
சிறிய flow க்கு LangGraph overkill. 2-3 step chain க்கு simple chain போதும். Graph வளரும்போது debugging கடினமாகும். Graph visualization தேவை.

**Latency & cost**
Graph ஒவ்வொரு step லும் LLM call செய்யும். Loop இருந்தால் token cost அதிகரிக்கும். Checkpointer DB call ஒவ்வொரு step க்கும் overhead.

**Failure modes**
Node தோல்வி அடைந்தால், graph எங்கே resume ஆகும்? Checkpointer இல்லை என்றால், state lost. Retry logic நீங்கள் node ல implement பண்ண வேண்டும். Infinite loop தவிர்க்க max iterations வைக்க வேண்டும்.

## 6. Practical Example

Enterprise support agent.

Flow:
`user_query` → `classify_intent` → if billing → `retrieve_billing_data` → `call_billing_tool` → `generate_answer`
if technical → `RAG_retrieval` → `LLM_answer` → `needs_clarification?` → `ask_user` → back to start

LangGraph ல இது ஒரு graph.

State ல `messages`, `intent`, `billing_data`, `rag_docs` இருக்கும்.

Checkpointer ல `thread_id = ticket_id`. Agent pause ஆனால், user reply வந்ததும் அதே state இருந்து தொடரும்.

இங்கே architectural win என்ன? Business logic மாறினாலும் graph edges மட்டும் மாற்றினால் போதும். Nodes reusable.

## 7. Reasoning Challenge

உங்களுக்கு ஒரு RAG agent உள்ளது. அது query வாங்கி, retrieval பண்ணி, answer generate பண்ணும். ஆனால் retrieval quality குறைவாக இருந்தால், அது automatically query ஐ rewrite பண்ணி மறுபடியும் retrieval செய்ய வேண்டும். மூன்று முறைக்கு மேல் retry பண்ணக்கூடாது.

இந்த flow ஐ LangGraph ல எப்படி மாடல் செய்வீர்கள்? Nodes என்னென்ன? Conditional edge எப்படி வேலை செய்யும்? State ல என்ன track பண்ண வேண்டும்?

## 8. Key Takeaways

* LangGraph = stateful graph execution for multi-step LLM workflows, not just linear chains.
* State, Nodes, Edges, Checkpointer என்பது core mental model.
* Flow ஐ explicit ஆக்குவது testability, observability, human-in-the-loop ஐ எளிதாக்குகிறது.
* சிறிய flow க்கு over-engineering; branching, loops, persistence தேவையானபோது மட்டும் பயன்படுத்து.
* Every cycle adds latency and cost; max iterations and clear termination conditions மிக முக்கியம்.
