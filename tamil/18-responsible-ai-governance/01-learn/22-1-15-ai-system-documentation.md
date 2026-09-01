# AI system documentation

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.15 — Learn

## 1. Problem

நீங்கள் ஒரு production LLM service-ஐ build பண்ணியிருக்கீங்க. RAG pipeline இருக்கு, vector database இருக்கு, agent workflow இருக்கு.

6 மாசம் கழித்து:

* ஒரு new engineer join பண்ணார். "இந்த prompt எங்க இருக்கு? Why this retrieval threshold 0.72?"
* Compliance team கேட்கிறார்: "இந்த model எந்த data-ல train ஆச்சு? Data retention policy என்ன?"
* Incident ஆனது. Production-ல output hallucinations அதிகமாகிறது. யார் மாற்றம் பண்ணினார்? எந்த version?
* Audit-க்கு: "இந்த decision எப்படி explain பண்ணுவீங்க?"

இதெல்லாம் வரும்போது docs இல்லாமல், scattered Notion pages, Slack threads, code comments-ல மட்டும் தகவல் இருந்தால், system-ஐ யாராலும் trust பண்ண முடியாது.

**What goes wrong if we don't have this?** Knowledge silo, compliance risk, slow onboarding, unsafe changes, audit failure.

## 2. Mental Model

AI system documentation என்பது code-க்கு அடுத்த layer-ல உள்ள **operational memory**.

ஒரு distributed system-லயும் நாம் runbook, architecture diagram, API contract வைக்கிறோம். AI system-ல அதோடு கூட:

* data lineage
* model card
* prompt version
* evaluation results
* risk and mitigation

எல்லாம் ஒரே source of truth-ல இருக்கணும்.

எளிமையாக சொன்னால்: **"இந்த system ஏன் இப்படி build ஆச்சு, என்ன data use ஆகுது, எப்படி fail ஆகும், யார் responsible"** என்பதை யாரும் கேட்டாலும் 5 நிமிடத்தில் பதில் கிடைக்க வேண்டும்.

## 3. How It Works

Practical-ஆ, documentation என்பது 4 layers.

**1. System Context**
Business problem, scope, stakeholders, success metrics. உதாரணம்: Customer support agent, latency < 2s, hallucination rate < 1%.

**2. Architecture & Data Flow**
Services, message queue, vector DB, LLM provider, RAG pipeline, agent tools. Request flow diagram.

**3. Model & Data Artifacts**
Model card: model name, version, fine-tune data, training cutoff, license.
Data card: source, PII handling, retention, consent, bias assessment.
Prompt library: versioned prompts, parameters, examples.

**4. Governance & Ops**
Evaluation suite, test sets, drift monitoring, rollback plan, incident history, access control, audit log.

இதை code repo-வுக்கு அருகில் வைக்கவும். Docs as code: Markdown + diagrams + automated metrics.

## 4. Architectural Reasoning

எப்போது இது useful ஆகும்?

* Team size > 3 people
* Model அல்லது prompt மாற்றம் frequent
* External audit / regulatory requirement உள்ளது
* Production incident risk உள்ளது

Constraint இது address பண்ணுவது: **knowledge decay and accountability gap**.

Alternatives:
* Ad-hoc wiki: cheap ஆரம்பத்தில், ஆனால் stale ஆகும்.
* Only code comments: developers-க்கு மட்டும் புரியும், compliance-க்கு இல்லை.
* Full enterprise GRC tool: heavy, slow.

Architect decision: Lightweight, versioned docs in repo + automated generation for metrics.

Why choose? Engineer can reason about system without tribal knowledge. Audit can happen without heroics.

## 5. Trade-offs

* **Accuracy vs Maintenance burden.** Auto-generated metrics help, ஆனால் narrative docs manual effort தேவை. Balance பண்ணணும்.
* **Granularity vs Readability.** Too detailed -> no one reads. Too high level -> useless. Audience segmentation முக்கியம்: exec summary vs engineer deep dive.
* **Openness vs Security.** Sensitive prompt or data details public repo-ல வைக்கக்கூடாது. Access control தேவை.
* **Staleness risk.** Docs மாறாமல் code மாறினால் trust இழக்கும். CI check: doc updated? Evaluation results auto-pushed?

Important failure mode: Documentation drift. Solution: make docs part of PR checklist, and embed key facts in code as structured metadata.

## 6. Practical Example

Enterprise finance chatbot.

Problem: Loan eligibility queries. RAG over policy PDFs + customer data.

Documentation set:

* Architecture diagram: API Gateway -> Auth -> Orchestrator service -> Retriever -> Vector DB -> LLM -> Guardrail -> Response.
* Data card: Policy PDFs v3.2, last updated 2024-11, PII masked, retention 90 days.
* Prompt version 1.4, temperature 0.2, max tokens 512.
* Evaluation: 500 golden questions, accuracy 92%, hallucination 0.8%.
* Risk: Model may leak internal rates. Mitigation: output filter + human review for rate queries.

6 மாசம் கழித்து new model upgrade வரும்போது, engineer 10 நிமிடத்தில் முந்தைய decision-ஐ புரிந்துகொண்டு safe rollout plan பண்ண முடியும். Auditor கேட்டால் data lineage காட்ட முடியும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு multi-agent RAG system இருக்கு. 3 agents: Planner, Retriever, Writer. Prompts weekly மாறுகிறது. Evaluation metrics daily run ஆகிறது.

Compliance கேட்கிறது: "Last 3 months-ல என்ன prompt மாற்றம் பண்ணீங்க? அதனால் accuracy எப்படி மாறியது?"

உங்களிடம் version control இல்லை, metrics scattered in Slack.

இங்கே documentation strategy என்னவாக இருக்க வேண்டும்? What artifacts will you create, where will you store, and how will you ensure it stays fresh?

## 8. Key Takeaways

* AI system docs = system understanding + accountability + auditability.
* Version prompts, data, model, evaluations together. Not separately.
* Docs as code, close to repo, auto-generate what you can, manually curate what you must.
* Every architectural decision should be explainable to next engineer and auditor without tribal knowledge.

இதை வைத்தால் மட்டுமே Responsible AI & Governance real ஆகும், பேப்பரில் மட்டும் இல்லை.
