# Training-data concerns

> **Learning Path:** Security Architecture
> **Section:** 6.3.9 — AI security

## Problem

உங்கள் company-க்கு internal knowledge base இருக்கு. Customer support tickets, internal design docs, code repos, sales call transcripts எல்லாம் ஒன்றாக சேர்ந்து இருக்கு. Business value கிடைக்கும் என்று நினைத்து அதை வைத்து ஒரு LLM-ஐ fine-tune பண்ண அல்லது RAG pipeline-க்கு source ஆக்க ஆசைப்படுகிறீர்கள்.

இப்போது கேள்வி: அந்த data-ல என்ன இருக்கு?

ஒரு log file-ல hardcoded API key இருக்கலாம். ஒரு support ticket-ல customer-ன் phone number, Aadhaar number, credit card last 4 digits இருக்கலாம். ஒரு engineer-ன் draft doc-ல unfinished product plan இருக்கலாம். Web scrape பண்ணிய data-ல copyrighted books, personal blogs இருக்கலாம்.

Model-ஐ train பண்ணினால் என்ன ஆகும்? Model அதை மெமரைஸ் பண்ணி, பின்னர் prompt கொடுத்தால் அதே secret-ஐ திருப்பி கொடுக்கும். அல்லது ஒரு attacker தனது malicious samples-ஐ training set-ல கொண்டு வந்து model behavior-ஐ மாற்றுவான்.

Training data என்பது input மட்டும் இல்லை. அது model-ன் behavior-ன் root cause. Data-ல பிரச்சனை இருந்தால் model-ல பிரச்சனை தானாக வரும்.

## Mental Model

Training data-ஐ ஒரு supply chain ஆக பார்க்கணும்.

Raw source -> Collection -> Cleaning / Classification -> Training -> Deployment

ஒவ்வொரு stage-லயும் trust assumption மாறும். Raw data என்பது untrusted. Training என்பது irreversible. ஒரு முறை model-ல memorize ஆன தகவலை பின்னால் எளிதாக அழிக்க முடியாது.

அதனால் data concern என்பது மூன்று கேள்விகள்:

* Confidentiality: இந்த data train ஆக வேண்டுமா?
* Integrity: இந்த data சரியானதா, poison ஆகியிருக்கிறதா?
* Provenance: இந்த data எங்கிருந்து வந்தது, யார் உரிமையாளர்?

## How It Works

LLM training என்பது statistical pattern matching. Model data-ல frequent patterns-ஐ strong weight-ஆக கற்றுக்கொள்ளும்.

இது இரண்டு risk-ஐ உருவாக்கும்:

**Memorization & Leakage.** Model training data-ல இருந்து verbatim chunks-ஐ கற்றுக்கொள்ளும். Small dataset-ல fine-tune பண்ணும்போது இது மிகவும் தீவிரமாகும். பின்னர் ஒரு attacker targeted prompt கொடுத்தால் PII, secret keys, internal strategy leak ஆகும்.

**Poisoning.** Training set-ல மாற்றங்களை செலுத்தி model output-ஐ கட்டுப்படுத்த முடியும். Public web data-ல இருந்து திரட்டினால், attacker தனது content-ஐ SEO பண்ணி corpus-ல கொண்டு வந்து backdoor trigger உருவாக்குவான். Fine-tuning data-ல ஒரு மாற்றப்பட்ட sample இருந்தால் model அதை trusted knowledge-ஆக கற்றுக்கொள்ளும்.

Data provenance இல்லாமல் நீங்கள் என்ன train பண்ணுகிறீர்கள் என்றே தெரியாது.

## Architectural Reasoning

Training-data concerns தேவைப்படுவது இங்கே:

* Internal data-ஐ model-ல பயன்படுத்த வேண்டும், ஆனால் data classification செய்யப்படவில்லை.
* Third-party data license, copyright தெளிவில்லை.
* Model output-ல sensitive data leak ஆகக்கூடாது என்ற compliance requirement இருக்கு.

Options:

1. **Data minimization + classification.** Sensitive data classes-ஐ identify பண்ணி train set-ல இருந்து அகற்று. PII detection, secret scanning pipeline வை.
2. **Sanitization pipeline.** Data cleaning, deduplication, redaction, consent filtering.
3. **Provenance & lineage.** Data source, license, collection timestamp, owner tag-ஐ metadata ஆக வைத்திரு.
4. **Technical controls.** Differential privacy, federated learning, training with data filters.

அரசாங்க regulation, customer trust, IP risk இருக்கும் போது 1+2+3 கட்டாயம்
