# Regression testing

> **Learning Path:** AI Evaluation
> **Section:** 18.1.6 — Evaluation

### 1. Problem

உங்களிடம் ஒரு AI Evaluation pipeline இருக்கு. ஒரு model version-ஐ release பண்ணினீங்க. புது model better accuracy கொடுத்தது. 

அடுத்த sprint-ல ஒரு small change செய்தீங்க - prompt template-ஐ tweak பண்ணீங்க, அல்லது embedding model மாற்றினீங்க, அல்லது RAG retrieval threshold குறைத்தீங்க.

இப்போது உங்கள் LLM agent-இன் answer quality குறைந்து விட்டது. ஆனால் எப்போது, ஏன், எந்த metric-ல கெட்டது என்று தெரியவில்லை.

இல்லையெனில், ஒவ்வொரு release-க்கும் முழு evaluation suite-ஐ manually ஓட வேண்டியிருக்கும். அது slow, expensive, மற்றும் non-deterministic AI outputs-ல compare பண்ண முடியாது.

**What goes wrong if we don't have this?** Good changes break silently, bad changes slip to production, and நம்பிக்கை இல்லாமல் ship செய்ய முடியாது.

### 2. Mental Model

Regression testing என்பது **"நாம் முன்பு வேலை செய்ததை இப்போது உடைக்கவில்லை என்பதை உறுதி செய்வது"**.

Software-ல, ஒரு bug fix பண்ணும்போது வேறு feature break ஆகிறது. அதை catch பண்ண regression test.

AI Evaluation-ல, regression testing என்பது: model, prompt, retrieval, tooling மாற்றம் செய்த பிறகும், ஒரு fixed set of critical scenarios-ல performance degrade ஆகவில்லை என்பதை prove பண்ணுவது.

இது test suite இல்லை, safety net.

### 3. How It Works

Regression testing-க்கு 3 பாகங்கள் தேவை:

**Golden dataset.** நிலையான inputs + expected behavior. AI-க்கு exact expected output இல்லாமல் இருக்கலாம். ஆனால் acceptability criteria இருக்கும்.

உதாரணம்: `input: "எனது கடைசி 3 மாத வருமான வரி..."` → `expected: tool call to get_tax_data, no hallucination, latency < 800ms, refusal if PII leak`.

**Baseline metrics.** முந்தைய version-ல இந்த golden set-ல எப்படி perform பண்ணியது என்று snapshot. Accuracy, faithfulness, latency, cost, safety score.

**Comparison gate.** புதிய version-ல அதே golden set-ஐ ஓடச்சு, metrics delta-வை check பண்ணு. Degradation threshold cross ஆனால் block release.

AI-ல non-determinism இருப்பதால், நாம் single output-ஐ compare பண்ணுவதில்லை. Distribution-ஐ compare பண்ணுவோம். LLM-as-judge, embedding similarity, rubric scoring.

### 4. Architectural Reasoning

Regression testing useful ஆகும் போது:

* உங்கள் system-ல multiple moving parts உள்ளன: model, prompt, RAG retriever, tool, guardrail.
* Stakeholders-க்கு trust தேவை: Finance, Legal, Customer Support.
* Release frequency அதிகம்.

Alternatives:

* Ad-hoc manual QA: cheap start-ல, scale ஆகாது.
* Full evaluation every time: comprehensive ஆனால் slow and costly.
* Regression suite: small, fast, focused, runs on every PR.

ஏன் choose? Because you want **fast feedback on stability, not full discovery**.

Decision point: Golden set எவ்வளவு பெரியதாக இருக்க வேண்டும்? 50-200 critical cases போதும். Coverage முக்கியம், quantity இல்லை.

### 5. Trade-offs

**Stability vs Coverage.** Golden set சிறியதாக இருந்தால் fast, ஆனால் edge cases miss ஆகும். பெரியதாக இருந்தால் expensive.

**Sensitivity vs Noise.** Threshold strict ஆக இருந்தால் false alarms அதிகம். Loose ஆக இருந்தால் real regression miss ஆகும். உதாரணம்: 2% accuracy drop accept செய்யலாமா? Domain-க்கு தகுந்தது.

**Determinism vs Realism.** Synthetic golden cases deterministic ஆக இருக்கும். Production traffic replay realistic ஆனால் privacy risk.

**Cost.** LLM-as-judge regression-க்கு inference cost வரும். Cache results, use smaller judge model.

Failure modes:

* Golden set stale ஆகி விடும். New product behavior reflect ஆகாது.
* Metric gaming: prompt-ஐ tweak பண்ணி golden set-ல மட்டும் pass ஆக வைப்பது.
* Flaky tests: non-deterministic model + weak judge = unstable gate.

### 6. Practical Example

Enterprise RAG agent for HR policy.

Golden set-ல 120 questions: 30 factual lookup, 30 refusal/PII, 30 multi-hop, 30 language mix Tamil/English.

Baseline v1.2: Faithfulness 0.91, Refusal accuracy 0.98, p95 latency 620ms.

v1.3-ல prompt-ஐ simplify பண்ணினீர்கள். Regression suite ஓடியது:

* Faithfulness 0.89 → -2 points, within threshold 3%.
* Refusal accuracy 0.84 → -14 points, threshold cross.

Reason: prompt simplification-ல safety instruction weaken ஆகி விட்டது. Release block.

இல்லையெனில் production-ல PII leak ஆகி இருக்கும்.

### 7. Reasoning Challenge

உங்களிடம் ஒரு customer support agent உள்ளது. Model upgrade செய்தீர்கள். Regression suite-ல 100 golden cases-ல Overall score 0.02 drop ஆகிறது, ஆனால் Tamil queries-ல score 0.12 drop ஆகிறது. English queries-ல improvement உள்ளது.

Ship செய்வீர்களா? Threshold என்ன set பண்ணுவீர்கள்? Golden set-ஐ எப்படி evolve பண்ணுவீர்கள்?

### 8. Key Takeaways

* Regression testing = stability guarantee, not performance discovery.
* Golden dataset + baseline metrics + delta gate = core loop.
* AI-ல exact match இல்லை, rubric and judge-based comparison தேவை.
* Small, curated critical cases > large random set, for fast feedback.
* Every architectural change creates trade-off: speed, cost, sensitivity.

இதை புரிந்துகொண்டால், நீங்கள் ship செய்யும் போது **என்ன உடையவில்லை என்பதை தெரிந்து** ship செய்ய முடியும்.
