# Input vs output tokens

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.2 — Learn to reason about

## 1. Problem

ஒரு AI system build பண்றீங்க. User query வருது, RAG pipeline run ஆகுது, LLM call போகுது. Bill வரும்போது shock ஆகுது.

"ஏன் இவ்வளவு cost?"

அங்கதான் input tokens vs output tokens என்ற distinction முக்கியம் ஆகுது.

Same prompt க்கு cost ஏன் வேறுபடுது? ஒரு request 200 tokens input, 50 tokens output. இன்னொரு request 2000 tokens input, 1500 tokens output. Pricing model என்ன? ஒரு service-ல 1M input tokens = $1, 1M output tokens = $5. இது ஏன்?

Cost optimize பண்ணனும் என்றால் எதை குறைக்கணும்? Context size-ஐயா, response length-ஐயா?

## 2. Mental Model

LLM-க்கு ஒரு request என்பது இரண்டு வேலை.

**Input tokens**: Model க்கு கொடுக்கும் everything. System prompt, user query, conversation history, retrieved documents. இதை model *read* பண்ணனும்.

**Output tokens**: Model generate பண்ணும் response. இதை model *write* பண்ணனும்.

Read vs Write என்று நினைச்சுக்கோங்க.

Read என்பது cheap-ish. Write என்பது expensive. ஏன்? ஏனென்றால் input ஒரு முறை process ஆகும். Output ஒவ்வொரு token-க்கும் next token predict பண்ணி, autoregressive generation போகும். Compute proportional to output length * context length.

## 3. How It Works

Token என்பது roughly word piece. 1 token ~ 0.75 English words.

Cost = input_tokens * input_price_per_token + output_tokens * output_price_per_token.

Input price generally 2x to 10x cheaper than output price.

உதாரணமாக GPT-4o class models-ல் input ~ $2.50 /1M, output ~ $10 /1M. Input cheap, output costly.

Context window fill ஆகும்போது input tokens அதிகமாகும். RAG-ல் 10 documents retrieve பண்ணினால் 15k tokens input ஆகும்.

Output tokens அதிகமாகும் when model long explanation, code, reasoning steps கொடுக்கும்.

## 4. Architectural Reasoning

Cost architecture பார்க்கும்போது இந்த distinction ஏன் முக்கியம்?

**Input heavy systems**: RAG, agents with large history, summarization pipelines.

இங்கே problem என்ன? Retrieval quality vs token cost trade-off. 20 chunks கொடுத்தால் context heavy, accuracy better ஆகலாம். ஆனால் input cost அதிகம். மேலும் larger input → larger KV cache → higher latency.

இதை கட்டுப்படுத்த options: better chunking, reranking, summary of retrieved docs, context compression, embeddings filter.

**Output heavy systems**: Chatbots, code generation, long form content generation.

இங்கே problem என்ன? User wants detailed answer. ஆனால் every extra 100 tokens = direct cost + latency.

Architectural decision: output length budget set பண்ணுவது. Streaming, early stop, structured output with concise schema, tool use instead of long text.

ஒரு architect என்ன பார்க்கணும்? 

* Input cost scales with number of users * context per request.
* Output cost scales with number of users * average response length * complexity.

Throughput தேவை இருக்கும் service-ல் output cost dominate பண்ணும்.

## 5. Trade-offs

**Input vs Output cost ratio**: Output 3-8x expensive. So 1 token reduce in output ≈ 3-8 tokens reduce in input.

**Latency**: Large input → higher prefill time. Large output → higher generation time.

**Quality vs Cost**: More input context = better grounding but cost + latency. Shorter output = cheaper but possibly less useful.

**Caching**: Input tokens repeat ஆனால் cache hit ஆகலாம். Prompt caching / context caching உள்ள models-ல் input cost குறையும். Output cache பண்ண கஷ்டம்.

Failure mode: Unbounded context growth. Conversation history keep adding. Input tokens linear grow ஆகி cost explode ஆகும். Need sliding window or summarization.

## 6. Practical Example

Enterprise support chatbot.

User asks: "My order 12345 status என்ன?"

Bad design: Full conversation history 8k tokens + 5 retrieved tickets 10k tokens + system prompt = 18k input. Model generates 800 token explanation.

Good design:
* Input: system prompt 500 tokens + conversation summary 300 tokens + 2 most relevant tickets 2k tokens = ~2.8k input.
* Output: structured JSON with status + short sentence 80 tokens.

Cost drop ~ 6x input, 10x output.

Architecture: retrieval reranking to top 2, conversation summarizer agent, output schema with max tokens.

## 7. Reasoning Challenge

உங்க RAG system-ல் average input 12k tokens, output 600 tokens. Monthly 1M requests. Input price $3/1M, output price $15/1M.

இப்போ context compression பண்ணினால் input 12k → 6k ஆகும், ஆனால் quality 5% drop ஆகும். Alternatively output limit 600 → 300 ஆக்கினால் user satisfaction 10% drop.

எந்த trade-off-ஐ முதலில் try பண்ணுவீங்க? ஏன்? Cost impact எவ்வளவு?

Think about cost per request, latency, user impact.

## 8. Key Takeaways

* Input = read cost, cheap. Output = write cost, expensive. Architecture decisions இதை மையமாக வைத்து செய்யணும்.
* Cost optimize பண்ண output length மற்றும் input context size இரண்டையும் கட்டுப்படுத்துங்க. Output க்கு 3-8x weight.
* Unbounded history மற்றும் over-retrieval தான் silent cost killers. Rerank, summarize, compress பண்ணுங்க.
* Every token decision என்பது latency, quality, cost மூன்று point-ல் trade-off.
