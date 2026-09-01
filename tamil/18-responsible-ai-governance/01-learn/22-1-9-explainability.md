# Explainability

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.9 — Learn

## 1. Problem

உங்கள் team ஒரு credit approval model deploy பண்ணியிருக்கு. Model ஒரு applicant-க்கு loan deny பண்ணுது. Customer support-க்கு call வருது: "ஏன் எனக்கு reject?"

உங்களால சொல்ல முடியுமா? "Model அப்படி சொன்னது" என்று சொன்னால் போதுமா?

Regulator கேட்கிறார்: "இந்த decision எப்படி வந்தது? Bias இல்லையா?" Auditor கேட்கிறார்: "இதை நீங்கள் எப்படி justify பண்ணுவீர்கள்?" Business team கேட்கிறார்: "இந்த model-ஐ trust பண்ணலாமா?"

இங்கே problem என்ன? Model correct ஆக இருந்தால் மட்டும் போதாது. Decision-ஐ விளக்க முடியாமல் போகிறது. Explainability இல்லாததால் trust, compliance, debug எல்லாம் முடங்குகிறது.

**What goes wrong if we don't have this?** Blame model, no root cause, silent bias, regulatory fine, customer churn.

## 2. Mental Model

Explainability என்பது model-ன் output-க்கு ஒரு human-understandable reason கொடுப்பது.

இது மூன்று layer-ல் வேலை செய்யும்:

* **Technical explainability**: Model எப்படி decide பண்ணியது? Feature contribution என்ன?
* **Business explainability**: அந்த decision business rule-க்கு align ஆகிறதா?
* **User explainability**: End user-க்கு simple language-ல் ஏன் இப்படி வந்தது என்று சொல்ல முடியுமா?

Think of it as a decision audit trail. Model என்பது black box. Explainability என்பது அதற்கு glass pane போடுவது.

## 3. How It Works

Explainability இரண்டு வகை:

**1. Intrinsic / Model-level**
Model design-இலேயே interpretable ஆக இருக்கும். Example: decision tree, linear model with coefficients. இங்கே explainability cheap. Accuracy கொஞ்சம் குறையலாம்.

**2. Post-hoc / Model-agnostic**
Complex model-க்கு பிறகு explanation generate பண்ணுவது. Examples:
* **SHAP / LIME**: Feature-க்கு contribution score கொடுக்கும். "income low ஆனதால் -0.32, credit history short ஆனதால் -0.18"
* **Counterfactual**: "உங்கள் income ₹5k அதிகமாக இருந்தால் approve ஆகியிருக்கும்"
* **Attention visualization** in LLM: எந்த part of input-க்கு model focus பண்ணியது

Production-ல் இது usually a separate explanation service. Model prediction வந்த பிறகு explainer model run ஆகி explanation artifact generate ஆகும். இதை log பண்ணி store பண்ணுவது முக்கியம்.

## 4. Architectural Reasoning

Explainability useful ஆகும் போது:

* High-stakes decisions: credit, hiring, medical triage, fraud block
* Regulated domain: Finance, insurance, healthcare
* Customer-facing AI: chatbot, recommendation
* Model drift / debug தேவைப்படும் system

Constraints it addresses:
* **Trust**: Stakeholder model-ஐ accept பண்ணுவாரா?
* **Compliance**: Audit, fairness, GDPR right to explanation
* **Operability**: Wrong prediction-ஐ debug எப்படி பண்ணுவது?

Alternatives:
* Don't explain, just show accuracy metrics. Works for low-risk recommendation.
* Use interpretable model only. Works when data simple.
* Use human-in-the-loop review. Costly, slow.

Architect choose பண்ணும்போது கேட்க வேண்டியது: Explanation-ஐ யாருக்காக தயார் பண்ணுகிறோம்? Regulator-க்கா? End user-க்கா? Data scientist-க்கா? Audience-க்கு ஏற்ப explanation granularity மாறும்.

## 5. Trade-offs

1. **Accuracy vs Interpretability**: Most interpretable models குறைவான accuracy. Complex models accurate ஆனால் explain hard. உண்மையான trade-off இது.

2. **Explanation fidelity vs Simplicity**: SHAP exact ஆக இருக்காது, approximation. Simple explanation தவறான reassurance கொடுக்கலாம்.

3. **Latency & Cost**: Post-hoc explainers add latency. Real-time fraud decision-ல் 50ms budget இருக்கும்போது SHAP run பண்ண முடியாது. Offline explanation batch பண்ண வேண்டும்.

4. **Security vs Transparency**: Explanation-ல் sensitive feature leak ஆகலாம். Example: model uses zip code as proxy for caste. Explanation reveal பண்ணி bias expose ஆகும். So explanation layer-ல் filtering தேவை.

Failure mode: Explanation hallucination. LLM agent சொல்லும் reason prediction-ஐ உண்மையாக reflect பண்ணாமல் போகலாம். User trust பண்ணி தவறு பண்ணுவார்.

## 6. Practical Example

Enterprise loan approval system.

Architecture:
`API Gateway → Risk Service → Model Service → Explanation Service → Audit Log`

Model Service XGBoost-ஐ use பண்ணி approve/deny return பண்ணும். Explanation Service SHAP values compute பண்ணி top 3 features extract பண்ணும். அதை business-friendly template-ல் மாற்றும்: "உங்கள் CIBIL score 620, requested amount high, employment tenure <2 years."

இந்த explanation JSON-ஐ event-ஆக send பண்ணி audit store-ல் save பண்ணுவோம். Customer portal-ல் simplified version காட்டுவோம். Regulator request வந்தால் full SHAP report + feature values கொடுக்க முடியும்.

இங்கே decision என்ன? Real-time path-ல் explanation skip பண்ணி async generate பண்ணுவோம். Latency protect பண்ண.

## 7. Reasoning Challenge

உங்களிடம் LLM-based resume screening agent இருக்கு. 10,000 resumes daily process பண்ணும். Hiring manager கேட்கிறார்: "ஏன் இந்த candidate reject ஆனார்?"

Real-time explanation வேண்டுமா? Async explanation போதுமா? Explanation-ஐ candidate-க்கு காட்ட வேண்டுமா, internal team-க்கு மட்டுமா?

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? SHAP போன்ற feature attribution use பண்ண முடியுமா? LLM-க்கு post-hoc explanation hallucination risk எப்படி குறைப்பீர்கள்?

## 8. Key Takeaways

* Explainability என்பது model accuracy-க்கு அடுத்த priority. Trust, compliance, debug-க்கு அவசியம்.
* Intrinsic vs Post-hoc trade-off உண்டு. Use case-க்கு ஏற்ப தேர்வு பண்ணுங்கள்.
* Explanation-ஐ audience-க்கு ஏற்ப tailor பண்ணுங்கள். Regulator, user, engineer எல்லாருக்கும் வேறு வேறு depth.
* Every explanation system adds latency, cost, and potential leakage. அதற்கான guardrail வேண்டும்.
* Explainability without actionability worthless. Explanation-ல் இருந்து model fix, bias mitigation, product improvement நடக்க வேண்டும்.
