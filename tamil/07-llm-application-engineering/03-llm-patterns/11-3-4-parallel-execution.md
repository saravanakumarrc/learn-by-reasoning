# Parallel execution

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.4 — LLM patterns

## 1. Problem

உங்களுக்கு ஒரு LLM agent இருக்கு. ஒரு user query வருது: "எங்கள் last quarter sales report-ஐ analyze பண்ணி, top 5 customers-ஐ கண்டுபிடிச்சு, ஒவ்வொருத்தருக்கும் personalized email draft கொடு."

இதை செய்ய agent-க்கு என்ன தேவை?
1. sales database-லிருந்து data fetch பண்ணணும்
2. data-வை summarize பண்ணணும்
3. top 5 customers list எடுக்கணும்
4. ஒவ்வொரு customer-க்கும் profile fetch பண்ணணும்
5. ஒவ்வொரு email-ஐ generate பண்ணணும்

Sequential-ஆ பண்ணினா, step 1 முடிந்த பிறகுதான் step 2, அப்புறம் step 3... இப்படி 10-15 seconds ஆகும். ஒவ்வொரு LLM call-க்கும் 1-2 seconds.

Problem என்ன? User wait பண்ண மாட்டார். Cost-ம் latency-ம் அதிகமாகுது. மேலும் சில tasks independent.

இங்கே தான் parallel execution தேவைப்படுது.

## 2. Mental Model

Parallel execution என்றால் independent tasks-ஐ ஒரே நேரத்தில் trigger பண்ணி, results வரும்போது combine பண்ணுவது.

Analogy: ஒரு restaurant-ல ஒரு order வந்தா, chef ஒருத்தர் மட்டும் முட்டை, ரொட்டி, சூப் எல்லாத்தையும் ஒவ்வொன்னா செய்வார். நிஜத்தில் மூன்று cooks ஒரே நேரத்தில் வேலை செய்வார்கள். தேவையான பொருள் தயாரானதும் plating செய்வார்கள்.

LLM-ல ஒவ்வொரு call-ம் network-bound, CPU-bound அல்ல. அதனால் நீங்கள் waiting time-ஐ hide பண்ணலாம்.

## 3. How It Works

Agent ஒரு plan பண்ணுது. Tasks-ஐ dependency graph-ஆ பார்க்குது.

`A -> B -> C` என்றால் sequential தான்.
`A, B, C` independent என்றால் அவைகளை parallel-ல launch பண்ணலாம்.

Implementation ல:
1. Planner task-ஐ decompose பண்ணும்
2. Dependency check: X தேவைப்படும் வரை Y wait
3. Independent branches-ஐ batch-ஆ call பண்ணும்
4. Results gather பண்ணி, orchestrator-க்கு return பண்ணும்

LLM patterns-ல இது `Map-Reduce`, `Fan-out / Fan-in` ஆகவும் வரும்.

## 4. Architectural Reasoning

Parallel execution useful ஆகும் போது:
- Multiple subproblems independent
- I/O bound work, especially LLM calls, database calls, API calls
- Latency budget குறைவு
- Throughput தேவை

Example constraint: User wants response in <5 sec, but 5 sequential LLM calls தேவை, ஒவ்வொன்றும் 1.5 sec. Sequential = 7.5 sec > budget. Parallel = ~1.5 sec.

Alternatives:
- Sequential execution: simple, predictable, less cost
- Streaming / incremental: user-க்கு partial results காட்டலாம்
- Caching: repeated work தவிர்க்கலாம்

Architect எப்போ choose பண்ணுவார்?
எப்போது tasks truly independent and failure isolated ஆக இருக்கும் போது. மேலும் error handling clear ஆக இருக்க வேண்டும்.

## 5. Trade-offs

**Latency vs Complexity:** Parallel reduces latency but adds orchestration complexity. Coordination, partial failure, timeout handling தேவை.

**Cost vs Speed:** Parallel means simultaneous API calls. Cost அதிகரிக்கும். Token usage same but billing per request concurrency increases.

**Failure modes:** ஒரு branch fail ஆனால் மற்றவை வேலை செய்யுமா? Retry policy எப்படி? All-or-nothing vs best-effort?

**Ordering and consistency:** Results combine பண்ணும்போது order matters ஆகுமா? Race condition வருமா?

**Resource limits:** LLM provider rate limits, concurrent connection limits, cost throttling. Blind parallel can hit 429 errors.

## 6. Practical Example

Enterprise RAG system:

User asks: "எங்கள் product catalog-ல இருந்து, pricing, reviews, return policy-ஐ compare பண்ணு."

Agent parallel-ல இதை செய்யலாம்:
- Tool 1: Vector DB-ல pricing info retrieve
- Tool 2: Vector DB-ல reviews retrieve
- Tool 3: Knowledge base-ல return policy retrieve

மூன்றும் independent. மூன்றையும் ஒரே நேரத்தில் call பண்ணி, results வந்ததும் synthesis LLM call பண்ணி final answer generate பண்ணுவது.

இதனால் latency 3 sequential calls-லிருந்து 1 call time-க்கு குறைகிறது. Trade-off: 3 vector DB queries ஒரே நேரத்தில் வரும், DB load அதிகரிக்கும்.

Another pattern: `Parallel agent generation`. 3 different prompts-ல ஒரே task-ஐ solve பண்ணி, best answer choose பண்ணுவது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு customer support agent இருக்கு. Ticket வந்ததும் அது செய்ய வேண்டியது:
1. Ticket history fetch
2. Customer profile fetch
3. Product knowledge search
4. SLA check

Ticket history தான் 1 மற்றும் 4-க்கு தேவை. 2 மற்றும் 3 independent.

Latency target 3 seconds. ஒவ்வொரு call-க்கும் ~1 sec.

நீங்கள் எந்த tasks-ஐ parallel-ல run பண்ணுவீர்கள்? எது sequential-ஆ wait பண்ண வேண்டும்? Failure ஒன்று ஆனால் என்ன செய்வீர்கள்?

## 8. Key Takeaways

- Parallel execution உருவானது waiting time-ஐ hide பண்ண, independent work-ஐ ஒரே நேரத்தில் செய்ய
- Dependency graph பார்த்துதான் parallelize பண்ண வேண்டும், blind parallel தவறு
- Latency குறைகிறது, ஆனால் complexity, cost, failure handling அதிகரிக்கிறது
- Architect-ஆ நீங்கள் எப்போது fan-out செய்யலாம், எப்போது sequential வைக்க வேண்டும் என்பதை constraints-லிருந்து முடிவு செய்ய வேண்டும்
