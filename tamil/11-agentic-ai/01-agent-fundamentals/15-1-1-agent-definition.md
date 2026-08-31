# Agent definition

> **Learning Path:** Agentic AI
> **Section:** 15.1.1 — Agent fundamentals

## 1. Problem

உங்களிடம் ஒரு chatbot இருக்கு. User கேட்கிறார்: "என் last 3 invoices-ஐ check பண்ணி, total > 10k என்றால் finance team-க்கு mail அனுப்பு."

Chatbot என்ன செய்யும்? 
தற்போதைய LLM-க்கு மட்டும் கொடுத்தால் அது knowledge-ல இருந்து ஒரு பதில் உருவாக்கும். Database-ஐ பார்க்காது, mail அனுப்பாது.

இங்கே problem என்ன?
User ஒரு goal கொடுக்கிறார், அது முடிக்க பல steps தேவை. Information தேட வேண்டும், decision எடுக்க வேண்டும், action எடுக்க வேண்டும், loop பண்ண வேண்டும்.

இதை ஒரு static prompt + completion-ஆல் செய்ய முடியாது. ஒரு system தேவைப்படுகிறது: goal புரிந்து, environment-ஐ observe பண்ணி, reason பண்ணி, action எடுத்து, result-ஐ பார்த்து திரும்ப reason பண்ணும்.

இந்த தேவையிலிருந்து தான் Agent concept வருகிறது.

## 2. Mental Model

Agent = Goal oriented autonomous system with a loop.

Core loop:
**Observe → Reason → Act → Observe...**

ஒரு LLM என்பது reasoning engine மட்டுமே. Agent என்பது அந்த engine-ஐ ஒரு loop-ல வைத்து, tools, memory, planning-உடன் கட்டுப்படுத்தும் wrapper.

அனலாகி: LLM என்பது brain. Agent என்பது brain + eyes + hands + memory + plan.

அதாவது Agent என்பது **சுயமாக செயல்படும் software entity** which takes input, sets internal goal, uses tools to interact with external world, and continues until goal achieved or fails.

## 3. How It Works

Minimal agent architecture:

1. **LLM as Reasoner / Planner**: Goal-ஐ parse பண்ணி next step என்ன என்று decide பண்ணும்.
2. **Tools / Actions**: API call, database query, search, send email, call another service. இதுதான் environment-உடன் connect ஆகும் வழி.
3. **Memory**: Short-term context window மற்றும் long-term memory / vector database. முந்தைய steps-ஐ நினைவில் வைத்துக்கொள்ள.
4. **Loop Controller**: ReAct style - Reason then Act. Output-ஐ observe பண்ணி மீண்டும் input-ஆக்கு.

உதாரண flow:
User: "Find high-value customers and create report"
Agent: Plan → step1: define high-value? → tool: query CRM → observe results → reason: 120 customers found → step2: fetch orders → tool call → observe → step3: generate report → tool: write file → done.

## 4. Architectural Reasoning

எப்போது Agent தேவை?

* Task multi-step ஆக இருக்கும்போது
* External data / actions தேவைப்படும்போது
* Dynamic decision making தேவைப்படும்போது
* User-இடம் constant clarification வாங்க முடியாத போது

Alternatives:
* **RAG + Chatbot**: Single query, external knowledge தேவை. Loop இல்லை. Action இல்லை.
* **Hardcoded Workflow / Orchestration**: Steps fixed. Flexibility இல்லை.
* **Human in the loop**: Slow.

Agent-ஐ choose பண்ணும்போது நீங்கள் trade-off பண்ணுகிறீர்கள்: autonomy vs predictability.

## 5. Trade-offs

**Autonomy vs Control**: Agent தன்னிச்சையாக tool கூப்பிடும். Wrong action வாய்ப்பு உள்ளது. Guardrails, tool allow-list தேவை.

**Latency & Cost**: Loop ஒவ்வொரு step-க்கும் LLM call. 1 user request → 5-10 LLM calls → cost & latency increase.

**Failure modes**: Tool fails, hallucinated tool name, infinite loop, context overflow. Observability முக்கியம்.

**Consistency**: Same goal-க்கு ஒவ்வொரு முறையும் வெவ்வேறு plan வரலாம். Determinism குறைவு.

**Security**: Agent-க்கு tools access கொடுக்கிறீர்கள் என்றால் அது privilege escalation போல. Input sanitization, output validation தேவை.

## 6. Practical Example

Enterprise support agent.

Problem: Customer ticket வந்தால், order status பார்க்க, refund policy check பண்ண, சில conditions-க்கு refund issue பண்ண.

Agent setup:
* Memory: ticket history
* Tools: getOrder API, getPolicy API, createRefund API, sendEmail API
* Planner: LLM

Flow:
Observe ticket → Reason: need orderId → Act: getOrder → Observe: order delayed → Reason: policy allows refund → Act: createRefund → Observe success → Act: sendEmail → Done.

இது human agent-ஐ replace பண்ணாது, but first-pass resolution-ஐ automate பண்ணும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு finance agent இருக்கு. அதற்கு database read மற்றும் email send tool மட்டுமே கொடுக்கப்பட்டுள்ளது. User கேட்கிறார்: "என் account-ஐ close பண்ணு".

Agent என்ன செய்ய வேண்டும்? Account close செய்ய delete API தேவை. அது இல்லை.

இங்கே நீங்கள் என்ன design decision எடுப்பீர்கள்? Agent-ஐ run செய்ய விடுவீர்களா? Guardrail எப்படி வைப்பீர்கள்?

## 8. Key Takeaways

* Agent என்பது LLM + Tools + Memory + Loop. LLM மட்டும் agent இல்லை.
* Core value என்பது goal-directed autonomous action, not just answer generation.
* Every agent introduces non-determinism, cost, latency, and safety risks.
* Agent-ஐ design பண்ணும்போது tools, boundaries, observability மூன்றும் முதலில் முடிவு செய்ய வேண்டும்.
