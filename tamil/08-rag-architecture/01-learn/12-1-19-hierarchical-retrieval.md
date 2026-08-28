# Hierarchical retrieval

> **Learning Path:** RAG Architecture
> **Section:** 12.1.19 — Learn

## 1. Problem

உங்களிடம் ஒரு RAG system இருக்கு. User query வருது, நீங்கள் vector database-ல search பண்ணி top-k chunks எடுக்கிறீர்கள். 

இப்போது ஒரு பெரிய enterprise knowledge base இருக்கு - மாதங்களுக்கான sales reports, product specs, policy documents, support tickets. 

Flat retrieval செய்தால் என்ன ஆகும்? Query: "Q3-ல் APAC region-ல் refund policy எப்படி மாறியது?" 

Vector search எல்லா chunks-லும் similarity பார்க்கும். 10M chunks-க்கு பார்த்தால் latency அதிகம். மேலும் முக்கியமான context missing ஆகும். ஒரு small paragraph மட்டும் match ஆகும், ஆனால் அந்த paragraph எந்த document-ன் எந்த section-க்கு சொந்தமானது, அது superseded ஆகியிருக்கிறதா என்பது தெரியாது.

Pain point: **Too much noise, too little context, and search cost grows linearly with corpus size.**

இதை தீர்க்கவே Hierarchical retrieval வருகிறது.

## 2. Mental Model

Hierarchical retrieval என்பது ஒரு மேல்தள மாடியில் இருந்து கீழ்தளத்திற்கு போவது.

முதலில் coarse level-ல் பார்க்கிறோம் - இந்த query எந்த domain/collection/document group-க்கு சொந்தமானது? பிறகு அந்த narrow set-க்குள் மட்டும் fine-grained chunk level-ல் search பண்ணுகிறோம்.

உதாரணம்: Library-ல புத்தகத்தை தேடுறீங்க. முதலில் subject section-க்கு போறீங்க, அப்புறம் shelf-க்கு, அப்புறம் exact book. முழு library-யும் ஒவ்வொரு புத்தகமாக தேட மாட்டீங்க.

## 3. How It Works

பொதுவாக 2-3 levels உண்டு.

**Level 1: Collection / Document Level**
ஒவ்வொரு document-க்கும் அல்லது document group-க்கும் ஒரு summary embedding உருவாக்கி வைத்துக்கொள்வோம். Query-ஐ இங்கே முதலில் match பண்ணுகிறோம். Top N collections/documents தேர்வு.

**Level 2: Section / Chapter Level**
தேர்ந்தெடுக்கப்பட்ட documents-க்குள், section-level embeddings. இங்கே context window பெரிது.

**Level 3: Chunk Level**
இறுதியாக selected sections-க்குள் மட்டும் fine-grained chunks-ல search.

Flow:
`Query → coarse retriever → candidate set prune → fine retriever → rerank → LLM`

சில implementations-ல் hierarchy metadata tree-ஆக வைத்து, tree traversal மூலம் path follow பண்ணுவார்கள். மற்றவை multi-stage retrieval.

## 4. Architectural Reasoning

இது எப்போது useful?

* Corpus பெரிதாகி, flat search latency/cost அதிகமாகும்போது
* Documents-க்கு natural hierarchy உண்டு: company → product → version → section
* Query-க்கு high-level context தேவை: "இந்த policy எந்த product-க்கு பொருந்தும்?"
* Filtering / access control தேவைப்படும்போது

Constraint அது address பண்ணுவது:
* **Recall vs Latency trade-off**: முழு corpus-ல search பண்ணினால் recall நல்லா இருக்கும் ஆனால் slow & expensive. Hierarchical பண்ணினால் search space குறையும்.
* **Contextual grounding**: ஒரு chunk மட்டும் தருவது போதாது, அது எந்த document-ல இருக்குன்னு தெரியணும்.

Alternatives:
* Flat retrieval + larger top-k + reranker. Simple ஆனால் cost அதிகம்.
* Hybrid search with metadata filtering. Hierarchy இல்லாமல் filter பண்ணலாம்.
* Graph-based retrieval. Relationship explicit ஆக வேண்டும்.

ஏன் choose பண்ணுறோம்? ஏனெனில் architect-க்கு **search space-ஐ prune பண்ண வேண்டிய கட்டாயம்** இருக்கு, ஆனால் blind prune பண்ணினால் relevant doc miss ஆகும். Hierarchy தரும் pruning guided ஆக இருக்கும்.

## 5. Trade-offs

**1. Latency vs Accuracy**
Coarse stage சரியா prune பண்ணலைன்னா, relevant doc-ஐ கூட drop பண்ணிடுவோம். Precision loss. மிகவும் aggressive pruning = recall drop.

**2. Build complexity**
Hierarchical embeddings, summaries, tree maintenance எல்லாம் pipeline complexity அதிகப்படுத்தும். Document update ஆனால் all levels rebuild செய்ய வேண்டி இருக்கும்.

**3. Storage cost**
ஒரு document-க்கு 1 summary + N section embeddings + M chunk embeddings. Storage மூன்று மடங்கு.

**4. Failure mode**
Coarse retriever bias உருவாகும். Query ambiguous ஆக இருந்தால், முதல் level தவறாக தேர்வு செய்துவிட்டால், கீழே எவ்வளவு fine search பண்ணினாலும் பயன் இல்லை. Cascade error.

## 6. Practical Example

Enterprise RAG: Bank-ன் internal knowledge base.

Structure:
`Division → Product Line → Document → Section → Chunk`

Query: "UPI refund T+1 rule for corporate accounts in 2025"

Hierarchical flow:
1. Collection level: Query embedding vs Division summaries. "Payments → UPI → Corporate Banking" top 3 தேர்வு.
2. Document level: அந்த division-ல உள்ள 2025 policy docs, circulars. Top 5 docs.
3. Section level: அந்த docs-ல "Refund", "Settlement" sections filter.
4. Chunk level: Exact rule text retrieve.

Result: 10M chunks-க்கு பதில் 50k chunks-க்குள் மட்டும் search. Latency 800ms → 180ms. மேலும் LLM-க்கு context-ஆக "Document: RBI Circular 2025/07, Section 3.2" கொடுக்க முடியும்.

## 7. Reasoning Challenge

உங்களிடம் 5 million support tickets உள்ளன. Ticket-க்கு hierarchy இருக்கு: Product → Version → Module → Ticket.

ஒரு user query: "login timeout issue on iOS app after v2.3 update".

Flat retrieval பண்ணினால் 2 sec ஆகும். Hierarchical retrieval பண்ணினால் என்ன levels-ஐ உருவாக்குவீர்கள்? Coarse pruning எவ்வளவு aggressive ஆக இருக்கலாம்? Recall drop ஆகாமல் இருக்க என்ன safety net வைப்பீர்கள்?

## 8. Key Takeaways

* Hierarchical retrieval என்பது search space-ஐ guided prune செய்வது, random prune அல்ல.
* முதலில் coarse context தேர்வு, பிறகு fine-grained details - இதுதான் mental model.
* Latency/cost குறையும், ஆனால் coarse stage தவறினால் cascade failure வரும்.
* Hierarchy natural ஆக corpus-ல இருந்தால் மட்டுமே இது பயனுள்ளது, artificial hierarchy create பண்ணுவது overhead.
