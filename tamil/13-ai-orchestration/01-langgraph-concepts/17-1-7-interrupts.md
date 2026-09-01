# Interrupts

> **Learning Path:** AI Orchestration
> **Section:** 17.1.7 — LangGraph concepts

## 1. Problem

உங்கள் AI agent ஒரு long-running workflow-ல இருக்கு. User-க்கு file upload பண்ணச் சொல்லுது, அல்லது confirmation கேக்குது, அல்லது extra information கேக்குது.

அந்த நேரத்தில் agent தொடர்ந்து run ஆகணுமா? அல்லது அப்படியே நின்னுடணுமா?

சாதாரண code-ல நீங்கள் `input()` போட்டால் thread block ஆகும். LangGraph-ல graph ஒரு state machine மாதிரி run ஆகும். ஒரு node முடிஞ்சதும் அடுத்த node-க்கு போகும்.

Agent-க்கு user input தேவைப்படும்போது, graph-ஐ எப்படி pause பண்ணுவது? எப்படி அதே state-ல திரும்ப resume பண்ணுவது? அதுதான் interrupt.

இல்லாமல் என்ன ஆகும்? நீங்கள் ஒரு workaround பண்ணுவீர்கள்: external database-ல state save பண்ணுவது, polling பண்ணுவது, அல்லது agent-ஐ முழுசா restart பண்ணுவது. அது error-prone, slow, மற்றும் operability கெடும்.

## 2. Mental Model

Interrupt என்பது graph execution-ஐ ஒரு checkpoint-ல நிறுத்தி, வெளியே போய் human அல்லது external system-இலிருந்து input எடுத்து, அதே checkpoint-ல இருந்து தொடர்வது.

அது `yield` பண்ணும் generator மாதிரி. Agent "நான் இங்கே நிக்கிறேன், உனக்கு இது வேணும்" என்று சொல்லி control-ஐ திருப்பிக் கொடுக்கும். பிறகு user response வந்ததும் அதே state, அதே context-உடன் தொடரும்.

LangGraph-ல இது built-in. நீங்கள் node-ஐ interrupt-க்கு mark பண்ணினால், graph அங்கே pause ஆகும், state persist ஆகும், மற்றும் external wait trigger ஆகும்.

## 3. How It Works

LangGraph-ல interrupt என்பது node boundary-ல நடக்கும்.

நீங்கள் graph build பண்ணும்போது `interrupt_before` அல்லது `interrupt_after` என்று specify பண்ணலாம்.

எளிய flow:
`entry -> retrieve -> need_user_input -> process -> end`

`need_user_input` node-க்கு முன் interrupt வைத்தால், retrieve முடிஞ்சதும் graph pause ஆகும். State இருக்கும். UI அல்லது API ல இருந்து user input வாங்கி, graph-ஐ resume பண்ணலாம்.

Internally LangGraph state-ஐ checkpoint store-ல save பண்ணும். Resume போது அந்த checkpoint-ல இருந்து தொடரும். Graph-ஐ முதல்ல இருந்து re-run பண்ண வேண்டாம்.

Interrupt ஒரு node-ல மட்டுமல்ல, conditional edge-க்கு முன்னும் வரலாம். Agent ஒரு decision எடுக்கணும், அந்த decision-க்கு human approval தேவைப்பட்டால் interrupt useful.

## 4. Architectural Reasoning

Interrupt எப்போது useful?

* Human-in-the-loop தேவைப்படும் workflows: approval, clarification, data input
* Long-running agent tasks: user context தேவைப்படும் போது pause
* Safety and compliance: sensitive action-க்கு முன் confirmation
* Multi-step RAG + tool use: tool result தேவைப்படும் போது pause செய்ய வேண்டாம், ஆனால் user correction தேவைப்படும்போது pause

Alternatives என்ன?

* Stateless retry: ஒவ்வொரு முறையும் graph முதல்ல இருந்து start. Context loss ஆகும், expensive.
* Polling loop: agent loop-ல திரும்ப திரும்ப check பண்ணும். Wasteful, latency அதிகம்.
* External orchestrator: Zapier / workflow engine வெளியே state manage. Complex, duplication.

Interrupt-ஐ தேர்வு செய்வது ஏன்? ஏனென்றால் stateful pause/resume ஒரே framework-ல கிடைக்கும். Operational complexity குறையும்.

## 5. Trade-offs

**State persistence cost:** Every interrupt = checkpoint write to store. DB cost, latency. Frequent interrupt செய்யக்கூடாது.

**Complexity in UX:** Frontend-க்கு pause/resume state manage பண்ண வேண்டும். User எவ்வளவு நேரம் wait பண்ணலாம்? Timeout எப்படி handle?

**Failure mode:** User never responds. Graph stuck. நீங்கள் TTL, auto-cancel logic வைக்க வேண்டும்.

**Scalability:** Checkpoint store becomes critical path. Redis / Postgres / DynamoDB latency affect resume time.

**Security:** Paused state-ல sensitive data இருக்கும். Checkpoint encryption, access control தேவை.

ஒவ்வொரு interrupt-மும் reliability-க்கு ஒரு new failure point create பண்ணும்.

## 6. Practical Example

Enterprise support agent.

Flow:
`classify -> retrieve KB -> draft reply -> human approval -> send`

`draft reply` node-க்கு பிறகு interrupt_before `send`.

Agent draft reply உருவாக்கும். Graph pause ஆகும். UI-ல agent manager-க்கு draft காட்டும். Manager edit பண்ணி approve பண்ணுவார். அந்த input resume செய்யும்.

இங்கே interrupt இல்லாமல் agent direct send பண்ணினால், hallucination / tone issue வரலாம். முழு workflow-ஐ external DB-ல save பண்ணி poll பண்ண வேண்டி வரும்.

Interrupt உடன் architecture clean ஆகும்: state ஒரே இடத்தில், resume deterministic.

## 7. Reasoning Challenge

உங்களிடம் finance agent இருக்கு. Agent ஒரு payment approve பண்ணும் முன் manager confirmation கேட்கிறது. ஒரு run-ல 3 வெவ்வேறு payments-க்கு confirmation தேவை.

நீங்கள் ஒரே interrupt-ல மூன்று approvals-ஐயும் சேர்த்து கேட்பீர்களா? இல்லை ஒவ்வொன்றாக தனித்தனி interrupt வைப்பீர்களா?

ஏன்? Latency, user experience, failure isolation என்ன ஆகும்?

## 8. Key Takeaways

* Interrupt என்பது graph execution-ஐ pause/resume செய்யும் built-in mechanism. Human-in-the-loop-க்கு core.
* State persistence ஆகும். Resume deterministic, re-run தேவை இல்லை.
* Use it for clarification, approval, input collection. Overuse cost மற்றும் complexity அதிகரிக்கும்.
* ஒவ்வொரு interrupt-க்கும் timeout, failure, security trade-off உண்டு.
