# Single agent vs workflow

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.1 — Learn

## 1. Problem

உங்களிடம் ஒரு complex business task இருக்கு. உதாரணமா: "ஒரு customer complaint-ஐ analyze பண்ணி, refund தேவையா என்று முடிவு செய்து, ஒரு email அனுப்பு, மற்றும் CRM-ல update பண்ணு."

ஒரே LLM agent-ஐ கொடுத்து, "இதை செய்" என்று சொன்னீர்கள். முதல் முறை நல்லா வேலை செய்தது.

இப்போது scale ஆகுது. Complaint types வளருது, refund rules மாறுது, email tone வேறுபடுது, CRM schema மாறுது. Agent சில நேரம் hallucinate பண்ணுது, ஒரு step-ல தவறினால் முழு task-ம் fail ஆகுது. Debugging கஷ்டம். "ஏன் இந்த முடிவு எடுத்தது?" என்று audit பண்ண முடியல.

இங்கே problem என்ன? **One agent trying to do too many different concerns in one shot.**

## 2. Mental Model

Single agent vs workflow என்பது **cognitive load-ஐ எப்படி பிரிக்கிறோம்** என்பது.

* **Single agent:** ஒரு smart generalist. ஒரே model/context-ல் தொடக்கம் முதல் முடிவு வரை செய்யும். Reasoning, tool calling, decision எல்லாம் ஒன்றாக.
* **Workflow:** ஒரு assembly line. சிறிய, focused agents/steps ஒன்றன் பின் ஒன்றாக. ஒவ்வொருவருக்கும் ஒரு role, input, output, validation.

Analogy: ஒரு chef ஒரேயடியாக முழு உணவும் சமைக்கலாம். ஆனால் restaurant-ல் prep, grill, plating என்று roles பிரிக்கிறோம். Quality, speed, consistency க்காக.

## 3. How It Works

**Single agent:**
User request → Agent with tools → LLM reasons internally → calls tools in loop → produces final answer.
All steps are implicit inside one reasoning trace. Control flow flexible, but opaque.

**Workflow:**
User request → Step 1 Agent → validation/guardrail → Step 2 Agent → validation → ...
ஒவ்வொரு step-க்கும் explicit input/output schema, error handling, retry, observability.
Control flow is explicit. You can route, parallelize, fallback.

## 4. Architectural Reasoning

**Single agent useful when:**
* Task small, well-defined, low risk.
* Exploration தேவை. User question open-ended.
* Speed > auditability.
* Example: "இந்த email-ஐ summarize பண்ணு", "code snippet generate பண்ணு".

**Workflow useful when:**
* Multi-step business process with dependencies.
* Each step has different data source, policy, or success criteria.
* Need audit trail, human-in-the-loop, compliance.
* Failure isolation தேவை. ஒரு step fail ஆனாலும் மற்றவை தொடரும்.
* Example: loan approval = document extraction → verification → risk scoring → policy check → decision → notification.

Constraint அடிப்படையில் தேர்வு:
* **Latency sensitive, simple** → Single agent
* **Correctness, compliance, replay** → Workflow

## 5. Trade-offs

**Single agent:**
* Pro: Simple to build, fast to prototype, less orchestration overhead, natural for ambiguous tasks.
* Con: Reasoning opaque, harder to debug, hallucination risk high, no step-level retry, testing கஷ்டம், prompt grows too big.

**Workflow:**
* Pro: Clear boundaries, testable steps, observability, can mix models per step, failure isolation, human approval points.
* Con: More operational complexity, latency adds up, schema contracts need maintenance, over-engineering risk for simple tasks.

Important failure mode: Workflow-ல் step coupling. ஒரு step output format மாறினால் அடுத்த step break ஆகும். Hence contract testing முக்கியம்.

## 6. Practical Example

Enterprise support automation.

Single agent approach:
Customer complaint → Agent reads ticket, calls refund API, sends email, updates CRM. 
Problem: Agent sometimes refunds without checking policy, email tone inconsistent, CRM field wrong.

Workflow approach:
Step 1: Classifier Agent → complaint type
Step 2: Policy Agent → refund eligibility, reads knowledge base
Step 3: Validator Agent → checks past refunds, fraud signals
Step 4: Human approval if amount > threshold
Step 5: Executor Agent → CRM update + email send

இப்போது ஒவ்வொரு step-ம் log ஆகும், retry ஆகும், மாற்றம் செய்யலாம். Policy update ஆனால் Policy Agent மட்டும் மாற்றினால் போதும்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. எல்லாருக்கும் same event தேவை. Consumer processing speed வேறுபடுகிறது. Producer-ஐ block பண்ணக்கூடாது. Replay-ம் வேண்டும். இங்கே என்ன architecture தேர்வு செய்வீர்கள்? ஏன்?

Wait, இது event streaming question. சரியான challenge:

உங்களிடம் "research a competitor, summarize financials, draft a sales email, and post to CRM" என்ற task உள்ளது. தற்போது ஒரே agent பயன்படுத்துகிறீர்கள். சில நேரம் email draft தவறாக வருகிறது, research incomplete ஆகிறது. Audit தேவை. 

Single agent-ஐ improve பண்ணுவீர்களா, workflow-ஆக பிரிப்பீர்களா? எந்த steps-ஐ பிரிப்பீர்கள், எதை ஒன்றாக வைப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Single agent = flexibility and speed, workflow = control and reliability.
* Task complexity, risk, audit needs வளரும்போது workflow-க்கு மாறு.
* ஒவ்வொரு architectural solution-ம் trade-off உருவாக்கும்: simplicity vs observability.
* Design decision-ஐ problem constraints-ல் இருந்து தொடங்கு, tool-ல் இல்லை.

இப்போது உங்களுக்கு தெரியும்: **இதை ஒரே agent-ல் செய்ய முடியுமா, அல்லது steps-ஆக பிரிக்க வேண்டுமா என்று எப்படி reason பண்ணுவது.**
