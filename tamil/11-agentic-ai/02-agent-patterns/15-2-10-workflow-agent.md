# Workflow agent

> **Learning Path:** Agentic AI
> **Section:** 15.2.10 — Agent patterns

## 1. Problem

நீங்கள் ஒரு complex business process-ஐ automate பண்ண வேண்டும். உதாரணமாக, ஒரு loan application வந்தது.

என்னென்ன நடக்க வேண்டும்?
1. Application form-ஐ validate பண்ணணும்
2. Credit score fetch பண்ணணும்
3. Document OCR பண்ணி verify பண்ணணும்
4. Risk model-ஐ run பண்ணணும்
5. Approval-க்கு human reviewer-க்கு escalate பண்ணணும்

இதை ஒரே LLM agent-க்கு கொடுத்துவிட்டால் என்ன ஆகும்? Agent hallucinate பண்ணும், steps-ஐ skip பண்ணும், tool call-ஐ தப்பா பண்ணும், state-ஐ track பண்ண முடியாது.

**Pain point:** Open-ended agent free-form பேசும். ஆனால் business process என்பது deterministic, ordered, auditable.

இப்போது கேள்வி: Unstructured reasoning-ஐ எப்படி structured workflow-ஆக மாற்றுவது?

## 2. Mental Model

Workflow agent என்பது **orchestrated multi-step process** ஆகும்.

நினைத்துக்கொள்ளுங்கள்: ஒரு factory assembly line. ஒவ்வொரு station-லும் ஒரு specific task. Conveyor belt items-ஐ அடுத்த station-க்கு கொண்டு செல்கிறது.

Workflow agent-ல், steps முன்கூட்டியே define செய்யப்பட்டுள்ளன. ஒவ்வொரு step-ம் ஒரு agent, tool, அல்லது LLM call ஆக இருக்கலாம். Execution order fixed, state explicit.

இது ReAct-style free agent இல்லை. இது **plan first, then execute with guardrails**.

## 3. How It Works

Core idea: State machine + tools.

1. **Definition:** Workflow-ஐ DAG ஆக define பண்ணுங்கள். Nodes = tasks. Edges = dependencies.
2. **Context Passing:** ஒவ்வொரு step-ன் output அடுத்த step-க்கு input ஆகிறது. Context object ஒன்று flow ஆகிறது.
3. **Execution Engine:** Orchestrator step-by-step run பண்ணுகிறது. Step fail ஆனால் retry, skip, அல்லது human handoff.
4. **Control:** Conditional branching உண்டு. உதாரணம்: credit score < 600 என்றால் auto reject path, இல்லையெனில் continue.

LLM இங்கே decision maker அல்ல, executor. அல்லது ஒவ்வொரு step-க்கும் small, focused LLM prompt கொடுக்கப்படுகிறது.

## 4. Architectural Reasoning

Workflow agent useful ஆகும் போது:

* Process predictable, repeatable, business rule driven
* Audit trail முக்கியம் - யார் என்ன முடிவு எடுத்தார் என்பது தேவை
* Multiple tools / services / humans ஒரு sequence-ல் தேவை
* Error handling & retry வேண்டும்
* Compliance / SLA தேவை

Alternatives:
* **Single autonomous agent:** flexible ஆனால் non-deterministic, hard to debug
* **Hard-coded microservices workflow:** robust ஆனால் LLM reasoning இல்லை
* **Human-in-the-loop only:** slow, expensive

Workflow agent இவற்றுக்கு இடையே middle ground. You get structure + adaptability.

Choose பண்ணுவது ஏன்? Because business process-ஐ code-போல் treat பண்ண முடியும். Unit test பண்ணலாம், version control பண்ணலாம், observability சேர்க்கலாம்.

## 5. Trade-offs

**Pros:**
* Predictability & debuggability: எந்த step-ல் fail ஆனது தெரியும்
* Auditability: Complete trace
* Safety: Steps bounded, hallucination குறைவு

**Cons:**
* Rigidity: Unforeseen cases-ஐ handle பண்ண முடியாமல் போகலாம்
* Maintenance overhead: Workflow definition change ஆனால் update வேண்டும்
* Latency: Sequential steps add up

**Important failure modes:**
* State loss between steps → use persistent context store
* One step slow → whole workflow slow → need timeout & async
* LLM step hallucinates output format → schema validation தேவை

## 6. Practical Example

Enterprise IT support ticket automation:

Workflow: Triage → Classify → Retrieve KB → Attempt Auto-Remediation → If fails, create ticket for L2 engineer

Steps:
1. Agent extracts issue from user message
2. Classifier LLM tags category: Network / App / Password
3. If Password → call Identity API to reset → end
4. If Network → fetch recent alerts from monitoring → summarize
5. If no clear fix → create Jira ticket with context bundle

இங்கே workflow orchestrator LangGraph / Temporal போன்றதை பயன்படுத்தி run பண்ணுகிறது. Each step has retry policy, timeout, and output schema validation.

## 7. Reasoning Challenge

உங்களிடம் customer onboarding workflow இருக்கிறது. Steps: KYC verification, risk check, welcome email send. KYC 30 sec எடுக்கும், risk check 5 sec, email 1 sec.

இப்போது KYC provider down ஆனால் 2 மணி நேரம் recovery எடுக்கும். இந்த workflow-ஐ எப்படி design பண்ணுவீர்கள்? Blocking wait செய்வீர்களா? அல்லது async / retry with backoff + dead letter? எந்த trade-off ஏற்படும்?

## 8. Key Takeaways

* Workflow agent = structured multi-step orchestration, not free-form chat
* Use it when process predictable, auditable, and tool-heavy
* Trade flexibility for predictability, debuggability, and safety
* Every workflow creates new problem: rigidity, state management, and operational complexity
