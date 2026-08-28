# User prompts

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.2 — Prompt engineering

## 1. Problem

நீங்கள் ஒரு LLM-ஐ API மூலம் call பண்ணுகிறீர்கள். Same input கொடுத்தாலும் output ஒவ்வொரு முறையும் கொஞ்சம் வேறுபடுகிறது. சில முறை output useful ஆக வருகிறது, சில முறை hallucination வருகிறது, சில முறை format சரியில்லை.

ஒரு production system-ல இது ஏற்க முடியாது. API-க்கு அனுப்பும் `user prompt` எப்படி எழுதப்படுகிறது என்பதாலேயே output-ன் quality, consistency, safety, cost எல்லாம் மாறுகிறது.

**என்ன வலிக்கிறது?**
* Unclear instruction → model guess பண்ணும்
* Too much freedom → irrelevant output
* No constraints → JSON parse ஆகாது, token waste ஆகும்
* Context missing → model க்கு domain knowledge இல்லை

User prompt என்பது user-இன் நோக்கத்தை model-க்கு தெளிவாக translate செய்யும் interface ஆகும். அது தெளிவாக இல்லாவிட்டால் system unreliable ஆகும்.

## 2. Mental Model

User prompt = **Instruction + Context + Constraints + Examples**

Model ஒரு junior engineer போல. அவனுக்கு task தெளிவாக சொல்லவேண்டும், what to do, why, what format, what not to do.

நல்ல prompt என்பது ambiguity-யை குறைக்கும். Bad prompt என்பது model-ஐ hallucinate செய்ய வைக்கும்.

Think of it as API contract for LLM. Input specification மாற்றினால் output distribution மாறும்.

## 3. How It Works

LLM ஒரு statistical pattern matcher. Prompt என்பது conditioning signal.

Three levers matter architecturally:

**Clarity of role and task.** "You are a..." என்பது model-ன் behavior prior-ஐ shift பண்ணும்.

**Context window usage.** Relevant facts, history, domain rules prompt-ல் இருக்க வேண்டும். Too much noise → dilution.

**Output constraints.** Format, length, style, forbidden content. இது parsing and downstream reliability-க்கு முக்கியம்.

Practical pattern:
```
Role: நீ ஒரு...
Task: நீ செய்ய வேண்டியது...
Context: இந்த data இதோ...
Constraints: JSON மட்டும் output, 200 words க்குள், Tamil-ல பதில்...
Example: Input -> Output
```

## 4. Architectural Reasoning

User prompt எப்போது critical?

* RAG pipeline-ல retrieval results-ஐ LLM-க்கு pass செய்யும்போது, prompt தான் relevance filter.
* Agent workflow-ல tool calling decision prompt-ல இருந்து வரும்.
* Structured output generation, classification, summarization எல்லாம் prompt quality-ல depend ஆகும்.

Alternatives:
* **Better prompt vs more data.** சில சமயம் prompt-ஐ refine பண்ணுவது fine-tuning-ஐ விட cheaper.
* **Prompt vs system prompt.** System prompt = global behavior. User prompt = request-specific instruction. Architecture-ல இரண்டையும் separate செய்ய வேண்டும்.
* **Prompt engineering vs tool use.** சில logic-ஐ prompt-ல வைக்காமல் code/tool-ல move பண்ணலாம்.

Choose good prompt when you need fast iteration, low cost, no training data. Choose fine-tuning / RAG / tool when prompt-ஐ மேலும் tight செய்ய முடியாது.

## 5. Trade-offs

**Specificity vs Flexibility**
மிகவும் specific ஆக இருந்தால் model creative ஆக முடியாது, brittleness வரும். மிகவும் vague ஆக இருந்தால் output inconsistent ஆகும்.

**Context length vs Cost & Latency**
நீளமான prompt = அதிக token, அதிக latency, அதிக cost. ஆனால் relevant context இல்லாமல் quality drop ஆகும். Window-ஐ smartly manage பண்ண வேண்டும்.

**Instruction complexity vs Reliability**
Complex multi-step instruction = model fail rate அதிகம். Break into steps, chain prompts.

**Safety vs Utility**
Too restrictive prompt → model refuses or gives generic answer. Too loose → risky output.

Failure modes: prompt injection, context contamination, token limit overflow, ambiguous role leading to mixed language output.

## 6. Practical Example

Enterprise support ticket classification.

Bad user prompt:
> "இந்த ticket-ஐ classify பண்ணு."

Good user prompt:
```
You are a support triage assistant.
Task: Classify the ticket into one of: billing, technical, account, other.
Context: Company uses specific SLA for billing.
Constraints:
- Output only valid JSON: {"category":"...", "confidence":0-1, "reason":"..."}
- Reason max 20 words.
- If unsure, choose "other".
Example:
Input: "I was charged twice"
Output: {"category":"billing","confidence":0.9,"reason":"duplicate charge mentioned"}
Ticket: {{ticket_text}}
```

இங்கே role, task, constraints, format, example எல்லாம் இருக்கு. Downstream parser எளிதாக ஆகும், cost predictable ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் customer chat history 10k tokens இருக்கு. User கேட்கிறார்: "எனக்கு refund தேவை". Model summary கொடுக்க வேண்டும் மற்றும் refund eligibility decide செய்ய வேண்டும்.

Prompt-ல முழு history-யும் போடலாமா? Token cost அதிகம். Relevant parts மட்டும் retrieve செய்து prompt-ல சேர்க்கலாமா? Retrieval error வந்தால் decision தவறும்.

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Prompt-ஐ எப்படி design பண்ணுவீர்கள்? Why?

## 8. Key Takeaways

* User prompt என்பது system reliability-க்கான first line of control. Clarity = consistency.
* Instruction + Context + Constraints + Examples என்ற frame-ஐ பயன்படுத்து.
* Prompt quality என்பது cost, latency, safety, operability எல்லாவற்றையும் பாதிக்கும்.
* ஒவ்வொரு prompt-க்கும் trade-off இருக்கு: specificity vs flexibility, context vs cost.
* Prompt-ஐ evolve செய்ய முடியும். Measure output quality, parse errors, cost, then iterate.
