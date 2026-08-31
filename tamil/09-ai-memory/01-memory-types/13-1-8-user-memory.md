# User memory

> **Learning Path:** AI Memory
> **Section:** 13.1.8 — Memory types

## 1. Problem

ஒரு LLM agent-ஐ நீங்கள் பயன்படுத்தும்போது ஒவ்வொரு முறையும் புது user மாதிரி பேசுது. கடந்த conversation-ல நீங்க சொன்ன preference, name, project context எல்லாம் மறந்துடுது.

அதை fix பண்ண context window-ல முழு chat history-யையும் அனுப்பலாம். ஆனா அது expensive ஆகும், slow ஆகும், முக்கியமான information கூட noise-ல மறைஞ்சுடும்.

உண்மையான பிரச்சனை: **எந்த information-ஐ எப்போது நினைவில் வைக்க வேண்டும், எப்படி organize செய்ய வேண்டும், எப்போது update அல்லது forget செய்ய வேண்டும்?**

User memory என்பது அந்த பிரச்சனையின் architectural solution.

## 2. Mental Model

User memory = ஒரு user-க்கு specific ஆக persist ஆகும் long-term knowledge store.

இது இரண்டு layer-ல வேலை செய்யும்:

* **Short-term / session memory**: இந்த conversation-ல இருக்கும் recent facts, context.
* **Long-term / user memory**: User-ன் preferences, facts, history, relationships across sessions.

LLM-க்கு context window என்பது working memory. User memory என்பது external brain. LLM தேவைப்படும்போது தேடி, retrieve செய்து, working memory-க்கு கொண்டு வரும்.

## 3. How It Works

பொதுவான flow:

1. **Capture**: Conversation-ல இருந்து useful facts-ஐ extract செய்ய. இதை செய்ய extractive summarization அல்லது LLM-based extraction பயன்படுத்தலாம்.
2. **Store**: Structured store-ல save செய்ய. Key-value store, graph database, vector database அல்லது hybrid.
3. **Retrieve**: புது query வரும்போது user ID-வை வைத்து relevant memories-ஐ retrieve செய்ய. Semantic search + recency + importance ranking.
4. **Inject**: Retrieved memories-ஐ system prompt / context-ல inject செய்ய.
5. **Update / Forget**: Conflicting info வந்தால் merge / version. Privacy / retention policy படி forget செய்ய.

Memory types architecturally மூன்றாக பிரிக்கலாம்:

* **Episodic**: What happened when? "நீங்க கடந்த வாரம் X project பற்றி கேட்டீர்கள்"
* **Semantic / Factual**: Stable knowledge. Name, preferences, role, timezone
* **Procedural / Preference**: How user likes responses. "short bullet points வேண்டும்", "Tamil-ல explain செய்ய"

## 4. Architectural Reasoning

User memory useful ஆகும் போது:

* Multi-session continuity வேண்டும். Chatbot, personal assistant, support agent.
* Personalization வேண்டும். Recommendation, content generation.
* Compliance / audit வேண்டும். User-ன் சொன்ன data-வை track செய்ய வேண்டும்.

Constraints:

* **Privacy & Security**: PII handle செய்கிறோம். GDPR / data residency.
* **Consistency**: Same user, multiple devices, multiple agents.
* **Scale**: Millions of users, each with growing memory.
* **Quality**: Hallucinated extraction வந்தால் memory poison ஆகும்.

Alternatives:

* No memory, only session context. Simple but forgetful.
* Full history replay. Simple but costly, slow.
* User memory with retrieval. Cost controlled, personalized.

Architect choose பண்ணும்போது தீர்மானிக்க வேண்டியது: எவ்வளவு structure வேண்டும்? Free-form vector search போதுமா? அல்லது schema-driven knowledge graph வேண்டுமா?

## 5. Trade-offs

* **Accuracy vs Coverage**: Aggressive extraction = more noise. Conservative = miss important facts. Ranking / confidence score தேவை.
* **Freshness vs Stability**: User preference மாறும். Old memory-ஐ எப்போது overwrite செய்ய? Versioning + timestamp.
* **Privacy vs Personalization**: More memory = better UX, but higher risk. Need encryption at rest, access control, user delete / export.
* **Cost vs Latency**: Every turn-ல retrieval செய்தால் latency + cost. Cache hot user memories, pre-fetch.

Failure modes:

* **Memory contamination**: Wrong user-க்கு wrong memory serve ஆகும். User ID isolation முக்கியம்.
* **Stale memory**: பழைய preference இன்னும் active-ல இருக்கும்.
* **Prompt bloat**: Too many memories inject செய்தால் LLM confuse ஆகும். Top-K limit வேண்டும்.

## 6. Practical Example

Enterprise support agent.

User A என்பவர் கடந்த 3 மாதமாக "Mumbai DC" deployment பற்றி பேசியுள்ளார். Timezone IST, prefers English technical terms with Tamil explanation.

இப்போது அவர் "status?" என்று கேட்கிறார்.

Session only context இருந்தால் agent கேள்வி தெளிவற்றது.

User memory system:

* Store: user_id -> {name, timezone, preferred language style, recent projects}
* Retrieve: Semantic search on query + user profile. Top 3 relevant memories get.
* Inject: "User prefers Tamil explanation with English tech terms. Last discussed Mumbai DC."

Result: Contextual, personalized answer. No repetition.

If user says "I am now in Singapore", memory update pipeline triggers: old timezone mark as deprecated, new timezone create with higher recency score.

## 7. Reasoning Challenge

உங்களிடம் 5M active users இருக்கிறார்கள். ஒவ்வொரு user-க்கும் சராசரி 200 memory entries. Retrieval latency <100ms வேண்டும். User data EU-ல இருக்க வேண்டும்.

நீங்கள் vector database மட்டும் பயன்படுத்தினால் என்ன problem வரும்? Hybrid approach எப்படி design செய்வீர்கள்? Privacy delete request வந்தால் என்ன செய்வீர்கள்?

## 8. Key Takeaways

* User memory என்பது continuity, personalization-க்கான external store. LLM-ன் context window-ஐ replace செய்வதல்ல.
* Capture, Store, Retrieve, Inject, Update என்ற lifecycle-ஐ design செய்ய வேண்டும்.
* Privacy, isolation, freshness, retrieval quality ஆகியவை architectural decisions-ஐ drive செய்கின்றன.
* Every memory system creates new trade-offs: consistency vs cost, personalization vs privacy, freshness vs stability.
