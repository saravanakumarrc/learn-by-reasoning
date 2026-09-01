# Checkpoints

> **Learning Path:** AI Orchestration
> **Section:** 17.1.5 — LangGraph concepts

## 1. Problem

LangGraph-ல ஒரு agent workflow-ஐ run பண்ணும்போது என்ன ஆகும்? ஒரு graph-ல nodes பல, branching இருக்கும், loop இருக்கும். ஒரு run முடிய 10 steps எடுக்கும். 

அப்புறம் ஒரு bug வந்துச்சு, அல்லது LLM response தப்பா வந்துச்சு, அல்லது user குறுக்கிட்டு "இந்த step-க்கு முன்னாடி திரும்புங்க"ன்னு சொன்னார். 

என்ன பண்ணுவீங்க? மறுபடியும் முதல் node-ல இருந்து தொடங்கனுமா? அப்படி பண்ணினா ஏற்கனவே செலவான tokens, API calls, tool calls எல்லாம் waste.

அப்புறம் ஒரு long-running workflow 2 மணி நேரம் run ஆகுது. Server restart ஆனால்? Memory-ல இருந்த state எல்லாம் போயிடும்.

இதுதான் **Checkpoints** தேவைப்படும் problem.

## 2. Mental Model

Checkpoint என்பது ஒரு graph execution-ன் **snapshot**.

> ஒரு workflow எந்த node-ல இருக்கு, அதுவரை என்ன data accumulate ஆகியிருக்கு, next என்ன step போகனும், எந்த branch எடுத்தோம் — இதையெல்லாம் ஒரு persistent place-ல save பண்ணிடுறது.

Think of it like git commit for a running workflow. ஒவ்வொரு step முடிந்ததும் commit போடுறோம். பிறகு வேண்டுமானால் அந்த commit-க்கு checkout பண்ணி தொடரலாம், அல்லது replay பண்ணலாம்.

## 3. How It Works

LangGraph-ல graph ஒரு state machine மாதிரி run ஆகும். ஒவ்வொரு node execute ஆனதும்:

1. State update ஆகும்.
2. Checkpoint saver க்கு current state, graph pointer, metadata save பண்ணப்படும்.
3. Thread ID என்கிற workflow instance id-க்கு இந்த checkpoint associate ஆகும்.

பிறகு அதே thread id-ல `invoke` பண்ணினால், LangGraph முதல்ல கடைசி checkpoint-ஐ load பண்ணி அங்கிருந்து தொடரும்.

LangGraph built-in `MemorySaver` உண்டு — இது in-memory. Test-க்கு நல்லது. Production-க்கு `SQLiteSaver`, `PostgresSaver`, `Redis` போன்ற persistent checkpointers use பண்ணுவோம்.

## 4. Architectural Reasoning

Checkpoints useful ஆகும் போது:

* **Interactive agents**: User mid-workflow-ல திருத்தம் கொடுக்க வேண்டும். Resume பண்ண வேண்டும்.
* **Long running / multi-step workflows**: Workflow hours நீளும். Crash ஆனாலும் தொடர வேண்டும்.
* **Human-in-the-loop**: ஒரு step-ல approval தேவை. Checkpoint save பண்ணி pause பண்ணி பிறகு resume.
* **Debugging & replay**: ஏன் இந்த output வந்துச்சு என்று trace பண்ண checkpoint history பார்க்கலாம்.
* **Parallel branches & loop**: State எப்போதும் consistent இருக்கணும். Checkpoint இல்லாமல் loop-ல state drift ஆகும்.

என்ன constraint address பண்ணுது? **Reliability + state continuity + cost saving**. மறுபடியும் expensive LLM calls avoid பண்ணலாம்.

## 5. Trade-offs

* **Durability vs Speed**: In-memory checkpoint fast ஆனால் process restart ஆனால் போய்விடும். DB checkpoint durable ஆனால் latency add ஆகும்.
* **Storage cost**: ஒவ்வொரு step-க்கும் snapshot save பண்ணினால் storage பெருகும். Pruning policy வேண்டும்.
* **Consistency**: Checkpointer-ஐ DB-ல வைத்தால் அதுவும் single source of truth ஆகும். DB failure என்றால் workflow history தொலையும்.
* **Privacy / Security**: Checkpoint-ல sensitive user data, prompt, tool outputs இருக்கும். Encryption மற்றும் retention policy தேவை.

Failure mode: Checkpoint save fail ஆனால் workflow continue ஆகுமா? LangGraph default-ல error raise பண்ணும். நீங்கள் decide பண்ணணும்: fail-fast vs best-effort.

## 6. Practical Example

Enterprise RAG agent workflow: `retrieve → summarize → rewrite → human review → finalize`

User ஒரு document analysis கேட்டார். `retrieve` மற்றும் `summarize` முடிந்தது. Checkpoint save ஆனது. `human review` node-ல user-க்கு wait பண்ணுது. 

அடுத்த நாள் user வந்து "summarize step-ல இந்த section விட்டுட்டீங்க, மாற்றுங்க" என்றார்.

Checkpoints இருந்தால்: நீங்கள் அந்த thread id-ஐ load பண்ணி, `summarize` node-க்கு முன்னால் resume பண்ணி மாற்றி தொடரலாம். Retrieve மறுபடியும் செய்ய வேண்டாம்.

Checkpoints இல்லாமல்: முழு workflow முதல்ல இருந்து restart, token cost double.

## 7. Reasoning Challenge

உங்களிடம் 20 concurrent users இருக்காங்க. ஒவ்வொருவருக்கும் multi-step agent workflow run ஆகுது. ஒவ்வொரு step-க்கும் checkpoint save பண்ணுகிறீர்கள். Postgres checkpointer use பண்ணீங்க. 1 மாதத்திற்குப் பிறகு DB size 200GB ஆகி விட்டது. 

இங்கே என்ன trade-off செய்வீர்கள்? Checkpoint frequency reduce பண்ணுவீர்களா? Retention policy வைப்பீர்களா? அல்லது cheaper storage-க்கு move பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* Checkpoint என்பது workflow-ன் state-ஐ persistent ஆக்கும் mechanism. Restart, resume, replay enable பண்ணும்.
* Checkpoints இல்லாமல் long / interactive agents unreliable மற்றும் costly ஆகும்.
* MemorySaver dev-க்கு, Postgres/SQLiteSaver production-க்கு.
* ஒவ்வொரு checkpoint-க்கும் cost உண்டு: latency, storage, privacy. Frequency மற்றும் retention-ஐ architecturally decide பண்ணுங்கள்.
* Good architecture: checkpoint என்பது feature இல்லை, reliability மற்றும் operability-ன் core part.
