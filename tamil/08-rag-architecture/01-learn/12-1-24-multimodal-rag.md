# Multimodal RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.1.24 — Learn

## 1. Problem

உங்க RAG system text மட்டும் handle பண்ணுது. User கேட்கிறார்: "இந்த product image-ல இருக்கும் defect-ஐ என் PDF spec sheet-ல எந்த section mention பண்ணியிருக்கு?" 

இப்போ text RAG எப்படி உதவும்? Image-ஐ பார்க்காது. Spec sheet text-ஐ மட்டும் பார்க்கும். User intent multimodal. Query-ல image + text இருக்கு. Document-ல image + text + table இருக்கு.

What goes wrong if we don't have this? 
* Relevant information தவறவிடும். Image-ல defect visible, text-ல description இல்லை.
* User experience break ஆகும். Agent blind ஆக இருக்கும்.
* Retrieval recall குறையும். Text embedding மட்டும் போதாது.

**Problem became painful:** Real world data multimodal ஆக இருக்கு. Product catalog, support tickets, medical records, legal contracts, all have image, video, audio, text mix.

## 2. Mental Model

Multimodal RAG = RAG, but retrieval and generation இரண்டும் multimodal ஆக இருக்கு.

Traditional RAG: `text query -> text embedding -> text chunks -> LLM`

Multimodal RAG: `multimodal query -> multimodal representation -> multimodal chunks -> multimodal understanding -> LLM`

Core idea: Different modalities-ஐ common representation space-க்கு map பண்ணி, அதே space-ல similarity search பண்ணுவது.

Think of it as: ஒரு shared vector space-ல image, text, audio எல்லாம் பேசும். ஒரு image embedding, relevant text embedding-க்கு close இருக்கும்.

## 3. How It Works

Pipeline simple ஆக 3 parts.

**Ingestion:**
1. Document-ஐ chunk பண்ணு. Text chunk, image chunk, table chunk என்று separate.
2. Each chunk-க்கு modality-specific encoder use பண்ணி embedding generate பண்ணு.
   * Text: text encoder
   * Image: vision encoder
   * Audio: audio encoder
3. All embeddings-ஐ same vector database-ல store பண்ணு, with metadata: modality type, source doc, page id.

**Retrieval:**
1. User query multimodal ஆக வரலாம்: text + image upload.
2. Query-க்கு multimodal embedding generate பண்ணு. Some models like CLIP, ColPali, multimodal LLM encoder.
3. Vector DB-ல cross-modal search பண்ணு. Text query image chunk-ஐ retrieve பண்ணும். Image query text chunk-ஐ retrieve பண்ணும்.

**Generation:**
Retrieved multimodal chunks-ஐ LLM-க்கு context ஆக கொடு. LLM-க்கு images-ஐ directly understand பண்ணும் capability வேண்டும், or image captioning + text context provide பண்ண வேண்டும்.

Simplified flow:
```
Query[Text+Image] -> Multimodal Encoder -> Query Vector
                                   |
Document Store -> Modality Encoder -> Vector DB
                                   |
Retrieved Chunks[Text, Image] -> Context Builder -> Multimodal LLM -> Answer
```

## 4. Architectural Reasoning

When useful?
* Query and corpus both multimodal: E-commerce visual search, medical imaging + report, video support.
* Cross-modal reasoning தேவை: "இந்த screenshot-ல error message எதை குறிக்கிறது? Documentation-ல என்ன solution இருக்கு?"

What constraint it addresses?
* Recall. Text-only RAG information loss ஆகும்.
* User intent capture. Human communication multimodal.

Alternatives:
* **Late fusion:** Each modality separate retrieve பண்ணி, results combine. Simple, but alignment weak.
* **Early fusion:** Modality-களை upfront combine பண்ணி joint embedding. Better alignment, harder to scale.
* **Modality-specific RAG:** Text RAG, image RAG separate pipelines. Operability simple, but cross-modal reasoning missing.

Architect choose பண்ணும் போது கேட்க வேண்டியது:
* Modality mix எவ்வளவு? 90% text + 10% image என்றால், multimodal full stack overkill.
* Latency budget எவ்வளவு? Vision encoding heavy.
* Grounding தேவையா? Image retrieve பண்ணி cite பண்ண வேண்டுமா?

## 5. Trade-offs

**Embedding quality vs coverage.** Generic multimodal encoder எல்லா domain-க்கும் சரியாக work பண்ணாது. Domain-specific fine-tune பண்ணினால் cost increase.

**Retrieval accuracy vs latency.** Multimodal search larger index, more compute. Real-time query-க்கு bottleneck.

**Storage and cost.** Same document-க்கு multiple embeddings. Image embedding size big. Vector DB cost scale ஆகும்.

**Hallucination risk.** LLM image-ஐ பார்த்து hallucinate பண்ணும். Retrieval grounding இல்லாமல், model own knowledge use பண்ணும்.

Failure mode: Modality mismatch. User image-ல product A, query text product B பற்றி கேட்கிறார். System இரண்டையும் mix பண்ணி wrong retrieval கொடுக்கும். Need clear query decomposition.

## 6. Practical Example

Enterprise support system.

Customer uploads screenshot of error in web app + types "why is this happening?"

Ingestion: Past tickets-ல screenshots, logs, resolution text எல்லாம் multimodal chunks ஆக index செய்யப்பட்டிருக்கு.

Retrieval: Screenshot embedding + text query embedding combine பண்ணி, similar error screenshots + related knowledge base articles retrieve ஆகும்.

LLM: "இந்த screenshot-ல 502 error தெரியுது. உங்கள் ticket #1245-ல இதே error, API timeout காரணமாக வந்தது. Resolution: retry with exponential backoff, check service X health."

Result: Text-only RAG would miss visual similarity.

## 7. Reasoning Challenge

உங்களிடம் medical RAG system இருக்கு. Doctors query-ல chest X-ray image + "இந்த patient-க்கு pneumonia history இருக்கா?" என்று text question வருகிறது.

Retrieval-ல X-ray image-களை மட்டும் retrieve பண்ணினால் போதுமா? Text history-ஐ எப்படி combine பண்ணுவீர்கள்? One joint embedding vs two separate retrievals then re-rank? எதை தேர்வு செய்வீர்கள், ஏன்?

## 8. Key Takeaways

* Multimodal RAG solves real world problem where information and query cross modalities.
* Core is shared embedding space + cross-modal retrieval, not just more models.
* Architect decision is about modality mix, latency budget, and grounding requirement.
* Every gain in recall comes with cost, latency, and operational complexity trade-off.
