# Debate

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.9 — Learn

## 1. Problem

ஒரு single LLM agent-க்கு ஒரு complex task கொடுத்தால் என்னாகும்? 
அது ஒரே முறை சிந்தித்து பதில் கொடுக்கும். ஆனால் அந்த பதில் hallucination ஆக இருக்கலாம், incomplete ஆக இருக்கலாம், அல்லது bias ஆக இருக்கலாம்.

உதாரணமாக, ஒரு financial decision support agent-க்கு "இந்த startup-க்கு loan approve பண்ணலாமா?" என்று கேட்கிறோம். Agent ஒரே முறை reasoning செய்து ஒரு conclusion கொடுக்கும். அது முக்கியமான risk factor-ஐ miss பண்ணியிருக்கலாம்.

ஒரே மாடல் தனியாக தன்னை சரிபார்க்க முடியாது. அதனால் தேவைப்படுவது **self-correction through confrontation**.

## 2. Mental Model

Debate என்பது ஒரு problem-க்கு multiple agents-ஐ different perspectives-ல இருந்து வாதாட வைப்பது.

ஒரு agent Proponent, ஒரு agent Opponent. அல்லது 3-5 agents ஒரே topic-ல debate பண்ணி, ஒரு judge agent இறுதியில் consensus எடுக்கும்.

மனிதர்கள் முக்கியமான decisions எடுக்கும்போது committee-ல debate பண்ணுவது போல. ஒவ்வொருவரும் தங்கள் angle-ல argue பண்ணுவார்கள். Weak points வெளியே வரும்.

## 3. How It Works

Basic flow:

1. **Prompt / Task** ஒரு coordinator agent-க்கு போகும்
2. Task multiple debate agents-க்கு பிரிக்கப்படும். ஒவ்வொருவருக்கும் role கொடுக்கப்படும்: Pro, Con, Critic, Devil's Advocate
3. Round-based exchange: Agent A argument சொல்லும், Agent B counter argument சொல்லும்
4. Each round-ல reasoning refine ஆகும்
5. Judge / Aggregator agent இறுதியில் arguments-ஐ evaluate செய்து best answer அல்லது summary தரும்

முக்கியமானது: Agents அதே base model-ஐ use பண்ணினாலும், different system prompt, different context, different persona கொடுத்தால் behavior மாறும்.

Debate-க்கு shared memory / context window இருக்க வேண்டும். இல்லை என்றால் agents ஒன்றுக்கொன்று கேட்டதை தெரியாமல் போகும்.

## 4. Architectural Reasoning

Debate எப்போது useful?

* **High-stakes decision making** - loan approval, medical diagnosis support, legal clause review
* **Ambiguous problems** - trade-off உள்ள problem, ஒரே சரியான பதில் இல்லாதது
* **Hallucination reduction** - ஒரு agent miss பண்ணியதை இன்னொரு agent catch பண்ணும்
* **Coverage** - ஒரு agent cost / risk மீது focus, இன்னொரு agent value / opportunity மீது focus

Alternative என்ன?
* **Self-reflection**: ஒரே agent தன்னைத்தானே critique பண்ணும். Simple, cheap. ஆனால் same bias இருக்கும்.
* **Ensemble voting**: Multiple agents independent-ஆ answer கொடுக்க, majority vote எடுக்க. Debate-ஐ விட cheap, ஆனால் reasoning improve ஆகாது.
* **ReAct with tool use**: Agent tools-ஐ use பண்ணி fact check பண்ணும். Good for factual errors, ஆனால் logical flaws-ஐ catch பண்ணாது.

Architect ஏன் debate-ஐ choose பண்ணுவான்? 
பதில் quality முக்கியம், latency / cost குறைவாக முக்கியம் இல்லை என்றால்.

## 5. Trade-offs

**Quality vs Cost**: Debate என்பது N agents x R rounds = N*R times inference. Cost, latency எல்லாம் linear-ஆ increase ஆகும்.

**Diversity vs Cohesion**: Agents-க்கு மிகவும் வேறுபட்ட persona கொடுத்தால் debate நல்லது, ஆனால் ஒரு point-ல முட்டி மோதி ஒன்றும் முடிவுக்கு வராமல் போகலாம்.

**Judge bias**: Final judge agent-ம் ஒரு LLM தான். அது தன்னுடைய bias-ஐ carry பண்ணும். Judge-ஐ debate-ல இருந்து independent-ஆ வைக்க வேண்டும்.

**Failure mode**: Agents එක மற்றவர் arguments-ஐ cherry pick பண்ணி, தங்கள் opinion-ஐ justify பண்ணும். Echo chamber ஆக மாறும். இதை தடுக்க explicit scoring rubric தர வேண்டும்.

## 6. Practical Example

Enterprise RAG-based policy compliance agent.

User asks: "Can we launch this new ad campaign in EU?"

System:
* Agent 1 - Legal Advocate: GDPR, data privacy clauses-ஐ check பண்ணி argue
* Agent 2 - Marketing Advocate: Reach, ROI, competitive advantage-ஐ argue
* Agent 3 - Risk Critic: Past violations, brand risk, enforcement trends-ஐ argue

3 rounds debate:
Round 1: Each agent initial stance தரும்
Round 2: Each agent மற்றவர் points-க்கு counter தரும்
Round 3: Revised stance

Judge agent இறுதியில்: "Campaign allowed with consent banner v2 and age gate. Reason: Legal risk high if not compliant, marketing benefit doesn't outweigh fine risk."

இங்கே debate வெறும் answer கொடுக்கவில்லை, decision-க்கு reasoning trail உருவாக்கியது. Audit-க்கு useful.

## 7. Reasoning Challenge

உங்களிடம் customer support escalation system இருக்கு. Tier-1 agent ஒரு refund request-ஐ decline பண்ணியது. Customer angry. நீங்கள் 2 debate agents வைக்க போகிறீர்கள்: Policy Agent மற்றும் Empathy Agent.

Debate-க்கு 3 rounds வைத்தால் latency 4.5 seconds ஆகும். 1 round வைத்தால் 1.8 seconds.

இங்கே rounds எத்தனை வைப்பீர்கள்? Judge தேவையா? ஏன்? Cost vs quality trade-off என்ன?

## 8. Key Takeaways

* Debate என்பது quality-க்காக cost-ஐ வாங்கும் technique. Single agent-க்கு பதில் multi-agent confrontation.
* ஒரே problem-க்கு different perspectives கொடுத்தால் blind spots குறையும், hallucination குறையும்.
* Architect முக்கியமாக சிந்திக்க வேண்டியது: rounds எத்தனை, agents எத்தனை, judge தேவையா, latency budget என்ன.
* Every architectural solution creates another trade-off: Debate improves correctness ஆனால் cost, latency, operational complexity அதிகரிக்கும்.
