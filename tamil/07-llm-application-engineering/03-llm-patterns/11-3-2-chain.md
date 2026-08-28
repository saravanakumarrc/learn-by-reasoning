# Chain

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.2 — LLM patterns

## 1. Problem

உங்ககிட்ட ஒரு user query வருது: "எனக்கு last 3 months expenses-ல ஒரு summary வேணும், அதை base பண்ணி next month budget suggest பண்ணு".

LLM-க்கு இதை ஒரே prompt-ல கொடுத்தா என்ன ஆகும்?

LLM-க்கு data தெரியாது. Database-ல இருந்து fetch பண்ணணும். Fetch பண்ணிய data-வை பார்த்து summarize பண்ணணும். Summarize பண்ணினதை base பண்ணி reasoning பண்ணி budget suggest பண்ணணும்.

ஒரே LLM call-ல இதெல்லாம் செய்ய முடியாது. Context window மீறும், hallucination வரும், tool use செய்ய முடியாது.

இந்த பிரச்சனை painful ஆனது எப்போ? **ஒரு task ஒன்றுக்கு மேற்பட்ட logical steps தேவைப்படும் போது**, ஒவ்வொரு step-க்கும் வெவ்வேறு input, tool, அல்லது reasoning தேவை.

இங்கே தேவை: ஒரு step-ன் output அடுத்த step-ன் input ஆக போகணும். Structured.

அதான் Chain.

## 2. Mental Model

Chain என்பது **பல LLM calls-ஐ ஒரு sequence-ல connect பண்ணுவது**. ஒவ்வொரு call-க்கும் தனி responsibility.

Analogy: Assembly line. ஒரு worker raw material எடுக்கிறார், இன்னொருவர் cut பண்ணுகிறார், இன்னொருவர் polish பண்ணுகிறார். Final product வரும்.

Chain-ல LLM ஒரு worker. Tools, data fetch, formatting எல்லாம் workers.

ஒரு chain = **Input → Step1 → Step2 → ... → StepN → Output**

முக்கியம்: ஒவ்வொரு step-லும் prompt engineer பண்ணி, context-ஐ குறைத்து, task-ஐ narrow பண்ணுகிறோம்.

## 3. How It Works

Basic flow:

1.  **Initial Input** user query
2.  **Step 1 LLM Call**: e.g., "Extract intent and entities". Output = structured JSON
3.  **Inter-step Processing**: Tool call to database, validation, formatting
4.  **Step 2 LLM Call**: e.g., "Summarize expenses using fetched data". Input = data + instruction
5.  **Step 3 LLM Call**: e.g., "Generate budget recommendation based on summary"

ஒவ்வொரு step-ன் output அடுத்த step-ன் prompt-ல inject ஆகும்.

இது **Chain of Thought** இல்லை. Chain of Thought என்பது ஒரே call-ல reasoning tokens. இது **Chain of Tasks**.

Pattern types:
* **Linear Chain**: Step A → Step B → Step C. இதுதான் basic.
* **Map-Reduce**: Parallel calls same task, then aggregate.
* **Router Chain**: First call decides which branch chain to follow.

## 4. Architectural Reasoning

Chain எப்போ useful?

* Task multi-step and dependencies உள்ளது.
* ஒவ்வொரு step-க்கும் different data source தேவை.
* Quality control தேவை. ஒவ்வொரு step-லும் validate பண்ணலாம்.
* Prompt complexity குறைக்கணும். One big prompt = confusion.

என்ன constraint-ஐ address பண்ணுது?
Latency vs Accuracy trade-off. ஒரே call-ல செய்தால் hallucination அதிகம். Split பண்ணினால் control அதிகம்.

Alternatives:
* **Single Prompt with all context**: Simple, fast, cheap. ஆனால் data heavy, error prone.
* **ReAct/Agent Loop**: Chain dynamic ஆக decision எடுக்கும். Chain static sequence.

ஏன் architect chain-ஐ choose பண்ணுவார்?
Predictability தேவைப்படும் production workflow-ல. Steps தெளிவாக தெரியும், test பண்ணலாம், debug பண்ணலாம், retry செய்யலாம்.

## 5. Trade-offs

**1. Latency & Cost**
ஒவ்வொரு step-க்கும் LLM call = latency add ஆகும், cost multiply ஆகும். 3 steps = ~3x cost.

**2. Error Propagation**
Step 1 தவறு செய்தால், அது step 2,3-க்கு பரவும். Need validation gate between steps.

**3. Brittleness**
Sequence fixed. User query மாறினால் chain முழுக்க redesign. Flexibility குறைவு.

**4. Observability Benefit**
ஒவ்வொரு step-ன் output log பண்ணலாம். எங்கே fail ஆச்சுன்னு தெரியும். Single prompt-ல இது கடினம்.

Failure mode: Intermediate output too large. அடுத்த prompt-ல token limit மீறும். Solution: Summarize/compress between steps.

## 6. Practical Example

RAG + Summarization Chain for Support Ticket.

Step 1: Intent Classification LLM
Input: "My payment failed but money deducted"
Output: intent = payment_failure, entities = {payment_id: null}

Step 2: Tool Call
Fetch recent transactions from database using user_id.

Step 3: Retrieval LLM
Input: transaction data + user query
Output: Relevant 2 transactions

Step 4: Reasoning LLM
Input: transactions + policy
Output: Root cause = duplicate charge, action = refund

Step 5: Response Generation LLM
Input: cause + action
Output: User-friendly Tamil/English apology + next steps

இங்கே chain வைத்ததால், database call மற்றும் policy reasoning isolate ஆகிறது. ஒவ்வொரு step-லும் prompt simple.

## 7. Reasoning Challenge

உங்களிடம் ஒரு resume screening system இருக்கு. Requirement:
1. Resume-ல skills extract பண்ணு
2. Job description-ல required skills compare பண்ணு
3. Match score கொடு
4. Shortlist reason generate பண்ணு

ஒரே LLM call-ல vs Chain of 3 steps. நீங்கள் எதை தேர்வு செய்வீர்கள்? Latency, accuracy, maintainability எப்படி மாறும்? Step 2-ல validation என்ன செய்யலாம்?

## 8. Key Takeaways

* Chain என்பது complex task-ஐ small, verifiable steps-ஆக பிரிப்பது.
* ஒவ்வொரு step-ன் output அடுத்த step-ன் input. Control மற்றும் debug எளிது.
* Cost & latency அதிகரிக்கும், ஆனால் accuracy & reliability கூடும்.
* Error propagation உண்மை. Inter-step validation முக்கியம்.
* Static linear flow. Dynamic logic வேண்டுமெனில் Agent/Router தேவை.
