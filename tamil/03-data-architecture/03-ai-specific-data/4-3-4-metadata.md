# Metadata

> **Learning Path:** Data Architecture
> **Section:** 4.3.4 — AI-specific data

## 1. Problem

நீங்கள் ஒரு enterprise RAG system build பண்ணீங்க. 10 மில்லியன் documents ingest ஆகி இருக்கு, embeddings vector database-ல இருக்கு. 

6 மாதம் கழிச்சு ஒரு user கேட்கிறார்: "எனக்கு கடந்த மாதம் வந்த compliance policy மட்டும் வேண்டும்". 

உங்களுக்கு தெரியாது: அந்த chunk எந்த document-ல இருந்து வந்தது, source யார், last updated எப்போது, அது internal மட்டுமா confidential-ஆ, எந்த embedding model version-ல generate ஆனது.

Producer வேகமாக documents போடுகிறார், consumer-கள் வெவ்வேறு speed-ல read பண்ணுகிறார்கள். அதே chunk-ஐ மீண்டும் மீண்டும் generate பண்ண வேண்டி வரும். 

இங்கே raw data இல்லாமல் metadata இல்லாமல் system blind ஆகி விடும். Filter, route, audit, replay எதுவும் செய்ய முடியாது.

## 2. Mental Model

Metadata என்பது data-வின் passport.

Raw content என்ன சொல்கிறது என்பது data. அந்த data யாருடையது, எப்போது பிறந்தது, எவ்வளவு நம்பகமானது, எந்த model-ல process ஆனது என்பது metadata.

AI-specific data-வுக்கு இது இன்னும் critical. ஒரு chunk-க்கு வெறும் text போதாது. அதன் lineage, quality, access control, embedding version, chunking strategy எல்லாம் தேவை.

## 3. How It Works

Architecture-ல metadata-வை பெரும்பாலும் sidecar-ஆ வைக்கிறோம்.

Document ingest pipeline:
`Raw Document -> Parser -> Chunk -> Embedding -> Vector DB`
அதே நேரம்: `Document -> Metadata Extractor -> Metadata Store`

Metadata schema-வில் AI-specific fields இருக்கும்:
* `source_url`, `doc_id`, `author`, `created_at`, `updated_at`
* `owner_team`, `sensitivity`, `PII_flag`
* `chunk_id`, `chunk_index`, `token_count`, `chunking_strategy`
* `embedding_model`, `embedding_version`, `embedding_created_at`
* `quality_score`, `label`, `language`
* `provenance` - எந்த pipeline run-ல generate ஆனது

Vector DB-ல primary key vector + metadata JSON-ஆ store செய்யலாம். அல்லது metadata-வை relational data catalog / metadata store-ல வைத்து vector id-வை reference செய்யலாம்.

Retrieval நேரத்தில்: user query + filters -> metadata filter -> vector search -> rerank.

## 4. Architectural Reasoning

Metadata எப்போது useful ஆகும்?

* **Retrieval control:** RAG-ல `sensitivity = internal` மட்டும் காட்ட வேண்டும் என்ற filter metadata இல்லாமல் முடியாது.
* **Freshness:** `updated_at` இருந்தால் மட்டுமே stale document-ஐ தள்ளி வைக்க முடியும்.
* **Reproducibility:** `embedding_model` version தெரியாமல், அதே result-ஐ மீண்டும் கொடுக்க முடியாது.
* **Audit & compliance:** யார் எந்த data பயன்படுத்தினார்கள் என்பதற்கு lineage தேவை.

Alternatives:
* Metadata-வை content-ல embed செய்வது - சிறிய dataset-க்கு okay, ஆனால் update கஷ்டம்.
* Inline JSON - flexible ஆனால் query performance குறையும்.
* Central data catalog + vector DB reference - scalable, ஆனால் join complexity வரும்.

Architect decision: scale பெரிதாக இருந்தால் metadata-வை separate store-ல வைத்து, vector id மூலம் join செய்யுங்கள். Low latency filter தேவை என்றால் vector DB-வுக்குள் metadata index செய்யுங்கள்.

## 5. Trade-offs

* **Schema rigidity vs flexibility:** AI data-வுக்கு fields அடிக்கடி மாறும். Strict schema data loss கொடுக்கும், schemaless query கஷ்டம். Solution: core fields strict, extended fields JSON blob.
* **Consistency vs availability:** Metadata update fail ஆனால் vector insert success ஆகுமா? Two-phase write complex. பெரும்பாலும் eventual consistency accept செய்யப்படும்.
* **Storage cost vs operability:** Metadata குவிந்தால் cost ஏறும், ஆனால் debugging, filtering, governance இல்லாமல் system unusable ஆகும்.
* **Freshness vs latency:** Real-time metadata update வேண்டுமா? Event-driven update வைக்கலாம், ஆனால் complexity கூடும்.

Failure mode: embedding model upgrade செய்தீர்கள், ஆனால் old metadata-வில் model version update செய்ய
