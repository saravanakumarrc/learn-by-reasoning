# Sequential agents

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.7 — Learn

## 1. Problem

உங்களிடம் ஒரு complex workflow இருக்கு. உதாரணமாக, ஒரு customer support ticket வந்தா:

1. Intent-ஐ classify பண்ணனும்
2. Relevant documents / past tickets-ல search பண்ணனும்
3. Draft reply generate பண்ணனும்
4. Tone check / policy check பண்ணனும்
5. Final answer-ஐ user-க்கு return பண்ணனும்

இதை ஒரே LLM agent-க்கு கொடுத்தால் என்ன ஆகும்? Model context overload ஆகும், reasoning மோசம் ஆகும், error handling கஷ்டம், மற்றும் ஒரு step fail ஆனால் முழு workflow-ம் fail ஆகும்.

What goes wrong if we don't split? One big prompt = brittle, hard to test, hard to improve one step without breaking others, and observability இல்லை.

Sequential agents என்பது இந்த pain-க்கு வந்த தீர்வு.

## 2. Mental Model

Sequential agents = Assembly line.

ஒரு task-ஐ clear stages ஆக பிரித்து, ஒவ்வொரு stage-க்கும் ஒரு specialized agent. Output of previous agent = Input of next agent.

ஒவ்வொரு agent-க்கும் ஒரு narrow responsibility, specific tools, specific prompt. Result is deterministic flow, easy to debug, easy to improve.

> Agent A → Agent B → Agent C → Final output

இது pipeline மாதிரி. Data ஒரு திசையில் போகும், loop இல்லை.

## 3. How It Works

Core idea: State handoff.

Step 1: **Router / Orchestrator** decides the sequence. பெரும்பாலும் static order.

Step 2: Each agent receives structured input, does its job, produces structured output. Output schema fixed ஆக இருக்கும்.

Step 3: Output validated. Schema match ஆகலைன்னா fail fast, retry or fallback.

Step 4: Next agent-க்கு pass.

இங்கே ஒவ்வொரு agent-ம் independent ஆக run ஆகலாம். Tools access வேறுபடலாம். உதாரணமாக, Step 2 agent-க்கு மட்டும் vector database access, Step 4 agent-க்கு policy checker tool.

Orchestration simple ஆக இருக்கும்: for i in agents: state = agents[i](state)

## 4. Architectural Reasoning

**When useful?**
* Workflow steps logically dependent ஆக இருக்கும் போது.
* Each step needs different tools, data sources, or guardrails.
* Quality and safety வேணும், step-by-step verification வேணும்.
* Observability and blame isolation வேணும்.

**Constraint it addresses:** Complexity மற்றும் reliability.

ஒரே agent-ல் செய்யும் போது prompt மிகப்பெரியதாகி, hallucination அதிகம். Sequential ஆக பிரிச்சால் each agent-க்கு focus clear ஆகும்.

**Alternatives:**
* **Single agent with big prompt:** Simple, but brittle, hard to debug.
* **Parallel agents:** Independent subtasks, need aggregation. Sequential-க்கு மாற்று இல்லை.
* **ReAct / Loop agents:** Agent self decides next step. More flexible but non-deterministic, harder to test.

Architect ஏன் sequential choose பண்ணுவார்? Because business process itself sequential ஆக இருக்கு. Eg: KYC verification → Risk check → Approval. Order மாற்ற முடியாது.

## 5. Trade-offs

**Pros:**
* Predictable flow, easy to reason about
* Each agent can be optimized independently: different model, different temperature, different tools
* Failure isolation: எந்த step fail ஆனது exact-ஆ தெரியும்
* Testing easy: unit test each agent with fixtures

**Cons / Failure modes:**
* **Latency adds up:** 5 agents × 1.5s = 7.5s total. User wait time increase.
* **Error propagation:** First agent hallucinate பண்ணா, அது downstream-க்கு poison ஆகும். Garbage in, garbage out.
* **Rigid:** Mid-workflow change செய்ய முடியாது. If step 3 needs info from step 5, architecture breaks.
* **State management overhead:** Handoff schema maintain பண்ணனும். Version mismatch வந்தால் system break.

Important trade-off: **Reliability vs Latency vs Flexibility**. Sequential = reliability கூடும், flexibility குறையும்.

## 6. Practical Example

Enterprise RAG support agent.

Flow:
1. **Classifier Agent**: Ticket text வாங்கி intent classify பண்ணும். Output: {intent: billing, confidence: 0.92}
2. **Retriever Agent**: Intent பார்த்து relevant knowledge base-ல search பண்ணும். Tools: vector database + ticket history. Output: {docs: [...], context_summary}
3. **Draft Agent**: Context + user query-ல இருந்து first draft generate பண்ணும். Model: larger LLM.
4. **Policy Guard Agent**: Draft-ஐ policy checklist-க்கு எதிராக check பண்ணும். Tools: regex rules, LLM judge. Output: {approved: true, issues: []}
5. **Formatter Agent**: Final reply-ஐ customer tone-க்கு format பண்ணும்.

ஒவ்வொரு step-ம் logged. Step 4 fail ஆனா, draft-ஐ rewrite பண்ணி retry பண்ணலாம், முழு flow restart தேவை இல்லை.

## 7. Reasoning Challenge

உங்களிடம் ஒரு loan application workflow இருக்கு. Steps: Document extraction → Credit check → Fraud check → Approval letter generation.

Fraud check agent சில நேரங்களில் 10-15 seconds எடுக்கும். மற்ற agents 1-2 seconds.

User experience முக்கியம். இங்கே sequential flow-ஐ எப்படி improve பண்ணுவீர்கள்? Parallelize செய்ய முடியுமா? எந்த step-ஐ முன்னாடி கொண்டு வருவீங்க? மற்றும் failure ஒன்னு வந்தா எப்படி handle பண்ணுவீங்க?

## 8. Key Takeaways

* Sequential agents என்பது complex workflow-ஐ deterministic pipeline ஆக பிரிப்பது.
* ஒவ்வொரு agent-க்கும் narrow responsibility, clear input/output schema வேணும்.
* இது reliability, testability, observability கொடுக்கும், ஆனால் latency add ஆகும் மற்றும் flexibility குறையும்.
* Agent sequence-ஐ design பண்ணும்போது business process order-ஐ follow பண்ணு, not model convenience.
