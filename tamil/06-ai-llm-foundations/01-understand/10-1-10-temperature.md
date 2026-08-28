# Temperature

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.10 — Understand

### 1. Problem

நீங்கள் ஒரு LLM-ஐ production-ல் போடும்போது முதலில் தெரியும் பிரச்சனை இது:

அதே prompt-க்கு அதே output வருகிறது. அல்லது மிகவும் ரேண்டம் ஆகி nonsense வருகிறது.

Customer support chatbot பண்ணும்போது நீங்கள் ஒரு policy question-க்கு திட்டவட்டமான, ஒரே மாதிரியான பதிலை எதிர்பார்க்கிறீர்கள். அதே LLM-ஐ creative copy writing-க்கு பயன்படுத்தும்போது ஒவ்வொரு முறையும் ஒரே மாதிரி வரக்கூடாது, வேறுபாடு வேண்டும்.

இந்த இரண்டு தேவைக்கும் ஒரு knob வேண்டும். அதுதான் temperature.

> "What problem became painful enough?" Same prompt, unpredictable variation. Sometimes you want lock-down, sometimes you want exploration.

### 2. Mental Model

Temperature என்பது next token-ஐ தேர்ந்தெடுக்கும்போதான randomness-ஐ கட்டுப்படுத்தும் ஒரு heat knob.

Temperature குறைவு = குளிர். Model தனக்கு மிகவும் confident ஆன token-ஐ மட்டும் தேர்வு செய்யும். பதில் predictable, focused.

Temperature அதிகம் = வெப்பம். Model probability distribution-ஐ flatten பண்ணி, குறைவான likely token-களுக்கும் வாய்ப்பு கொடுக்கும். பதில் creative, diverse, ஆனால் risky.

எளிமையாக சொன்னால், temperature என்பது sampling-ன் sharpness.

### 3. How It Works

LLM ஒவ்வொரு step-லும் logits எனும் raw scores கொடுக்கும். அதை softmax-க்கு போட்டு probability distribution ஆக்குவார்கள்.

Temperature T என்பது logits-ஐ scale செய்யும்:
`logits / T`

T = 0.1 என்றால் logits பெரிதாகி distribution sharp ஆகும். Top token-ன் probability ~1 ஆகும்.
T = 1.0 என்றால் மாற்றமில்லை.
T = 1.5+ என்றால் logits சிறியதாகி distribution flat ஆகும். Random token-களும் வரும்.

இதன் பின்னால் greedy decoding-க்கு T=0, sampling-க்கு T>0 என்பது உள்ளது. Top-k, top-p என்பவை இதற்கு மேல் safety net.

### 4. Architectural Reasoning

Temperature-ஐ தேர்வு செய்வது ஒரு product decision, not a hyperparameter tuning game.

When low temperature useful:
* Factual extraction, RAG QA, classification
* Code generation, JSON output, tool calling
* Customer support, compliance-heavy responses
* Reproducibility தேவைப்படும் evaluation

When higher temperature useful:
* Brainstorming, ideation, marketing copy
* Creative writing, story generation
* Rephrase, paraphrase with variety
* User experience-ல் boredom தவிர்க்க

Alternative controls: temperature மட்டும் இல்லை. Top-p nucleus sampling diversity-ஐ கட்டுப்படுத்தும். Frequency penalty / presence penalty repetition-ஐ குறைக்கும். Architect ஆக நீங்கள் இவற்றை combo-வாக பயன்படுத்துவீர்கள்.

### 5. Trade-offs

* **Consistency vs Creativity**: Low temp = deterministic, safe. High temp = diverse, unpredictable.
* **Hallucination risk**: Temperature அதிகரிக்கும்போது low probability token-கள் வர வாய்ப்பு அதிகம். Factuality குறையும்.
* **Reproducibility vs UX**: Production debugging-க்கு நீங்கள் log-ல் temperature fix பண்ண வேண்டும். A/B test-ல் temp மாற்றினால் output distribution மாறும்.
* **Latency / cost**: Temperature தனியாக latency-ஐ மாற்றாது. ஆனால் high temp-ல் retries, re-ranking தேவை வரும்.

முக்கிய failure mode: High temperature-ஐ factual RAG pipeline-ல் போட்டுவிட்டால், context-இல் இருக்கும் தகவலை தவறாக மாற்றி hallucination கொடுக்கும்.

### 6. Practical Example

Enterprise helpdesk RAG system.

Flow: User query → Retrieve docs → Build context → LLM generate answer.

இங்கே temperature = 0.2 to 0.4. நீங்கள் deterministic answer வேண்டும், citations match ஆக வேண்டும். Output JSON schema follow ஆக வேண்டும்.

அதே org-ல் marketing team "Generate 10 campaign taglines for Diwali sale" என்று கேட்கிறார்கள். இங்கே temperature = 0.8 to 1.0. Variety வேண்டும், ஒரே மாதிரி வரக்கூடாது.

இரண்டும்
