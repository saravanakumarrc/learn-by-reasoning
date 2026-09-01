# Prompt caching

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.6 — Learn to reason about

## 1. Problem

நீங்கள் ஒரு AI Solution Architect. RAG system அல்லது agent workflow build பண்ணியிருக்கீங்க. ஒரு user query வரும்போது:

1. System prompt + user instruction + retrieved context + previous conversation history எல்லாம் சேர்த்து ஒரு பெரிய prompt உருவாகுது.
2. அதே system prompt, அதே few-shot examples, அதே tool definitions எல்லா request-லயும் repeat ஆகுது.
3. Context window 8k-128k வரை இருக்கு. ஒவ்வொரு request-க்கும் அதே 4k tokens-ஐ மறுபடியும் LLM-க்கு அனுப்புறோம்.

What goes wrong? **Latency அதிகம், cost அதிகம்.** ஒரு request-க்கு $0.02 என்றால், 1M request-க்கு $20k. அதில் 60% tokens repeat ஆகும் system prompt + conversation history.

உங்களுக்கு தேவை: *ஏற்கனவே model பார்த்த பகுதிகளுக்கு மறுபடியும் compute பண்ண வேண்டாம்.*

## 2. Mental Model

Prompt caching என்பது LLM inference-ல் **compute reuse**.

Model ஒரு prompt-ஐ process பண்ணும்போது, tokens-ஐ sequential-ஆக read பண்ணி Key-Value cache உருவாக்கும். அடுத்த request-ல் prefix ஒரே மாதிரி இருந்தால், அந்த prefix-க்கான Key-Value cache-ஐ மறுபடியும் compute பண்ணாமல் reuse பண்ணலாம்.

உதாரணத்துக்கு: ஒரு library card-ஐ ஒரு முறை checkout பண்ணி return பண்ணினா, அடுத்த முறை அதே book-ஐ தேடி புத்தக அலமாரி முழுக்க நடக்க வேண்டாம். Card இருக்கு.

அதனால் Prompt caching = **prefix hit = no recompute**.

## 3. How It Works

Inference-ல் 2 phase இருக்கு:

1. **Prefill**: Prompt tokens-ஐ முழுவதும் process பண்ணி KV cache build ஆகும். இது compute heavy.
2. **Decode**: ஒவ்வொரு token-ஐயும் ஒன்றன் பின் ஒன்றாக generate பண்ணும்.

Prompt caching prefill-ஐ cache பண்ணும்.

Provider side-ல் implementation வேறுபடும்:
* **System prompt / developer message caching**: ஒவ்வொரு request-லயும் மாறாத prefix-ஐ குறிப்பிட்டு, provider அதை cache-ல் வைத்துக்கொள்ளும். 5-10 mins வரை valid.
* **Conversation history caching**: previous turns-ஐ prefix-ஆக வைத்து reuse.
* **Embedding-based semantic cache** வேறு concept. அது output cache. இது input prefix cache.

நீங்கள் client-ல் செய்ய வேண்டியது: stable prefix-ஐ தனியாக அனுப்பி, அதை cacheable என்று mark பண்ணுவது. API-ல் `cache_control` அல்லது `prompt_cache` parameter உண்டு.

## 4. Architectural Reasoning

எப்போது useful?

* **High reuse prefix**: System prompt, persona, tool definitions, few-shot examples, large retrieved documents.
* **Multi-turn conversation**: Same user session-ல் history repeat ஆகும்.
* **Batch / high QPS**: Same prompt template-ஐ பல users பயன்படுத்துவார்கள்.

Constraints it addresses:
* **Cost**: Prefill tokens குறைவான price-ல் வரும். Input tokens மொத்த cost-ல் 60-80%.
* **Latency**: Prefill time குறையும். TTFT குறையும்.

Alternatives:
* **Shorter prompts**: Context-ஐ trim பண்ணுவது. Information loss.
* **Summarization**: History-ஐ summarize பண்ணுவது. Fidelity loss.
* **Semantic output cache**: Same query-க்கு same answer return. Prompt caching-க்கு மாற்று இல்லை, complement.

எப்போது choose பண்ணக்கூடாது?
Prefix ஒவ்வொரு request-லும் மாறும் dynamic data அதிகம் இருந்தால், cache hit rate குறைவாக இருக்கும்.

## 5. Trade-offs

**Hit rate vs staleness**: Cache validity window 5-10 mins. System prompt மாறினால் cache invalidate பண்ண வேண்டும். Versioning முக்கியம்.

**Cost model complexity**: Provider-கள் cache read tokens-க்கு தனி price வைக்கிறார்கள். Prefill-க்கு குறைவு. ஆனால் cache miss ஆனால் double compute? இல்லை. வெறும் normal cost.

**Operability**: Prefix boundaries சரியாக set பண்ண வேண்டும். தவறாக set பண்ணினால், model context leak ஆகும் அல்லது cache hit ஆகாது.

**Security / multi-tenancy**: Cache shared infrastructure-ல் இருக்கும். Sensitive data-ஐ cache-ல் வைக்காதீர்கள். PII, secrets-ஐ prefix-ல் வைக்காதீர்கள்.

**Provider lock-in**: Cache format provider specific. Anthropic, OpenAI, etc.

Failure mode: Cache stampede. புதிய system prompt deploy ஆனதும் எல்லா request-ம் cache miss ஆகி spike வரும்.

## 6. Practical Example

Enterprise customer support agent.

System prompt: 2,500 tokens. Company policy, tone, tools definitions.
Few-shot: 1,500 tokens.
Average user query + retrieved KB: 500 tokens.

Without cache: 4,500 input tokens/request.
1M requests/day = 4.5B tokens/day.

Prompt caching enable பண்ணினால்: System prompt + few-shot = 4k tokens cache hit. Compute ஆகும் tokens 500 மட்டும்.

Latency: TTFT 800ms → 250ms.
Cost: Input token price $3/1M. Cache read price $0.3/1M. Saving ~70% on prefix.

Implementation: System prompt-ஐ request payload-ல் முதலில் வைத்து `cache_control: {type:"ephemeral"}` mark செய்யுங்கள். Conversation history-ஐ incremental-ஆக append பண்ணுங்கள்.

## 7. Reasoning Challenge

உங்கள் RAG pipeline-ல் ஒவ்வொரு request-க்கும் 3 documents retrieve ஆகுது. Documents ஒவ்வொரு query-க்கும் வேறுபடும். System prompt 3k tokens stable. User session history 2k tokens.

Cache-ஐ எங்கே apply பண்ணுவீர்கள்? Prefix-ஐ எப்படி partition பண்ணுவீர்கள்? Documents-ஐ cache பண்ணலாமா? ஏன்?

## 8. Key Takeaways

* Prompt caching என்பது **prefix prefill reuse**, output cache அல்ல.
* System prompt, tools, few-shot examples, stable conversation history தான் ideal candidates.
* Cost saving TTFT குறைப்பு ஆகும், ஆனால் cache hit rate, staleness, provider lock-in trade-off உண்டு.
* Architecture decision: Cache boundaries-ஐ சரியாக define பண்ணுங்கள், sensitive data-ஐ cache-ல் வைக்காதீர்கள்.
