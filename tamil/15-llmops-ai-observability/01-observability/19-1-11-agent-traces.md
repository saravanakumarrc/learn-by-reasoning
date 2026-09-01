# Agent traces

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.11 — Observability

## 1. Problem

உங்க team ஒரு agent build பண்ணியிருக்கு. Tool use பண்ணும், multiple steps போகும், LLM call பண்ணும்.

Customer சொல்றார்: "இந்த request-க்கு output தப்பா வந்திருக்கு."

உங்களுக்கு என்ன தெரியும்? 
Final output மட்டும் தெரியும். Agent எந்த tool-ஐ call பண்ணுச்சு, எந்த prompt use பண்ணுச்சு, எந்த reasoning step-ல தவறு நடந்துச்சு, எவ்வளவு latency வந்துச்சு - இதெல்லாம் black box.

Traditional API logging வச்சாலும் போதாது. ஏன்னா agent என்பது ஒரு single request/response அல்ல. அது ஒரு **multi-step execution graph**.

Without trace, debug பண்ணுவது குருட்டு தனமாகும். Production-ல bug reproduce பண்ண முடியாது, cost எங்கே போகுதுன்னு தெரியாது, failure mode எது என்று predict பண்ண முடியாது.

**What goes wrong if we don't have this?** Silent failures, unpredictable cost spikes, inability to improve prompts, and no way to prove compliance.

## 2. Mental Model

Agent trace என்பது ஒரு request-ன் **complete execution history**-யை capture பண்ணும் structured record.

ஒரு distributed system-ல ஒரு request எப்படி service-ல இருந்து service-க்கு போகுதுன்னு trace பண்றோமோ, அதே போல் agent-ல ஒரு user query எப்படி LLM call, tool call, reasoning step, retrieval step-ன்னு flow ஆகுதுன்னு trace பண்ணணும்.

Mental model: `Trace = Span Tree`

Root span = user request. 
Children spans = LLM inference, tool execution, vector search, RAG retrieval, code execution, etc.

ஒவ்வொரு span-லும்: start time, end time, inputs, outputs, metadata, errors, cost, tokens.

இது ஒரு observability backbone.

## 3. How It Works

Agent trace build ஆவது மூன்று விஷயங்களை capture பண்ணி:

**1. Execution flow:** Agent ஒவ்வொரு step-லும் என்ன செய்தது. Tool A call பண்ணியதா? அதற்கு முன் prompt என்ன? LLM output என்ன?

**2. Context:** Prompt template, system message, retrieved documents, tool parameters, environment variables.

**3. Telemetry:** Latency, token usage, cost, retry count, error type, LLM provider, model version.

Implementation-ல இதை செய்ய, agent framework-ல middleware / instrumentation போடணும். ஒவ்வொரு LLM call, tool call முன்/பின் hook-ல span create பண்ணி context propagate பண்ணணும்.

Trace store ஆகும் போது, இது time-series data + structured logs + graph. Query பண்ணும்போது, ஒரு specific user request-ன் முழு path-ஐ reconstruct பண்ண முடியும்.

## 4. Architectural Reasoning

**எப்போது useful?**
Agent ஒன்றுக்கு மேற்பட்ட steps வச்சிருக்கும் போது. Stateless single LLM call-க்கு தேவை குறைவு. Multi-tool, multi-turn, RAG, agentic loop உள்ள system-க்கு must-have.

**எந்த constraint-ஐ address பண்ணும்?**
Debuggability, reliability, cost control, performance optimization.

Alternatives:
* Just logs: unstructured, correlation கடினம்.
* Metrics only: average latency தெரியும், but which step fail என்று தெரியாது.
* Manual replay: non-deterministic, expensive.

Agent trace-ஐ choose பண்ணும் reason: You need **causality**. Which decision led to which tool call led to wrong output.

Trade-off இங்கே: Observability adds overhead. ஒவ்வொரு span capture பண்ணுவது latency-ஐ கொஞ்சம் அதிகப்படுத்தும், storage cost வரும், PII leak risk வரும்.

## 5. Trade-offs

**1. Fidelity vs Cost**
Full prompt + output + tool input/output capture பண்ணினால் debug சுலபம். ஆனால் storage huge ஆகும், sensitive data leak risk. Solution: sampling, redaction, retention policy.

**2. Structured vs Flexible**
Strict schema வச்சால் query சுலபம். ஆனால் agent behavior evolve ஆகும் போது schema break ஆகும். Flexible JSON store பண்ணினால் query கடினம்.

**3. Real-time vs Batch**
Real-time tracing வேண்டும் என்றால் alert trigger பண்ணலாம். ஆனால் high cardinality data stream கையாள வேண்டும். Batch analysis cheap ஆனால் slow.

**4. Privacy & Compliance**
Traces-ல user query, internal reasoning, tool outputs இருக்கும். GDPR, PII masking தேவை. Trace retention என்பது legal risk.

Failure mode: Trace loss = blind spot. Incomplete spans = misleading root cause.

## 6. Practical Example

Enterprise support agent. User: "My invoice #12345 is wrong, please refund."

Trace shows:
Root span: user request
- Span 1: LLM classify intent -> `refund_request`
- Span 2: RAG retrieval -> fetch invoice doc, latency 800ms
- Span 3: Tool `get_invoice` -> success, amount $500
- Span 4: LLM decide -> call `create_refund` tool
- Span 5: Tool `create_refund` -> error `insufficient_permission`

இங்கே trace இல்லாமல் நீங்கள் பார்ப்பது: "Refund failed". Trace உடன் நீங்கள் பார்ப்பது: Permission error at tool level, not LLM hallucination.

இதன் மூலம் நீங்கள் decide பண்ணலாம்: Tool auth fix பண்ணணும், அல்லது agent-க்கு fallback prompt கொடுக்கணும்.

இதே trace aggregation மூலம் நீங்கள் கண்டுபிடிக்கலாம்: 15% requests-ல RAG retrieval slow ஆகுது, அது timeout-க்கு வழிவகுக்குது.

## 7. Reasoning Challenge

உங்களிடம் production agent இருக்கு. Daily 1M requests. ஒவ்வொரு trace-லும் full prompt + output + tool I/O store பண்றீங்க. Cost மாசம் $20k ஆகுது. Debugging still difficult ஏன்னா too much noise.

நீங்கள் என்ன trade-off செய்வீர்கள்? Sampling எப்படி design பண்ணுவீங்க? Which spans முக்கியம்? PII எப்படி handle பண்ணுவீங்க?

## 8. Key Takeaways

* Agent trace என்பது request-ன் step-by-step execution graph, not just logs.
* Trace இல்லாமல் multi-step agent-ஐ debug, improve, cost control பண்ண முடியாது.
* Trace design-ல முக்கிய trade-offs: fidelity vs cost, privacy vs debuggability, real-time vs batch.
* Good traces help you move from "output wrong" to "which step failed and why".
