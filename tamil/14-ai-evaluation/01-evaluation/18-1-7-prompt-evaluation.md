# Prompt evaluation

> **Learning Path:** AI Evaluation
> **Section:** 18.1.7 — Evaluation

## 1. Problem

நீங்கள் ஒரு LLM agent-ஐ production-க்கு deploy பண்ணினீர்கள். First week-ல கஸ்டமர் கேட்கிறார்: "இது சரியாக வேலை செய்கிறதா?"

உங்களுக்கு என்ன metrics இருக்கு? Latency, cost இருக்கு. ஆனால் **quality** எப்படி measure பண்ணுவீர்கள்?

Prompt-ஐ மாற்றினீர்கள். Model-ஐ மாற்றினீர்கள். Temperature மாற்றினீர்கள். இப்போது output worse ஆகிவிட்டதா? Better ஆகிவிட்டதா? உணர்வால் மட்டும் தெரியாது.

Engineering team ஒன்று சேர்ந்து கைமுறையாக 100 samples படித்து score பண்ணுகிறது. அது slow, inconsistent, மற்றும் non-repeatable. 

What goes wrong if we don't have prompt evaluation? Silent regression, hallucination increase, guardrail bypass, cost overrun, மற்றும் production incident.

Prompt evaluation என்பது **quality-ஐ measurable ஆக்குவது** தான்.

## 2. Mental Model

Prompt evaluation என்பது software testing போன்றது.

Unit test = input-output pair expect செய்யும்.
Prompt evaluation = prompt + context + model -> output quality-ஐ measure செய்யும்.

ஒரு good evaluation system மூன்று விஷயங்களை கொடுக்கும்:
1. **Score**: இந்த run எவ்வளவு நல்லது?
2. **Comparison**: A vs B எது better?
3. **Debug**: எங்கே fail ஆகிறது?

Mental model: நீங்கள் ஒரு judge-ஐ உருவாக்குகிறீர்கள். அந்த judge தான் உங்கள் product-ஐ evaluate செய்யும்.

## 3. How It Works

Evaluation என்பது 3 components-ஆல் build ஆகிறது.

**Dataset**: Realistic prompts + context + expected behavior.
உதாரணம்: customer support ticket, factual question, coding task. Gold reference வைத்தால் நல்லது, இல்லையெனில் rubric-based.

**Metric**: என்ன measure பண்ணுவது?
* Reference-based: ROUGE, BLEU, exact match. Factual task-க்கு உதவும்.
* Reference-free: LLM-as-judge, factuality check, toxicity, style adherence.
* Task-specific: tool call correctness, JSON schema validity, latency, cost per request.

**Evaluator**: யார் score பண்ணுவது?
* Human: gold standard ஆனால் expensive, slow.
* LLM-as-judge: fast, consistent. Bias உண்டு, cost உண்டு.
* Rule-based: regex, schema validation, embedding similarity. Deterministic.

Typical flow:
`prompt -> model -> output -> evaluator -> score -> dashboard`

முக்கியம்: evaluation-ஐயும் version control பண்ணுங்கள். Dataset, rubric, judge prompt எல்லாம் artifact.

## 4. Architectural Reasoning

எப்போது தேவை?
* Prompt iteration செய்யும் போது. A/B test செய்ய வேண்டும்.
* Model upgrade செய்யும் போது. New model cheaper ஆனால் quality drop ஆகுமா?
* Guardrail தேவை. Toxic, hallucination, PII leakage.
* Production monitoring. Drift detect பண்ண.

Alternatives:
* Ad-hoc manual review -> not scalable.
* Only latency/cost monitor -> quality blind.
* Online user feedback only -> late, noisy.

Architect ஏன் choose பண்ணுவார்? Because prompt என்பது code போல change ஆகிறது. CI/CD இல்லாமல் ship பண்ண முடியாது. Evaluation என்பது test suite.

## 5. Trade-offs

**LLM-as-judge vs Human**
Judge fast மற்றும் cheap. ஆனால் judge-ஐயும் prompt பண்ண வேண்டும், அது bias கொடுக்கும். Human slow ஆனால் ground truth.

**Reference-based vs Reference-free**
Reference இருந்தால் objective. ஆனால் creative task-ல reference இல்லை. Reference-free flexible ஆனால் judge quality மீது depend.

**Offline eval vs Online eval**
Offline: safe, reproducible. Production reality-ஐ catch பண்ணாது.
Online: real user data, distribution shift catch ஆகும். Privacy risk, cost.

**Coverage vs Cost**
பெரிய dataset = better signal. ஆனால் evaluation cost அதிகம், especially LLM-as-judge.

Failure mode: Goodhart's law. Model evaluation metric-ஐ game பண்ணும். உதாரணம்: judge-க்கு பிடிக்கும் style-ல எழுதும், actual usefulness குறையும்.

## 6. Practical Example

Enterprise RAG chatbot.

Problem: Knowledge base update ஆன பிறகு hallucination அதிகரிக்கிறதா?

Architecture:
* Dataset: 500 real user questions, 50 golden facts from KB.
* Metrics: 
  - Factuality: LLM-as-judge checks if answer grounded in retrieved chunks.
  - Citation correctness: reference doc id present and correct?
  - Style adherence: tone, length.
  - Tool call accuracy: retrieve vs search decision correct?
* Evaluator pipeline: nightly run on same dataset for every prompt version.
* Dashboard: score per metric, regression alert if >2% drop.

Result: Prompt v3 cheaper ஆனால் factuality 94% -> 87%. Rollback செய்தீர்கள். Cost saving கிடைக்காமல் போனாலும் trust protect ஆனது.

## 7. Reasoning Challenge

உங்கள் agent 20% requests-ல tool call செய்கிறது. Tool call format சரியாக இல்லாமல் downstream failure ஆகிறது.

உங்களுக்கு 10k production logs உள்ளன. Human review செய்ய முடியாது.

Evaluation system எப்படி design பண்ணுவீர்கள்? Metrics என்ன? Offline மட்டும் போதுமா? Online monitoring தேவையா?

## 8. Key Takeaways

* Prompt evaluation என்பது quality-ஐ measurable ஆக்கும் test suite.
* Good evaluation = realistic dataset + clear metric + repeatable evaluator.
* LLM-as-judge fast ஆனால் bias உண்டு; human gold ஆனால் expensive. Mix பண்ணுங்கள்.
* Every prompt change = evaluation run. Regression இல்லாமல் ship பண்ணாதீர்கள்.
