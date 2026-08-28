# Tokens

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.4 — Understand

### 1. Problem

LLM-க்கு நீங்கள் raw text கொடுக்க முடியாது. Model-க்கு input வருவது numbers மட்டும்தான். 

உண்மையான வலி இங்கே இருக்கு:
* ஒரு பயனர் query வரலாம் 5 words-ல, இன்னொருவர் வரலாம் 500 words-ல. Neural network-க்கு fixed size input வேண்டும்.
* Character level-ல் பார்த்தால் Tamil ஒரு sentence-க்கே 200+ characters. Model அதை process பண்ணுவது மிகவும் slow, context window விரைவில் தீர்ந்துவிடும்.
* Word level-ல் பார்த்தால் rare words, misspellings, English-Tamil code-mix எல்லாம் vocabulary-ல் இருக்காது.

இந்த inconsistency தான் token என்ற concept-ஐ உருவாக்கியது. Billing, latency, context window எல்லாம் token count-ல்தான் முடிவாகிறது.

> "What problem became painful enough?" Cost மற்றும் context limit. ஒரு LLM call $0.001 per 1k tokens என்றால், token எண்ணிக்கை நேரடியாக cost-ஐ தீர்மானிக்கிறது.

### 2. Mental Model

Token என்பது model-க்கு தெரிந்த ஒரு குறியீடு. ஒரு word அல்ல, ஒரு character அல்ல. பெரும்பாலும் sub-word.

Mental model: ஒரு tokenizer என்பது text-ஐ small reusable pieces-ஆக வெட்டும் மெஷின். `நீங்கள்` என்பது ஒரு token. `நீ` + `ங்கள்` என்று split ஆகலாம். `transformer` என்பது `trans`, `former` என்று இரண்டு tokens ஆகலாம்.

Model பார்ப்பது token IDs மட்டுமே. `Embedding` layer அந்த ID-யை vector-ஆக மாற்றுகிறது.

### 3. How It Works

Tokenization பொதுவாக Byte-Pair Encoding, BPE அல்லது byte-level BPE.

எப்படி நடக்கும்:
1. முதலில் அனைத்து bytes-ஐயும் base tokens ஆக எடுக்கவும்.
2. Training data-ல் அடிக்கடி வரும் character pair-களை merge செய்யவும். `a` + `t` = `at`, பின் `at` + `t` = `att`...
3. இறுதியில் ஒரு vocabulary உருவாகும் ~50k - 200k tokens.

தமிழுக்கு இது முக்கியம். தமிழில் ஒரு word சராசரியாக English விட அதிக characters எடுக்கும். `பயன்படுத்துதல்` என்பது ஒரே token ஆக இருக்கலாம், அல்லது `பயன்` + `படுத்து` + `தல்` என்று split ஆகலாம்.

Detokenization திரும்ப மென்மையாக நடக்கும், ஆனால் exact original formatting திரும்ப வராது. இது ஒரு trade-off.

### 4. Architectural Reasoning

Architect-க்கு token என்பது 3 constraints-ஐ control செய்கிறது:

* **Context window**: Model ஒரு முறை பார்க்கும் max tokens. 4k, 128k. அதற்குள் prompt + system + history + output எல்லாம் வர வேண்டும்.
* **Latency**: Token generation autoregressive. Output tokens அதிகமாகும் போது latency linearly increase ஆகும்.
* **Cost**: Provider billing input tokens மற்றும் output tokens-க்கு தனித்தனியாக.

எனவே prompt design என்பது token budgeting. RAG pipeline-ல் chunk size-ஐ tokens-ல் வைக்கிறோம், characters-ல் அல்ல. `chunk_size=500 tokens, overlap=50 tokens` என்பது நடைமுறை.

எப்போது பிரச்சினை வரும்? Code-mix Tamil-English. ஒரு English sentence சராசரியாக 1.3 tokens per word. தமிழ் sentence சராசரியாக 2.5 - 3 tokens per word ஆக இருக்கலாம், tokenizer training data bias காரணமாக. இதனால் same meaning-க்கு தமிழ் அதிக tokens செலவழிக்கும்.

### 5. Trade-offs

* **Vocabulary size vs efficiency**: Vocabulary பெரிதாக இருந்தால் common words ஒரே token ஆகிறது, tokens குறையும். ஆனால் model size அதிகரிக்கும், rare token learning கடின
