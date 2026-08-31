# When should memory be updated?

> **Learning Path:** AI Memory
> **Section:** 13.2.5 — Architecture

## 1. Problem

ஒரு AI agent ஒரு user-கிட்ட chat பண்ணிக்கிட்டு இருக்கு. User சொல்றான்: "என்னோட billing address Chennai-க்கு மாத்து". Agent மாத்திட்டு பதில் சொல்றான்.

5 நிமிஷம் கழிச்சு user கேக்குறான்: "என்னோட address என்ன?"

என்ன ஆகணும்? Agent அதே session-ல தெரிஞ்ச மாதிரி memory-ல பார்க்கணும். Session முடிஞ்சதும் அடுத்த conversation-லயும் அது தெரியணும்.

இப்போ இன்னொரு scenario: User ஒரு typo பண்ணி சொல்றான்: "நான் Python 2 use பண்றேன்". அதை agent உடனே memory-ல save பண்ணிட்டா, அடுத்த முறை agent தப்பா advice கொடுக்க ஆரம்பிச்சிடும்.

அப்போ கேள்வி என்ன?

> எந்த information-ஐ உடனே memory-ல எழுதணும், எதை தள்ளி வைக்கணும், எதை எழுதவே கூடாது?

Memory update-ஐ தப்பா handle பண்ணினா என்ன வரும்?
- **Stale / wrong facts** permanent ஆகிடும்
- **Noise** memory-ல accumulate ஆகி retrieval தவறாகும்
- **Privacy leak** - user சொன்ன sensitive temporary info நிரந்தரமாகி விடும்
- **Cost & latency** - ஒவ்வொரு token-க்கும் memory write பண்ணினா system slow ஆகும்

## 2. Mental Model

Memory update என்பது ஒரு write policy decision. 

நாம் மூன்று layer memory பார்க்கலாம்:
- **Short-term / session memory**: இந்த conversation-க்குள்ள மட்டும் வேலை செய்யும் context window.
- **Working memory**: session முடிஞ்சும் கொஞ்ச நாள் வைத்திருக்கும் ephemeral store.
- **Long-term memory**: durable, user profile / knowledge graph மாதிரி persistent store.

Update decision என்பது எந்த layer-க்கு எப்போ transfer பண்ணுவது என்பது.

அடிப்படை கொள்கை: **Verify before persist, summarize before store, expire before forget.**

## 3. How It Works

ஒரு typical AI Memory architecture-ல update flow இப்படி இருக்கும்:

User utterance → Intent Classifier → Information Extractor → Confidence Scorer → Policy Gate → Write to memory with metadata

Policy Gate தான் முக்கியம். அது பார்க்கும் signals:

- **Stability**: இந்த fact மாற வாய்ப்பு உண்டா? `address`, `name`, `preference` stable. `current weather`, `today's mood` transient.
- **Source trust**: User confirmed-ஆ? Agent inferred-ஆ? External API-ல இருந்து வந்ததா?
- **User explicit signal**: User சொன்னான் "ஞாபகம் வச்சுக்கோ", "இது முக்கியம்" - explicit.
- **Repetition**: ஒரே fact 2-3 sessions-ல repeat ஆகுதா? அது signal for long-term.
- **Sensitivity / Compliance**: PII, health, financial data - extra guard.

Implementation-ல இதை செய்ய:
- **Event-driven writes** - not per token. Conversation end-ல அல்லது explicit trigger-ல summarize.
- **Versioned memory** with timestamp, source, confidence.
- **TTL / decay** for transient facts.
- **Human-in-the-loop confirmation** for high-impact writes.

## 4. Architectural Reasoning

Memory update எப்போ useful?

**உடனே update பண்ணணும்:**
- User explicitly corrects a fact: "இல்ல, என் name Arjun இல்ல, Arjun K"
- Security-critical change: role, access, billing.
- User says "இதை ஞாபகம் வச்சுக்கோ".

**Session end-ல summarize பண்ணி update:**
- Long conversation-ல preferences, goals, project context emerge.
- Batch write reduces write amplification and allows deduplication.

**Never update or update with short TTL:**
- One-off opinions, jokes, temporary plans.
- Inferred facts with low confidence.
- Sensitive data user didn't ask to remember.

Alternatives:
- **Eager write**: ஒவ்வொரு turn-க்கும் write. Simple ஆனா noisy, expensive.
- **Lazy write**: conversation end-ல மட்டும். Cheaper, ஆனா loss risk.
- **Policy-driven write**: confidence + policy gate. Architecturally correct.

## 5. Trade-offs

**Freshness vs Accuracy**: உடனே எழுதினா fresh ஆ இருக்கும், ஆனா noisy. தள்ளி வைத்தால் accurate ஆக refine பண்ணலாம், ஆனா user expect immediate recall.

**Recall vs Privacy**: Memory strong ஆக இருந்தா personalization நல்லா இருக்கும். அதே memory leak ஆனா compliance risk.

**Cost vs Quality**: Embedding + vector DB write, graph update cost உண்டு. ஒவ்வொரு utterance-க்கும் பண்ணினா cost explode ஆகும். Batching helps ஆனா latency கூடும்.

**Failure mode**: Wrong memory update irreversible ஆனா impact பெரியது. நீங்கள் "memory hallucination" create பண்ணி விடலாம். அதனால versioning + rollback தேவை.

## 6. Practical Example

Enterprise support agent.

User: "என்னோட order #12345 ல product X வேண்டாம், product Y கொடு". Agent process பண்ணி order modify செய்யுது.

Architecture decision:
- Session memory-ல immediately note பண்ணு.
- Working memory-ல 7 days TTL உடன் store பண்ணு: `user prefers product Y over X for order 12345`.
- Long-term profile-க்கு promote பண்ணாதே. ஏனெனில் இது order-specific, not lifelong preference.

அடுத்து user சொல்றான்: "என்னோட default shipping address ஐ மாத்து, இனிமேல் எல்லா order-க்கும் இதே address use பண்ணு". Agent confirm பண்ணி long-term memory-ல versioned write பண்ணு, with source = user explicit + timestamp.

இங்கே memory update policy தான் correctness கொண்டு வருது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG agent இருக்கு. User தினமும் 200 messages அனுப்புறான். Messages-ல 80% casual chat, 15% project updates, 5% personal facts.

Memory store என்பது vector DB + graph DB. Write cost $0.001 per embedding.

நீங்கள்:
- ஒவ்வொரு message-க்கும் memory-ல எழுதலாமா?
- Session end-ல summarize பண்ணி எழுதலாமா?
- Policy gate வைத்து confidence >0.8 மட்டும் எழுதலாமா?

Cost, accuracy, recall ஆகியவற்றை balance பண்ணி உங்கள் update policy என்னவாக இருக்கும்? எந்த signal-ஐ policy gate-ல பயன்படுத்துவீர்கள்?

## 8. Key Takeaways

- Memory update என்பது write policy problem, not just storage problem.
- Verify, summarize, then persist. Eager writes create noise.
- Stable, explicit, repeated facts மட்டுமே long-term memory-க்கு போக வேண்டும்.
- Transient, low-confidence, sensitive data-க்கு TTL / no-persist policy வை.
- Versioning + source metadata இல்லாமல் memory system architecturally unsafe.
