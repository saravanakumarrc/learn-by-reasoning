# Structured prompting

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.4 — Prompt engineering

## 1. Problem

உங்க team ஒரு LLM agent build பண்ணுது. Same task கொடுத்தா ஒவ்வொரு முறையும் output format மாறுது. சில முறை JSON வருது, சில முறை plain text, சில முறை field names தப்பா வருது.

Downstream service அந்த output-ஐ parse பண்ண முயற்சிக்கும் போது crash ஆகுது. Engineer எப்பவும் "please give JSON"ன்னு request பண்ணி fix பண்ணுறார், ஆனா மறுபடியும் break ஆகுது.

**What goes wrong if we don't have this?** Model-ஐ நம்பி free-form text generate பண்ணுவது என்பது reliability இல்லாதது. Production-ல deterministic contract வேண்டும்.

இங்கே problem என்னவென்றால் LLM என்பது probabilistic generator. அதற்கு structure என்ற concept இயற்கையாக தெரியாது.

## 2. Mental Model

Structured prompting என்பது model-க்கு **output contract** கொடுப்பது.

நீங்கள் user-க்கு API spec கொடுப்பது போல, model-க்கும் input + expected output schema கொடுக்கிறீர்கள்.

இதன் core idea: *prompt என்பது instruction அல்ல, specification*.

Model-க்கு "think like this, then output like this" என்று reasoning path + format constraint இரண்டையும் கொடுப்பது.

## 3. How It Works

Structured prompting 3 layer-களை use பண்ணும்:

**Role + Task framing:** Model எப்படி behave பண்ண வேண்டும் என்பதை set பண்ணு.
> "You are a data extraction agent."

**Constraints as rules:** Hard rules-ஐ explicit-ஆக list பண்ணு.
> "Output only valid JSON. No extra text. Keys must be exactly: name, age, city."

**Schema enforcement:** Output shape-ஐ define பண்ணு.
> "Return JSON matching this schema: {...}"

முக்கியம்: Few-shot examples. Model-க்கு ஒரு correct example காட்டினால், அதே pattern repeat பண்ணும் probability அதிகரிக்கும்.

உதாரணம்:
```
Input: "Invoice #123, amount $500, due 2025-01-10"
Output: {"invoice_id":"123","amount":500,"due_date":"2025-01-10"}
```

## 4. Architectural Reasoning

எப்போது structured prompting useful?

* Downstream code model output-ஐ programmatically consume பண்ணும் போது
* RAG pipeline-ல extraction, classification, routing decisions
* Agent workflow-ல step output consistent-ஆக இருக்க வேண்டும்
* Testing & observability தேவைப்படும் போது

Constraint it addresses: **Output reliability & parseability**.

Alternatives:
* Free-form prompting + post-processing with regex/parsing -> brittle, cost high
* Tool/function calling with JSON schema enforcement -> strong, but model & API support தேவை
* Structured prompting is middle ground: no code change, just better prompt design

Architect choose பண்ணுவார் when you need quick reliability without changing model provider, and when output schema relatively stable.

## 5. Trade-offs

**Reliability vs Flexibility.** Strict schema கொடுத்தால் model creative response குறையும். Edge cases-ல hallucinate பண்ணி schema violate பண்ணும்.

**Prompt complexity vs Token cost.** Good structured prompt longer ஆகும். Context window & latency increase ஆகும்.

**False confidence.** Model JSON produce பண்ணினாலும் content valid இல்லாமல் இருக்கலாம். Syntax correct, semantics wrong.

**Failure mode:** Model "sorry, I cannot" என்று extra text add பண்ணும். அதனால் parser fail. இதற்கு "Output only JSON, no markdown code fences" போன்ற rule தேவை.

## 6. Practical Example

Enterprise support ticket classification.

Problem: 10k tickets/day வருது. Human agent manually tag பண்ண முடியாது.

Structured prompt:
```
You are a ticket classifier.
Input: customer message.
Output ONLY valid JSON with keys: intent, priority, product, needs_human.

Rules:
1. intent must be one of: billing, technical, refund, account
2. priority must be low|medium|high|critical
3. product must be one of: mobile, broadband, tv
4. No extra text.

Example:
Input: "My internet is down since morning"
Output: {"intent":"technical","priority":"high","product":"broadband","needs_human":false}
```

இப்போது downstream service JSON-ஐ directly database-ல insert பண்ண முடியும். No regex.

## 7. Reasoning Challenge

உங்களிடம் product review summarization system உள்ளது. Model-ஐ கேட்கிறீர்கள்: "Summarize pros and cons". சில முறை bullet list, சில முறை paragraph, சில முறை JSON வருகிறது. Analytics pipeline parse பண்ண முடியவில்லை.

Schema தேவை: `{"pros":[string], "cons":[string], "rating":1-5}`

இங்கே structured prompting மட்டும் போதுமா? இல்லை function calling / output validation layer தேவையா? ஏன்?

## 8. Key Takeaways

* Structured prompting என்பது model-க்கு output contract கொடுப்பது, instruction கொடுப்பது அல்ல
* Few-shot example + explicit rules + schema definition = reliability
* Always assume model will break format. Plan validation layer
* Every extra constraint improves parseability but reduces flexibility. Choose based on downstream needs
