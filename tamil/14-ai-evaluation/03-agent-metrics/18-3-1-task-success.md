# Task success

> **Learning Path:** AI Evaluation
> **Section:** 18.3.1 — Agent metrics

## 1. Problem

ஒரு LLM agent-ஐ production-ல விட்டாச்சு. UI-ல user happy ஆ இருக்காங்க, சிலர் complaint பண்றாங்க.

இப்போ நீங்க கேட்குறீங்க: இந்த agent உண்மையிலேயே வேலையை செய்யுதா?

Accuracy of model பார்த்தால் போதாது. Model token ஐ சரியாக predict பண்ணுதா என்பது வேறு, agent முழு task-ஐ complete பண்ணுதா என்பது வேறு.

ஒரு customer support agent-க்கு user சொல்றார்: "என் last order-ன் status சொல்லு, refund வேண்டும்". Agent chat-ஐ நல்லா பண்ணும், polite ஆ இருக்கும், ஆனால் order ID தப்பா கண்டுபிடிச்சு refund process பண்ணாம விட்டுடும்.

அப்போ என்ன metric வைப்பீங்க? Response quality? Token quality? இல்லை.

**Task success** தான் முக்கியம். User-க்கு தேவையான outcome கிடைச்சுதா?

## 2. Mental Model

Task success = Agent ஒரு well-defined goal-ஐ achieve பண்ணிச்சா இல்லையா.

இது binary அல்ல, graded ஆக இருக்கலாம். Fully done, partial, failed.

ஒரு test-ஐ நினைச்சுக்கோங்க. Exam-ல question கொடுத்தோம், student answer கொடுத்தார். Correct / incorrect என்பது task success. Explanation nice-ஆ இருந்ததா என்பது வேறு metric.

Agent metrics-ல Task success என்பது **outcome-oriented** metric. Process-oriented அல்ல.

## 3. How It Works

Measure பண்ணுவதற்கு மூன்று வழிகள் உண்டு.

**Human judgment**: Real user task-ஐ human evaluator ஆடிட் பண்ணி success/fail மார்க் போடுவது. Gold standard, ஆனால் expensive & slow.

**LLM-as-judge**: Reference answer / expected outcome ஒன்றை உருவாக்கி, agent output-ஐ அதோடு compare பண்ண ஒரு strong LLM-ஐ பயன்படுத்துவது. Cheap & scalable. Bias இருக்கும்.

**Rule-based / programmatic check**: Task objective nature-ல இருந்தால் automated check பண்ணலாம். உதாரணமாக agent-க்கு goal "create a database record with fields X,Y,Z". Record create ஆச்சா? Fields correct ஆ? API call success ஆ? இதை logs-ல verify பண்ணலாம்.

பெரும்பாலும் hybrid பயன்படுத்துவோம். Programmatic checks for tool actions, LLM-as-judge for open-ended reasoning.

## 4. Architectural Reasoning

Task success ஏன் தேவை?

Agent-க்கு multiple steps இருக்கும். Planning, tool calling, reasoning. ஒவ்வொரு step-லயும் model accuracy இருந்தாலும், end-to-end goal fail ஆகலாம்.

எப்போது use பண்ணணும்?
* Agent evaluation pipeline-ல baseline metric ஆக
* Different prompt, tool, model variants compare பண்ண
* Production monitoring-ல regression catch பண்ண

Alternatives:
* **Response quality / helpfulness**: User experience ஐ பார்க்கும், ஆனால் goal completion கிடையாது.
* **Tool call accuracy**: Agent சரியான tool-ஐ call பண்ணுதா என்பது மட்டும். Final outcome-ஐ guarantee பண்ணாது.
* **Latency / cost**: Operability metrics. Success-ஐ பார்க்காது.

Architect தேர்வு: Task success ஐ primary north-star metric ஆக வைத்து, அதை break down பண்ணி sub-metrics ஆக tool success rate, plan adherence பார்ப்பது.

## 5. Trade-offs

**Definition complexity**: Task success என்பது task-க்கு தகுந்த மாதிரி define பண்ணணும். "Book a flight" என்பதில் success = booking confirmed ID கிடைத்ததா? Price within range? Same destination? Definition fuzzy ஆனால் metric meaningless ஆகும்.

**Automation vs fidelity**: LLM-as-judge cheap, ஆனால் judge model bias, prompt sensitivity உண்டு. Human judgment accurate ஆனால் scale ஆகாது.

**Partial success**: Real world-ல full success rare. 70% done but last step fail. Binary metric அப்போ misleading. Partial scoring or success criteria hierarchy தேவை.

**False positive**: Agent சரியான output-ஐ generate பண்ணி, ஆனால் environment change ஆனதால் fail. அதை agent fault என்று சொல்லக்கூடாது.

## 6. Practical Example

Enterprise RAG agent: "Get Q2 revenue for APAC region and email summary to finance@company.com"

Task success evaluate பண்ண:
1. Programmatic check: Email sent? recipient correct? attachment present?
2. Data correctness check: Retrieved revenue number matches ground truth from database? LLM-as-judge with retrieved context compare.
3. Human spot check: 5% samples-ல human verify summary accurate & polite.

இதில் agent நல்ல summary எழுதினாலும், wrong number எடுத்தால் task failed. Agent polite ஆ இருந்தாலும் email wrong person-க்கு போனால் failed.

Metric dashboard-ல Task Success Rate = successful tasks / total tasks. Per task type breakdown வைப்போம்.

## 7. Reasoning Challenge

உங்களிடம் 3 agent variants இருக்கு. Variant A 92% Task Success, avg latency 4s, cost $0.12/task. Variant B 85% Task Success, latency 1.5s, cost $0.04/task. Variant C 78% Task Success, latency 0.8s, cost $0.02/task.

Product is customer support refund agent. SLA says <2s response feels interactive. Cost matters at 1M tasks/month. Which variant தேர்வு செய்வீர்கள்? ஏன்? Task success-ஐ எப்படி define பண்ணுவீங்க?

## 8. Key Takeaways

* Task success என்பது outcome, not output quality. Goal achieve ஆச்சா என்பது மட்டும்.
* Definition clear ஆக இருந்தால் தான் metric useful. Success criteria-ஐ explicit ஆக எழுது.
* Programmatic checks first, LLM-as-judge for semantic parts, human for calibration.
* Every architectural change-ஐ task success-ல impact பார்த்து evaluate பண்ணு, isolated model metrics-ல அல்ல.
