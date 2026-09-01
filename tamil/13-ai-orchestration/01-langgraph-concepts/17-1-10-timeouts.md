# Timeouts

> **Learning Path:** AI Orchestration
> **Section:** 17.1.10 — LangGraph concepts

## 1. Problem

AI Orchestration-ல ஒரு agent மற்றொரு agent-ஐ call பண்ணும். அல்லது LLM call, tool call, API call.

நீங்கள் ஒரு LangGraph workflow-ஐ run பண்ணீங்க. Node 1 -> Node 2 -> Node 3. Node 2 ஒரு external service-ஐ call பண்ணுது. அந்த service slow ஆகுது. அல்லது hang ஆகுது.

என்ன ஆகும்?

Graph முழுவதும் stuck. அடுத்த step க்கு போகாது. User-க்கு response வராது. Timeout இல்லை என்றால் thread, connection, resource எல்லாம் கட்டுப்படி இல்லாமல் தங்கி விடும்.

AI Orchestration-ல timeout இல்லாமல் ஒரு call பண்ணுவது என்பது "நீ எப்போ வேண்டுமானாலும் வா" என்று கேட்பது போல. System-க்கு கட்டுப்பாடு இல்லாமல் போகும்.

**What goes wrong?** Cascading wait, resource exhaustion, user experience மோசம், cost ஏறும்.

## 2. Mental Model

Timeout என்பது ஒரு contract: **"இந்த கால அளவுக்குள் result வரணும், இல்லை என்றால் நான் வேறு action எடுப்பேன்."**

இது deadline மாதிரி. ஒரு service call-க்கு நீங்கள் சொல்லும் SLA.

LangGraph-ல ஒரு node எவ்வளவு நேரம் run ஆகலாம் என்பதை நீங்கள் control செய்ய வேண்டும். இல்லை என்றால் graph-இன் overall latency unpredictable ஆகும்.

## 3. How It Works

Simple mechanism:

1. Call start பண்ணு, start time record பண்ணு.
2. Wait for response.
3. Response வந்தால் proceed.
4. Response வராமல் timeout duration கடந்தால், call-ஐ cancel / abort / fallback.

LangGraph-ல இதை நீங்கள் node level-ல அல்லது edge level-ல போடலாம்.

எடுத்துக்காட்டாக ஒரு tool node-க்கு:
`timeout=5s`

5 வினாடிக்குள் tool respond இல்லை என்றால் node fails, exception raise ஆகும். அதை graph-ல catch பண்ணி retry, fallback, அல்லது alternative path எடுக்கலாம்.

Timeout என்பது fail fast-க்கு ஒரு trigger.

## 4. Architectural Reasoning

**When useful?**
* External LLM / tool / API call செய்யும் போது
* User-facing orchestration flow-ல
* Multiple parallel branches இருக்கும் போது, slowest branch எல்லாவற்றையும் கட்டுப்படுத்தும் போது

**What constraint it addresses?**
Latency predictability, resource utilization, user experience.

**Alternatives:**
* No timeout: wait forever. Simple but dangerous.
* Infinite retry with backoff: eventually success ஆகும், ஆனால் latency unpredictable.
* Circuit breaker + timeout: timeout முதல் step.

ஒரு architect timeout-ஐ ஏன் choose பண்ணுவார்?
காரணம்: **நம்பகத்தன்மைக்கு கட்டுப்பாடு தேவை.** Slow dependency-ஐ முழு system slow ஆக்கக் கூடாது.

LangGraph concepts-ல timeout ஒரு control plane decision. Graph-ஐ deterministic ஆக்குவதற்கு.

## 5. Trade-offs

**Timeout மிகக் குறைவாக இருந்தால்:**
* False positive failures அதிகம்
* Flaky network-ல unnecessary retry
* Cost increase

**Timeout மிக அதிகமாக இருந்தால்:**
* User wait time அதிகம்
* Resource hold time அதிகம்
* Cascading delay

**Retry vs Timeout:**
Timeout கொடுத்து immediate fallback செய்யலாம். அல்லது timeout கொடுத்து retry செய்யலாம். Retry என்பது அதே call-ஐ மீண்டும் try பண்ணுவது, அது cost & latency-ஐ அதிகரிக்கும்.

**Failure modes:**
* Timeout ஆன call-ஐ client-க்கு எப்படி handle பண்ணுவது? Partial result return? Graceful degradation?
* Timeout காரணமாக orphaned request backend-ல run ஆகிக்கொண்டே இருக்கும். Idempotency தேவை.

**Most important trade-off:** Availability vs Correctness. Timeout குறைவாக வைத்தால் system available ஆக இருக்கும் ஆனால் correctness குறையலாம். Timeout அதிகமாக வைத்தால் correctness improve ஆகலாம் ஆனால் availability குறையும்.

## 6. Practical Example

Enterprise support agent workflow.

Graph: Triage -> Knowledge Retrieval -> Tool Call for CRM -> Summarize

Tool Call for CRM sometimes 8-12 seconds எடுக்கும்.

User chat-ல 15 seconds wait செய்ய மாட்டார்.

Decision: CRM tool node-க்கு timeout = 4s வைக்கிறோம்.

4s க்குள் response வந்தால் proceed.
Timeout ஆனால் fallback path: cached CRM data use பண்ணி, "இப்போது live data கிடைக்கவில்லை, கடைசி update..." என்று respond பண்ணு.

Result: User experience predictable ஆகிறது. Graph hang ஆகாது. Cost controlled.

## 7. Reasoning Challenge

உங்களிடம் LangGraph-ல ஒரு agent workflow இருக்கு. அது 3 parallel branches-ல LLM call பண்ணுது.

Branch A: fast, 1s average
Branch B: slow, 5s average
Branch C: flaky, 50% time 10s+

User-க்கு overall response 7s க்குள் வேண்டும். 

ஒவ்வொரு branch-க்கும் timeout எப்படி set பண்ணுவீர்கள்? Timeout ஆன branch-ஐ என்ன செய்வீர்கள்? Retry செய்யலாமா? ஏன்?

## 8. Key Takeaways

* Timeout என்பது latency-க்கு ஒரு contract, fail fast-க்கு tool
* LangGraph-ல ஒரு node-ஐ control செய்ய timeout தேவை, இல்லை என்றால் graph unpredictable ஆகும்
* Timeout value என்பது business SLA, network reality, மற்றும் cost-இன் trade-off
* Timeout + fallback / retry strategy-ஐயும் சேர்த்து design பண்ணுங்கள், timeout மட்டும் போதாது
