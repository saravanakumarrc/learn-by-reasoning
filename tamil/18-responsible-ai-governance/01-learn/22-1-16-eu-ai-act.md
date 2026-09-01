# EU AI Act

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.16 — Learn

## 1. Problem

நீங்கள் ஒரு AI Solution Architect. உங்கள் company ஒரு hiring tool build பண்ணுது. Resume scan பண்ணி shortlist பண்ணும். ஒரு நாள் candidate complain பண்ணார்: "என்னை reject பண்ணது bias ஆக இருக்கு". உங்களுக்கு explain பண்ண evidence இல்லை. Audit log இல்லை. Model எப்படி decide பண்ணிச்சுன்னு தெரியாது.

அடுத்து EU client வரார். "உங்கள் system EU AI Act compliant ஆ?" என்று கேட்கிறார். இல்லைன்னா contract கிடைக்காது.

இதுதான் பிரச்சனை. AI system வெறும் accuracy மட்டும் பார்த்தால் போதாது. Risk, transparency, accountability வேண்டும். அரசாங்கம் அதை law ஆக்கியிருக்கு.

**What goes wrong if we don't have this?** Fines வரும், product ban ஆகும், trust இழக்கும், audit-ல fail ஆவீங்க.

## 2. Mental Model

EU AI Act என்பது AI system-ஐ risk-ன் அடிப்படையில் classify பண்ணும் ஒரு governance framework.

அதன் core idea simple:
> Risk அதிகமா இருக்கும் system-க்கு கட்டுப்பாடுகள் அதிகம்.

ஒரு toy recommendation system-க்கும், credit scoring system-க்கும் ஒரே rule இருக்கக் கூடாது.

## 3. How It Works

EU AI Act 4 risk tiers-ஆக பிரிக்கிறது.

**1. Unacceptable Risk - Prohibited**
உதாரணம்: social scoring by government, real-time biometric identification in public spaces for mass surveillance, emotion recognition at workplace/school to manipulate. இதை outright ban பண்ணியிருக்காங்க.

**2. High Risk**
இதுதான் architect-க்கு முக்கியம். Examples:
- Biometric identification
- Critical infrastructure
- Education/vocational training
- Employment hiring & promotion
- Credit scoring
- Law enforcement

High risk system-க்கு **mandatory obligations** உண்டு:
- Risk management system
- Data governance: training data quality, bias mitigation
- Technical documentation
- Record keeping / logging
- Transparency & user information
- Human oversight
- Accuracy, robustness, cybersecurity
- Conformity assessment before market placement

**3. Limited Risk**
Chatbots, deepfakes, emotion recognition. Transparency obligations மட்டும். User-க்கு "you are talking to AI" என்று தெரிய வேண்டும்.

**4. Minimal Risk**
எந்த special obligation இல்லை. General purpose AI model என்றாலும் transparency முக்கியம்.

Act என்பது provider மற்றும் deployer இருவருக்கும் பொறுப்பு வழங்குகிறது. உங்கள் hiring tool-ஐ build பண்ணியவர் provider, use பண்ணியவர் deployer.

## 4. Architectural Reasoning

**When does this become useful?**
EU market-ல விற்கும், அல்லது EU citizen-க்கு serve பண்ணும் எந்த AI system-க்கும்.

**What constraint it addresses?**
Legal compliance + trust + accountability.

**Why choose what?**
High risk system design பண்ணும்போது, architecture-ஐ compliance-first-ஆக design பண்ணணும். Model accuracy மட்டும் பார்த்து deploy பண்ணக்கூடாது.

உதாரணமாக hiring tool high risk. அப்போ:
- Training data-ல bias audit log வைக்கணும்
- Decision explainability வேண்டும்
- Human-in-the-loop மandatory
- Model performance metrics-ஐ continuously monitor பண்ணணும்

## 5. Trade-offs

**1. Speed vs Compliance**
Compliance documentation, risk assessment, human oversight எல்லாம் time and cost அதிகரிக்கும். MVP fast-ஆ launch பண்ண முடியாது.

**2. Transparency vs IP protection**
Model documentation, data governance திறந்து காட்டணும். உங்கள் proprietary training data, architecture expose ஆகும் risk.

**3. General purpose model vs fine-tuned control**
Foundation model provider vs deployer. Provider-க்கு obligations வேறு, deployer-க்கு வேறு. Responsibility chain clear ஆக்கணும்.

**4. Innovation vs restriction**
Unacceptable risk list expand ஆகலாம். நீங்கள் design பண்ணிய feature நாளைக்கு banned ஆகலாம்.

Failure mode: நீங்கள் system-ஐ high risk என்று classify பண்ணாமல் limited risk என்று assume பண்ணீங்கன்னா, post-deployment audit-ல fine வரும். Up to 7% global turnover.

## 6. Practical Example

Enterprise RAG system for HR policies.

Problem: Employee chatbot gives wrong policy answer. High risk இல்லை போல தெரியும்.

But if that chatbot auto-approves leave or salary change, அது high risk ஆகிவிடும்.

Architectural decision:
- Separate read-only Q&A vs action-taking agent
- Read-only = Limited risk, just disclose AI use
- Action-taking = High risk, need human approval workflow, audit trail, data governance

நீங்கள் architecture-ஐ இரண்டு service-ஆக பிரித்தீர்கள். Audit log centralize பண்ணீர்கள். Human override button வைத்தீர்கள்.

இப்போ compliance team-க்கு evidence கொடுக்க முடியும்.

## 7. Reasoning Challenge

உங்களிடம் EU bank-க்கு credit scoring model உள்ளது. Model 95% accuracy. Training data 3 years old. Model-ஐ retrain பண்ணாமல் deploy பண்ணலாமா? EU AI Act-ன் பார்வையில் என்ன risk உள்ளது? Architecture-ல என்ன கூடுதல் components வேண்டும்?

சிந்தியுங்கள்: data governance, monitoring, human oversight, documentation.

## 8. Key Takeaways

- EU AI Act risk-based governance ஆகும். Risk அதிகமானால் obligations அதிகம்.
- High risk AI system-க்கு compliance என்பது model performance அல்ல, lifecycle governance.
- Provider மற்றும் deployer இருவருக்கும் legal responsibility உள்ளது.
- Architecture design-ல auditability, human oversight, transparency-ஐ முதலில் build பண்ணுங்கள், பிறகு accuracy.
- Every architectural solution creates trade-off: compliance adds cost, latency, complexity.
