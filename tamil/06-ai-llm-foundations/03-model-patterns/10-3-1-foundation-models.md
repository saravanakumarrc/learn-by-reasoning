# Foundation models

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.1 — Model patterns

## 1. Problem

உங்களிடம் ஒரு LLM இருக்கு. அதை எல்லா use case-க்கும் ஒரே மாதிரி பயன்படுத்த முயற்சிக்கிறீர்கள்.

Customer support chat, code generation, summarization, classification, agent tool calling — எல்லாவற்றுக்கும் ஒரே prompt, ஒரே model.

என்ன நடக்கும்?
* Prompt பெரிசாகும், confusing ஆகும்
* Model சில task-ல துல்லியமாக இல்லை
* Latency அதிகம், cost அதிகம்
* Evaluation-ல எது fail ஆகுதுன்னு தெரியாது

இங்கே பிரச்சனை: **foundation model ஒரு general purpose tool. நீங்கள் அதை ஒரு specific job க்கு fit செய்ய வேண்டும்.**

What problem became painful enough? One model, many jobs. Quality, cost, control எல்லாம் குழம்புது.

## 2. Mental Model

Foundation model = pre-trained, large, general capability.

Model pattern = அந்த general capability-ஐ ஒரு specific problem-க்கு பயன்படுத்தும் வழி.

நீங்கள் மூன்று மட்டங்களில் control செய்யலாம்:

1. **Prompting** - same model, better instruction
2. **Fine-tuning / Adaptation** - model weights-ஐ tweak செய்ய
3. **Orchestration** - model-ஐ system-ல வைத்து workflow design செய்ய

Pattern என்பது இந்த மூன்றில் எது, எப்போது, எதற்காக என்பதன் தேர்வு.

## 3. How It Works

Foundation model-ன் core capability: pattern matching on text.

நீங்கள் அதை ஒரு job-க்கு பயன்படுத்தும்போது நீங்கள் effectively இதை செய்கிறீர்கள்:

* **Zero-shot / Few-shot prompting:** Model-க்கு instruction கொடு, examples காட்டு. No training.
* **In-context learning:** Prompt-ல context, retrieved docs, tools வைத்து behavior-ஐ steer செய்.
* **Fine-tuning:** Domain data-ல model-ஐ re-train செய்து style, accuracy மாற்று.
* **RAG:** Model-க்கு external knowledge கொடு, hallucination குறை.
* **Agent pattern:** Model-க்கு tools கொடு, loop-ல reason செய்ய விடு.

Pattern என்பது இவற்றின் combination.

## 4. Architectural Reasoning

எப்போது எந்த pattern?

**Prompt engineering மட்டும் போதுமா?**
ஆமாம், problem stable, data limited, latency sensitive, cost sensitive. உதாரணம்: email summarization, simple classification.

Constraint: Prompt size limit, non-determinism, every request-ல் context repeat செய்ய வேண்டும்.

**RAG தேவையா?**
Model-க்கு real-time / private data தேவை. Factual correctness முக்கியம். உதாரணம்: internal knowledge base Q&A, product catalog search.

Trade-off: Retrieval quality = system quality. Retrieval latency + token cost.

**Fine-tuning தேவையா?**
Same task, thousands of examples, consistent style/tone, low latency, reduced prompt cost. உதாரணம்: legal clause extraction, code style conversion, brand voice chatbot.

Constraint: Data quality, retraining cycle, versioning, cost.

**Agent pattern தேவையா?**
Multi-step, tool use, dynamic planning தேவை. உதாரணம்: travel booking, data analysis workflow.

Constraint: Error propagation, non-determinism, observability கடினம்.

Architect-ஆக நீங்கள் கேட்க வேண்டியது:
* Data எவ்வளவு மாறுகிறது?
* Accuracy vs latency vs cost எது முக்கியம்?
* Team-க்கு model ops வருமா?

## 5. Trade-offs

1. **Prompt vs Fine-tune:** Prompt cheap, fast to iterate. Fine-tune expensive, but deterministic and cheaper per inference at scale. Every fine-tune locks you to a model version.

2. **RAG vs Parametric memory:** RAG fresh, controllable, auditable. Parametric memory fast, no retrieval failure. Hybrid-ல complexity அதிகம்.

3. **General vs Specialized model:** Larger foundation model = better general reasoning, higher cost/latency. Smaller fine-tuned model = cheaper, faster, but brittle outside domain.

4. **Orchestration complexity:** Agent pattern powerful ஆனால் failure modes அதிகம். Retry, timeout, tool error handling தேவை. Observability கடினம்.

Important failure mode: Prompt drift. Model update ஆனால் behavior மாறும். No regression test = silent quality drop.

## 6. Practical Example

Enterprise support chatbot.

வெறும் LLM prompting: Model generic answers கொடுக்கும், internal policy மீறும், hallucinate செய்யும்.

Architecture reasoning:
* Data private + changing → RAG on Confluence + Zendesk
* Brand tone consistent → light fine-tune on past good responses
* Tool use தேவை → agent pattern for order lookup, refund initiation

Flow:
User query → intent classification → retrieve relevant docs → context + policy injection → LLM generates draft → tool call if needed → human review gate for sensitive actions

Cost control: Small model for classification, large model only for generation. Cache frequent answers.

## 7. Reasoning Challenge

உங்களிடம் ஒரு fintech app இருக்கு. Fraud detection explanation generate செய்ய வேண்டும். Explanations must be regulator compliant, consistent wording, and data changes daily.

Options:
A. Pure few-shot prompting with daily data in prompt
B. RAG over policy docs + fine-tuned small model for wording
C. Large model agent with web search

நீங்கள் எதை தேர்வு செய்வீர்கள்? Why? என்ன trade-off ஏற்படும்?

## 8. Key Takeaways

* Foundation model என்பது capability, model pattern என்பது அதை job-க்கு fit செய்யும் வழி.
* Prompt, RAG, fine-tune, agent — இவை எல்லாம் trade-off between control, cost, latency, freshness.
* Architect-ஆக நீங்கள் தேர்வு செய்ய வேண்டியது data volatility, consistency need, operational complexity-ன் அடிப்படையில்.
* Every pattern creates new failure mode: retrieval failure, prompt drift, fine-tune staleness, agent loop explosion.
