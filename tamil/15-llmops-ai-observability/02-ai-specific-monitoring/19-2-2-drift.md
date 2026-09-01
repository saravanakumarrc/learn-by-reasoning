# Drift

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.2 — AI-specific monitoring

## 1. Problem

உங்கள் production-ல ஒரு RAG system இருக்கு. LLM + vector database + retriever. 

முதல் வாரம் output நல்லா இருந்தது. இப்போ 3-வது மாதத்தில் users சொல்றாங்க: "answers are off", "hallucinations அதிகமாகுது", "relevance குறைஞ்சுடுச்சு".

Code மாறல. Model மாறல. Prompts மாறல. அப்புறம் என்ன ஆச்சு?

இங்க தான் drift வருது.

Drift என்பது **system-ன் behavior மெதுவாக மாறுவது, code change இல்லாமல்**. AI system-க்கு இது குறிப்பாக கொடுமையானது, ஏனெனில் data, model, user, world எல்லாமே move ஆகுது.

## 2. Mental Model

Drift = உங்கள் assumption உடைஞ்சுடுச்சு.

நீங்கள் train/test செய்த environment வேறு, production வேறு ஆகிடுச்சு.

ஒரு analogy: நீங்கள் ஒரு கார்-ஐ Chennai road-க்கு tune பண்ணீங்க. 6 மாசம் கழிச்சு அதே கார் Leh-ல ஓடுது. Engine அதேதான், road மாறிடுச்சு.

AI system-ல drift முக்கியமா 3 இடத்துல வரும்:

* **Data drift**: input distribution மாறிடுச்சு
* **Concept drift**: உண்மையான relationship மாறிடுச்சு
* **Model drift**: performance degrade ஆகுது, காரணம் தெரியாம

## 3. How It Works

AI-specific monitoring-ல drift-ஐ catch பண்ண ஒரு feedback loop வேணும்.

Production input → embedding → retrieval → generation → user interaction → telemetry capture → comparison with baseline

Baseline என்ன? நீங்கள் define பண்ணிய reference distribution.

நீங்கள் track பண்ணுவது:

* Input embeddings distribution shift. e.g., cosine distance from training centroid அதிகமாகுதா?
* Retrieval quality metrics: hit rate, recall@k, context relevance score
* Output metrics: latency, token usage, refusal rate, toxicity, factuality score
* Business metrics: user thumbs down, follow-up question rate, task completion

இதை statistical test-களால detect பண்ணலாம். KS test, PSI, Wasserstein distance for embeddings. Model-ல score drift-க்கு population stability index.

Drift detect ஆனதும் alert வரணும், அது automatic retrain/rollback trigger பண்ணலாம்.

## 4. Architectural Reasoning

ஏன் drift monitoring வேணும்?

LLMOps-ல **you cannot assume static world**. 

Data drift: user queries seasonal ஆக மாறும். Festive season-ல e-commerce queries மாறும். News-based RAG-ல topics change.

Concept drift: world facts மாறும். Model பழைய knowledge-ஐ use பண்ணும். உதாரணம்: CEO change, product price change.

Prompt drift: users prompt-ஐ creative-ஆ மாற்றுவாங்க. System prompt அப்படியே இருக்கும்.

எப்போ useful?

* Production RAG / agents இருக்கும்போது
* User-generated content input இருக்கும்போது
* External data source sync ஆகும்போது
* LLM-ன் knowledge cutoff-க்கு அப்பால் world மாறும்போது

Alternatives? Blind monitoring. அது பண்ணினா நீங்கள் பார்ப்பது error rate மட்டும். Root cause தெரியாது. Drift monitoring காரணத்தை சீக்கிரம் சொல்லும்.

## 5. Trade-offs

**Detect sensitivity vs noise**: Threshold strict ஆக்கினா false positive அதிகம். Loose ஆக்கினா late detection.

**Granularity**: Per query drift track பண்ணுவது expensive. Sampling + aggregation வேணும். Cost vs observability trade-off.

**Label dependency**: Drift detect பண்ண ground truth வேண்டாம். ஆனால் concept drift-க்கு labeled data தேவை. So unsupervised proxy metrics use பண்ணுவோம். அது imperfect.

**Actionability**: Drift detect பண்ணினால் என்ன பண்ணுவீங்க? Auto-retrain பண்ணலாம், அது risk. Manual review பண்ணலாம், அது slow. Architect முடிவு தான் முக்கியம்.

Failure mode: Drift monitor itself drift ஆகும். Baseline stale ஆகும். Monitoring pipeline fail ஆனால் நீங்கள் blind ஆகிறீர்கள்.

## 6. Practical Example

Enterprise support bot.

Baseline: training data = last 12 months tickets. Embedding centroid stable.

Production telemetry:
* Average query embedding distance from baseline +18% last 2 weeks
* Retrieval recall@5 drop from 0.72 → 0.58
* User thumbs down +32%
* New top tokens: "new billing portal", "UPI autopay"

Reasoning: company launched new billing portal 3 weeks ago. Knowledge base update ஆகல. Vector DB-ல புது docs இல்ல.

Action: Drift alert triggered. Data ingestion pipeline check → missing. Hotfix: crawl new portal docs → re-index → A/B test retrieval.

இல்லாமல் இருந்தா நீங்கள் பார்ப்பது மட்டும் "model bad" என்று.

## 7. Reasoning Challenge

உங்கள் RAG system-க்கு drift monitor இருக்கு. Input embedding distribution shift detect ஆகுது. ஆனால் retrieval recall, generation quality metrics normal-ஆ இருக்கு.

இதை ignore பண்ணலாமா? அல்லது investigate பண்ணனுமா? ஏன்?

*Hint: Data drift always leads to concept drift?*

## 8. Key Takeaways

* Drift = environment மாறியதால் system behavior மாறுவது, code மாறாமல்
* AI system-ல data drift, concept drift, model drift எல்லாம் production reality
* Drift monitoring = statistical comparison of production vs baseline distribution, not just error rate
* Early detection உங்களுக்கு retrain / re-index / prompt update முடிவை சரியான நேரத்தில் எடுக்க உதவும்
* Every detection needs an action policy: alert, auto-remediate, or human review

Drift-ஐ புரிஞ்சுக்கிட்டா நீங்கள் AI system-ஐ static model அல்ல, living system ஆக treat பண்ண ஆரம்பிப்பீங்க.
