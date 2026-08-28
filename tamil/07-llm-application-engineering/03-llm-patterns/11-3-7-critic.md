# Critic

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.7 — LLM patterns

### 1. Problem

நீங்கள் ஒரு LLM agent-ஐ build பண்ணிருக்கீங்க. அது user query-க்கு answer generate பண்ணுது. சில நேரம் answer-ல hallucination இருக்கு, format தப்பா இருக்கு, policy violate பண்ணுது, அல்லது task-ஐ முழுசா complete பண்ணல.

நீங்கள் என்ன பண்ணுவீங்க? Prompt-ஐ மேலும் strict ஆக்கி மீண்டும் generate பண்ணச் சொல்லலாம். ஆனால் அது எப்போதும் வேலை செய்யாது. Model தன்னைத்தானே correct பண்ணத் தெரியாமல் இருக்கலாம்.

இந்த pain point-தான் Critic pattern-ஐ உருவாக்கியது: **Model-ன் output-ஐ மற்றொரு reasoning pass-ல evaluate பண்ணி, திருத்தி, அல்லது reject பண்ண வேண்டும்.**

### 2. Mental Model

Critic என்பது ஒரு separate judge.

> Generator உற்பத்தி பண்ணுது, Critic அதை தரமாய் பார்க்குது.

இது code review-ல senior engineer-க்கு junior-ன் PR-ஐ review பண்ணுவது போல. Critic-ன் job தான் மட்டும் generate பண்ணுவது அல்ல, **feedback கொடுப்பது**. அந்த feedback-ஐ வைத்து generator திருத்தம் பண்ணலாம்.

இரண்டு வடிவம் உண்டு:

* **Self-critic**: அதே model தன்னுடைய output-ஐ திரும்ப evaluate பண்ணுது
* **External critic**: வேறு model / rule / human / verifier செய்கிறது

### 3. How It Works

Basic loop மிக எளிமையானது:

1. **Generate**: LLM-ஐ கொண்டு initial output உருவாக்கு
2. **Critique**: Output-ஐ Critic-க்கு கொடு. Critic rubric-ஐ follow பண்ணி score / reason கொடுக்கும்
3. **Revise or Reject**: Score threshold-க்கு கீழே இருந்தால் regenerate செய், அல்லது feedback-ஐ மீண்டும் prompt-ல சேர்த்து refine செய்

முக்கியம்: Critic-க்கு clear criteria தேவை. "Good answer" என்பது vague. "Factual correctness, no hallucination, JSON schema valid, tone polite" என்பது measurable.

உதாரணமாக RAG pipeline-ல:
Generator answer create பண்ணும் → Critic checks: each claim has citation? Citation context-ல இருக்கா? → இல்லை என்றால் "missing citation for claim X" என்று feedback தரும்.

### 4. Architectural Reasoning

Critic pattern எப்போது useful?

* **High-stakes output**: Finance summary, medical info, legal clause generation. தப்பு கூடாது.
* **Structured output requirement**: JSON schema, function call format. Model சில நேரம் format-ஐ break பண்ணும்.
* **Policy / safety**: Toxicity, PII leak, brand tone violation தடுக்க.
* **Multi-step reasoning**: Agent tool use சரியாக நடந்ததா என்று verify.

Alternatives:
* **Better prompt only**: Cheaper, ஆனால் ceiling உண்டு. Model bias-ஐ தீர்க்காது.
* **Guardrails / rule-based validation**: Regex, schema validator. Fast & cheap, ஆனால் semantic errors catch ஆகாது.
* **Human in the loop**: Gold standard, ஆனால் latency & cost அதிகம்.

Critic இவற்றுக்கு நடுவில் இருக்கிறது: automated, semantic understanding உண்டு, human-ஐ விட cheap.

### 5. Trade-offs

* **Latency vs Quality**: ஒவ்வொரு generation-க்கும் critique + possible revision என்றால் 2-3x LLM calls. Latency அதிகரிக்கும். Cost அதிகரிக்கும்.
* **Critic quality**: Critic தானே தப்பு பண்ணலாம். Weak critic → false positive/negative. Strong critic-க்கு often larger model தேவை.
* **Over-correction**: திரும்ப திரும்ப revise பண்ணினால் answer generic ஆகி, nuance குறையும். முடிவில்லாத loop ஆகவும் ஆகலாம்.
* **Operational complexity**: Rubric maintain பண்ண வேண்டும். Critic prompt drift ஆகும். Monitoring தேவை.

Failure mode: Critic generator-ஐ பயமுறுத்தி over-safe output தர வைக்கும்.

### 6. Practical Example

Enterprise support ticket summarizer.

Generator: ticket thread-ல இருந்து summary + root cause + next steps generate பண்ணும்.

Critic rubric:
1. Summary 50 words-க்குள் இருக்கா?
2. Root cause ticket-ல mention ஆனதா?
3. Next steps actionable-ஆ?
4. Tone professional?

Critic score 0-1 தரும் + reason. Score < 0.8 என்றால் feedback-ஐ சேர்த்து regenerate. இது production-ல hallucinated root cause-ஐ 60% குறைக்கும்.

### 7. Reasoning Challenge

உங்களுக்கு RAG-based financial report generator உள்ளது. 100 reports / day. ஒவ்வொரு report-லும் numbers முக்கியம். LLM சில நேரம் source document-ல இல்லாத number-ஐ invent பண்ணுது.

Critic-ஐ சேர்க்கலாம். ஆனால் latency SLA 3 seconds. Critic call + possible retry 2x cost ஆக்கும்.

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Self-critic vs external critic? Retry எத்தனை முறை? முடிவு எப்படி?

### 8. Key Takeaways

* Critic pattern என்பது generate-க்கு பிறகு evaluate & refine செய்யும் reasoning loop
* Quality / safety க்கு பதிலாக latency & cost கொடுக்கிறோம்
* Critic-க்கு clear, measurable rubric தேவை, vague "good/bad" வேலை செய்யாது
* Self-critic cheap ஆனால் bias உண்டு; external critic strong ஆனால் expensive

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியும்.
