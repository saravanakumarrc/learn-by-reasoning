# PARTIAL — Context length

> Reason: Ollama reached num_predict
> num_predict: 32768

## 1. Problem

உங்களுக்கு ஒரு customer support agent இருக்கு. User 30 நிமிடம் chat பண்ணியிருக்கார், ticket history இருக்கு, knowledge base-ல 15 articles relevant ஆக இருக்கு. Agent-க்கு அந்த முழு context-உம் கொடுக்கணும், இல்லைன்னா அவர் திரும்ப திரும்ப அதே கேள்வியை கேட்பார், முந்தைய உறுதிமொழியை மறந்துவிடுவார்.

இங்கே என்ன பிரச்சனை? LLM-க்கு ஒரு hard limit இருக்கு - **context window**. அதுக்கு அப்புறம் போன token-கள் காணாமல் போய்விடும்.

Small context model-ஐ எடுத்தா conversation ஆரம்பத்தில் இருந்து information truncate ஆகும். RAG pipeline-ல போதுமான chunks-ஐயே pass பண்ண முடியாது. Agent-க்கு tool results + conversation history + system prompt எல்லாம் ஒரே window-ல fit ஆகணும்.

இதுதான் **model selection-ல context length ஏன் முக்கியம்** என்பதன் root cause.

## 2. Mental Model

Context window-ஐ ஒரு working memory ஆக நினைச்சுக்கோங்க.

ஒரு human engineer 8 மணி நேரம் focus பண்ண முடியும். ஆனால் table-ல 5000 page document வச்சுக்கிட்டு ஒரே முறையில் படிக்க முடியாது. அதே மாதிரி LLM-க்கு fixed size memory இருக்கு.

Context length = எத்தனை tokens-ஐ model ஒரே முறை attention பண்ண முடியும். அதில் system prompt, conversation history, retrieved chunks, tool outputs எல்லாம் சேரும்.

அதிக context window = அதிக memory. ஆனால் memory அதிகமானால் cost, latency, complexity எல்லாம் மாறும்.

## 3. How It Works

Context length token-களில் அளக்கப்படும். Roughly 1 token ≈ 0.75 English words. Tamil-க்கு சற்று வித்தியாசம் இருக்கும்.

Model inference போது, input tokens + output tokens மொத்தம் context window-க்குள் இருக்கணும். 128k context model இருந்தாலும், நீங்கள் 120k input கொடுத்தால் output-க்கு இடமே இருக்காது.

அதனால் real usable context = window size - reserved output budget.

Attention mechanism cost-ம் quadratic-க்கு close-ஆக grow ஆகும். அதனால் window அதிகமானால் compute அதிகமாகும்.

## 4. Architectural Reasoning

Context length தேர்வு என்பது requirement-driven.

**எப்போது small context போதும்?**
- Simple Q&A chatbot, short turn-based interaction
- Classification, summarization of single doc
- Latency முக்கியம், cost sensitive

**எப்போது large context தேவை?**
- Long conversation history preserve பண்ணணும்
- RAG-ல 50-100 chunks ஒரே shot-ல pass பண்ணணும்
- Agent workflows, where tool calls accumulate
- Code repo whole file analyze பண்ணணும்

Alternative இருக்கு: context window-ஐ நீட்டிக்காமல் **context compression** பண்ணலாம். Summarize history, retrieve only top-k chunks, use hierarchical summarization. ஆனால் அது information loss risk கொடுக்கும்.

Architect-ஆக நீங்கள் கேட்க வேண்டியது: "என் real use case-க்கு எவ்வளவு tokens தேவை? Peak-ல எவ்வளவு?" அதுக்கு 20-30% buffer வச்சு model தேர்வு செய்யுங்க.

## 5. Trade-offs

**Cost vs Memory.** Large context model-கள், especially 128k+ , per token price அதிகம். Input cost-ம் output cost-ம் கூடும். Production-ல monthly bill பெரிய factor.

**Latency vs Quality.** Long context = more tokens to process = higher latency. Real-time agent-க்கு இது painful.

**Quality degradation.** 100k window இருந்தாலும், model 80k+ tokens-ல மத்தியில் இருக்கும் information-ஐ நல்லா பயன்படுத்தாது. **Lost in the middle** problem. அதிக context என்பது அதிக quality அல்ல.

**Operability.** Large context = larger prompt size = logging, monitoring, retry cost எல்லாம் அதிகம். Network timeout வாய்ப்பு அதிகம்.

Failure mode: நீங்கள் context window-ஐ மீறி prompt அனுப்பினால் API error வரும். அல்லது silent truncation நடக்கும். அப்போ model முக்கிய context-ஐ இழந்து hallucinate செய்யும்.

## 6. Practical Example

Enterprise support RAG system.

Requirement: Ticket history 10k tokens, knowledge base top 30 chunks × 500 tokens = 15k, conversation history 5k, system prompt + tools 2k. மொத்தம் ~32k tokens. Output budget 2k.

4k context model-ஐ எடுத்தால் முடியாது. நீங்கள் chunks-ஐ குறைக்க வேண்டும். Information loss ஆகும்.

இங்கே 128k context model தேர்வு செய்யல
