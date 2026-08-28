# Context windows

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.5 — Understand

## 1. Problem

உங்களுக்கு ஒரு customer support agent build பண்ணணும். User 20-30 turns chat பண்ணியிருக்கார், பிறகு "முன்னாடி சொன்ன plan பத்தி என்ன ஆச்சு?"ன்னு கேக்குறார்.

LLM-க்கு அந்த முழு conversation-ம் கொடுக்கணும், இல்லைன்னா context இழந்துடும். ஆனா ஒவ்வொரு turn-க்கும் history அதிகமாகிக்கிட்டே போகும். 50 turns ஆனதும் prompt size பல ஆயிரம் tokens ஆகிடும்.

இன்னொரு case: 100 page PDF-ஐ summarise பண்ணணும். முழு document-ஐ ஒரே முறையில் கொடுத்தால் LLM அதை முழுசா பார்க்க முடியுமா? முடியாது.

இங்கே தான் **context window** பிரச்சனை தெரிய வரும். Model-க்கு ஒரே நேரத்தில் பார்க்க முடிந்த maximum input+output tokens ஒரு limit. அதுக்கு மேல history வந்தால் என்ன செய்வது?

## 2. Mental Model

Context window = LLM-ன் working memory.

நாம் நினைவில் வைத்துக்கொள்ளும் குறிப்புகளின் எண்ணிக்கைக்கு ஒரு limit இருக்கிறது போல. Model-க்கும் ஒரு limit இருக்கு. அந்த window-க்குள் இருக்கும் tokens மட்டுமே அது பார்க்கும், மீதி கட் ஆகும்.

அதில் system prompt, conversation history, retrieved documents, tool outputs எல்லாம் சேரும். Output-க்கும் tokens தேவை, அதனால் உண்மையில் usable input space இன்னும் குறைவு.

## 3. How It Works

LLM input-ஐ tokens ஆக மாற்றும். ஒரு token ~ 4 characters.

Context window size என்பது model spec-ல் சொல்லப்படும் max tokens, உதாரணமாக 8k, 32k, 128k, 200k.

Attention mechanism-க்கு complexity ~ O(n²). Window பெரிதாகும்போது compute, memory, latency எல்லாம் அதிகரிக்கும். அதனால் limit வைக்கப்படுகிறது.

நீங்கள் window-க்கு மேல் தரும் content-ஐ model பார்க்கவே முடியாது. அது silently drop ஆகும் அல்லது நீங்கள் truncate செய்ய வேண்டும்.

## 4. Architectural Reasoning

Context window ஒரு constraint. அதை மீறாமல் useful information-ஐ model-க்கு கொண்டு செல்வது தான் design problem.

Options:

* **Truncate**: பழைய history-ஐ cut பண்ணுவது. simple ஆனால் coherence போகும்.
* **Summarize**: பழைய turns-ஐ summary ஆக்கி window-ல் வைத்துக்கொள்வது. long-term memory கிடைக்கும், ஆனால் detail இழக்கும்.
* **Retrieve selectively**: RAG போல, relevant chunks மட்டும் fetch பண்ணி சேர்ப்பது. conversation history-க்கு கூட vector store பயன்படுத்தி relevant turns மட்டும் திருப்பி கொடுக்கலாம்.
* **Streaming / Chunk
