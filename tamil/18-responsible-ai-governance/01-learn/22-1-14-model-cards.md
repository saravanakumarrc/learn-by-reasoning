# Model cards

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.14 — Learn

## 1. Problem

உங்கள் team ஒரு LLM-based agent build பண்ணியிருக்கு. Model change பண்ணப்போறீங்க. Production-ல ஏற்கனவே வேறொரு model இருக்கு.

இப்போ கேள்வி வரும்:

- இந்த model எந்த data-ல train ஆச்சு?
- Bias உண்டா? Safety எப்படி test பண்ணீங்க?
- Latency, throughput என்ன?
- License என்ன? Commercial use அனுமதிக்கிறதா?
- Limitations என்ன? எந்த use case-ல fail ஆகும்?

இந்த கேள்விகளுக்கு engineer-கிட்ட clear answer இல்லை. PM கேக்கார், compliance கேக்கார், customer கேக்கார். Repo-ல README மட்டும் இருக்கு, ஆனா scattered notes.

Model ஒரு black box-ஆ மாறிடுது. பின்னாடி incident வந்தா root cause அடைய முடியாது.

**What goes wrong if we don't have this?** Trust இல்லாம போகும், audit fail ஆகும், wrong model wrong place-ல deploy ஆகும்.

## 2. Mental Model

Model card என்பது model-க்கான nutrition label + datasheet.

ஒரு model-ஐ use பண்ணுறவங்களுக்கு தேவையான context-ஐ ஒரே இடத்தில் கொடுக்கிற ஒரு standardized document.

இது marketing brochure இல்லை. இது architectural decision-க்கு தேவையான facts.

Think of it like API contract, but for model behavior, data, risks, and operational constraints.

## 3. How It Works

Model card ஒரு structured record. Usually JSON/YAML/Markdown. Key sections:

**Model Details:** Model name, version, owner, license, release date
**Intended Use:** Primary use cases, out-of-scope uses
**Training Data:** Data sources, size, time range, filtering, known biases
**Metrics:** Performance on benchmark datasets, eval metrics like accuracy, F1, latency, throughput
**Evaluation:** Safety tests, red-teaming results, failure modes
**Ethical Considerations:** Bias, fairness, privacy risks
**Operational:** Deployment requirements, cost per 1k tokens, rate limits, monitoring signals

இது model artifact-உடன் version control-ல இருக்கும். Model registry-ல link ஆகும்.

## 4. Architectural Reasoning

Model card ஏன் தேவை?

**Constraint: Governance and trust.** Responsible AI & Governance path-ல நீங்கள் model-ஐ product-ல போடுறீங்க. Stakeholder-களுக்கு explainability தேவை.

**When useful:**
- Model selection பண்ணும்போது. 3 models இருக்கு, எது business requirement-க்கு fit?
- Model update/retrain பண்ணும்போது. Regression உண்டா?
- Compliance audit வரும்போது. EU AI Act, internal policy-க்கு evidence தேவை.
- Handoff between teams. Research -> MLOps -> Product.

**Alternatives:**
- Ad-hoc README / Confluence doc. Works for one model, scales இல்லை.
- Model registry metadata only. Too technical, non-technical stakeholders புரியாது.
- No documentation. Fast initially, expensive later.

Architect ஏன் choose பண்ணுவார்? Because it reduces decision risk and operational surprise. Model-ஐ ஒரு component மாதிரி treat பண்ண முடியும்.

## 5. Trade-offs

**Standardization vs. completeness.** Too strict template, teams fill with garbage. Too loose, no comparability.

**Maintenance cost.** Model evolve ஆகும், data drift ஆகும். Card stale ஆகும். இது living document ஆக இருக்கணும்.

**Transparency vs. IP risk.** Training data details share பண்ணலாமா? Competitor advantage போயிடுமோ? Balance needed.

**Human readable vs. machine readable.** Compliance-க்கு human readable வேணும். Automation-க்கு structured schema வேணும். Both maintain பண்ணணும்.

Failure mode: Card இருக்கு, ஆனா outdated. Team card-ஐ trust பண்ணி wrong decision எடுக்கும். அதனால card-க்கும் model version-க்கும் tight coupling வேணும்.

## 6. Practical Example

Enterprise RAG system. Two embedding models available:

Model A card சொல்லுது:
- Intended use: General search, English only
- Training data: 2023 cut-off, web crawl filtered
- Latency: 25ms, cost $0.0001/query
- Known limitation: Tamil performance drops 30%

Model B card சொல்லுது:
- Intended use: Multilingual retrieval, includes Tamil
- Training data: 2024 cut-off, licensed corpus
- Latency: 45ms, cost $0.0003/query
- License: Non-commercial only

Product requirement: Tamil support தேவை, commercial use.

Decision: Model B technical fit, ஆனா license block பண்ணும். So you either negotiate license or go back to Model A with augmentation.

இல்லாமல் card இருந்தா, நீங்கள் latency மட்டும் பார்த்து Model A தேர்வு பண்ணி production-ல Tamil queries fail ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் internal LLM fine-tuned for financial advice இருக்கு. Model card-ல Intended Use: "Internal research only, not for customer-facing advice". Product team அதை customer chatbot-ல deploy பண்ண request பண்ணுது.

Latency fine, cost fine. Card-ல Safety evaluation: "Hallucination rate 8% on financial QA, no guardrails for disallowed advice".

நீங்கள் என்ன decision எடுப்பீங்க? Model card-ல இருக்கும் எந்த 2 facts உங்கள் decision-ஐ drive பண்ணும்? Deploy பண்ணாமல் இருந்தால் alternative என்ன?

## 8. Key Takeaways

- Model card என்பது model-க்கான decision-making context, marketing material அல்ல
- Problem-ஐ solve பண்ணுது: model about-ஐ யாருக்கும் தெளிவாக, repeatably communicate பண்ண
- Card stale ஆனால் harmful. Version it with model artifact
- Intended use, limitations, and risks மூன்றும் architectural fit-க்கு முக்கியம்
- Good model card = faster, safer model adoption
