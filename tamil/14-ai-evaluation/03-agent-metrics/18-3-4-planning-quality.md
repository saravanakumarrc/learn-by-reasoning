# Planning quality

> **Learning Path:** AI Evaluation
> **Section:** 18.3.4 — Agent metrics

## 1. Problem

ஒரு agent-ஐ deploy பண்ணினீங்க. Task செய்து முடிக்குது. Success rate நல்லா இருக்கு. ஆனால் production-ல production team complain பண்ணுது: "Agent ரொம்ப steps எடுக்குது, cost அதிகம், சில சமயம் loop-ல சுத்துது, plan பண்ணும்போதே தப்பா start பண்ணுது."

இங்கே என்ன missing? Correctness மட்டும் போதாது. **Agent எப்படி think பண்ணுது, எவ்வளவு efficiently plan பண்ணுது** என்பது முக்கியம்.

ஒரு agent metrics-ல planning quality என்பது: Agent ஒரு goal-க்கு ஒரு plan உருவாக்கும் திறன், அந்த plan valid ஆக இருக்கிறதா, minimal ஆக இருக்கிறதா, unnecessary steps இல்லாமல் இருக்கிறதா என்பதை measure பண்ணுவது.

## 2. Mental Model

Planning quality = **Plan correctness + Plan efficiency + Plan robustness**

Correctness: Plan-ல steps logical ஆகவும், goal-ஐ achieve பண்ணும் வகையிலும் இருக்கிறதா?
Efficiency: தேவையான steps மட்டும் இருக்கிறதா? Redundant actions, backtracking குறைவா?
Robustness: Environment மாறினாலும் plan adapt ஆகுமா? Wrong assumption-ல தொடங்காமல் இருக்கிறதா?

ஒரு human planner-க்கு ஒப்பிடுங்கள். நல்ல planner ஒரே முறையில் destination-க்கு செல்லும் route-ஐ தேர்வு செய்வார், traffic இல்லாத சாலையில் போவார், தேவையில்லாத U-turn எடுக்க மாட்டார். Agent-க்கும் அதே.

## 3. How It Works

Planning quality-ஐ measure பண்ண evaluation-ல ஒரு task-ஐ ground truth plan-உடன் ஒப்பிட்டு பார்க்கிறோம், அல்லது agent-ன் generated plan-ன் properties-ஐ inspect பண்ணுகிறோம்.

பொதுவாக பயன்படுத்தும் signals:

* **Plan validity**: Steps ஒவ்வொன்றும் preconditions satisfy பண்ணுதா? Tool call syntax சரியா? Dependency order சரியா?
* **Plan completeness**: Goal-ஐ achieve பண்ண தேவையான எல்லா steps இருக்கிறதா? Missing critical step உண்டா?
* **Redundancy / Suboptimality**: தேவையில்லாத steps, repeated calls, loop இருக்கிறதா? Optimal step count-க்கு எவ்வளவு அருகில்?
* **Consistency**: Same task-க்கு multiple runs-ல plan ஒத்திருக்கிறதா? அல்லது random ஆக மாறுகிறதா?
* **Plan adaptability**: Intermediate failure வந்தால் plan revise பண்ண முடிகிறதா?

இவை எல்லாம் LLM-based judge, rule-based checker, or human evaluation-ல measure பண்ணலாம்.

## 4. Architectural Reasoning

எப்போது இது useful?

* **Agent cost அதிகம்** என்றால்: Every extra step = extra LLM call + tool call + latency. Planning quality குறைவு என்றால் cost blow up ஆகும்.
* **Reliability தேவை**: Financial, healthcare workflow-ல wrong plan = irreversible action.
* **Tool usage கட்டுப்பாடு**: Agent-க்கு limited API quota இருக்கும் போது, efficient plan தேவை.

Alternatives:

* Only measure final outcome success. இது cheap ஆனால், agent lucky ஆக correct result-க்கு வந்தாலும் inefficient plan-ஐ catch பண்ணாது.
* Measure step count மட்டும். இது efficiency-ஐ காட்டும் ஆனால் correctness-ஐ காட்டாது.

Architect decision: Planning quality-ஐ track பண்ணுவது, agent prompt, planning module, tool selection strategy improve பண்ண உதவும். Planning quality மோசமாக இருந்தால், fine-tune planning prompt, add constraint checker, use planner-critic loop.

## 5. Trade-offs

* **Validity vs Creativity**: Strict validation plan-ஐ safe ஆக்கும் ஆனால் novel solutions-ஐ block பண்ணும்.
* **Efficiency vs Exploration**: Agent short plan-ஐ force பண்ணினால், சில சமயம் critical step miss ஆகும். Better to explore then prune.
* **Automated evaluation cost**: Planning quality-ஐ judge பண்ண LLM judge வேண்டும். அதுவே expensive. Rule-based checker cheap ஆனால் limited.
* **Granularity**: Plan level-ல measure பண்ணினால் understanding அதிகம், ஆனால் implementation complex. Task level success மட்டும் simple.

Failure mode: Agent plan looks valid ஆனால் hidden assumption உள்ளது. உதாரணமாக database idempotent இல்லை என்று assume பண்ணி plan போட்டு, retry பண்ணும்போது duplicate data create ஆகும்.

## 6. Practical Example

Enterprise RAG agent: User கேட்கிறார் "Last quarter top 5 customers by revenue, and send summary email to sales head."

Good plan:
1. Identify quarter dates
2. Query revenue table for last quarter
3. Aggregate by customer, top 5
4. Fetch customer contact details
5. Generate summary
6. Send email via tool

Poor planning quality agent:
1. Query revenue table without date filter
2. Query again with different filter
3. Fetch all customers
4. Try to send email before summary ready
5. Loop back to query again

இரண்டும் final success ஆகலாம், ஆனால் second plan-ல 2x tool calls, latency அதிகம், rate limit risk. Planning quality metric இதை catch பண்ணும்: step redundancy high, order violation உள்ளது.

## 7. Reasoning Challenge

உங்கள் agent-க்கு task: "Create a new project in Jira, add 3 tasks, assign to team, and post summary in Slack."

Agent-ன் two runs:

Run A: 12 steps, 2 backtracks, plan contains 1 invalid tool call, finally succeeds.
Run B: 7 steps, 0 backtracks, plan valid, succeeds.

Success rate same. நீங்கள் production-க்கு எந்த run-ன் planning behavior-ஐ target பண்ணுவீர்கள்? Cost, latency, reliability ஆகியவற்றை கருத்தில் கொண்டு ஏன் planning quality-ஐ improve பண்ண வேண்டும் என்று reason பண்ணுங்கள்.

## 8. Key Takeaways

* Planning quality என்பது agent correct ஆக முடிக்கிறதா என்பதை மட்டும் அல்ல, **எப்படி முடிக்கிறது** என்பதையும் measure பண்ணும்.
* Good planning = valid steps + minimal steps + correct order + robustness to failures.
* Final success மட்டும் track பண்ணுவது inefficient மற்றும் costly agents-ஐ hide பண்ணும்.
* Planning quality metrics-ஐ track பண்ணாமல், prompt improvement மற்றும் cost control செய்ய முடியாது.
