# PARTIAL — Model capabilities

> Generation was not accepted as complete.
> Reason: Ollama reported done_reason=length

## 1. Problem

உங்களுக்கு ஒரு LLM கிடைத்துவிட்டது. அதை வைத்து agent பண்ணலாம், RAG பண்ணலாம், summarization பண்ணலாம் என்று நினைக்கிறீர்கள்.

ஆனால் உண்மையில் என்ன நடக்கிறது?

ஒரு நாள் model சரியாக structured JSON extract பண்ணும். அடுத்த நாள் அதே prompt-க்கு hallucination பண்ணி fake fields கொடுக்கும். சில requests-ல் reasoning நல்லா இருக்கும், சிலவற்றில் chain-of-thought முற்றிலும் தவறாக போகும்.

**Problem என்ன?** Model-ஐ deterministic function போல நடத்துகிறோம், ஆனால் அது probabilistic system.

ஒரு engineer-க்கு தேவை: *இந்த model இந்த task-ஐ எந்த confidence-ல் செய்யும்? எப்போது fail ஆகும்?* என்பதை தெரிந்து அதற்கேற்ப architecture போட வேண்டும்.

## 2. Mental Model

Model capabilities என்பது ஒரு fixed spec அல்ல. அது **three dimensions-ல் மாறும்**:

1. **What it can recall vs reason.** Training data-ல் இருந்ததை retrieve பண்ணுவது வேறு, புது problem-ஐ step-by-step reason பண்ணுவது வேறு.
2. **Context capacity.** Context window size, token limit, attention decay. நீளமான conversation-ல் முன்னாடி கொடுத்த instruction மறந்துவிடும்.
3. **Reliability under distribution shift.** Seen distribution-ல் நல்லா வேலை செய்யும், ஆனால் edge case, ambiguous input, adversarial prompt-ல் விழுந்துவிடும்.

எளிய analogy: படித்த இன்டர்ன், ஞாபகம் அதிகம், ஆனால் grounding இல்லை. சொன்னதை repeat பண்ணுவான், ஆனால் சரி தவறு என்று தெரியாது.

## 3. How It Works

Model capability பெரும்பாலும் இதைப் பொறுத்தது:

* **Base pre-training + fine-tuning.** General language understanding, instruction following, tool use pattern.
* **Context window and prompt design.** Few-shot examples, system prompt quality, formatting constraints மாற்றினால் performance மாறும்.
* **Inference time compute.** Temperature, top-p, max tokens, chain-of-thought prompting. அதிக reasoning steps கொடுத்தால் சில task-ல் துல்லியம் அதிகரிக்கும், latency கூடும்.
* **External grounding.** RAG, tools, function calling வைத்தால் knowledge cutoff மற்றும் hallucination குறையும்.

இதை benchmark score-ஆல் மட்டும் அளவிட முடியாது. Production traffic pattern-ல் தான் உண்மையான capability தெரியும்.

## 4. Architectural Reasoning

Model capability-ஐ புரிந்து கொள்வது architect-க்கு முக்கியம் ஏனெனில் அது **system boundary-ஐ define பண்ணும்**.

* Model-ஐ நம்பி business critical decision எடுக்கலாமா? இல்லை என்றால் human-in-the-loop வேண்டும்.
* Parsing, classification போன்ற structured task-க்கு model + validation layer தேவை.
* Long reasoning task-க்கு model-ஐ multiple rounds-ல் பிரித்து, tool use மூலம் intermediate state-ஐ externalize பண்ண வேண்டும்.

Alternative: Small deterministic rules vs large LLM. சில task-ல் regex + classifier போதும். LLM-ஐ overuse பண்ணினால் cost, latency, unpredictability அதிகரிக்கும்.

Decision rule: **Model-ஐ மட்டும் நம்பாதீர்கள், model-ஐ ஒரு component ஆக treat பண்ணி அதன் failure mode-க்கு guardrail போடுங்கள்.**

## 5. Trade-offs

* **Capability vs Cost & Latency.** Larger model = better reasoning, ஆனால் higher cost per token, higher latency. Production-ல் 95th percentile latency முக்கியம்.
* **Generality vs Reliability.** General instruction following எளிது, deterministic output consistency கடினம். Same prompt-க்கு மாறுபட்ட output வரும்.
* **Autonomy vs Safety.** Agent-க்கு tool access கொடுத்தால் capability அதிகரிக்கும், ஆனால் incorrect tool call, infinite loop, hallucinated parameters போன்ற failure modes வரும்.
* **Context length vs Attention quality.** Window அதிகரித்தால் முழு conversation-ஐ பிடிக்கலாம், ஆனால் middle part-ல் information loss ஆகும்.

Important failure modes: hallucination, instruction drift, prompt injection, context overflow, inconsistent formatting.

## 6. Practical Example

Enterprise support chatbot.

Requirement: Internal KB-ல் இருந்து answer கொடுக்க வேண்டும், ticket classification பண்ண வேண்டும்.

Capability analysis:
Model alone knowledge cutoff-க்கு அப்பால் உள்ள internal policy-ஐ தெரியாது. அதனால் RAG mandatory.
Classification task simple, ஆனால் model sometimes invent new categories. அதனால் output-ஐ enum-ல் restrict பண்ணி validation layer வைக்கிறோம்.
Reasoning for escalation: model confidently wrong ஆகும். அதனால் confidence score + low confidence-ல் human review queue.

Architecture: User query → Retrieval
