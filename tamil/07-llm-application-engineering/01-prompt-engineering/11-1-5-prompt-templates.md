# Prompt templates

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.5 — Prompt engineering

## 1. Problem

நீங்க ஒரு LLM-ஐ உங்கள் product-ல use பண்ண ஆரம்பிச்சீங்க. முதல் முறை `prompt` கொடுத்தீங்க, output ok வந்தது. இரண்டாவது முறை same user request, வேற output வந்தது. மூன்றாவது முறை hallucination வந்தது.

அடுத்து product team சொன்னாங்க: "Output format JSON-ஆ இருக்கணும், tone formal-ஆ இருக்கணும், brand guidelines follow பண்ணணும், sensitive data reveal பண்ணக்கூடாது."

இப்போ நீங்க எல்லாத்தையும் ஒரு free-form prompt-ல எழுதி கொடுத்தால், ஒவ்வொரு run-க்கும் result மாறும். Developers prompt-ஐ tweak பண்ணிக்கொண்டே இருக்காங்க, QA-க்கு reproduce பண்ண முடியல.

**What goes wrong if we don't have this?** Non-deterministic, inconsistent output, no reusability, prompt drift across services, operational nightmare.

## 2. Mental Model

Prompt template என்பது code-ல function signature மாதிரி.

Function-க்கு input parameters fixed, return type fixed, behavior predictable.

Prompt template-க்கு placeholders fixed, instructions fixed, output format fixed.

நீங்கள் LLM-க்கு ஒரு contract கொடுக்கிறீர்கள். "இதை இப்படி கேளு, இதை இப்படி திருப்பிக் கொடு."

Template என்பது reasoning-ஐ standardize செய்வது, not just text formatting.

## 3. How It Works

Basic template = **Instruction + Context + Input placeholders + Output constraints**

```
You are a {role}. 
Task: {task_description}
Rules:
1. ...
2. ...

Input:
{user_query}

Output format: {format}
```

Real world-ல இது 3 layers-ஆ பிரிக்கப்படும்:

1. **System / Base instruction** - role, tone, do/don't. Rarely changes.
2. **Dynamic variables** - user query, customer data, previous conversation.
3. **Guardrails** - output schema, max length, language, safety checks.

Template engine renders: `template.format(user_input) -> final prompt -> LLM -> parse output`

## 4. Architectural Reasoning

**When it becomes useful?**

* Multiple services same LLM-ஐ use பண்ணும்போது consistency வேண்டும்
* Output-ஐ downstream system-க்கு parse பண்ண வேண்டும் -> schema முக்கியம்
* A/B test பண்ண வேண்டும் -> version control தேவை
* Audit / compliance வேண்டும் -> prompt history track பண்ண வேண்டும்

**What constraint it addresses?** Predictability, maintainability, operability.

Alternatives:
* **Ad-hoc prompts**: fast for prototype, breaks at scale
* **Prompt chaining with agents**: more flexible but complex
* **Fine-tuning**: expensive, slow to iterate

Architect choose template when: requirements stable, output format strict, team size >1, production deployment.

## 5. Trade-offs

**Consistency vs Flexibility**
Template strict ஆக இருந்தால் output consistent ஆகும், ஆனால் creative tasks-ல rigidity வரும். Too loose template = no benefit.

**Reusability vs Context Window Cost**
Common template reuse செய்யலாம், ஆனால் generic instructions context window-ஐ waste செய்யும். Every token cost.

**Versioning complexity**
Prompt-ஐ code மாதிரி version பண்ணினால் good. ஆனால் prompt library grow ஆனால் discoverability, ownership problem வரும்.

**Failure modes**
* Placeholder missing -> LLM hallucinates value
* Instruction conflict -> LLM confused, output degrades
* Template leakage -> internal rules user-க்கு தெரியும்
* Output parsing fail -> downstream error

## 6. Practical Example

Enterprise support chatbot.

Requirement: Customer ticket-ஐ analyze பண்ணி, category, priority, summary, next action திருப்பிக் கொடுக்கணும். Output must be valid JSON.

Template:

```
You are a support triage assistant.
Task: Analyze ticket and return structured data.
Rules:
1. Category must be one of: billing, technical, account, refund
2. Priority: low/medium/high/critical
3. Do NOT reveal internal policy
4. Respond ONLY in JSON

Ticket:
{customer_message}
Customer tier: {tier}

Output format:
{
  "category": "...",
  "priority": "...",
  "summary": "...",
  "next_action": "..."
}
```

இப்போ service A, service B எல்லாம் same template-ஐ call பண்ணும். Output schema fixed ஆக இருப்பதால் parser break ஆகாது. Template version bump பண்ணினால் all services update ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG-based customer FAQ bot இருக்கு. Same template-ஐ use பண்ணி, retail site-க்கும் banking site-க்கும் deploy பண்ணப்போறீங்க.

Retail-ல tone casual, emojis allow, answer in 2 lines.
Banking-ல tone formal, no emojis, compliance disclaimer mandatory.

ஒரே template-ஐ reuse பண்ணலாமா? அல்லது two variants வைக்கலாமா? Template-ல என்ன parameter-ஐ externalize பண்ணுவீங்க?

## 8. Key Takeaways

* Prompt template = LLM contract. Instruction fixed, input variable.
* Template இல்லாமல் production LLM app = prompt drift, inconsistent output, unmaintainable.
* Version template like code. Track changes, test outputs.
* Strict output schema + parsing validation = architectural reliability.
* Every template adds rigidity. Choose strictness based on downstream constraints, not perfection.
