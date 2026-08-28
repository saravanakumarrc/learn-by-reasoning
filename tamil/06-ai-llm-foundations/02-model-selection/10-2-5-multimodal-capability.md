# Multimodal capability

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.5 — Model selection

## 1. Problem

உங்கள் AI system-க்கு text மட்டும் போதுமா?

ஒரு customer support agent chatbot இருக்கு. User எழுதுறார்: "என் order-ல வந்த product-இன் photo பாருங்க, colour mismatch இருக்கு". 

Text-only LLM-க்கு என்ன தெரியும்? Photo பார்க்க முடியாது. User-க்கு "photo upload பண்ணுங்க, நான் பார்க்க முடியாது"ன்னு சொல்ல முடியும். அது bad experience.

இன்னொரு scenario: RAG system-ல support tickets-இல் உள்ள screenshots, PDF invoices, voice notes எல்லாம் இருக்கு. Text-only model அதை புரிஞ்சுக்க முடியாது. Information loss ஆகும்.

அதனால் வந்த பிரச்சனை: **World is multimodal, but model is unimodal.** User input, business data, output medium எல்லாம் text அல்ல.

What goes wrong if we don't have multimodal capability?
* Context loss - visual evidence, audio nuance போய்விடும்
* Extra preprocessing pipeline - OCR, speech-to-text போன்ற brittle layers தேவை
* Latency + error propagation - conversion step-ல தப்பு நடக்கும்
* Poor user experience - natural interaction முடியாது

## 2. Mental Model

Multimodal capability = ஒரு model ஒன்றுக்கு மேற்பட்ட modalities-ஐ ஒரே representation space-ல புரிஞ்சுக்கும் திறன்.

Text, image, audio, video - இதை ஒரே embedding space-ல map பண்ணி, cross-modal reasoning செய்யும்.

Mental model: **Modality = different sensors.** Model-க்கு ஒரே brain இருக்கு, ஆனால் eyes, ears, language input எல்லாம் அதே brain-க்கு feed ஆகும்.

நாம் தனித்தனி translator வைக்காமல், model-ஐயே multi-sensor ஆக்குறோம்.

## 3. How It Works

Text-only LLM: tokens → embeddings → attention → output.

Multimodal LLM: 
1. Each modality-க்கு encoder இருக்கும். Vision encoder for image, audio encoder for speech.
2. Encoder output-ஐ text token embeddings-க்கு ஒத்த format-ல project பண்ணும். "Visual tokens" ஆக்கும்.
3. இப்போ LLM backbone அதை text tokens மாதிரியே process பண்ணும். Cross-attention மூலம் text + image context mix ஆகும்.
4. Output-ம் multimodal ஆக இருக்கலாம் - text, image generation, audio.

முக்கியமானது: Model-க்கு alignment தேவை. Image-ல ஒரு cat இருக்கு என்பதை text token "cat" உடன் associate பண்ணுவது. அதற்கு large-scale paired data training.

## 4. Architectural Reasoning

When does multimodal become useful?

* User interaction is natural: Chat with photo, voice note, screen recording
* Data is inherently multimodal: Product catalog with images, medical reports with scans, video support logs
* Output needs richness: Generate chart from description, create image from prompt, summarize video

What constraint it addresses?
* Completeness of context. Text conversion-ல தகவல் இழப்பு இல்லை.
* Reduced pipeline complexity. OCR + STT + LLM என்ற chain-க்கு பதில் single model.

Alternatives:
* Unimodal LLM + preprocessing pipeline. OCR, speech-to-text, image captioning பின்னர் LLM. Cheaper, modular. ஆனால் error cascade, latency அதிகம்.
* Specialist models per modality. Vision model + LLM separately. Control அதிகம், integration complexity அதிகம்.

Architect ஏன் choose பண்ணுவார்?
Latency sensitive, user-facing agent-க்கு direct multimodal தேவை. Internal batch processing job-க்கு preprocessing pipeline போதும்.

## 5. Trade-offs

**1. Cost vs Fidelity**
Multimodal models are larger, more expensive per token. Image token ~ hundreds of text tokens. Inference cost உயரும். Operability கடினம்.

**2. Latency vs Context Richness**
Vision/audio encoding adds latency. Real-time voice agent-ல 300ms vs 1500ms வித்தியாசம் user experience-ஐ மாற்றும்.

**3. Generality vs Accuracy**
One model does everything, ஆனால் specialist vision model-விட குறைவான accuracy கொடுக்கலாம். Medical image diagnosis-க்கு specialist தேவை.

**4. Data Privacy & Safety**
Image/audio input-ல PII, sensitive content வரும். Text-only pipeline-விட moderation கடினம். Audio transcription-ல privacy leakage risk.

Failure modes:
* Hallucination across modalities - model image-ல இல்லாததை பார்த்ததாக சொல்லும்
* Modal bias - text-ஐ அதிக weight கொடுத்து visual cue-ஐ ignore பண்ணும்
* Token budget overflow - high-res image-ஐ process பண்ண முடியாமல் truncate ஆகும்

## 6. Practical Example

Enterprise support RAG system.

Problem: 10M support tickets உள்ளன. 40% tickets-ல screenshots, 15% voice call transcripts, 10% PDF invoices.

Option A: All media-ஐ text-க்கு convert செய். OCR for screenshots, ASR for calls, PDF parser. Text embeddings store. Retrieval works, but OCR errors, audio emotion loss.

Option B: Multimodal embeddings. Image, audio, text எல்லாம் same vector database-ல store. Query is text + image. Model directly cross-modal retrieve செய்யும்.

Architectural decision: User query "இது போன்ற error screen வருகிறது" + screenshot upload. Unimodal system-க்கு caption generate பண்ணி search. Multimodal system-க்கு image + text ஒன்றாக search.

Trade-off accept பண்ணினோம்: 3x inference cost, ஆனால் retrieval relevance 35% improve ஆச்சு. Customer resolution time குறைந்தது.

## 7. Reasoning Challenge

உங்களிடம் banking fraud detection agent உள்ளது. User voice note-ல transaction dispute பண்ணுகிறார், அதோடு bank statement PDF upload பண்ணுகிறார்.

இதற்கு multimodal LLM use பண்ண வேண்டுமா, இல்லை speech-to-text + PDF parser பின்னர் text-only LLM போதுமா?

Constraints: Latency <2s, PII data strict, cost sensitive, accuracy critical.

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? ஏன்? என்ன trade-off ஏற்படும்?

## 8. Key Takeaways

* Multimodal capability தேவைப்படுவது world is multimodal என்பதால், model unimodal இருக்க கூடாது என்பதால்.
* Preprocessing pipeline vs native multimodal என்பது cost, latency, accuracy, complexity trade-off.
* Model selection-ல multimodal support இருக்கிறதா என்பது user experience மற்றும் data completeness-ஐ தீர்மானிக்கும்.
* Every multimodal gain comes with cost, privacy, and operational complexity cost.
