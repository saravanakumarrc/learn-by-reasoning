# Transparency

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.10 — Learn

## 1. Problem

நீங்கள் ஒரு production LLM agent-ஐ deploy பண்ணியிருக்கீங்க. Customer complaint வருது: "என் loan application reject ஆச்சு, ஏன்?"

Team கிட்ட கேட்டா, "Model அப்படி decide பண்ணிச்சு"ன்னு சொல்றாங்க.

Regulator கேட்கிறார்: "எந்த data use பண்ணீங்க? எந்த policy base பண்ணி decision எடுத்தீங்க? Audit trail என்ன?"

இப்போ தெரியலை. Log இருக்கு, ஆனா அது input-output மட்டும். *Why* தெரியலை.

இது ஒரு real pain: trust இல்லை, compliance fail ஆகுது, debugging கஷ்டம், model change பண்ண முடியலை.

Transparency இல்லாம இருந்தா, system ஒரு black box ஆகிடும்.

## 2. Mental Model

Transparency என்பது "எல்லாத்தையும் காட்டு" இல்லை. 

இது மூணு layers:

* **What happened?** - input, output, timestamp, which model/version, which data used
* **How was it decided?** - policy, features, retrieval results, tool calls, chain of reasoning
* **Why can we trust it?** - data lineage, bias checks, limits, who approved

ஒரு experienced engineer-க்கு இது ஒரு observability problem மாதிரி. ஆனா user, regulator, operator க்கு வேற level clarity வேணும்.

## 3. How It Works

Transparency ஒரு feature இல்லை, அது architecture decision.

Practical ஆக இது மூணு things-ஐ capture பண்ணும்:

1. **Decision record**: request ID, user context, prompt, system prompt, retrieved documents with IDs, tool calls, final answer. Immutable log.
2. **Explainability artifact**: model-ன் reasoning trace, RAG context, confidence scores. இது human-readable summary ஆகவும் machine-readable ஆகவும் இருக்கும்.
3. **Governance metadata**: data source lineage, model version, policy version, human-in-the-loop approval if any, risk classification.

இதை build பண்ணும்போது, நீங்கள் explicit ஆக முடிவு எடுக்கணும்: என்ன log பண்ணுறோம், எவ்வளவு நேரம் வைக்கிறோம், யார் access பண்ணலாம்.

## 4. Architectural Reasoning

Transparency எப்போ useful ஆகும்?

* High-risk decisions: credit, hiring, medical triage, fraud block
* Regulated domains: finance, healthcare, government
* Multi-agent workflows where output depends on multiple tools
* RAG systems where hallucination risk இருக்கு

Alternatives:
* No logging: fast, cheap, zero privacy overhead. ஆனா debug முடியாது.
* Output only logging: basic observability. Why தெரியாது.
* Full trace + explainability: heavy, but auditable.

Architect choose பண்ணும்போது constraint பார்க்கணும்:
* Latency: trace capture synchronous ஆக இருந்தா latency increase ஆகும்
* Cost: storage, vector search for retrieval provenance
* Privacy: PII logging சட்டப்படி limit
* Team size: who will review these traces?

## 5. Trade-offs

**Transparency vs Privacy**
Full transparency என்றால் user data முழுசா log ஆகும். GDPR, data minimization conflict ஆகும். Trade-off: redact PII, log references not raw data.

**Transparency vs Performance**
Every tool call, retrieval, reasoning step record பண்ணுவது overhead. Async pipeline, sampling, tiered retention வேணும்.

**Transparency vs Model IP**
Model reasoning expose பண்ணுவது competitive risk. Summarized explanation vs raw logits.

**Completeness vs Usability**
Too much trace = noise. Architect should define *decision-relevant* signals. என்ன info இல்லாம போனா audit fail ஆகும் என்பதை identify பண்ணணும்.

Failure mode: log இருக்கு ஆனா tamperable. Immutable append-only store, signed logs, else audit value zero.

## 6. Practical Example

Enterprise RAG for policy Q&A.

User asks: "Remote work policy என்ன?"

System:
1. User ID, session ID capture
2. Retrieve top 5 docs from vector DB, with doc IDs and scores
3. Call LLM with system prompt v2.3
4. Generate answer + citation
5. Write to Decision Ledger: request_id, timestamp, user dept, retrieved doc IDs, prompt version, model version, answer hash

6 months later audit கேட்கும்போது, நீங்கள் exact doc set reproduce பண்ண முடியும், model version தெரியும், policy change impact analyze பண்ண முடியும்.

Implementation wise: API gateway layer-ல middleware trace capture, event bus-க்கு send, separate immutable store. UI-ல "Why this answer?" button shows citations and data lineage.

## 7. Reasoning Challenge

உங்களிடம் healthcare triage chatbot இருக்கு. High risk. Regulator கேட்கிறார் transparency.

Option A: Log only final answer + user ID.
Option B: Log full prompt, retrieved patient history snippets, model reasoning trace, and store for 7 years.

Latency budget 200ms, data privacy strict. இங்கே என்ன log பண்ணுவீங்க? என்ன skip பண்ணுவீங்க? ஏன்?

## 8. Key Takeaways

* Transparency is not open source, it's auditable decision lineage for the right stakeholders
* Design for three audiences: user trust, operator debugging, regulator audit
* Capture what is needed to reconstruct *why* a decision was made, not everything
* Every transparency decision has cost, privacy, and performance trade-offs. Make them explicit
