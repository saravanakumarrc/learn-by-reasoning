# PARTIAL — Multimodal capability

> Reason: Ollama reached num_predict
> num_predict: 32768

## 1. Problem

உங்களிடம் ஒரு LLM-powered customer support service இருக்கு. Text chat மட்டும் நல்லா work ஆகுது.

ஒரு நாள் user screenshot அனுப்பி "இந்த error ஏன் வருது?" என்று கேட்கிறார். 
இன்னொரு user voice note அனுப்பி "எனக்கு இந்த order status சொல்லுங்க" என்கிறார். 
இன்னொரு user product photo upload பண்ணி "இதுக்கு similar product காட்டுங்க" என்கிறார்.

Text-only LLM-க்கு என்ன பண்ண முடியும்? Nothing. 

இப்போது நீங்கள் pipeline போட வேண்டும்:
Image -> OCR / Vision model -> text -> LLM
Audio -> Speech-to-text -> text -> LLM

இது work ஆகும், ஆனால்:
* Latency கூடும். ஒவ்வொரு step-க்கும் round trip.
* Error propagate ஆகும். Transcription தப்பா இருந்தால் LLM சரியாக பதில் சொல்லாது.
* Context loss ஆகும். Image-ல உள்ள visual layout, chart trend, handwriting style எல்லாம் text-ல மாறும்போது போய்விடும்.
* Maintenance nightmare. 3 models, 3 APIs, 3 failure modes.

**What problem became painful?** Real world data multimodal. User intent multimodal. Text மட்டும் போதாது.

## 2. Mental Model

Multimodal capability என்பது ஒரே model-க்குள் பல input modalities-ஐ புரிந்துகொள்ளும் திறன்.

ஒரு unified representation space. Image, audio, video, text எல்லாம் அங்கே map ஆகும். LLM அந்த shared representation-ஐ read/write பண்ணும்.

Analogy: ஒரு engineer-க்கு முன்னால் ஒரே desk-ல drawing, spec sheet, voice message இருக்கு. அவர் எல்லாவற்றையும் ஒன்றாக பார்த்து முடிவு எடுக்கிறார். Separate assistants translate பண்ணி சொல்வதை விட இது faster and more accurate.

## 3. How It Works

High level-ல:
`Input Modality -> Modality Encoder -> Shared Embedding -> LLM Decoder -> Output`

Text encoder என்பது LLM-இன் tokenizer.
Image encoder என்பது Vision Transformer அல்லது CLIP போன்றது.
Audio encoder என்பது speech encoder.

இவை எல்லாம் training-ல cross-modal alignment பண்ணப்படும். "A dog" என்ற text embedding, dog photo embedding, dog bark audio embedding ஒரே region-ல இருக்கும்.

Inference-ல model ஒரே forward pass-ல எல்லா modalities-ஐயும் பார்க்கும். Output text மட்டுமே இருக்கலாம், அல்லது image generation, audio generation.

முக்கியம்: Model selection-ல multimodal capability என்பது built-in encoder + alignment quality.

## 4. Architectural Reasoning

**When does this become useful?**

* User input itself multimodal: chat + image upload, voice note, video call transcript.
* Reasoning requires cross-modal grounding: chart interpretation, UI screenshot debugging, document with tables + images.
* Retrieval needs multimodal: photo search, video Q&A.

**Alternatives:**
* Unimodal LLM + separate specialist models pipeline. Cheaper, modular, controllable. ஆனால் latency, error propagation.
* Fine-tuned specialist models per modality. Best accuracy for narrow task. ஆனால் ops cost high.
* Multimodal foundation model. One model, one API.

Architect-ஆக நீங்கள் கேட்க வேண்டியது:
* Input எப்போதும் text மட்டுமா? 80% text, 20% image என்றால் pipeline போதும்.
* Accuracy vs latency எது முக்கியம்? Medical image diagnosis-க்கு specialist model தேவை.
* Cost constraint என்ன? Multimodal models-க்கு inference cost 2-5x higher.

Decision is not "multimodal is better". Decision is "unified understanding worth the cost".

## 5. Trade-offs

* **Cost & Latency**: Multimodal model larger, context window expensive. Image tokenization costly. 1 image = 256-1024 tokens.
* **Accuracy vs Generality**: General multimodal model ஒரு நல்ல all-rounder ஆனால் specialist OCR, speech model-ஐ விட துல்லியம் குறைவு.
* **Hallucination mode மாறும்**: Model image-ல இல்லாத detail-ஐ imagine பண்ணும். Grounding கடினம்.
* **Data privacy & Ops**: Audio/video data sensitive. On-prem deployment வேண்டுமா? Streaming input handle பண்ண முடியுமா?

Failure mode: User blurry photo அனுப்பினால் model confidently wrong answer கொடுக்கும். Pipeline-ல ஆவது transcription confidence score பார்க்கலாம். Multimodal-ல அந்த signal மறைந்துவிடும்.

## 6. Practical Example

Enterprise returns portal.

Customer photo எடுத்து upload பண்ணி "இந்த product defective" என்று complaint அனுப்புகிறார். Photo-ல defect இருக்கிறதா, product model என்ன, order ID label visible-ஆ இருக்கிறதா என்று agent-க்கு தெரிய வேண்டும்.

Unimodal approach:
Image -> Vision model for defect detection -> text summary -> LLM for reply.
Audio note -> STT -> LLM.

Multimodal approach:
Photo + text complaint + customer history ஒன்றாக multimodal model-க்கு input.
Model directly "இந்த photo-ல torn packaging தெரிகிறது, order #12345 match ஆகிறது, refund approve செய்யலாம்" என்று reasoning செய்யும்.

Architectural decision: High volume, low criticality? Unimodal pipeline. High trust needed, cross-modal reasoning தேவை? Multimodal.

## 7. Reasoning Challenge

உங்களிடம் ஒரு healthcare triage chatbot இருக்கு. 
50% users text-ல symptoms எழுதுகிறார்கள்.
30% voice note அனுப்புகிறார்கள்.
