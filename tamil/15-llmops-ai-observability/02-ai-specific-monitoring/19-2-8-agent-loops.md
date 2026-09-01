# Agent loops

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.8 — AI-specific monitoring

## 1. Problem

ஒரு agent-ஐ நீங்கள் production-ல விட்டீர்கள். User ஒரு request கொடுக்கிறார், agent ஆரம்பத்தில் ஒரு LLM call பண்ணி, அதன் படி tool-ஐ call பண்ணுகிறது, tool result வந்ததும் மீண்டும் LLM-க்கு போகிறது. இது 5-10 steps ஓடுகிறது.

இப்போது என்ன கேள்வி வரும்?

* இந்த loop எத்தனை steps-க்குள் முடியும்?
* ஒரு step தோல்வி அடைந்தால் loop முழுக்க fail ஆகுமா?
* Agent ஒரே tool-ஐ திரும்ப திரும்ப call பண்ணுகிறதா? infinite loop-ல மாட்டிக்கொண்டதா?
* Cost எவ்வளவு ஆகிறது? latency எவ்வளவு?

Traditional API monitoring-ல ஒரு request = ஒரு latency, ஒரு status code. Agent-ல ஒரு user request = பல LLM calls + பல tool calls + பல intermediate decisions. அதை ஒரு single request-ஆக monitor பண்ணினால் உங்களுக்கு எதுவும் தெரியாது.

**What goes wrong if we don't have this?** Silent cost blow-up, unpredictable latency, agent hallucination loop, tool misuse, மற்றும் production incident-க்கு root cause கண்டுபிடிக்க முடியாமல் போகும்.

## 2. Mental Model

Agent loop-ஐ ஒரு **multi-hop workflow** என்று பாருங்கள். ஒவ்வொரு hop-ம் ஒரு decision point.

```
User Query -> LLM Reason -> Tool Call -> Tool Result -> LLM Reason -> ...
```

Monitoring என்பது ஒவ்வொரு hop-ஐயும் track பண்ணுவது, அதன் quality, cost, latency, மற்றும் loop health-ஐ பார்ப்பது. முழு trace ஒன்று = ஒரு user request.

## 3. How It Works

AI-specific monitoring என்பது மூன்று layer-ஐ track பண்ணும்:

**1. Trace / Span Layer:** ஒரு agent execution-க்கு ஒரு trace ID. அதனுள் ஒவ்வொரு LLM call, tool call, retrieval step ஒரு span. Jaeger/Tempo போல trace பண்ணி, ஆனால் span attributes-ல token count, model name, prompt, tool name சேர்க்க வேண்டும்.

**2. Agent Metrics Layer:** Loop-specific metrics.
* `agent.steps_per_request` - average steps
* `agent.loop_count` - same tool repeated?
* `agent.tool_success_rate`
* `agent.latency_p95_per_step`

**3. Quality / Observability Layer:** LLM output quality signals.
* Tool call validity, schema compliance
* Repeating reasoning, self-correction count
* Final answer relevance / guardrail hits

இதை implement பண்ண OpenTelemetry spans + custom attributes + LLM observability tools like LangSmith, Arize, or custom logs.

## 4. Architectural Reasoning

இது ஏன் useful?

* **Cost control:** ஒரு request 1 LLM call இல்லை, 8 calls. Token usage multiply ஆகும்.
* **Latency predictability:** ஒவ்வொரு step-க்கும் network + LLM latency. User-க்கு 30 sec wait ஏற்படலாம்.
* **Failure isolation:** LLM timeout ஆனால் tool call தொடருமா? Retry எங்கே போட வேண்டும்?
* **Loop detection:** Agent stuck ஆனால் அதை early stop பண்ண வேண்டும்.

Alternatives:
* Traditional APM மட்டும்: request latency மட்டும் தெரியும், agent internal reasoning தெரியாது.
* Log-only: post-mortem-க்கு மட்டும் உதவும், real-time alerting இல்லை.
* LLM provider dashboard: model level metrics மட்டும், your tool calls தெரியாது.

நீங்கள் architect ஆக choose பண்ணுவது: Trace per agent execution + step-level metrics + alert on anomalies.

## 5. Trade-offs

**Granularity vs Overhead:** ஒவ்வொரு LLM prompt/response-ஐயும் store பண்ணினால் cost & storage அதிகம். Sampling or summarization தேவை.

**PII / Privacy:** Prompt-ல user data இருக்கலாம். Logging-க்கு முன் redaction தேவை. Compliance risk.

**Signal vs Noise:** ஒவ்வொரு step-லும் metrics வரும். எது alert worthy? Loop repetition, sudden step increase, tool failure spike மட்டும் alert பண்ண வேண்டும்.

**Observability cost:** Tracing itself adds latency and storage cost. High volume agent-க்கு 10-20% extra cost வரும்.

Failure modes:
* Infinite loop: Agent same tool-ஐ திரும்ப திரும்ப call பண்ணும். `max_steps` இல்லாமல் cost blow-up.
* Tool drift: Tool schema மாறினால் agent invalid call பண்ணும். Success rate drop ஆகும்.
* Cascading retry: LLM transient failure-க்கு retry பண்ணி latency explode ஆகும்.

## 6. Practical Example

Enterprise support agent. User: "என் invoice-க்கு payment status என்ன?"

Agent steps:
1. LLM -> parse intent
2. Tool `get_user_id` 
3. Tool `fetch_invoices`
4. LLM -> summarize
5. Tool `check_payment_gateway`

Production-ல நீங்கள் monitor பண்ண வேண்டியது:
* Trace ID: `req_abc123`
* Steps: 5, latency: 4.2s
* Token usage: 1,200 input / 400 output
* Tool success: get_user_id OK, fetch_invoices 2s latency, check_payment_gateway timeout then retry success

இதில் fetch_invoices slow ஆகிறது என்று தெரிந்தால், அது database issue. அதை agent level-ல பார்த்தால் மட்டுமே தெரியும்.

## 7. Reasoning Challenge

உங்கள் agent-ல average steps per request 4-ல இருந்து திடீரென 9-க்கு increase ஆகிறது. Tool success rate same. Latency double ஆகிறது. Cost per request 2.3x ஆகிறது.

இதற்கு காரணம் என்னவாக இருக்கலாம்? Monitoring-ல நீங்கள் எந்த signal-ஐ பார்ப்பீர்கள், எந்த alert-ஐ set பண்ணுவீர்கள்?

## 8. Key Takeaways

* Agent monitoring என்பது request monitoring அல்ல, **trace per execution with step-level spans**.
* Steps, token usage, tool success, loop repetition ஆகியவை core metrics.
* Cost & latency blow-up-க்கு காரணம் தெரிய வேண்டும் என்றால் hop-by-hop observability தேவை.
* Infinite loop & tool misuse ஆகியவற்றை early detect பண்ண `max_steps`, repetition alerts வேண்டும்.
* Observability-க்கு trade-off உண்டு: granularity vs cost, privacy vs debugging.
