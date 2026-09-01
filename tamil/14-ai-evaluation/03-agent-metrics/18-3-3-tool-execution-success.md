# Tool execution success

> **Learning Path:** AI Evaluation
> **Section:** 18.3.3 — Agent metrics

## 1. Problem

உங்க agent ஒரு task-ஐ solve பண்ணும்போது tool-ஐ call பண்ணுது. `search_web`, `fetch_url`, `create_ticket`, `call_api` மாதிரி.

அப்போ என்ன கேள்வி வரும்?

> Tool call success ஆச்சா? இல்ல failure ஆச்சா? Failure ஆனால் agent-க்கு தெரியுமா? Agent அதை retry பண்ணுமா? அல்லது hallucinate பண்ணி முன்னே போயிடுமா?

ஒரு RAG agent-க்கு vector database-ல் search பண்ண சொல்லி இருக்கீங்க. Search tool timeout ஆகுது. Agent-க்கு empty result கிடைக்குது. Agent "எனக்கு தகவல் கிடைக்கல"ன்னு user-க்கு சொல்லுமா? இல்ல "நான் தேடினேன், எதுவும் இல்லை"ன்னு தப்பா conclude பண்ணுமா?

Tool execution success என்பது agent evaluation-ல் **ground truth of action** ஆகும். Agent சரியான tool-ஐ சரியான parameter-உடன் call பண்ணியதா? Call succeed ஆச்சா? Result-ஐ சரியா interpret பண்ணியதா?

இதை measure பண்ணாமல் agent quality-ஐ மதிப்பிட முடியாது.

## 2. Mental Model

Tool execution success = **Intention → Call → Outcome** chain-இன் reliability.

Agent-க்கு ஒரு goal இருக்கு. அதற்கு tool தேவை. Agent tool-ஐ invoke பண்ணுது. Tool ஒரு observable result தருது.

நாம் மூன்று layer-ஐ பார்க்கணும்:

1. **Invocation Correctness**: Agent சரியான tool-ஐ சரியான args-உடன் call பண்ணிச்சா?
2. **Execution Success**: Tool call technically succeed ஆச்சா? Timeout, error, exception இல்லையா?
3. **Result Utilization**: Agent tool output-ஐ புரிஞ்சு, அடுத்த step-ஐ சரியா எடுத்ததா?

இது accuracy அல்ல. இது **operational reliability**.

## 3. How It Works

Evaluation-ல் ஒரு trace-ஐ எடுக்கிறோம்.

```
User query -> Agent decides tool A with params {x,y} -> Tool returns output O or error E -> Agent produces next action
```

Tool execution success metric இதை capture பண்ணும்.

Simple definition:

**Tool execution success rate = Successful tool executions / Total tool attempts**

Successful என்றால் என்ன?

* Tool call syntax valid
* Tool returns 2xx / expected schema
* No exception, timeout, auth failure
* Agent got usable output

அதற்கு மேல் advanced version:

**Effective success rate = Tool calls that both succeed AND lead to correct downstream reasoning**

ஏனெனில் tool succeed ஆனாலும் agent output-ஐ ignore பண்ணி hallucinate பண்ணலாம்.

## 4. Architectural Reasoning

இது எப்போ useful?

* Agent tool-heavy workflows-ல்: RAG, coding agents, ticket creation, API orchestration
* Production monitoring-ல்: real tool calls fail rate அதிகமா இருக்கா?
* Evaluation-ல்: Model A vs Model B எது better tool user?

Constraint இது address பண்ணுது: **Observability of agent action**.

Alternatives?

* End-to-end task success மட்டும் பார்ப்பது. அது tool failure-ஐ hide பண்ணிடும்.
* Latency மட்டும் பார்ப்பது. Success இல்லாமல் latency meaningless.

Architect ஏன் choose பண்ணுவார்?

Tool execution success பார்த்தால் தெரியும்:

* Agent தப்பான tool-ஐ தேர்வு செய்கிறதா?
* Tool itself flaky-ஆ இருக்கா?
* Retry logic தேவையா?
* Parameter formatting தவறா?

## 5. Trade-offs

**1. Success vs Effectiveness**
Tool succeed ஆனாலும் agent அதை சரியா use பண்ணாமல் இருக்கலாம். Success rate high, task success low. இரண்டையும் track பண்ணணும்.

**2. Strictness of success definition**
Tool returned 200 ஆனால் empty result. இது success-ஆ? Architect decision. Empty result என்பது valid outcome ஆக இருக்கலாம், அல்லது upstream failure-ஆக இருக்கலாம்.

**3. Retry masking**
Agent 3 முறை retry பண்ணி 3rd-ல success ஆச்சு. Attempt count 3, success 1. Metric-ஐ எப்படி count பண்ணுவது? Attempts per successful execution என்று separate metric வேண்டும்.

**4. Tool diversity**
`search_web` success rate 95%, `create_invoice` success rate 60%. Aggregate metric misleading. Tool-wise breakdown தேவை.

Failure modes:

* Network timeout → transient
* Invalid params → agent bug
* Auth error → config bug
* Schema mismatch → tool contract drift
* Hallucinated tool name → model limitation

## 6. Practical Example

Enterprise support agent.

Tools: `search_kb`, `fetch_ticket`, `create_jira_ticket`, `call_customer_api`.

100 tasks run.

Total tool attempts = 340
Successful executions = 298
Failed = 42

Success rate = 87.6%

Breakdown:
`search_kb`: 120 attempts, 118 success → 98%
`fetch_ticket`: 90 attempts, 85 success → 94%
`create_jira_ticket`: 80 attempts, 55 success → 69%
`call_customer_api`: 50 attempts, 40 success → 80%

இங்கே architect-க்கு தெரியும் `create_jira_ticket` தான் problem area. Inspect பண்ணினால் 20 failures-ல் 15 invalid params - `priority` field wrong enum. Agent training data outdated.

Fix = tool schema update + prompt correction. Success rate 69% → 92%.

Tool execution success metric இல்லாமல், நீங்கள் task success drop-ஐ மட்டும் பார்த்து root cause கண்டுபிடிக்க முடியாது.

## 7. Reasoning Challenge

உங்கள் agent-க்கு 2 tools இருக்கு: `search_db` latency 200ms, success rate 99%. `search_vector` latency 800ms, success rate 85% ஆனால் recall better.

User query க்கு agent முதலில் `search_vector` call பண்ணி fail ஆகுது. அப்புறம் fallback-ஆ `search_db` call பண்ணி success ஆகுது.

Tool execution success metric-ஐ எப்படி define பண்ணுவீங்க? Overall success? Per tool? Fallback success-ஐ credit யாருக்கு தருவீங்க? Agent-க்கா, system-க்கா?

என்ன trade-off இருக்கு?

## 8. Key Takeaways

* Tool execution success என்பது agent-ன் action reliability-ன் முதல் signal. Task success-க்கு முன் இது வரும்.
* Success = invocation correctness + execution success + usable output. மூன்றையும் தனித்தனியாக பார்க்கவும்.
* Aggregate metric போதாது. Tool-wise, error type-wise breakdown தேவை.
* High success rate + low task success = agent result utilization problem. Low success rate + high retry = tool reliability / agent robustness problem.

இந்த metric இல்லாமல் agent evaluation என்பது blind.
