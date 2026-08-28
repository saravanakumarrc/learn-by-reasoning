# Simple completion

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.1 — LLM patterns

## 1. Problem

உனக்கு ஒரு text இருக்கு. User-கிட்ட வந்த query-க்கு அதற்கு பொருத்தமான next words-ஐ generate பண்ணணும்.

பழைய approach என்ன? Rule-based templates, hard-coded responses, if-else chain.

அது வேலை செய்யும் வரை செய்யும். ஆனால்:
* Input சற்று மாறினாலும் response mismatch ஆகும்
* New use-case வந்தால் code மாற்றணும், deploy பண்ணணும்
* Tone, style, length control பண்ண முடியாது
* Context வளர வளர logic explode ஆகும்

அப்போ பிரச்சனை என்ன? **Language generation-ஐ explicit programming-ஆல் கட்டுப்படுத்த முடியாது.** நமக்கு வேண்டியது ஒரு system எது கொடுத்த input-ல் இருந்து statistically plausible continuation-ஐ உருவாக்கும்.

அதான் Simple completion பிறந்தது.

## 2. Mental Model

Simple completion என்பது: **LLM-க்கு ஒரு prompt கொடு, அது அதற்கு அடுத்து என்ன வரும் என்று predict பண்ணி text-ஐ தொடரும்.**

எந்த tool call இல்லை, retrieval இல்லை, multi-step reasoning இல்லை. ஒரே input → ஒரே output.

Analogy: நீ ஒரு experienced writer-க்கு first sentence கொடுக்கிறாய். அவன் style-ஐ புரிந்து கொண்டு மீதியை எழுதுவான். நீ outline கொடுக்கவில்லை, editor இல்லை. Just completion.

## 3. How It Works

Architecture ரொம்ப simple.

```
User Input → Prompt Formatting → LLM → Completion Output → Post-process → User
```

LLM internally auto-regressive generation பண்ணும். Prompt-ஐ context window-ல் வைத்து, next token probability distribution-ல் இருந்து sample பண்ணி தொடர்ந்து generate பண்ணும்.

Parameters முக்கியம்:
* **temperature**: creativity vs determinism
* **max_tokens**: length control
* **top_p / top_k**: sampling control
* **stop sequences**: எங்கே நிறுத்த வேண்டும் என்பது

இதில் system prompt, user prompt, maybe few examples இருக்கலாம். ஆனால் core pattern இதுதான்: single forward pass, no external calls.

## 4. Architectural Reasoning

இது useful எப்போது?

* **Latency முக்கியம்.** One round trip, no I/O. 200-500ms-ல் response வேண்டும்.
* **Content generation simple.** Summarize, rewrite, translate, expand, classification via text output.
* **Deterministic control தேவையில்லை.** Creative writing, email draft, product description.
* **Cost முக்கியம்.** Token usage minimal, no retrieval, no tool calls.

எப்போது தேர்வு செய்வது?
நீ புதிய LLM feature try பண்ணும்போது முதலில் இதில் ஆரம்பி. Baseline-ஆக வைத்து, போதாதென்றால் பின்னர் RAG, tools சேர்.

Alternatives:
* **RAG**: completion தேவை, ஆனால் facts தேவை.
* **Tool-using Agent**: completion தேவை, ஆனால் external data / actions தேவை.
* **Chain of Thought**: reasoning output தேவை.

Simple completion தேர்வு என்பது: **நமக்கு external truth அல்லது action தேவையில்லை. Language pattern மட்டும் போதும்.**

## 5. Trade-offs

* **Speed vs Accuracy**: மிக வேகம், ஆனால் hallucination வாய்ப்பு உண்டு. Model தன் knowledge cutoff-க்குள் இருப்பதை மட்டுமே generate பண்ணும்.
* **Control vs Flexibility**: Prompt engineering-ல் control உண்டு, ஆனால் hard guarantee இல்லை. Output format மாறலாம்.
* **Cost vs Capability**: Cheapest pattern. ஆனால் complex task-க்கு போதாது.
* **Operability**: Monitor பண்ண எளிது. Input/output log மட்டும் போதும். No retrieval latency, no tool failure modes.

முக்கிய failure mode: **Prompt injection, toxic output, length explosion**. இதற்கு output validation, stop sequences, moderation filter தேவை.

## 6. Practical Example

E-commerce product description generation.

Input: product title, features bullet list, tone = friendly.

Prompt:
```
Write a 2-sentence product description in Tamil-English mix for an engineer audience.
Title: Wireless Noise Cancelling Headphones X200
Features: 30h battery, Bluetooth 5.3, ANC, foldable
```

Simple completion output:
> X200 headphones 30 மணி நேர battery-உடன் வருகிறது, Bluetooth 5.3-ல் stable connection தருகிறது. ANC on பண்ணினால் office noise-ஐ குறைத்து focus-க்கு உதவும், foldable design-ல் travel-க்கு easy.

No database call, no search. 300 tokens, <1 sec. 1000 products-க்கு batch generate பண்ணலாம்.

இங்கே decision: Description creative + brand voice தேவை, factual accuracy product team கொடுத்த features-ல் மட்டும் இருக்கு. So simple completion போதும். Price, inventory தேவை இல்லை.

## 7. Reasoning Challenge

உனக்கு customer support chatbot இருக்கு. 90% queries "order status", "return policy", "refund" போன்ற repeatable questions. Current system Simple completion மட்டும் use பண்ணுகிறது. 

User கேட்கிறார்: "Order #12345 status என்ன?" Model தன்னிச்சையாக "shipped" என்று கற்பனை பண்ணி பதில் கொடுக்கிறது.

இங்கே Simple completion-ஐ தொடர வேண்டுமா? இல்லை வேறு pattern-க்கு மாற வேண்டுமா? ஏன்? என்ன architecture trade-off வரும்?

## 8. Key Takeaways

* Simple completion = prompt in → text out, no retrieval, no tools. Fast and cheap baseline.
* இது useful when task is language transformation, not fact lookup or action.
* Control comes from prompt + parameters, not from external system.
* Hallucination, non-determinism, format drift ஆகியவை முக்கிய trade-offs.
* Complex ஆகும் முன் Simple completion-ஆல் start செய்து, constraint தெளிவாகும்போது RAG / Agents-க்கு evolve பண்ணு.
