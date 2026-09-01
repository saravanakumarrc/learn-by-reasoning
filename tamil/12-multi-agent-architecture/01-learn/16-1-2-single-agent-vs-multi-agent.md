# Single agent vs multi-agent

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.2 — Learn

## 1. Problem

ஒரு LLM agent-ஐ எடுத்துக்கோங்க. அது ஒரு user query-க்கு respond பண்ணணும். Query சாதாரணமாக இருந்தால் பரவாயில்லை. ஆனால் real world-ல் query complex ஆகுது.

> "என் last quarter sales-ஐ analyze பண்ணி, top 3 products-ஐ எடுத்து, அதுக்கான marketing budget-ஐ suggest பண்ணு, Slack-ல team-க்கு summary அனுப்பு, மறுபடியும் Google Sheet-ல update பண்ணு."

இதை ஒரே single agent பண்ண முயற்சித்தால் என்ன ஆகும்?

- Agent-க்கு tool use, data analysis, reasoning, writing, integration எல்லாம் ஒரே context-ல handle பண்ணணும்.
- Prompt மிகப்பெரியதாகும், hallucination அதிகம்.
- One mistake-ல் எல்லாம் fail ஆகும்.
- Maintenance கஷ்டம். Model-ஐ upgrade பண்ணினால் whole behavior மாறும்.

இங்கே painful problem: **Complexity, reliability, and operability scale badly with a single agent.**

## 2. Mental Model

Single agent = ஒரே மூளை, எல்லா வேலையும் தானே பண்ணும்.

Multi-agent = specialization. ஒரு team of agents, ஒவ்வொருவரும் ஒரு role-ல திறமையாக இருப்பார்கள். Coordinator agent வேலையை split பண்ணி, assign பண்ணி, results-ஐ aggregate பண்ணும்.

அனுபவம் உள்ள engineer-க்கு இது familiar. Monolith vs microservices போலதான் இது.

## 3. How It Works

Single agent architecture:
User -> LLM + tools + memory -> Response
எல்லா reasoning, tool calling, planning ஒரே model-ல நடக்கும்.

Multi-agent architecture:
User -> Orchestrator / Coordinator -> Planner -> Specialist agents
Specialist agents: Researcher, Analyst, Writer, Coder, Tool Executor
அவை தங்களுக்குள் message pass பண்ணும். Final aggregator output-ஐ synthesize பண்ணும்.

Communication usually via messages, shared memory, or event bus. Each agent has its own system prompt, tools, maybe even different model.

## 4. Architectural Reasoning

Single agent எப்போ useful?
- Task well-defined, linear, small number of tools.
- Latency முக்கியம். Orchestration overhead வேண்டாம்.
- Team small, operational complexity குறைக்கணும்.
- Example: simple RAG chatbot, classification, single-step API call.

Multi-agent எப்போ useful?
- Task multi-step, heterogeneous skills தேவை.
- Different quality requirements: research accuracy vs summary speed.
- Failure isolation தேவை. ஒரு agent fail ஆனாலும் மற்றது தொடரும்.
- You want to upgrade/replace one capability without touching everything.
- Example: financial report generation + email + sheet update, code review pipeline, customer support triage.

Decision என்பது task complexity vs operational cost.

## 5. Trade-offs

**Single agent**
*Pros:* Simple to build, low latency, low cost, easy to debug.
*Cons:* Prompt bloat, brittle. One model must be expert in everything. Long context = hallucination. Hard to test in parts.

**Multi-agent**
*Pros:* Specialization, modularity, better reliability, you can use cheaper model for simple agents and strong model for critical ones. Easier to reason about.
*Cons:* Orchestration complexity. Inter-agent communication latency. State management கஷ்டம். Cost அதிகம். Debugging hard - which agent messed up? Coordination failures.

Important failure modes:
- Agent loop: A asks B, B asks A again.
- Context loss between agents.
- Inconsistent outputs from different agents.
- Orchestrator becomes bottleneck / single point of failure.

## 6. Practical Example

Enterprise sales analysis system.

Single agent approach:
User asks for quarterly analysis + budget suggestion + Slack + Sheet update. One agent tries to do all. It calls sales database, analyzes, writes budget, calls Slack API, calls Sheets API. Context 20k tokens. It hallucinates a product name, Slack message goes out wrong.

Multi-agent approach:
- Coordinator receives request.
- Analyst Agent: reads DB via SQL tool, returns top 3 products with numbers.
- Strategist Agent: takes numbers, suggests budget based on policy.
- Writer Agent: formats summary for Slack.
- Integrator Agent: writes to Google Sheet and posts to Slack.

Each agent has focused system prompt and limited tools. If Strategist fails, Analyst output still saved. You can test each agent independently. You can even use a smaller fast model for Writer and a strong reasoning model for Analyst.

## 7. Reasoning Challenge

உங்களிடம் customer support chatbot உள்ளது. 80% queries simple FAQs. 20% queries need DB lookup + refund processing + escalation to human.

நீங்கள் single agent vs multi-agent எதை தேர்வு செய்வீர்கள்? Model cost, latency, reliability கருத்தில் வைத்து ஏன்?

## 8. Key Takeaways

- Single agent = simplicity and speed. Multi-agent = specialization and resilience.
- Problem complexity, not coolness, should drive the choice.
- Multi-agent adds operational complexity: orchestration, messaging, failure isolation, observability.
- Architecturally, think about team boundaries: each agent is a service with a contract.
- Every solution creates new trade-off: you gain modularity but lose latency and increase cost.
