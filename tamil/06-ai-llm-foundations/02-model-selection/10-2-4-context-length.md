# Context length

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.4 — Model selection

## 1. Problem

ஒரு LLM-ஐ உபயோகிக்கும்போது நீங்கள் கவனித்திருப்பீர்கள்: சில மாடல்கள் 4k tokens வரை மட்டும் புரிந்து கொள்கின்றன, சில 128k, சில 1M வரை போகின்றன.

ஏன் இந்த வித்தியாசம்? 

நிஜ உலகில் உங்களுக்கு வரும் பிரச்சனை:
ஒரு customer support agent உருவாக்குகிறீர்கள். ஒரு conversation 10 message-க்கு மேல் போனால், முந்தைய context மறைந்து விடுகிறது. Model "நான் முன்பு என்ன சொன்னேன்" என்று மறந்து விடுகிறது.

அல்லது RAG system-ல் 50 documents-ஐ retrieve பண்ணி prompt-ல் சேர்க்கிறீர்கள். அது token limit-ஐ தாண்டி விடுகிறது. Model truncate பண்ணி, முக்கியமான தகவலை விட்டு விடுகிறது.

**What goes wrong if we don't have enough context length?** Hallucination அதிகரிக்கும், coherence குறையும், task failure வரும். 

Context length என்பது மாடலுக்கு ஒரே நேரத்தில் பார்க்க முடியும் மொத்த input + output window-ன் அளவு.

## 2. Mental Model

Context length = மாடலின் working memory.

ஒரு மனிதன் 2 மணி நேர meeting-ஐ முழுவதுமாக நினைவில் வைத்திருக்க முடியாது. Notes எடுக்கிறான். LLM-க்கு context window தான் அந்த notes.

Tokens என்பது roughly words-க்கு 3/4 விகிதத்தில் இருக்கும். English-ல் 1 token ≈ 0.75 word.

முக்கியம்: context length = maximum tokens model can process in one forward pass. இது training-ல் fix செய்யப்படுகிறது.

## 3. How It Works

Transformer architecture-ல் attention mechanism-க்கு ஒவ்வொரு token-ம் ஒவ்வொரு token-உடனும் தொடர்பு பார்க்க வேண்டும். இது O(n²) compute ஆகும்.

அதனால் context length அதிகரிக்கும்போது:
- Memory அதிகம் தேவை
- Latency அதிகரிக்கும்
- Cost per request அதிகரிக்கும்

Models இதை handle பண்ண positional encoding, sliding window attention, sparse attention போன்ற techniques-ல் செய்கின்றன. ஆனால் fundamental limit இருக்கிறது.

Prompt = system + user history + retrieved documents + tools output. இவை எல்லாம் சேர்ந்து context window-க்குள் இருக்க வேண்டும்.

## 4. Architectural Reasoning

Context length உங்கள் design-ஐ எப்படி மாற்றும்?

**Short context, 4k-8k:** 
Chatbots, simple Q&A, classification. Conversation ஒவ்வொரு turn-க்கும் summary செய்ய வேண்டும். முழு history-யை வைக்க முடியாது.

**Medium context, 32k-128k:**
Long documents summarization, code base understanding, multi-turn agents. ஒரு சில மணி நேர conversation-ஐ maintain பண்ண முடியும்.

**Long context, 200k-1M:**
Legal contract analysis, whole codebase in one shot, RAG with hundreds of chunks, meeting transcripts.

எப்போது large context தேவை?
- Replay தேவை இல்லாத, holistic understanding வேண்டிய use case.
- Latency முக்கியம் இல்லை, accuracy முக்கியம்.

எப்போது small context போதும்?
- High-throughput API, low latency தேவை.
- Cost sensitive.
- Conversation can be summarized.

Alternatives to larger context:
- Summarization / compression: history-ஐ condense பண்ணி token save பண்ணுதல்.
- RAG with selective retrieval: முழு data-வையும் கொடுக்காமல் relevant chunks மட்டும்.
- Hierarchical summarization: conversation-ஐ layer-களாக சுருக்குதல்.
- Agents with external memory: vector database + tool calls.

## 5. Trade-offs

**1. Context length vs Latency & Cost**
அதிக context = அதிக compute. Attention O(n²). 128k context-ல் inference 4k-ஐ விட பல மடங்கு விலை உயரும். Production-ல் இது direct cost impact.

**2. Context length vs Quality**
அதிக context கொடுத்தாலும் model "lost in the middle" பிரச்சனை உண்டு. மிக நீண்ட context-ல் நடுவில் உள்ள தகவலை மாடல் கவனிக்க தவறும். Position bias உண்டு.

**3. Context length vs Training efficiency**
Long context train பண்ணுவது மிக செலவு அதிகம். அதனால் பல models-ல் context length ஒரு product decision.

**4. Context length vs Memory**
Long context models need more GPU memory for KV cache. Throughput குறையும். Batch size குறையும்.

Failure mode: Token overflow. நீங்கள் limit-ஐ தாண்டினால் model truncate பண்ணும், அல்லது error தரும். Silent truncation = silent data loss.

## 6. Practical Example

Enterprise support agent.

System prompt + last 10 user messages ≈ 3k tokens
RAG retrieval: top 10 chunks, each 500 tokens ≈ 5k tokens
Tool output: 1k tokens

Total ≈ 9k tokens. Output budget 1k.

Model A: 8k context → overflow. நீங்கள் retrieval-ஐ 6 chunks-க்கு குறைக்க வேண்டும் அல்லது history-ஐ truncate பண்ண வேண்டும்.

Model B: 128k context → எல்லாம் சேர்க்கலாம், ஆனால் cost 3x, latency 2x.

Architect decision: Model B எடுத்து retrieval quality-ஐ மேம்படுத்தலாம், அல்லது Model A எடுத்து intelligent summarization + selective retrieval செய்யலாம்.

பெரும்பாலும் production-ல் hybrid தான் வேலை செய்யும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு financial analysis agent இருக்கு. ஒரு user quarterly report PDF-ஐ upload பண்ணி, அதில் உள்ள 50 tables-ஐ analyze செய்ய சொல்கிறார்.

Option A: 1M context model, முழு PDF-ஐ text-ஆக convert செய்து ஒரே prompt-ல் கொடு.
Option B: 32k context model, PDF-ஐ chunk பண்ணி RAG + map-reduce summarization செய்.

Latency budget 5 seconds, cost per request < $0.10. என்ன தேர்வு செய்வீர்கள்? ஏன்?

## 8. Key Takeaways

- Context length = மாடலின் ஒரே நேர memory. அதிகம் என்றால் அதிக cost, latency, memory.
- அதிக context எப்போதும் நல்லது அல்ல. Relevant context-ஐ தேர்வு செய்வது முக்கியம்.
- "Lost in the middle" பிரச்சனை உண்மை. நீளமான context-ல் முக்கிய தகவலை முன்னால்/பின்னால் வைக்கவும்.
- Architecture choice: larger context vs summarization + RAG. இது cost, latency, accuracy trade-off.
- Model selection-ல் context length-ஐ requirement-இலிருந்து தொடங்கு, not hype-இலிருந்து.
