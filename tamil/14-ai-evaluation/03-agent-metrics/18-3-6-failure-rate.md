# Failure rate

> **Learning Path:** AI Evaluation
> **Section:** 18.3.6 — Agent metrics

## 1. Problem

ஒரு agent-ஐ production-ல விட்டுட்டோம். ஒரு நாள் 10,000 user queries வருது. Agent 9,200 queries-க்கு சரியான output கொடுத்துது. 800 queries-ல பதில் முழுசா கிடைக்கல, அல்லது agent crash ஆகுது, timeout ஆகுது, அல்லது hallucination-னால useless answer கொடுத்துது.

இங்கே கேள்வி என்ன? Success rate எவ்வளவு? இந்த 800 failures ஏன் நடந்துது? எல்லா failures-ம் சமமா?

Engineer-க்கு வேண்டியது ஒரு simple number இல்ல. **Failure rate என்பது agent எவ்வளவு அடிக்கடி fail ஆகுதுன்னு சொல்லும் metric.** ஆனா எந்த failure-ஐ count பண்றோம்? அதுதான் architectural decision.

Failure rate இல்லாம agent-ஐ improve பண்ண முடியாது. நீங்க latency மட்டும் பார்த்தா, agent fast-ஆ இருந்தாலும் useless answer கொடுக்கும். Accuracy மட்டும் பார்த்தா, slow and flaky agent-ஐ மிஸ் பண்ணிடுவீங்க.

## 2. Mental Model

Failure rate = `failed runs / total runs`

Simple. ஆனா `failed` என்பதன் definition முக்கியம்.

ஒரு agent run என்பது start to finish ஒரு complete task execution. Failure என்பது:

* **Hard failure:** exception, crash, timeout, tool call error, LLM service down
* **Soft failure:** task completed ஆனா output invalid, wrong format, hallucination, policy violation, user intent satisfy ஆகல

Agent metrics-ல failure rate என்பது இந்த இரண்டையும் பிரிச்சு பார்க்க வேண்டியது.

Mental model: Failure rate என்பது reliability-ன் first signal. Throughput, latency, cost எல்லாம் வேலை செய்யும். ஆனா agent தொடர்ந்து fail ஆகிட்டே இருந்தா business value zero.

## 3. How It Works

Agent run-க்கு ஒரு run ID கொடு. Start time, end time, status track பண்ணு.

Status categories:

* `success` - task completed and validation passed
* `hard_failure` - system error, timeout, tool error, LLM error
* `soft_failure` - validation failed, wrong output, policy violation

Failure rate = `(hard_failure + soft_failure) / total_runs`

பெரும்பாலும் இதை slice பண்ணுவாங்க:

* failure rate by task type
* failure rate by tool
* failure rate by user segment
* failure rate over time

இதுக்கு evaluation harness வேண்டும். ஒவ்வொரு run-க்கும் automated checker இருக்கும். Output format valid-ஆ? Expected fields உள்ளனவா? Factuality check? Policy check? இது pass ஆகலன்னா soft failure.

## 4. Architectural Reasoning

Failure rate எப்போ useful?

* **Reliability SLO define பண்ண** - "agent 99% runs succeed"ன்னு target வைக்கலாம்
* **Regression detect பண்ண** - model upgrade பண்ணின பிறகு failure rate spike ஆச்சா?
* **Root cause find பண்ண** - hard failures அதிகமா? soft failures அதிகமா?

Alternatives?

* Success rate மட்டும் பார்ப்பது - ஏன் fail ஆச்சுன்னு தெரியாது
* Error logs மட்டும் பார்ப்பது - trend தெரியாது
* Manual review - scale ஆகாது

ஏன் failure rate தேவை? Agent என்பது non-deterministic system. Same prompt-க்கு வெவ்வேறு output வரும். அதனால் average performance போதாது. Consistency தேவை. Failure rate அந்த consistency-ஐ quantify பண்ணும்.

## 5. Trade-offs

**Hard vs Soft failure definition:** Hard failure-ஐ மட்டும் count பண்ணினா number குறைவா தெரியும். Soft failure-ஐ சேர்த்தா failure rate உயரும். ஆனா business impact உண்மையானது. Trade-off: strict definition vs actionable signal.

**Granularity:** Per-run failure rate easy. ஆனா user session level failure rate வேற. ஒரு user 3 attempts பண்ணி 3rd time success ஆனா, அது success-ஆ failure-ஆ? Architecture-ல retry logic இருந்தா metric skewed ஆகும்.

**False positives:** Validation checker-ஐ over strict-ஆ வைத்தால் good outputs-ஐயும் failure-ஆ mark பண்ணிடுவோம். Under strict-ஆ வைத்தால் bad outputs escape ஆகும்.

**Cost vs observability:** Every run-க்கு validation run பண்ணுவது cost ஆகும். Sampling பண்ணலாம். ஆனா rare failures miss ஆகும்.

Failure modes: timeout cascade, tool rate limit, LLM output format drift, prompt injection leading to policy violation. Failure rate இந்த எல்லாத்தையும் catch பண்ணும் ஆனா *why* சொல்லாது. அதுக்கு error taxonomy தேவை.

## 6. Practical Example

Enterprise support agent. User ticket-ஐ read பண்ணி, knowledge base search பண்ணி, summary generate பண்ணி, CRM-ல update பண்ணும்.

1000 runs:

* 870 success
* 80 hard failure - vector DB timeout, CRM API 500
* 50 soft failure - output format invalid, hallucinated ticket ID

Failure rate = 130/1000 = 13%

Architect decision: Hard failures 8% என்பது infra reliability issue. Soft failures 5% என்பது prompt + validation issue.

Hard failures-க்கு retry with exponential backoff + circuit breaker வேண்டும். Soft failures-க்கு output schema validation + few-shot prompt improve பண்ண வேண்டும்.

இங்கே failure rate ஒரே number-ல பிரச்சனையை split பண்ணி கொடுத்துது.

## 7. Reasoning Challenge

உங்க agent-ல failure rate 4% இருக்கு. ஆனா user complaints அதிகமா வருது. Investigation-ல தெரியுது 90% failures soft failure, output technically valid ஆனா user intent satisfy ஆகல. Hard failure மட்டும் track பண்ணினா உங்களுக்கு என்ன பிரச்சனை வரும்? Failure definition-ஐ எப்படி மாற்றுவீங்க? அதனால failure rate எப்படி மாறும்?

## 8. Key Takeaways

* Failure rate என்பது agent reliability-ன் baseline signal. Success rate அல்ல, failure-ஐ categorize பண்ணுங்கள்.
* Hard failure = system reliability. Soft failure = task quality. இரண்டும் வேற வேற root cause.
* Definition of failure தான் metric-ன் value decide பண்ணும். Strict and business-aligned definition வைக்கவும்.
* Failure rate trend தான் முக்கியம், absolute number அல்ல. Deployment, model, prompt change-க்கு பிறகு spike ஆகிறதா பார்க்கவும்.
* Failure rate alone போதாது. எந்த task, எந்த tool, எந்த user segment-ல fail ஆகுதுன்னு slice பண்ணுங்கள்.
