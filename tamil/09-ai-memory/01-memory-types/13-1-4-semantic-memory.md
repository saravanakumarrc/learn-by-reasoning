# Semantic memory

> **Learning Path:** AI Memory
> **Section:** 13.1.4 — Memory types

## 1. Problem

நீங்கள் ஒரு AI agent-ஐ build பண்ணுறீங்க. அது user-க்கு முந்தைய conversation-ஐ remember பண்ணணும். 

ஒரு user கேட்டார்: "என் budget பத்தி நீ முன்னாடி என்ன சொன்ன?"
மற்றொரு user கேட்டார்: "பொதுவா travel insurance எப்படி வேலை செய்யும்?"

முதல் கேள்விக்கு personal history தேவை. இரண்டாவது கேள்விக்கு general knowledge தேவை.

இதை எல்லாம் ஒரே episodic log-ல வச்சு search பண்ணினா என்ன ஆகும்? Noise அதிகம், relevant fact கண்டுபிடிக்க கஷ்டம். Agent தன் சொந்த experience-லயே குழம்பும்.

**What goes wrong if we don't have this?** Agent கற்றதை generalize பண்ண முடியாது. ஒவ்வொரு முறையும் அதே context-ஐ மீண்டும் கற்றுக்கொள்ள வேண்டும்.

## 2. Mental Model

Semantic memory = **facts about the world, not memories of events**.

இது "எப்போது நடந்தது?" இல்லை, "என்ன உண்மை?" என்பது.

உங்களுக்கு நினைவு வருது: "Paris France-ன் capital" என்பது ஒரு semantic fact. நீங்கள் Paris போன experience ஒரு episodic memory.

System-ல சொன்னால்:
* **Episodic memory**: யார், எப்போது, என்ன conversation நடந்தது. "User A on 2024-10-01 said budget is 50k"
* **Semantic memory**: extracted knowledge, generalized. "Travel insurance covers trip cancellation, medical emergencies"

Semantic memory என்பது agent-ன் long-term knowledge base. இது time-stamped story இல்லை, distilled meaning.

## 3. How It Works

பொதுவா இது இப்படி build ஆகும்:

User interaction / document → embedding → vector database → knowledge graph / structured store

ஒரு agent conversation-ல இருந்து important facts-ஐ extract பண்ணி summarize செய்வோம். உதாரணமா, 10 turns-ல user repeatedly mention அவருக்கு vegetarian preference. அதை episodic log-ல வச்சிட்டு, semantic memory-ல "user dietary preference = vegetarian" என்று write பண்ணுவோம்.

பின்னர் retrieval நடக்கும் போது, query-ஐ embed பண்ணி semantic store-ல cosine similarity-யால் relevant facts-ஐ fetch பண்ணுவோம்.

RAG pipeline-ல இதுவே persistent knowledge layer ஆகிறது.

## 4. Architectural Reasoning

Semantic memory எப்போ useful?

* Agent-க்கு domain knowledge தேவைப்படும் போது. Financial advisor, medical assistant போன்றவை.
* Same fact-ஐ பல users / பல conversations-ல reuse பண்ண வேண்டும் போது.
* Model context window-க்கு அப்பால் தகவல் வைத்திருக்க வேண்டும் போது.

Constraints அது address பண்ணும்:
* **Latency**: Every time from scratch generate பண்ணுவதை விட retrieve பண்ணுவது cheap
* **Consistency**: பொதுவான facts ஒரே மாதிரி இருக்கும்
* **Scalability**: Knowledge grows, but model weights fixed

Alternatives:
* Episodic memory only: raw conversation history. Simple but noisy, expensive
* Parametric memory only: fine-tune LLM. Expensive, slow to update, hallucination risk
* Hybrid: semantic memory + episodic memory = best of both

Architect choose பண்ணுவான் semantic memory-ஐ, when agent needs to learn and retain generalizable facts over time without retraining.

## 5. Trade-offs

**1. Accuracy vs Freshness**
Extracted facts stale ஆகலாம். "Best hotel in Chennai" 2023-ல உண்மை, 2025-ல இல்லை. Versioning மற்றும் TTL தேவை.

**2. Generalization vs Hallucination**
Summary பண்ணும்போது model over-generalize பண்ணி wrong fact create பண்ணும். "User likes vegetarian" என்பது "user is vegan" ஆக மாறலாம். Validation layer தேவை.

**3. Structured vs Unstructured**
Pure vector store flexible ஆனால் reasoning கடினம். Knowledge graph structured ஆனால் maintenance heavy.

**4. Privacy & Scope**
Semantic memory often cross-user. Personal data leak ஆகும் risk. Access control, tenant isolation must be explicit.

Failure mode: Agent semantic memory-ல தவறான fact-ஐ reinforce பண்ணி, அதை எப்போதும் retrieve பண்ணும். Garbage in, garbage out.

## 6. Practical Example

Enterprise support agent.

Episodic: Ticket #12345, 2024-09-10, user reported login failure due to MFA.

Semantic extraction: "MFA reset requires admin approval and takes 24 hours"

அடுத்த user கேட்டால் "MFA reset எவ்ளோ நேரம் ஆகும்?" என்று, agent semantic memory-ல இருந்து துல்லியமாக பதில் சொல்லும். Episodic-ல தேடினால் அது specific ticket-க்கு மட்டும் பொருந்தும்.

Architecture:
User Query → Embedding → Vector DB [Semantic facts] + Episodic store → Reranker → LLM context

Facts periodically reviewed by human-in-the-loop.

## 7. Reasoning Challenge

உங்களிடம் ஒரு customer support agent இருக்கு. 1M conversations/மாதம் வருது. User-specific preferences-ஐ தக்கவைக்க வேண்டும். பொதுவான product knowledge-ஐயும் தக்கவைக்க வேண்டும். Episodic store cost அதிகம் ஆகுது.

நீங்கள் semantic memory-ஐ எப்படி design பண்ணுவீர்கள்? என்ன தகவலை semantic-ல move பண்ணுவீர்கள், என்ன episodic-ல வைத்திருப்பீர்கள்? Retrieval-க்கு என்ன trade-off எடுப்பீர்கள்?

## 8. Key Takeaways

* Semantic memory = distilled facts about world, not personal event logs
* Episodic gives you *what happened*, semantic gives you *what is true*
* Good architecture uses both: semantic for general knowledge, episodic for personal context
* Extraction quality is the bottleneck, not retrieval speed
* Every update to semantic memory is an architectural decision about truth, privacy, and staleness
