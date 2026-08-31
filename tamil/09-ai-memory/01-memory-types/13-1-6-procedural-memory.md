# Procedural memory

> **Learning Path:** AI Memory
> **Section:** 13.1.6 — Memory types

## 1. Problem

ஒரு LLM-ஐ ஒரு agent ஆக run பண்ணும்போது என்ன பிரச்சனை வரும்? 

RAG இல்லைனா, model-க்கு வெளியே இருக்கும் knowledge எல்லாம் தெரியாது. Long conversation-ல user என்ன சொன்னான்னு forget ஆகும். Tool use பண்ணணும், ஆனா எந்த tool, எப்போ call பண்ணணும், எந்த parameter கொடுக்கணும் என்பது மாறிக்கிட்டே இருக்கும்.

இன்னும் painful ஆனது: model-க்கு ஒரு skill-ஐ ஒரே மாதிரி செய்ய சொல்லிக் கொடுக்கணும். எடுத்துக்காட்டாக, ஒவ்வொரு முறை "என்னுடைய weekly sales report-ஐ Slack-ல அனுப்பு"ன்னு சொன்னா, ஒவ்வொரு முறையும் steps ஞாபகம் வைத்து reasoning பண்ண வேண்டியிருக்கு. 

இது expensive, slow, மற்றும் inconsistent. ஏன்னா LLM தன் context window-க்குள் மட்டுமே remember பண்ணும். Procedural knowledge - *எப்படி செய்யணும்* - ஐ எப்படி persistent ஆக, reliable ஆக வைக்கிறது?

## 2. Mental Model

Memory types ஐ ஒரு engineer க்கு புரிய வைக்க, நமக்கு தெரிந்த human memory-ஐ use பண்ணலாம்.

* **Episodic memory**: என்ன நடந்தது. "நேற்று user X என்ன கேட்டான்."
* **Semantic memory**: என்ன தெரியும். "Interest rate என்ன?"
* **Procedural memory**: எப்படி செய்யணும். "Git merge conflict solve பண்ணும் steps."

Procedural memory என்பது *skills and habits*. இது explicit recall இல்லாமல், automatic ஆக run ஆகும். நீங்கள் cycle பைக் ஓட்ட கற்றுக்கொண்டதும், ஒவ்வொரு முறையும் physics யோசிக்க மாட்டீர்கள்.

AI system-ல, procedural memory = *reusable, step-by-step behavior* ஐ store பண்ணி, எப்போது தேவைப்படுகிறதோ அப்போது invoke பண்ணுவது.

## 3. How It Works

Procedural memory-ஐ implement பண்ண மூன்று common patterns உள்ளன.

**1. Tool / Function Schema as Procedure**
Agent framework-ல ஒரு tool define பண்ணுவது procedural memory-ன் முதல் layer. `get_sales_report(week_start, region)` என்பது ஒரு procedure. Model-க்கு tool description கொடுக்கப்படும், அது எப்போது use பண்ணணும் என்பதை learn பண்ணும்.

**2. Few-shot / Prompted workflow**
ஒரு task-க்கான successful trajectory ஐ examples ஆக store பண்ணி, next time prompt-ல சேர்ப்பது. இது in-context procedural memory. Cheap, ஆனால் context window limited.

**3. Explicit workflow store**
Procedures ஐ structured format-ல external memory-ல வைத்துக்கொள்வது. எடுத்துக்காட்டாக:
* A workflow graph / state machine: nodes = steps, edges = conditions
* A library of reusable agents / skills: `OnboardingSkill`, `RefundSkill`
* Fine-tuned model or LoRA adapter per skill

Agent-க்கு task வரும்போது, retriever procedure name-ஐ match பண்ணி, அந்த procedure-ஐ load பண்ணி execute பண்ணும். இது RAG for procedures.

முக்கியம்: Procedural memory-க்கு *parameters* தேவை. Procedure static இல்லை, dynamic context-ஐ bind பண்ணணும்.

## 4. Architectural Reasoning

எப்போது procedural memory தேவை?

* Repeated multi-step tasks with same pattern, but different data.
* Low latency தேவை, full reasoning ஒவ்வொரு முறையும் செய்ய முடியாது.
* Consistency தேவை. Human operator error குறைக்க.
* Auditability & control தேவை. Business process compliance.

Alternatives:
* Pure LLM in-context reasoning: flexible, ஆனால் non-deterministic, expensive, மற்றும் forgetful.
* Hard-coded business logic in code: deterministic, fast, ஆனால் change கடினம், LLM flexibility இல்லை.
* Procedural memory = middle ground. Code-like reliability + LLM-like flexibility.

Architect choose procedural memory when *how* is stable but *what* is variable.

## 5. Trade-offs

**Consistency vs Flexibility**
Procedural memory gives repeatable steps. ஆனால் edge cases-ல rigid ஆகிவிடும். Model-க்கு override permission கொடுக்க வேண்டுமா?

**Retrieval Accuracy vs Latency**
Procedure-ஐ vector DB-ல store பண்ணி retrieve பண்ணுவது slow ஆகலாம். Cache பண்ணினால் stale ஆகலாம்.

**Maintenance Burden**
Procedures version manage பண்ண வேண்டும். ஒரு process மாறினால், எல்லா agents-க்கும் update போக வேண்டும். இது operational complexity.

**Failure Mode**: Wrong procedure retrieval. Model-க்கு ஒத்த procedure வந்துவிட்டால் hallucination போல் தவறான workflow run ஆகும். அதனால் procedure selection-க்கு guardrails தேவை.

Cost: In-context procedural memory cheap but context heavy. External store + retrieval cost + latency add ஆகும்.

## 6. Practical Example

Enterprise support agent.

User: "Customer ID 12345-க்கு last month refund செய்யணும்."

எபிசோடிக் memory: customer chat history.
செமாண்டிக் memory: refund policy.
Procedural memory: `process_refund` workflow.

Procedure steps stored externally:
1. verify_customer_exists
2. check_refund_eligibility
3. calculate_amount
4. get_manager_approval_if > $500
5. create_refund_ticket
6. notify_customer

Agent task planner procedure-ஐ retrieve பண்ணி, each step-க்கு relevant tool-ஐ call பண்ணும். Steps fixed, data dynamic.

இது ஒவ்வொரு முறையும் model-க்கு "எப்படி refund செய்யணும்" என்று யோசிக்க விடாமல், guaranteed path-ல run ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 20 different customer onboarding flows இருக்கு. ஒவ்வொன்றும் 10-15 steps. Flows மாதத்திற்கு ஒரு முறை மாறுகின்றன. Agent ஒவ்வொரு flow-ஐயும் துல்லியமாக follow பண்ண வேண்டும், ஆனால் user inputs dynamic.

நீங்கள் procedural memory-ஐ எப்படி design பண்ணுவீர்கள்? In-context examples, vector store, இல்லை code-based state machine? ஏன்? அதன் trade-off என்ன?

## 8. Key Takeaways

* Procedural memory = *how to do it*, not *what happened* or *what is known*.
* LLM context window alone is not procedural memory. Persistence + retrieval தேவை.
* Procedures give consistency and cost saving, ஆனால் maintenance and rigidity கொண்டு வரும்.
* Architecturally, procedural memory is a bridge between rigid code logic and free-form LLM reasoning.
