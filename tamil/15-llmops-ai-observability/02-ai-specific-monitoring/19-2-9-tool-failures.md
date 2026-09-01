# Tool failures

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.9 — AI-specific monitoring

## 1. Problem

உங்க system ல LLM ஒரு agent மாதிரி run ஆகுது. அது user query வாங்கி, reasoning பண்ணி, tool call பண்ணுது — database query, web search, calculator, internal API call, RAG retrieval.

இப்போ tool fail ஆகுது. Timeout ஆகுது. API rate limit அடிச்சுது. Wrong output தந்துது. அல்லது tool கிடைக்கவே இல்லை.

என்ன ஆகும்? LLM agent அதை notice பண்ணாம, hallucination பண்ணி ஒரு முடிவு கொடுத்துடும். அல்லது retry loop ல மாட்டிக்கும். User க்கு inconsistent answer வரும். 

Traditional monitoring ல service down, latency spike பார்ப்போம். ஆனா AI system ல tool failure என்பது **silent failure** ஆக மாறும். LLM "tool failed, but I will assume..." என்று தொடரும். இதை catch பண்ணாம விட்டால் trust போய்விடும்.

**What goes wrong if we don't have this?** Agent output தரமிழக்கும், debugging கடினம், user sees flaky behavior, and you don't know if failure is from LLM, tool, or orchestration.

## 2. Mental Model

Tool failures என்பது distributed system failure + LLM interpretation failure இன் கலவை.

ஒரு service call service ஐ call பண்ணும்போது network failure வரலாம். அதை retry, timeout, circuit breaker வச்சி handle பண்ணுவோம்.

Agent system ல இதுக்கு மேல ஒரு layer இருக்கு: LLM tool output ஐ interpret பண்ணி next step decide பண்ணும். Tool தந்த output invalid ஆ இருந்தாலும் LLM அதை valid ஆ accept பண்ணிடும்.

Mental model: **Tool = external dependency with non-deterministic contract.** LLM = consumer that is overly trusting.

நாம் monitor பண்ண வேண்டியது:
1. Tool invocation success/failure
2. Tool latency & error types
3. LLM's reaction to tool failure — did it retry, fallback, or hallucinate?

## 3. How It Works

AI-specific monitoring ல tool failures ஐ track பண்ண, நாம் three signals பார்க்க வேண்டும்.

**Invocation signal:** ஒவ்வொரு tool call க்கும் trace ID create பண்ணு. tool_name, input args, timestamp, model step.

**Execution signal:** tool return code, latency, error message, partial output. Timeout, rate limit, 5xx, validation error எல்லாம் tag பண்ணு.

**Agent reaction signal:** LLM அடுத்த turn ல என்ன செய்தது? Retry செய்ததா? Different tool க்கு switch செய்ததா? Apologize பண்ணி user க்கு generic answer தந்ததா? இது crucial.

இதை log பண்ணி, structured observability pipeline ல அனுப்பு. OpenTelemetry spans ல tool call ஒரு child span. LLM prompt/completion ஒரு span. Correlation மூலம் end-to-end view கிடைக்கும்.

## 4. Architectural Reasoning

இது எப்போ useful?

* Multi-tool agent உள்ள system. RAG + web search + calculator + internal API.
* Tool reliability uneven ஆ இருக்கும். External API flaky ஆக இருக்கும்.
* Cost sensitive. Failed tool calls waste tokens.
* Compliance / audit தேவை.

Alternatives:
* **No monitoring:** cheapest, but blind.
* **Only tool-level monitoring:** API success rate தெரியும், ஆனால் agent எப்படி react பண்ணுது தெரியாது.
* **Full AI observability:** tool + LLM + orchestration trace together.

Architect ஏன் choose பண்ணுவார்? Because tool failure often leads to bad user experience, and without correlation you will blame LLM when problem is tool latency.

Decision factor: Team size and criticality. Production agent ஆனால் tool failure dashboard must.

## 5. Trade-offs

**Observability vs overhead.** Every tool call ல tracing, logging add பண்ணினால் latency + cost + storage increase ஆகும். Sampling பண்ணலாம், ஆனால் rare failures miss ஆகும்.

**Granularity vs noise.** Too many metrics — every tool error type. Alert fatigue வரும். Important errors மட்டும் alert பண்ணு: persistent failure, high latency p95, LLM hallucination after failure.

**Retry logic vs amplification.** Agent auto-retry பண்ணினால், flaky tool ல cascade failure வரும். Circuit breaker வேண்டும். ஆனால் circuit breaker போட்டால் agent ல fallback reasoning தேவை.

**Structured logs vs privacy.** Tool input/output ல PII இருக்கலாம். Logging முழு payload வேண்டாம். Hash or redact பண்ணு.

Failure modes:
* Silent degradation: tool slow ஆகுது, LLM timeout ஆனதை notice பண்ணாம wait பண்ணி overall latency spike.
* Error misinterpretation: LLM tool error message ஐ user facing answer ஆ convert பண்ணிடும்.
* Retry storm: multiple agents same failing tool ஐ hit பண்ணி rate limit amplify.

## 6. Practical Example

Enterprise support agent. User asks "இந்த மாத invoice total எவ்வளவு?" Agent steps:
1. RAG retrieve contract
2. Database tool call to fetch invoices
3. Calculator tool to sum

Database tool 2 seconds ல timeout ஆகுது. Agent logs show: tool_name=db_query, status=timeout, latency=5000ms, retry_count=1.

Agent reaction signal shows LLM tried retry, got same timeout, then said "Data temporarily unavailable". 

Monitoring dashboard ல இதை பார்த்தால், நீங்கள் தெரிந்து கொள்வது:
* Tool failure rate spike for db_query
* 80% of failures lead to agent fallback, not hallucination — good
* p95 latency increased from 200ms to 4.8s

இல்லாமல் நீங்கள் நினைத்திருப்பது: LLM quality degrade ஆகுது.

## 7. Reasoning Challenge

உங்களிடம் 3 tools இருக்கு: vector_db, web_search, internal_api. Web_search 5% time rate limit தருது. Agent 20 concurrent users handle பண்ணுது.

Tool failure ஆனால் LLM மீண்டும் same tool call பண்ணும். இது cost increase பண்ணும், user wait time increase பண்ணும்.

இங்கே என்ன architecture decision செய்வீர்கள்? Retry with backoff, circuit breaker, fallback tool, அல்லது user ஐ ask செய்ய? ஏன்?

## 8. Key Takeaways

* Tool failure ஐ மட்டும் பார்க்காதே. LLM அதற்கு எப்படி react பண்ணுது என்பதையும் monitor பண்ணு.
* Trace correlation between LLM step and tool execution தேவை. இல்லாமல் root cause கண்டுபிடிக்க முடியாது.
* Retry, timeout, circuit breaker ஆகியவை agent reliability க்கு critical. Blind retry cost ஐ அதிகரிக்கும்.
* Observability overhead உண்மை. Sample, aggregate, alert only on patterns.

இது தெரிஞ்சா tool failures ஐ silent degradation ஆ விடாம தடுக்கலாம்.
