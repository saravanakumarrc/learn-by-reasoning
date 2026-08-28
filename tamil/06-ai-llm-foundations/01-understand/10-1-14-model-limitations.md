# Model limitations

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.14 — Understand

### 1. Problem

உங்க team ஒரு LLM-based chatbot build பண்ணுது. முதல் demo-ல அது நல்லா பதில் சொல்லுது. Production-க்கு போனதும் user கேள்வி கொஞ்சம் நீளமா இருந்தா, அல்லது context window நிறைஞ்சா, அல்லது முந்தைய conversation-ஐ reference பண்ண சொன்னா, அது hallucinate பண்ணுது.

இன்னொரு case: ஒரு financial report generate பண்ண சொன்னீங்க. Model தான் generate பண்ணிய மாதிரி தோன்றும் numbers கொடுத்துடுது. உண்மையான data-வை fetch பண்ணல.

இன்னொரு case: நீங்க model-க்கு "safe" prompt கொடுக்கிறீங்க, அதே prompt-ஐ சின்ன twist-ல கொடுத்தா அது disallowed content generate பண்ணுது.

**What goes wrong if we don't have this?** Model-ஐ perfect knowledge source மாதிரி நினைச்சு architecture design பண்ணிட்டா, system-ம் reliability, accuracy, safety எல்லாம் உடைஞ்சு போகும்.

### 2. Mental Model

LLM என்பது ஒரு statistical pattern matcher. Memory இல்லாத, deterministic calculator இல்லாத, real-time knowledge இல்லாத.

அதை ஒரு senior engineer-ஆ நினைக்காதீங்க. அதை ஒரு very fluent writer ஆ நினைங்க, யாருக்கு:

- limited context window உண்டு
- training data cut-off உண்டு
- confidence calibration இல்லை
- ground truth தெரியாது

இதை புரிஞ்சுக்காம system design பண்ணுறது, கண்ணாடி வீட்டுல குண்டு வீசுற மாதிரி.

### 3. How It Works

Model limitations mainly 4 வகை.

**1. Context and Memory limitation**
Context window finite. 128k tokens என்றாலும், effective reasoning degrades at the edges. Long documents-ல middle part forget ஆகும். Model-க்கு session memory இல்லை, unless you explicitly provide via conversation history.

**2. Knowledge cutoff and hallucination**
Model training data-க்கு அப்புறம் நடந்தது தெரியாது. Unknown facts-க்கு பதில் தேவைன்னா, அது plausible but fake answer generate பண்ணும். இது hallucination.

**3. Reasoning and tool use limitation**
Chain-of-thought உண்டு, ஆனால் multi-step arithmetic, logical deduction, code execution துல்லியம் சரியாக இருக்காது. No built-in verification loop.

**4. Safety and alignment brittleness**
Prompt injection, jailbreak, adversarial input-ல model behavior மாறும். Guardrails பெரும்பாலும் heuristic.

### 4. Architectural Reasoning

Model limitations-ஐ புரிஞ்சுக்கிறது ஏன் முக்கியம்? Because architect-ஆ நீங்க model-ஐ wrapper பண்ணி system ஆக்கணும்.

**When this becomes useful:** LLM-ஐ source of truth ஆக்கும் எந்த system-லயும்.

**What constraint it addresses:** Accuracy, reliability, latency, cost, safety.

Alternatives:

- RAG with vector database + source citation
- Tool use with real APIs / calculator / database
- Fine-tuning / RAG hybrid for domain knowledge
- Multi-agent verification with critic model
- Output validation and confidence scoring

Architect choose பண்ணுவார்:

- Knowledge freshness தேவைன்னா RAG
- Deterministic computation தேவைன்னா tool use
- Long context தேவைன்னா summarization + retrieval
- High risk domain-ல safety தேவைன்னா guardrails + human-in-the-loop

### 5. Trade-offs

**Accuracy vs Latency and Cost**
RAG, tool calls, multi-step reasoning accuracy improve பண்ணும். ஆனால் latency increase ஆகும், cost per request increase ஆகும்.

**Context completeness vs Reasoning quality**
More context add பண்ணினா window fill ஆகி reasoning degrade ஆகும். Summarize பண்ணா info loss.

**Automation vs Safety**
Full auto agent fast, ஆனால் hallucination risk அதிகம். Human-in-the-loop safe, ஆனால் throughput குறையும்.

**General model vs Domain model**
General LLM flexible. Fine-tuned or RAG-augmented model accurate. Maintenance overhead அதிகம்.

Failure modes:

- Silent hallucination: confident but wrong output
- Context overflow: important instruction truncated
- Prompt injection: user input controls model behavior
- Drift: model behavior change across versions

### 6. Practical Example

Enterprise customer support agent.

Problem: Model training data-ல product docs 2023 வரை தான் உண்டு. Product 2024-ல major update ஆகியிருக்கு.

Architectural decision:

1. Vector DB-ல latest knowledge base index செய்ய
2. User query வந்ததும் retrieval + re-ranking
3. Retrieved chunks-ஐ context-ல கொடு, source citation enforce பண்ணு
4. Answer generate பண்ணிய பிறகு, LLM critic-ஆக ஒரு second pass: "Is answer grounded in sources?"
5. Low confidence ஆனா human escalation

Result: Hallucination குறையும். Trade-off: latency ~2x, cost ~1.8x.

இல்லாமல் direct LLM use பண்ணினா, agent confident-ஆ outdated or fake instructions கொடுக்கும்.

### 7. Reasoning Challenge

உங்க RAG system-ல user ஒரு 200 page legal contract upload பண்ணி, "Clause 7.3-ல penalty என்ன?" என்று கேட்கிறார்.

Model context window 32k. Contract 150k tokens. Model retrieved top 10 chunks மட்டும் கொடுக்கிறீங்க.

Potential problem என்ன? Retrieval correct ஆக இருந்தாலும் answer reliable ஆகுமா? இங்கே என்ன architecture pattern பயன்படுத்துவீங்க, ஏன்?

### 8. Key Takeaways

- LLM-ஐ perfect knowledge engine ஆ நினைக்காதே. Statistical pattern matcher ஆ நினை.
- Context window, cutoff, hallucination, reasoning brittleness என்பது inherent limitations, bugs அல்ல.
- System reliability வேணும்னா model-ஐ RAG, tools, validation, guardrails-உடன் wrap பண்ணு.
- Every mitigation adds latency and cost. Trade-off-ஐ conscious-ஆ choose பண்ணு.
