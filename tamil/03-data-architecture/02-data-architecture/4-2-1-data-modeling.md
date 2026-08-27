# Data modeling

> **Learning Path:** Data Architecture
> **Section:** 4.2.1 — Data architecture

## 1. Problem

ஒரு e-commerce service start பண்ணும்போது `users`, `orders`, `products` மூன்று table போதும் என்று தோன்றும். 6 மாதத்தில்:

* Mobile app-க்கு order summary வேண்டும், ஆனால் ஒவ்வொரு முறையும் 5 table join பண்ண வேண்டியிருக்கிறது. Latency 2 sec ஆகிறது.
* Analytics team அதே DB-ல் heavy aggregation query run பண்ணி, transactional traffic-ஐ slow ஆக்குகிறது.
* Product name மாறினால், அது historical orders-லும் மாற வேண்டுமா? வேண்டாமா? யாருக்கும் தெளிவில்லை.
* New service வந்ததும் schema change செய்தால் downstream services break ஆகிறது.

இது எல்லாம் data எப்படி shape ஆகி இருக்கிறது என்பதால் வரும் பிரச்சனை. Data modeling என்பது table design அல்ல, **உன் system எந்த கேள்விகளுக்கு எப்படி பதில் சொல்ல வேண்டும் என்பதை முடிவு செய்வது**.

## 2. Mental Model

Data model = **Entities + Relationships + Access Patterns**.

Entity என்பது business concept. Relationship என்பது அதற்கு இடையேயான link. Access Pattern என்பது யார், எப்போது, எந்த query-ஐ எப்படி run பண்ணுவார்கள்.

ஒரு mental model: நீ data-வை ஒரு warehouse-ல் வைக்கவில்லை. நீ ஒரு library-ஐ design பண்ணுகிறாய். Catalog எப்படி இருக்கும், books எங்கே stack ஆகும், reader எந்த path-ல் நடந்து வருவார் என்பதை முன்கூட்டியே தீர்மானிக்கிறாய்.

erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    ORDER_ITEM }o--|| PRODUCT : references

இது ER. ஆனால் architect-க்கு முக்கியமானது: இந்த model-ல் ஒரு order-க்கு total amount கண்டுபிடிக்க எத்தனை join தேவை? அது real-time-ல் வேண்டுமா?

## 3. How It Works

Architectural reasoning-ல் data modeling என்பது 3 decisions-ஆக பிரிக்கலாம்:

**1. Normalization vs Denormalization.** Transactional system-ல் integrity முக்கியம். ஒரு product price ஒரே இடத்தில் இருக்க வேண்டும். அதனால் normalize பண்ணுவாய். Read-heavy dashboard-ல் 5 joins தேவை என்றால், அந்த data-வை pre-joined shape-ல் வைத்து read performance காப்பாற்றுவாய்.

**2. Write model vs Read model.** Same data, different shape. Write model ACID, normalized. Read model query-driven, denormalized. CQRS என்பது இதன் formal name.

**3. Modeling for evolution.** Schema change வந்தால் என்ன ஆகும்? Backward compatible-ஆ? Versioning எப்படி? Event sourcing-ல் ஒரு event என்பது immutable fact. அதிலிருந்து வேண்டிய projection-ஐ build பண்ணலாம்.

## 4. Architectural Reasoning

Data model-ஐ தேர்வு செய்யும்போது constraints-ஐ முதலில் list பண்ணு:

* Latency requirement: 50ms கீழ் வேண்டுமா?
* Read/Write ratio: 1000:1?
* Consistency model: strong vs eventual?
* Team size & operability: complex model-ஐ maintain செய்ய ஆட்கள் இருக்கிறார்களா?
* Cost: storage cheap, compute expensive.

உதாரணமாக, social feed. Write model: User, Post, Like tables normalized. Read model: `user_feed` என்ற denormalized document, जिसमें posts pre-merged and sorted. ஏன்? Feed read 100x more than write, மற்றும் personalized ranking வேண்டும்.

Alternative: Graph DB for recommendation. Relational for transactional. Vector DB for semantic search. Model-ஐ use case-க்கு ஏற்ப தேர்வு செய்வது தான் architecture.

## 5. Trade-offs

* **Consistency vs Performance.** Normalized model correctness கொடுக்கும், ஆனால் read latency அதிகரிக்கும். Denormalization performance கொடுக்கும், ஆனால் update complexity உருவாக்கும்.
* **Flexibility vs Query Simplicity.** Schema-less document model flexible, ஆனால் ad-hoc reporting கடினம். Strict schema predictable ஆனால் change expensive.
* **Single
