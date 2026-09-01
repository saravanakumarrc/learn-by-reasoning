# Agent delegation

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.11 — Learn

## 1. Problem

நீங்கள் ஒரு AI agent-ஐ பணி கொடுக்கிறீர்கள். User சொல்கிறார்: "Q3-ல என் sales drop ஆனதற்கான காரணத்தை கண்டுபிடித்து, மார்க்கெட்டிங் டீம்-க்கு ஒரு action plan அனுப்பு".

ஒரே agent-ஐ வைத்து இதை செய்ய முயற்சித்தால் என்ன நடக்கும்?

Data கிடைக்க வேண்டும், SQL query பண்ண வேண்டும், trends analyze பண்ண வேண்டும், insights generate பண்ண வேண்டும், email draft பண்ண வேண்டும். ஒரு agent-க்கு எல்லா tools-ம் தெரியும், ஆனால் அது slow ஆகும், hallucinate செய்யும், context window முடிந்து விடும். ஒரு mistake ஆனால் முழு workflow தோல்வி.

இங்கே painful problem என்ன? **One agent cannot be expert at everything, and it cannot reliably orchestrate long multi-step work.**

இதற்காகவே delegation தேவைப்படுகிறது.

## 2. Mental Model

Agent delegation என்பது ஒரு manager போல் யோசிப்பது.

Manager தானே எல்லா வேலையும் செய்வதில்லை. அவர் problem-ஐ புரிந்து கொண்டு, sub-tasks-ஆக பிரித்து, சரியான specialist-க்கு delegate செய்கிறார், result-ஐ review செய்கிறார், combine செய்கிறார்.

அதே போல் ஒரு **coordinator agent** பெரிய goal-ஐ புரிந்து கொண்டு, smaller agents-க்கு துண்டு வேலைகளை கொடுக்கிறது.

இது divide-and-conquer for agents.

## 3. How It Works

Simple flow:

1. **Planner / Coordinator Agent** receives user request.
2. It decomposes goal into sub-tasks with clear inputs/outputs.
3. It routes each sub-task to a **specialist agent** with right tools.
4. Specialist executes, returns result.
5. Coordinator validates, aggregates, and produces final answer.

உதாரணமாக tools:

* Data Analyst Agent - has access to database, SQL tool
* Report Writer Agent - has access to doc generator
* Email Agent - has access to email API

Coordinator இவர்களுக்கு task brief அனுப்புகிறது, "SQL query output-ஐ இப்படி summarize பண்ணு" என்பது போல்.

Delegation dynamic-ஆகவும் இருக்கலாம். Specialist தனக்கு தெரியாத step வந்தால், அதற்கு மற்றொரு agent-ஐ call செய்யலாம்.

## 4. Architectural Reasoning

எப்போது delegation useful?

* **Complex multi-step workflow** - 3+ steps, different tools தேவை
* **Specialization** - ஒவ்வொரு domain-க்கும் தனி knowledge, prompt, tools
* **Parallelism** - independent sub-tasks-ஐ parallel-ல run பண்ணலாம்
* **Reliability & containment** - ஒரு agent fail ஆனால் மற்றவை தொடரும்

Alternatives என்ன?

* **Monolithic agent with all tools** - Simple, ஆனால் context pollution, error propagation, slow
* **Human-in-the-loop** - Accurate ஆனால் slow and costly
* **Rule-based pipeline** - Deterministic, ஆனால் flexible இல்லை

Architect ஏன் delegation தேர்வு செய்வார்? 
ஏனெனில் system maintainable ஆகிறது. ஒவ்வொரு agent-ஐ தனியாக test, version, improve பண்ண முடியும். Team size பெரிதாகும் போது, different engineers can own different agents.

## 5. Trade-offs

**1. Latency vs Quality**
Delegation adds hop latency. Coordinator wait செய்ய வேண்டும். ஆனால் quality better, error rate குறையும்.

**2. Complexity of orchestration**
நீங்கள் agent-ஐ build பண்ணுவதற்கு பதிலாக, coordination logic-ஐ build பண்ண வேண்டும். Task decomposition, result validation, retry logic எல்லாம் வேண்டும். Operational complexity அதிகரிக்கும்.

**3. Failure modes**
Specialist agent hallucinate செய்தால், coordinator அதை detect செய்ய வேண்டும். இல்லை என்றால் bad output propagate ஆகும். Need guardrails, schema validation, confidence check.

**4. Cost**
Multiple LLM calls = higher cost. ஆனால் smaller focused prompts = token usage குறையலாம். Trade-off இருக்கும்.

## 6. Practical Example

Enterprise customer support.

User: "My order #12345 is delayed, check status and offer refund if delay > 7 days".

Coordinator Agent:

1. Decompose:
   a. Fetch order status from order service
   b. Check SLA policy for refund eligibility
   c. Draft response

2. Delegate:
   * OrderLookup Agent → calls order API, returns status and delay days
   * Policy Agent → reads refund policy from knowledge base
   * Response Agent → generates empathetic reply with offer

3. Coordinator aggregates: Delay = 9 days → eligible → final email drafted and sent.

இங்கே ஒவ்வொரு agent-க்கும் specific tool and context மட்டும் கொடுக்கப்பட்டுள்ளது. Coordinator overall goal-ஐ track செய்கிறது.

## 7. Reasoning Challenge

உங்களிடம் 3 agents உள்ளன: Research Agent, Summarizer Agent, FactChecker Agent.

User asks: "Latest AI regulation news in EU, summarize in Tamil and ensure no hallucination".

Research Agent 50 sources-ல் இருந்து 2000 words தருகிறது. Summarizer அதை 200 words-க்கு குறைக்கிறது. FactChecker அதன் claims-ஐ verify செய்ய வேண்டும்.

இங்கே delegation order எப்படி வைப்பீர்கள்? Research → Summarizer → FactChecker என்பது சரியா? அல்லது வேறு வழி? ஏன்?

## 8. Key Takeaways

* Delegation solves the problem of one agent trying to be expert at everything.
* Coordinator decomposes, routes, validates, and aggregates.
* Use delegation when workflow is multi-step, specialized, or needs parallelism.
* Every delegation adds latency, cost, and orchestration complexity — design for failure containment.
* Good delegation = clear task boundaries and verifiable outputs, not just passing messages.
