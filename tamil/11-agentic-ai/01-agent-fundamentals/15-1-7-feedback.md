# Feedback

> **Learning Path:** Agentic AI
> **Section:** 15.1.7 — Agent fundamentals

## 1. Problem

ஒரு agent-ஐ நீங்கள் release பண்ணினீங்க. அது tasks-ஐ autonomously செய்யுது. ஆனால் பயனர்கள் சொல்றாங்க: "இது சரியா வேலை செய்யல, இதை இப்படி வேண்டும்".

அந்த feedback-ஐ agent எப்படி capture பண்ணும்? அடுத்த முறை அதே தவறை திரும்ப செய்யுமா?

Agent fundamentals-ல மிக முக்கியமான விஷயம்: agent ஒரு closed loop-ல இருக்கணும். **Action → Observe → Learn → Improve**. இந்த loop-இல் `Feedback` தான் Observe/Learn-ஐ trigger பண்ணும் signal.

Feedback இல்லாமல் agent என்பது blind automation. ஒரு முறை train பண்ணினது போதும் என்று நினைத்தால் production-ல drift ஆகும்.

## 2. Mental Model

Feedback என்பது agent-க்கு வரும் external or internal signal, அதன் behavior சரியா தவறா என்பதை சொல்லும்.

இதை மூன்று வகையாக பார்க்கலாம்:

* **Explicit feedback**: User directly சொல்றது. "இது தவறு", "இதை மாற்று", thumbs up/down, rating.
* **Implicit feedback**: User behavior-ல இருந்து infer பண்ணுவது. Agent ஒரு summary கொடுத்தது, user அதை edit பண்ணி save பண்ணார். Agent tool-ஐ call பண்ணியது, user result-ஐ ignore பண்ணினார்.
* **Environment feedback**: Agent action-க்கு world தரும் response. API call failed, database constraint violated, test failed, KPI drop ஆச்சு.

ஒரு agent என்பது state + policy. Feedback தான் policy-யை update பண்ணும் data.

## 3. How It Works

Agent ஒரு task-ஐ செய்யும்போது:

1. **Plan** → 2. **Act** → 3. **Observe result** → 4. **Compare with intent** → 5. **Generate feedback signal**

Feedback signal என்பது scalar, vector அல்லது natural language-ல வரலாம்.

அதை handle பண்ண மூன்று வழிகள் உண்டு:

* **Online correction**: Immediate. User "இல்லை இப்படி வேண்டும்" என்றால், agent அதே conversation-ல revise பண்ணும்.
* **Short-term memory update**: Session context-ல சேமிக்கும். "User prefers concise answers, no bullet points". அடுத்த turn-ல use பண்ணும்.
* **Long-term learning**: Feedback-ஐ aggregate பண்ணி model or policy-யை update பண்ணும். Fine-tuning, preference learning, reward model training, tool selection policy update.

இங்கே architecturally முக்கியமானது: feedback loop-ஐ synchronous ஆகவா, asynchronous ஆகவா handle பண்ணுவது.

## 4. Architectural Reasoning

Feedback எப்போது useful?

* Agent தனியாக decision எடுக்கும் போது. Planning, tool choice, summarization style.
* Non-deterministic output வேண்டும் போது.
* User preference personalization தேவைப்படும் போது.

Constraint it addresses: **uncertainty and drift**. World மாறும், user expectation மாறும்.

Alternatives:

* **No feedback loop**: Static agent, periodic manual retraining. Cheap, simple, but slow to adapt.
* **Human-in-the-loop**: Every action human approve பண்ணுவது. High quality, but latency & cost அதிகம்.
* **Closed-loop with automated feedback**: Agent self-critiques, uses environment signals. Fast, but risk of reinforcing bad behavior.

Architect choose feedback loop when cost of wrong action > cost of collecting feedback + learning overhead.

## 5. Trade-offs

* **Signal quality vs coverage**: Explicit feedback தரமானது ஆனால் sparse. Implicit feedback abundant ஆனால் noisy. Architect எதை trust பண்ணுவது என்று decide பண்ணணும்.
* **Learning latency**: Immediate in-context correction fast ஆனால் long term மாறாது. Model-level learning durable ஆனால் expensive and slow.
* **Feedback loop stability**: தவறான feedback-ஐ கொண்டு agent தன்னை degrade பண்ணிக்கொள்ளலாம். Reward hacking, bias amplification.
* **Privacy & cost**: User feedback storage, annotation, human review எல்லாம் cost & compliance issue. Especially PII கொண்ட feedback-ஐ log பண்ணக்கூடாது.

Failure mode: Agent negative feedback-ஐ ignore பண்ணும், அல்லது overfit ஆகி ஒரு user-க்கு மட்டும் optimize ஆகும்.

## 6. Practical Example

Enterprise support agent. User ticket-ஐ read பண்ணி response draft பண்ணுகிறது.

Flow:
User query → Agent retrieves context → Agent drafts reply → User edits reply before send.

இங்கே implicit feedback = user edit diff. அந்த diff-ஐ capture பண்ணி, we can extract pattern: "Agent too formal", "Agent missed SLA mention".

Architecture:
`Feedback Collector` service captures explicit thumbs up/down + implicit edit diffs + environment signal: ticket reopened?

Data goes to `Preference Store` vector DB. Session level-ல retrieval augments agent prompt. Weekly batch-ல data goes to reward model fine-tuning.

Result: Agent slowly learns tone, compliance phrasing.

## 7. Reasoning Challenge

உங்களிடம் customer-facing agent இருக்கிறது. 10,000 users. Explicit rating கொடுப்பவர் 2% மட்டுமே. மீதி users தங்கள் behavior மூலம் feedback கொடுக்கிறார்கள்: copy, edit, discard, retry.

நீங்கள் agent-ஐ improve பண்ண வேண்டும், ஆனால் learning should not be too slow, nor should it overfit to noisy implicit signals.

நீங்கள் feedback pipeline-ஐ எப்படி design பண்ணுவீர்கள்? Explicit vs implicit signals-ஐ எப்படி weight பண்ணுவீர்கள்? Short-term vs long-term learning-க்கு எல்லை எங்கே வைப்பீர்கள்?

## 8. Key Takeaways

* Agent என்பது one-shot model அல்ல, feedback loop தான் agent-ஐ agent ஆக்குகிறது.
* Feedback-ஐ explicit, implicit, environment என மூன்று வகையாக பிரித்து handle பண்ண வேண்டும்.
* Immediate correction, short-term memory, long-term learning என மூன்று timescales-ல feedback-ஐ apply பண்ணுவது தான் practical.
* ஒவ்வொரு feedback loop-மும் trade-off-ஐ உருவாக்கும்: adaptability vs stability, cost vs quality, personalization vs generalization.
