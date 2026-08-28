# Output constraints

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.8 — Prompt engineering

## 1. Problem

நீங்கள் ஒரு LLM-ஐ production API-யாக வைத்திருக்கிறீர்கள். ஒரு user chat input கொடுக்கிறார், model பதில் தருகிறது. 

இப்போது நடக்கும் பிரச்சனைகள்:
- சில responses மிக நீளமாக வந்து token cost விழுங்குகிறது
- சில responses JSON format-ல் இல்லாமல் free text ஆக வருகிறது, downstream parser fail ஆகிறது
- சில responses user context-க்கு தொடர்பில்லாமல் hallucinate செய்கிறது
- latency அதிகமாகிறது, user வெயிட் பண்ண மாட்டார்
- PII / sensitive data திரும்ப வருகிறது

Prompt-ஐ மட்டும் மாற்றினால் போதாது. Model-க்கு **என்ன output எதிர்பார்க்கிறோம்** என்பதை சொல்லும் வழிமுறை வேண்டும். அதுதான் output constraints.

## 2. Mental Model

Output constraints என்பது LLM-க்கு ஒரு **output contract** கொடுப்பது.

ஒரு API contract போல நினைத்துக்கொள்ளுங்கள்: input என்ன வரும், output எப்படி இருக்க வேண்டும், format என்ன, length எவ்வளவு, என்ன மறுக்க வேண்டும்.

Model ஒரு creative writer அல்ல, அது ஒரு unreliable worker. அதற்கு guardrails வைக்காவிட்டால் அது தன் இஷ்டத்திற்கு எழுதும்.

## 3. How It Works

Constraints-ஐ நீங்கள் 3 இடங்களில் வைக்கலாம்:

**a. Prompt level:** System / user prompt-ல் explicit instructions.
> "Respond in JSON only with keys: intent, entities. Max 200 words. Do not add explanation."

**b. Structured output schema:** Model-க்கு schema கொடுத்து force பண்ணுவது.
LLM providers இப்போது JSON Schema, Pydantic, function calling மூலம் output-ஐ validate செய்கிறார்கள். Model output-ஐ parse பண்ண முயற்சிக்கிறது, fail ஆனால் retry.

**c. Post-processing guardrails:** Output வந்த பிறகு validate செய்து reject / re-prompt செய்வது.
Regex check, JSON schema validation, length check, toxicity / PII filter.

Effective system என்பது prompt constraint + schema enforcement + post validation கலவையாக இருக்கும்.

## 4. Architectural Reasoning

எப்போது இது தேவை?

- Downstream system deterministic parsing எதிர்பார்க்கும்போது: RAG pipeline, agent tool calling, form filling
- Cost control தேவைப்படும்போது: token usage cap, max output tokens
- Compliance தேவைப்படும்போது: no PII, no disallowed content
- UX consistency தேவைப்படும்போது: tone, length, language

Alternatives:
- முழுக்க prompt engineering மட்டும் -> fragile, model drift ஆனால் break ஆகும்
- முழுக்க post-processing -> wasteful, model wasted tokens
- Fine-tuning -> expensive, slow to update

ஆர்கிடெக்ட் தேர்வு: **Constraint as code**. Prompt-ல் intent சொல்லுங்கள், schema-வில் structure enforce செய்யுங்கள், validator-ல் safety enforce செய்யுங்கள்.

## 5. Trade-offs

**Structure vs Creativity:** கடுமையான schema வைத்தால் output predictable ஆகும், ஆனால் nuanced answers குறையும். Balance தேவை.

**Latency vs Reliability:** Schema validation + retry செய்தால் latency அதிகரிக்கும். First-pass accuracy முக்கியம்.

**Cost vs Control:** Max tokens, short output என்று கட்டுப்படுத்தினால் cost குறையும், ஆனால் complex tasks-ல் quality drop ஆகும்.

**False positives:** Over-constrained prompt model-ஐ overly conservative ஆக்கும். "I cannot comply" என்று அடிக்கடி சொல்ல ஆரம்பிக்கும்.

Failure mode: Model schema-வை follow பண்ணாமல் escape செய்யும். அதனால் **always validate output, never trust model**.

## 6. Practical Example

உங்களுக்கு customer support agent இருக்கிறது. User query வந்தால், agent ticket classification செய்ய வேண்டும்.

Bad prompt:
> "Classify the ticket"

Output: free text, inconsistent.

Constrained design:
System prompt: "You are a classifier. Output ONLY valid JSON. No extra text."
User prompt: Query + 
```
{
  "intent": "refund|billing|technical|other",
  "priority": "low|medium|high",
  "entities": {"order_id": "..."}
}
```
Schema enforced via structured output. Post validator checks intent enum valid, order_id regex match.

Result: downstream routing service JSON parse பண்ணி நேரடியாக ticket create செய்யலாம். Cost predictable ஆகிறது. Error rate குறைகிறது.

## 7. Reasoning Challenge

உங்களிடம் financial advice chatbot உள்ளது. User கேட்கிறார்: "என் portfolio-வை எப்படி diversify பண்ணுவது?"

நீங்கள் output-ஐ constrain செய்ய வேண்டும்:
- General info மட்டும் கொடுக்க வேண்டும், personalized advice கொடுக்கக்கூடாது
- Disclaimer கண்டிப்பாக சேர்க்க வேண்டும்
- Max 250 words
- Bullet points-ல் மட்டும்

இந்த constraints-ஐ எப்படி prompt + schema + validation-ல் பிரித்து implement செய்வீர்கள்? எந்த constraint-ஐ எங்கே வைப்பீர்கள், ஏன்?

## 8. Key Takeaways

- Output constraints என்பது reliability மற்றும் cost control-க்கான architectural guardrail
- Prompt instruction மட்டும் போதாது, schema enforcement + post validation தேவை
- Constraint every time creates trade-off between creativity, latency, and control
- Never trust LLM output. Validate as you would validate any external API response
