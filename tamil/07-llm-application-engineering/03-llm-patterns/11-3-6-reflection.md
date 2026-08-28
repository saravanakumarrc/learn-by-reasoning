# Reflection

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.6 — LLM patterns

## 1. Problem

ஒரு LLM agent ஒரு task-ஐ செய்யும்போது, முதல் முயற்சியிலேயே சரியாக வருமா?

நிஜத்தில் வராது. 

உதாரணமாக, ஒரு customer support agent-க்கு "இந்த order-ஐ cancel பண்ணி refund கொடு"ன்னு சொன்னா. LLM தானாக:

* order ID-ஐ தவறாக புரிந்துகொள்ளலாம்
* policy check-ஐ skip பண்ணிடலாம்
* refund amount-ஐ தவறாக கணக்கிடலாம்

இப்போ என்ன பண்ணுவது? Agent-ஐ human review-க்கு அனுப்பினால் cost அதிகம். மீண்டும் மீண்டும் try பண்ணினால் hallucination அதிகரிக்கும்.

இந்த தவறுகளை agent-ஐ தானே கண்டுபிடித்து சரி செய்ய வைக்க முடிந்தால் என்ன? அதுதான் Reflection pattern.

## 2. Mental Model

Reflection = **உன் output-ஐ நீயே ஒரு critic போல review பண்ணு, தவறு இருந்தா சரி பண்ணு.**

இது human-ல நாம எப்படி பண்ணுறோமோ அதே. நீ ஒரு email எழுதினப்புறம், ஒரு நிமிஷம் நிறுத்தி "இது தொனி சரியா? spelling சரியா?"ன்னு பார்ப்பது.

LLM-ல இதை self-critique loop-ஆ மாற்றுறோம். Output generate பண்ணியதும், அதே LLM-ஐ வேற role-ல போட்டு review பண்ண சொல்றோம். Review result-ஐ பார்த்து improve பண்ணுறோம்.

## 3. How It Works

Basic flow:

1. **Generate** - LLM ஒரு initial response / plan / code produce பண்ணும்
2. **Reflect** - அதே response-ஐ review பண்ண, criteria கொடுத்து: correctness, completeness, policy compliance, formatting
3. **Revise** - Reflection-ல கிடைத்த feedback-ஐ பயன்படுத்தி, generate-ஐ மறுபடியும் செய்
4. Loop-ஐ 1-2 times வரை repeat பண்ணலாம்

இது self-contained. External tools தேவையில்லை. பெரும்பாலும் same model-ஐ தான் பயன்படுத்துவோம், ஆனால் different prompt with system role = critic.

உதாரண prompt idea:
> "You are a senior reviewer. Check this output for factual errors, policy violations, and missing steps. Return specific feedback, not rewrite."

பிறகு second prompt:
> "Based on this feedback: [...], rewrite your output to fix the issues."

இது RAG அல்ல. RAG external knowledge-ஐ கொண்டு வரும். Reflection internal consistency-ஐ improve பண்ணும்.

## 4. Architectural Reasoning

Reflection useful ஆகும் போது:

* **Output quality critical**: financial advice, code generation, policy decisions
* **Single-pass error costly**: refund, database update, email to customer
* **No human in loop allowed**: latency குறைக்கணும், cost குறைக்கணும்
* **Evaluation criteria clear**: checklist இருக்கு, ஆனால் model அதை முதலில் follow பண்ணல

Alternatives:

* **Self-consistency**: same prompt-ஐ multiple times run பண்ணி majority vote எடு. Diverse reasoning வேண்டும் என்றால் நல்லது. ஆனால் systematic bias இருந்தால் எல்லா runs-லும் அதே தவறு வரும்.
* **Tool use / validation**: external validator, rule engine, schema check. Strong correctness கிடைக்கும். ஆனால் building cost அதிகம்.
* **Human review**: உச்ச தரம். ஆனால் slow + expensive.

Reflection-ஐ தேர்வு செய்யும் போது architect யோசிக்க வேண்டியது: error pattern systematic-ஆ? அப்படி என்றால் reflection உதவும். Random hallucination என்றால் reflection மட்டும் போதாது, RAG + grounding தேவை.

## 5. Trade-offs

**Quality vs Latency & Cost**
Reflection = additional LLM calls. 1 task-க்கு 2-3x tokens. Latency 2-3x ஆகும். High-stakes tasks-க்கு worth it, high-volume low-stakes chat-க்கு அல்ல.

**Self-improvement limit**
Model தன் தவறை தானே பார்க்க முடியுமா? Weak model-ல reflection superficial ஆகும். "Looks good"ன்னு சொல்லிடும். Stronger model or critic model தேவைப்படலாம்.

**Over-refinement risk**
Loop அதிகம் போனால் model தன் original intent-ஐ மாற்றி over-correct பண்ணும். "Safe" output-க்கு converge பண்ணும். Creativity குறையும்.

**Operational complexity**
Reflection criteria எப்படி define பண்ணுவது? Vague feedback = no improvement. Good checklist design தேவை. Monitoring-ல "how many revisions happened?" என்பதை track பண்ணணும்.

Failure mode: Critic model too lenient → false confidence. Critic model too strict → infinite loop.

## 6. Practical Example

Enterprise RAG assistant, internal policy Q&A.

User: "Employee-க்கு annual bonus எப்படி கணக்கிடுவது?"

First pass LLM output: "Bonus = 10% of salary."

Reflect step: Critic checks against policy checklist.
Feedback: "Missing criteria: tenure >1 year, performance rating >=3, company profit condition. Amount capped at 2 months salary. No citation."

Revise step: LLM outputs improved answer with conditions + citation to policy doc.

இங்கே reflection-ஆல factual completeness வந்தது. RAG இல்லாமலும் policy knowledge model-ல இருந்தால் தவறை catch பண்ண முடியும். RAG உடன் சேர்த்தால் even better.

இது architecturally clean: generate → reflect → revise. No human needed for first-line quality.

## 7. Reasoning Challenge

உங்களிடம் code generation agent இருக்கு. ஒரு API endpoint-க்கு code generate பண்ணுது. 80% cases-ல code compile ஆகும், 20% cases-ல runtime error வருது. Reflection loop சேர்க்கலாமா?

அப்படி செய்தால் cost 2.5x ஆகும். ஆனால் human review-லிருந்து தப்பிக்கலாம்.

நீங்கள் என்ன செய்வீர்கள்? Reflection மட்டும் போதுமா? வேறு என்ன validation layer சேர்ப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Reflection என்பது LLM-ஐ தானே review பண்ணி சரி செய்ய வைக்கும் self-critique loop.
* இது quality-ஐ improve பண்ணும், ஆனால் latency மற்றும் cost-ஐ அதிகரிக்கும்.
* Systematic errors-க்கு வேலை செய்யும், random hallucination-க்கு மட்டும் போதாது.
* Good reflection-க்கு clear evaluation criteria தேவை, vague critic பயனற்றது.
* Reflection + external validation = strong architecture for high-stakes LLM tasks.
