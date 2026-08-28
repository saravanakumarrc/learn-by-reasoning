# Attention — conceptual understanding

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.7 — Understand

## 1. Problem

ஒரு sentence-ஐ புரிஞ்சுக்கணும்னா ஒவ்வொரு word-க்கும் அதன் அர்த்தம் அந்த sentence-ல இருக்குற மத்த words-ஆல மாறும்.

> "Bank-க்கு போய் loan எடுத்தேன்" vs "River bank-ல உட்கார்ந்தேன்"

`bank` எதை குறிக்குதுன்னு தெரியணும்னா அதுக்கு பக்கத்துல இருக்குற words முக்கியம். சில சமயம் 100 tokens தூரத்துல இருக்குற word-கூட முக்கியமாகும்.

RNN / LSTM போன்ற sequential models இருந்தன. ஒவ்வொரு token-ஐயும் ஒன்னுக்கு பின்னால ஒன்னு படிக்கும். அதனால்:

* Training-ல parallelization குறைவு, latency அதிகம்
* Long-range dependency-ல vanishing gradient வரும்
* "The animal ... it ..." என்றால் `it` எதை குறிக்குதுன்னு 200 tokens தூரத்துல இருந்து memory-ல தக்கவைக்கணும்

இந்த வலி பெருசா ஆனப்போ தான் engineers `attention` என்ற concept-ஐ தேடினார்கள். பிரச்சனை என்னவென்றால்: **ஒரு token எழுதும்போது, அதற்கு எந்த முந்தைய tokens தேவை? எவ்வளவு முக்கியம்?**

## 2. Mental Model

Attention = ஒரு spotlight.

ஒரு token ஐ read பண்ணும்போது, முழு context window-லயும் ஒரு கணம் பார்த்து, "எனக்கு இது முக்கியம், இது கொஞ்சம் முக்கியம், இது தேவையில்லை" என்று weight கொடுப்பது.

அது மனித மூளை படிக்கும்போது செய்வது போல: ஒரு paragraph-ல முக்கியமான phrase-ஐ மட்டும் focus பண்ணுவது.

## 3. How It Works

Transformer-ல attention ஒரு simple math operation ஆக வந்தது.

ஒவ்வொரு token-க்கும் மூன்று representation உருவாக்கப்படுகிறது:
* **Query**: "நான் என்ன தேடுகிறேன்?"
* **Key**: "நான் என்ன பற்றி விவரிக்கிறேன்?"
* **Value**: "நான் உண்மையில் கொண்டு வரும் தகவல்"

ஒரு token-ன் Query-வை மற்ற எல்லா tokens-ன் Key-களோடு dot product பண்ணினால் relevance score கிடைக்கும். அதை scale பண்ணி softmax மூலம் 0-1 weights ஆக normalize செய்வார்கள்.

அந்த weights-ஐ Value-களோடு weighted sum பண்ணினால், அந்த token-க்கு தேவையான context மட்டும் கிடைக்கும்.

இது self-attention எனப்படும். அதாவது input sequence தன்னையே கவனித்துக்கொள்வது.

Multi-head attention என்றால்: வெவ்வேறு "spotlights" வெவ்வேறு விஷயங்களை பார்க்கும். ஒரு head syntax பார்க்கும், இன்னொரு head long-range coreference பார்க்கும்.

## 4. Architectural Reasoning

ஏன் attention முக்கியமானது?

* **Parallelism**: RNN போல sequential dependency இல்லை. எல்லா tokens-க்கும் query/key/value ஒரே சமயத்தில் கணக்கிடலாம். Training throughput பெருகும்.
* **Long-range dependency**: 10 tokens தூரமா, 1000 tokens தூரமா என்பது attention-க்கு பெரிய வித்தியாசம் இல்லை. Dot product எப்போதும் வேலை செய்யும்.
* **Interpretability**: எந்த token எதை கவனித்தது என்பதை weight matrix-ல பார்க்கலாம்.

இதனால் தான் Transformer architecture வந்தது. Attention is all you need என்பது ஒரு architectural decision, not a feature list.

## 5. Trade-offs

* **Quadratic cost**: Sequence length n என்றால் attention matrix n x n. 32k context என்றால் 1B operations. Compute, memory, latency எல்லாம் அதிகரிக்கும். இது production cost-ஐ நேரடியாக தீர்மானிக்கும்.
* **Context window limit**: Hardware memory காரணமாக practical limit வரும். Long document-க்கு sliding window, chunking, retrieval augmentation தேவைப்படும்.
* **No inherent recurrence**: Attention மட்டும் memory இல்லை. State எதுவும் carry ஆகாது. அதனால் streaming / real-time use case-ல additional mechanisms தேவை.
* **Overfitting to training distribution**: Attention weights data-driven. Out-of-distribution patterns-ல relevance தவறாக கற்றுக்கொள்ளலாம்.

## 6. Practical Example

RAG system-ல LLM ஒரு user query-ஐ பார்க்கும் போது, retrieved chunks ஒரு context window-ல வரும்.

உதாரணமாக 10 chunks உள்ளன. User கேட்கிறார் "Q3 revenue எவ்வளவு". Attention mechanism automatically Q3, revenue, financial report போன்ற tokens-க்கு high weight கொடுக்கும், unrelated marketing text-க்கு low weight கொடுக்கும்.

இங்கே attention தான் "relevant chunk-ஐ தேர்ந்தெடுக்கும்" மெக்கானிசம். RAG retrieval மட்டும் போதாது, LLM உள்ளே attention தான் முடிவு செய்யும்.

## 7. Reasoning Challenge

உங்களிடம் 100k tokens நீளமான legal contract உள்ளது
