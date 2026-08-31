# Autonomous agent

> **Learning Path:** Agentic AI
> **Section:** 15.2.9 — Agent patterns

## 1. Problem

உங்க system-ல ஒரு user கேட்கிறார்: "Last quarter sales report எடு, top 3 products கண்டுபிடி, அதுக்கு marketing email draft பண்ணி sales team-க்கு அனுப்பு."

இதை ஒரே API call-ல செய்ய முடியுமா?

இல்லை. இது multiple steps. Database query, analysis, text generation, email send. ஒவ்வொன்றும் வெவ்வேறு tools.

Traditional workflow-ல நீங்கள் அனைத்தையும் ஒரே code-ல hard-code செய்வீர்கள். Requirement மாறினால் code மாறும். New tool வந்தால் மீண்டும் refactor.

இந்த pain point தான் **Autonomous agent** concept-ஐ உருவாக்கியது. User goal-ஐ புரிந்து கொண்டு, தன்னிச்சையாக steps திட்டமிட்டு, tools-ஐ use செய்து, முடிவை அடையும் system.

## 2. Mental Model

Agent என்பது **goal-driven loop**.

`Observe → Reason → Act → Observe`

ஒரு experienced engineer போல சிந்திக்கிறது. LLM தான் reasoning engine. Tools தான் hands. Memory தான் experience.

Autonomous agent என்றால் human intervention இல்லாமல் தொடர்ச்சியாக திட்டமிட்டு செயல்படும்.

## 3. How It Works

ஒரு agent-க்கு மூன்று core parts தேவை:

**1. LLM as brain:** Goal-ஐ புரிந்து, next step என்ன என்பதை decide பண்ணும்.
**2. Tools:** Database, API, search, code execution, email sender போன்றவை.
**3. Memory:** Short-term context window + long-term memory store. இல்லாவிட்டால் ஒவ்வொரு step-லும் மறந்துவிடும்.

Flow:
1. User goal input வரும்.
2. Agent plan generate பண்ணும். e.g., `fetch sales data → filter quarter → aggregate → find top 3 → draft email`
3. ஒவ்வொரு step-க்கும் சரியான tool-ஐ தேர்ந்தெடுத்து call பண்ணும்.
4. Tool output-ஐ observe செய்து, plan-ஐ update செய்யும். Failure வந்தால் retry அல்லது alternative plan.
5. Goal complete ஆனதும் respond.

## 4. Architectural Reasoning

இது எப்போது useful?

- **Multi-step, tool-using tasks** உள்ள போது.
- User intent ambiguous ஆக இருக்கும் போது.
- Process dynamic ஆக மாறும் போது.

Alternatives என்ன?

**RAG only:** Single question → retrieve → answer. Tools use இல்லை. Multi-step இல்லை.
**Hard-coded workflow:** Reliable ஆனால் rigid. New requirement வந்தால் developer தேவை.
**Agent:** Flexible, adaptable. ஆனால் non-deterministic.

Architect ஏன் agent தேர்வு செய்வார்?
Business logic வேகமாக மாறும், human-like reasoning தேவை, tool ecosystem பெரியது. ஆனால் முழு autonomy வேண்டாம் என்றால், agent-ஐ human-in-the-loop-ல் வைத்து கட்டுப்படுத்தலாம்.

Agent patterns-ல் முக்கியமானவை:
* **ReAct:** Reason then Act. Step by step.
* **Planner-Executor:** Separate planning and execution.
* **Reflection:** Output-ஐ self-evaluate செய்து improve.
* **Multi-agent:** Different agents for different skills, coordinator ஒன்று.

## 5. Trade-offs

**1. Reliability vs Flexibility**
Agent flexible ஆனால் unpredictable. Same prompt-க்கு வெவ்வேறு plan வரலாம். Production-ல determinism முக்கியம் என்றால், tool choice, plan validation போன்ற guardrails தேவை.

**2. Cost vs Capability**
ஒவ்வொரு step-க்கும் LLM call. Token cost, latency இரண்டும் அதிகரிக்கும். 10 step task = 10 LLM calls. Caching, prompt optimization, smaller models for tool selection போன்ற optimizations தேவை.

**3. Safety and Control**
Agent தவறான tool-ஐ தவறான parameter-உடன் call பண்ணலாம். Email அனுப்பும் tool-க்கு அதிகாரம் கொடுத்தால், hallucination-ல data leak ஆகலாம். Tool permissions, validation layer, human approval for critical actions must.

**4. Observability**
Traditional code-ல் trace easy. Agent-ல் plan, tool calls, reasoning traces எல்லாம் log செய்ய வேண்டும். இல்லாவிட்டால் debug செய்ய முடியாது.

## 6. Practical Example

Enterprise support agent.

User: "My invoice #12345 is wrong. Last month discount apply ஆகல."

Agent steps:
1. `observe` user query → extract invoice id.
2. `reason` → need to fetch invoice, check discount policy, verify.
3. `act` → call `billing API` to fetch invoice.
4. `observe` → discount not applied.
5. `reason` → check if customer eligible for discount.
6. `act` → call `CRM` tool to fetch customer tier.
7. `act` → call `policy DB` to confirm discount rule.
8. `act` → draft correction email via `email tool`.
9. Final summary to user.

இங்கே agent ஒரே interface-ல multiple backend systems-ஐ orchestrate செய்கிறது. Hard-code செய்தால், discount policy மாறினால் code deploy வேண்டும். Agent-ல் tool description மட்டும் update செய்தால் போதும்.

## 7. Reasoning Challenge

உங்களிடம் financial reconciliation agent உள்ளது. ஒவ்வொரு நாளும் 10,000 transactions-ஐ match செய்ய வேண்டும். Agent தற்போது ஒவ்வொரு transaction-க்கும் LLM-ல் reason பண்ணி tool call செய்கிறது. Cost அதிகம், latency அதிகம்.

இங்கே agent pattern எப்படி மாற்றுவீர்கள்? Full autonomy வேண்டாம், accuracy முக்கியம். ஏன்?

## 8. Key Takeaways

* Agent என்பது goal-driven observe-reason-act loop, LLM + tools + memory.
* Agent-ஐ உருவாக்குவது hard-coded workflow-க்கு மாற்றாக flexibility கொடுக்கிறது, ஆனால் reliability, cost, safety trade-off வருகிறது.
* Production agent-க்கு observability, tool guardrails, human-in-the-loop முக்கியம்.
* Pattern தேர்வு task complexity, risk, cost constraint-ஐ பொறுத்தது.
