# Agent specialization

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.3 — Learn

## 1. Problem

ஒரே general agent-ஐ வைத்து எல்லா task-உம் செய்ய முடியுமா? Customer support chat, code review, invoice extraction, real-time trading decision — எல்லாத்தையும் ஒரே LLM agent-இல் போட்டால் என்ன ஆகும்?

Latency அதிகமாகும். Context window நிரம்பும். Prompt பெரிதாகும். ஒரு task-க்கு தேவையான tool, data source, reasoning depth மாறும். General agent-க்கு ஒவ்வொரு முறையும் "என்ன செய்யணும்" என்று கற்றுக்கொடுக்க வேண்டும். Error rate உயரும். Evaluation கடினமாகும்.

Pain point: **One model, many jobs = jack of all trades, master of none.** Production-ல் reliability, cost, latency எல்லாம் பாதிக்கும்.

## 2. Mental Model

Agent specialization என்பது **work specialization போல**.

ஒரு factory-ல் ஒரே worker எல்லா part-ஐயும் make பண்ணுவதை விட, assembly line-ல் ஒவ்வொரு worker-க்கும் ஒரு skill கொடுப்பது எப்படி efficiency கூட்டுமோ, அதே போல agent-களுக்கும் role கொடுப்பது.

Specialized agent = narrow scope + specific tools + specific data + specific success criteria.

General orchestrator = யார் என்ன செய்ய வேண்டும் என்பதை decide பண்ணும்.

## 3. How It Works

ஒரு multi-agent system-ல் specialization மூன்று அடுக்கில் வரும்:

**a. Skill specialization:** ஒரு agent code generation மட்டும். மற்றொரு agent summarization மட்டும்.
**b. Domain specialization:** Finance agent, Legal agent, HR agent. Same capability, different knowledge base.
**c. Workflow specialization:** Ingestion agent, Validation agent, Enrichment agent, Decision agent.

ஒவ்வொரு agent-க்கும்:
* Clear input schema
* Clear output schema
* Allowed tools list — e.g., vector DB access, calculator, API call
* Prompt template optimized for that job
* Evaluation metric — e.g., extraction F1, latency < 500ms

Orchestrator agent வரும் request-ஐ classify பண்ணி, சரியான specialist-க்கு route பண்ணும். Result-ஐ combine பண்ணும்.

## 4. Architectural Reasoning

When use பண்ணணும்?

* Task variety அதிகம், ஆனால் ஒவ்வொரு task-க்கும் pattern repeat ஆகிறது.
* Quality & latency requirements task-க்கு task-ல் வேறுபடுகிறது.
* Different data sources / tools தேவைப்படுகிறது. General agent-க்கு எல்லா tool-ஐயும் கொடுத்தால் prompt மிகப் பெரியதாகும்.
* Cost control தேவை. Small specialized model for simple task, large model for complex task.

Alternatives:
* **One big general agent with huge prompt.** Simple start, but scaling-ல் brittle.
* **Fine-tuned model per domain.** Strong performance, but training & maintenance cost அதிகம்.
* **Specialized agents with same base model but different prompts/tools.** Good balance. No retraining.

Architect decision: Specialization is about **boundaries**. System boundary clear ஆனால் reasoning easy, failure isolation easy.

## 5. Trade-offs

**Reliability vs Complexity.** Specialized agents தனித்தனியாக test பண்ணலாம், failure isolate பண்ணலாம். ஆனால் orchestration logic, handoff protocol, error handling complex ஆகும்.

**Latency vs Quality.** Specialist smaller prompt + focused tools = faster, cheaper. ஆனால் cross-domain reasoning தேவைப்பட்டால் handoff overhead வரும்.

**Maintainability vs Duplication.** ஒவ்வொரு agent-க்கும் prompt, tool config தனியாக. Change propagation தேவை. General agent-ல் ஒரே place-ல் மாற்றம்.

**Evaluation easier but coordination harder.** Specialist-க்கு metric clear. Orchestrator-க்கு end-to-end correctness ensure பண்ண வேண்டும்.

Failure mode: Wrong routing. Orchestrator தவறான specialist-க்கு போனால் garbage in garbage out. Handoff-ல் context loss. Agent-கள் தங்களுக்குள் loop பண்ணி deadlock.

## 6. Practical Example

Enterprise RAG assistant.

General agent: "Employee question answer பண்ணு". Poor results.

Specialized:
* **Router Agent:** Question intent classify — HR policy, IT support, Finance, Product docs.
* **Retriever Agent:** Domain-specific vector DB-க்கு query. HR agent-க்கு HR embeddings only.
* **Extractor Agent:** Invoice / payslip PDF-ல் fields extract. Tools: OCR + regex.
* **Summarizer Agent:** Long policy doc-ஐ concise answer-ஆக மாற்று.
* **Validator Agent:** PII leak உள்ளதா? Policy compliance உள்ளதா? Check.

ஒவ்வொரு agent-க்கும் different latency SLO. Retriever 200ms, Summarizer 1s. Cost different. Failure of Extractor affects only finance flow, not HR.

## 7. Reasoning Challenge

உங்களிடம் customer support platform இருக்கு. 3 types tickets வருகின்றன: Billing dispute, Technical bug, Feature request. ஒரே general agent-ஐ use பண்ணும்போது average resolution time 90 seconds, accuracy 72%.

Specialization செய்யலாம் என்றால் என்ன agents பிரிப்பீர்கள்? ஒவ்வொரு agent-க்கும் என்ன tool/data தேவை? Orchestrator எப்படி route பண்ணும்? Specialization-ஆல் என்ன new problem create ஆகும்?

## 8. Key Takeaways

* Specialization solves **scope creep** and **context overload** in general agents.
* Agent = narrow input/output + specific tools + measurable success.
* Orchestrator + specialists pattern gives control over latency, cost, quality per workflow.
* Every specialization adds coordination cost. Boundaries must be clear, handoffs explicit.
* Start general, specialize when pain shows up in latency, accuracy, or cost.
