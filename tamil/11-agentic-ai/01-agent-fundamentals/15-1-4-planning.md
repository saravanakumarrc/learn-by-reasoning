# Planning

> **Learning Path:** Agentic AI
> **Section:** 15.1.4 — Agent fundamentals

## 1. Problem

ஒரு simple chatbot க்கு user கேள்வி வந்தா, அது direct ஆக LLM-ல கொடுத்து answer திருப்பி அனுப்பும். அது fine.

ஆனா ஒரு real agent use case ல user சொல்றது:
> "என் கடந்த 3 மாத விற்பனை data-வை எடுத்து, top 5 products-ஐ கண்டுபிடி, அதுக்கு discount plan ஒன்னு உருவாக்கு, அதை sales team-க்கு email அனுப்பு."

இது ஒரே step இல்ல. இது multi-step.

இங்க என்ன problem வரும்?
* எந்த step முதல்? எந்த data source-க்கு போகணும்?
* முந்தைய step output அடுத்த step input ஆக வேணும்.
* தவறு நடந்தா எங்க retry பண்ணணும்?
* Plan மாற வேண்டியிருந்தால்?

ReAct agent இல்லாமல், இதை ஒரே prompt-ல செய்ய முயற்சித்தால் LLM hallucinate பண்ணும், tool call சரியா order பண்ணாது, context கரைஞ்சு போகும்.

**Planning என்பது ஒரு agent-க்கு "என்ன செய்யணும், எந்த வரிசையில் செய்யணும், எப்போ stop பண்ணணும்" என்பதை தீர்மானிக்கும் திறன்.**

## 2. Mental Model

Planning என்பது to-do list உருவாக்குவது மட்டும் இல்ல.

அது ஒரு **constraint-aware search** .

Agent கிட்ட ஒரு goal இருக்கு, அதை அடைய பல possible action paths இருக்கு. Planning என்பது அதில் feasible, efficient, safe ஆன path-ஐ தேர்ந்தெடுப்பது.

Analogy: ஒரு experienced project manager க்கு task வந்தால், அவர் முதலில் dependencies பார்ப்பார், எது parallel பண்ணலாம், எது risky என்பதை முடிவு செய்வார். Agent-க்கும் அதே reasoning தேவை.

## 3. How It Works

பெரும்பாலும் planning 2 வழியில் நடக்கும்:

**a) LLM-based plan generation**
Goal input ஆக வரும். LLM ஒரு high-level plan உருவாக்கும்:
1. fetch sales data
2. aggregate by product
3. rank top 5
4. generate discount plan
5. send email

இது natural language plan அல்லது structured JSON steps.

**b) Planner-Executor loop**
Planner ஒரு step-ஐ தீர்மானிக்கும், Executor tool-ஐ கூப்பிடும், observation திரும்ப வரும். Planner அடுத்த step-ஐ revise பண்ணும்.

முக்கியமான concept: **plan is not static**. Observation வந்ததும் plan re-plan ஆகணும். இதுதான் ReAct / Thought-Action-Observation loop.

Planning-க்கு தேவையான context: current state, available tools, constraints like cost/latency, previous failures.

## 4. Architectural Reasoning

Planning useful ஆகும்போது?

* Task multi-step, tool use தேவைப்படும் போது.
* Tools-க்கு dependencies இருக்கும் போது.
* Error handling & retry தேவைப்படும் போது.
* Goal ambiguous ஆக இருந்து clarification தேவைப்படும் போது.

Alternatives:
* **Fixed workflow / hard-coded chain**: எல்லா steps முன்னாடியே தெரிந்தால். Simple, deterministic, but brittle.
* **Pure reactive agent**: ஒவ்வொரு observation-க்கும் immediate next action. No lookahead. Simple but inefficient.
* **Hierarchical planning**: High-level planner sub-agents-க்கு sub-goals கொடுக்கும். Complex domain-க்கு scalable.

Architect choose planning when flexibility > predictability, and task complexity grows over time.

## 5. Trade-offs

**Plan quality vs latency**: Detailed planning செய்ய long chain-of-thought வேணும், அது cost மற்றும் latency அதிகரிக்கும். Over-planning பண்ணி time waste.

**Plan stability vs adaptability**: Static plan deterministic ஆக இருக்கும் ஆனா environment மாறினால் fail. Dynamic re-planning robust ஆனா non-deterministic.

**Centralized planner vs distributed**: Single planner simple ஆனா bottleneck. Multiple planners scale ஆனா coordination complex.

Failure modes:
* Hallucinated steps / non-existent tools
* Infinite loops - goal reached என்பதை detect பண்ணாமல்
* Context loss - long plan-ல intermediate results மறந்துவிடும்
* Over-reliance on plan - observation contradict பண்ணினாலும் plan-ஐ stick பண்ணும்

## 6. Practical Example

Enterprise support agent.

Goal: "Customer ticket #12345-ஐ resolve பண்ணு"

Available tools: fetch ticket, query CRM, check subscription, refund tool, send email, escalate.

Good planning:
1. fetch ticket → customer context தெரியும்
2. query CRM → account health
3. if billing issue → check subscription, then decide refund vs credit
4. if technical issue → pull logs, suggest fix
5. send summary email
6. close ticket

If step 2-ல account not found, planner should re-plan to ask clarification instead of blindly proceeding.

இங்க planning இல்லாமல் agent direct refund பண்ணினால் security issue.

## 7. Reasoning Challenge

உங்களிடம் ஒரு travel booking agent இருக்கு. User சொல்றார்: "Chennai to Delhi weekend trip plan பண்ணு, budget under 15k".

Available tools: flight search, hotel search, train search, weather check.

Constraints: user wants cheapest option, but flight delay risk குறைவா இருக்கணும்.

நீங்கள் planner ஆக இருந்தால், முதல் step என்ன? Flight, train, hotel எந்த order-ல plan பண்ணுவீர்கள்? Weather check எப்போ செய்வீர்கள்? ஏன்?

## 8. Key Takeaways

* Planning என்பது goal-ஐ steps ஆக break பண்ணுவது மட்டும் இல்ல, constraints மற்றும் observations-ஐ கொண்டு plan-ஐ revise பண்ணும் திறன்.
* Agent architecture-ல plan என்பது reasoning artifact, deterministic code அல்ல.
* Good planning reduces tool calls, avoids hallucination, improves reliability.
* Every planning strategy adds latency and cost, choose based on task complexity and failure tolerance.
