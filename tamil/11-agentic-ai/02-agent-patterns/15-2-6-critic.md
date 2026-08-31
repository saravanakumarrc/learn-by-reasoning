# Critic

> **Learning Path:** Agentic AI
> **Section:** 15.2.6 — Agent patterns

## 1. Problem

உங்கள் agent ஒரு output generate பண்ணுது. உதாரணமா, ஒரு code snippet, ஒரு summary, ஒரு customer reply.

அது சரியா இருக்கா? Hallucination இல்லையா? Requirements-ஐ satisfy பண்ணுதா? Tone சரியா இருக்கா?

ஒரு முறை generate பண்ணினதும் நம்பிவிட முடியாது. Especially LLM output non-deterministic.

**What goes wrong if we don't have this?**
Bad output production-க்கு போகும். Reviewer கண்டுபிடிச்சு திரும்ப அனுப்புவார். Cost அதிகரிக்கும். Trust குறையும்.

## 2. Mental Model

Critic என்பது ஒரு separate evaluator.

அது generator-ன் output-ஐ பார்த்து judge பண்ணும். Good/Bad என்று சொல்லும். Why bad என்று explain பண்ணும். Sometimes fix suggestions தரும்.

மனித workflow-ல ஒருவர் write பண்ணுவார், இன்னொருவர் review பண்ணுவார். அதே pattern.

Critic pattern = **generate → critique → improve / reject**

## 3. How It Works

Simple loop:

1. **Generator** task-ஐ செய்து output தரும்.
2. **Critic** அந்த output-ஐ input ஆக எடுத்து rubric-படி evaluate பண்ணும்.
3. Pass ஆனால் output release.
4. Fail ஆனால் feedback-ஐ generator-க்கு திருப்பி அனுப்பும். Re-generate.

Critic can be:

* **Self-critic**: Same LLM model, different prompt with critic role
* **Separate model**: Smaller cheaper model for validation, or stronger model for quality gate
* **Rule-based critic**: Regex, schema validation, unit tests
* **Human-in-the-loop critic**: Final approval

## 4. Architectural Reasoning

எப்போது useful?

* Output quality critical: financial advice, code generation, legal summary
* Hallucination risk அதிகம்
* Output-க்கு clear criteria உண்டு: format, factuality, safety, style
* Cost of bad output > cost of extra LLM call

Alternatives:

* **Better prompt only**: Simple but brittle. No feedback loop.
* **RAG + grounding**: Helps factuality, but doesn't evaluate style/coherence.
* **Multi-agent debate**: Heavy. Critic is lighter.

Architect ஏன் choose பண்ணுவார்? Because you want **quality gate without human bottleneck**.

Constraint solve பண்ணும்: reliability and trust.

## 5. Trade-offs

**Latency**: Generate + Critique = 2x calls. Real-time chat-ல problem.

**Cost**: Extra LLM inference. Critic model-ஐ smaller model-ஆக run பண்ணி குறைக்கலாம்.

**False positives/negatives**: Critic itself can be wrong. Overly strict critic = infinite loop. Too lenient = useless.

**Loop control**: எத்தனை முறை retry? Max iterations வைக்க வேண்டும். இல்லைன்னா cost blow up.

**Feedback quality**: Critic சொல்லும் "bad" என்பது உதவாது. Actionable reason வேண்டும்.

## 6. Practical Example

RAG agent ஒரு customer support answer generate பண்ணுது.

Generator: "உங்கள் refund 3 days-ல வரும்" என்று சொல்லுது.

Critic prompt: 
> "இந்த answer-ஐ evaluate பண்ணு. Criteria: 1) Factual grounded in retrieved docs? 2) No hallucinated timeline? 3) Tone polite? Output JSON with pass/fail and reason."

Critic finds: retrieved doc says refund 5-7 business days. Hallucination detected.

Feedback: "Timeline mismatch. Use doc value 5-7 days."

Generator re-writes. Second pass passes.

Production-ல இது bad advice போவதை தடுக்கும்.

## 7. Reasoning Challenge

உங்களிடம் code generation agent உள்ளது. அது 100 functions per day generate பண்ணும். உங்களுக்கு correctness முக்கியம். Unit tests எழுதி run பண்ண 2 seconds ஆகும். LLM critic பண்ண 1 second ஆகும்.

நீங்கள் Critic-ஐ எப்படி design பண்ணுவீர்கள்? LLM critic மட்டும் போதுமா? அல்லது test runner-ஐ critic ஆக use பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* Critic pattern என்பது generate-க்கு பிறகு explicit quality check. Trust கூட்டும்.
* Critic should be fast, cheap, and give actionable feedback, இல்லைன்னா loop waste.
* Every retry adds latency and cost. Max iterations and fallback வேண்டும்.
* Best setup: Rule-based critic first, then LLM critic for nuanced judgment.
