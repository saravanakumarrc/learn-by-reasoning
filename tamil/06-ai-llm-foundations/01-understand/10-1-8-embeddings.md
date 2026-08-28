# Embeddings

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.8 — Understand

## Problem

உன்கிட்ட ஒரு enterprise knowledge base இருக்கு. ஆயிரக்கணக்கான support tickets, product docs, policy PDFs. User ஒரு question கேக்கறான்:

> "எனக்கு refund கிடைக்கல, ஆனா order cancel ஆகி இருக்கு"

நீ keyword search போட்டா `refund`, `cancel` exact match வரும். ஆனா user "money back வரல"ன்னு கேட்டா, keyword match fail ஆகும். Meaning same ஆனாலும் wording வேற.

LLM-க்கு context முழுவதும் கொடுக்க முடியாது. 10M documents-ஐ எல்லாம் prompt-ல போட முடியாது. அப்போ relevant few chunks மட்டும் எப்படி எடுப்பது?

இதான் painful problem. Exact match போதாது, meaning match வேணும். அதுக்கு text-ஐ எண்களா மாற்றி compare பண்ணணும்.

## Mental Model

Embedding என்பது ஒரு text snippet-ஐ high-dimensional space-ல ஒரு point ஆக்குறது. 768, 1024, 1536 dimension vector.

Mental model simple: **similar meaning = close vectors, different meaning = far vectors**.

"refund request" மற்றும் "money back ask" vector-ல ஒன்னுக்கொன்னு பக்கத்துல இருக்கும். "refund request" மற்றும் "shipping address" தூரமா இருக்கும்.

Distance measure பொதுவா cosine similarity. ஒரே direction என்றால் meaning similar.

இது keyword இல்லை. Model training time-ல உலக மொழி patterns பார்த்து, semantics learn பண்ணியிருக்கும்.

## How It Works

ஒரு encoder model, பெரும்பாலும் transformer-based, text-ஐ input ஆக எடுத்து fixed size dense vector output பண்ணும்.

Process:

Query அல்லது document chunk → Tokenize → Encoder → Embedding vector → Store / Compare

RAG pipeline-ல இரண்டு பக்கமும் embed பண்ணுறோம். Query vector vs document vectors. Top-k nearest neighbors எடுக்கிறோம்.

Search exact இல்லை. Approximate Nearest Neighbor ANN index வச்சு Pinecone, Weaviate, pgvector, Qdrant மாதிரி vector database-ல fast retrieve பண்ணுறோம்.

Important: embedding model ஒன்னு தான் இரண்டு பக்கத்துக்கும் use ஆகணும். Same model, same dimension, இல்லைன்னா compare பண்ண முடியாது.

## Architectural Reasoning

எப்போ embedding தேவை?

* Semantic search வேண்டும், keyword போதாது
* RAG-ல relevant context retrieve பண்ண
* Clustering, deduplication, recommendation
* Classification-க்கு feature ஆக

Constraint address பண்ணுறது: **meaning comparison at scale**.

Alternatives:

* BM25 lexical search: cheap, fast, exact term match. Synonym miss ஆகும்.
* LLM re-ranking only: expensive, slow.
* Hand-crafted rules: maintain பண்ண முடியாது.

Architect choose embedding when recall quality > exact match, and you can tolerate ANN approximation error.

## Trade-offs

**Model quality vs cost & latency.** Bigger model like text-embedding-3-large better recall, ஆனா per embedding cost அதிகம், inference latency அதிகம். Small model cheap, but nuance miss ஆகும்.

**Dimension vs storage & speed.** 3072 dim vector தரமானது, ஆனா 10M docs × 3072 × 4 bytes ≈ 120 GB. ANN index memory அதிகம்.

**Static vs dynamic embeddings.** Document update ஆனா re-embed பண்ணணும். Pipeline add பண்ணணும். Drift வரும். Embedding model upgrade பண்ணினா whole index rebuild தேவை.

**Retrieval quality failure mode.** Bad embedding → bad recall → LLM hallucinate. Embedding தான் RAG-ன் first failure point.

**Language coverage.** Multilingual model தேவைப்பட்டால் Tamil, English mixed query handle ஆகுமா? Model choice critical.

## Practical Example

Enterprise support bot.

Documents: 500k support articles. Chunk size 500 tokens with overlap.

Pipeline: Document ingest → clean → chunk → embed with e.g., `intfloat/multilingual-e5-large` → store in pgvector with metadata.

User query வரும் → same model-ல embed → ANN search top 5 chunks → LLM-க்கு context + query கொடு → answer generate.

Operability: Embedding generation async batch job. Vector DB-ல metadata filter பண்ணி product line, region-ல filter போடலாம். Query latency target <100ms.

Cost: 500k chunks × embedding cost + storage. Monthly re-embed pipeline வேணும்.

## Reasoning Challenge

உங்கிட்ட 10M product catalog இருக்கு. User free text-ல "lightweight laptop for video editing under 1 lakh"ன்னு கேக்கறான். Exact keyword search மிஸ் பண்ணுது.

Latency budget 80ms, budget tight. Embedding model
