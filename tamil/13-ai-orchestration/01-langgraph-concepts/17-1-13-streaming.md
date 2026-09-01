# Streaming

> **Learning Path:** AI Orchestration
> **Section:** 17.1.13 — LangGraph concepts

## 1. Problem

ஒரு LLM agent உங்களுக்கு பதில் generate பண்ணும்போது என்ன நடக்குது? ஒரு request அனுப்பி, model முழுசா output எழுதி முடிச்சதும் response வருது.

இது சின்ன prompt-க்கு ஓகே. ஆனால் RAG, tool calling, multi-step reasoning உள்ள AI Orchestration flow-ல ஒரு step 5-10 seconds எடுக்கும். User UI-ல cursor blink பண்ணிகிட்டு இருக்கும். User-க்கு தெரியாது system வேலை செய்யுதா இல்ல hang ஆயிடுச்சான்னு.

இன்னொரு பிரச்சனை: agent ஒரு பெரிய reasoning chain run பண்ணும்போது, ஒரு step fail ஆனால் முழு output-ம் போயிடும். Streaming இல்லாமல், நீங்கள் முழு result-ஐயும் collect பண்ணி, பிறகு UI-க்கு அனுப்புவீங்க. இதில் latency அதிகம், failure பார்ப்பது கடினம், user experience மோசம்.

**What goes wrong if we don't have streaming?** Time to first token அதிகம், perceived latency அதிகம், UI முழுவதும் block ஆகும், error-ஐ early detect பண்ண முடியாது, backpressure handle பண்ண முடியாது.

## 2. Mental Model

Streaming என்பது முழு result-ஐ wait பண்ணாமல், data produce ஆகும் போதே chunk-களாக consume பண்ணுவது.

நினைச்சுக்கோங்க: tap-ல இருந்து தண்ணீர் ஓடுது. குடம் நிறையும் வரை காத்திருக்க வேண்டாம். Glass-ஐ கீழே வச்சதும் ஓட ஆரம்பிச்சிடும். அதே மாதிரி LLM token generate ஆகும் போதே UI-க்கு அனுப்புறது streaming.

LangGraph-ல இது இன்னும் ஆழமானது. Agent என்பது nodes + edges ஆக இருக்கும். ஒவ்வொரு node run ஆகும் போதே அதன் intermediate state-ஐ stream பண்ணலாம். User-க்கு "இப்போது search tool call பண்ணுது", "இப்போது summarization node run ஆகுது" என்று real-time visibility கிடைக்கும்.

## 3. How It Works

LangGraph-ல streaming என்பது 3 levels-ல வேலை செய்யும்:

**Token streaming:** LLM ஒரு token generate பண்ணும்போதே அதை stream பண்ணும். `stream` method-ல `StreamMode.TOKENS`.

**Node streaming:** Graph-ல ஒரு node complete ஆகும்போதோ, state update ஆகும்போதோ event emit ஆகும். `StreamMode.UPDATES`. இதில் உங்களுக்கு `{"node": "search", "state": {...}}` போன்ற events கிடைக்கும்.

**Custom streaming:** உங்கள் node-ல `stream` callback வைத்து custom events emit பண்ணலாம். எ.கா tool call started, tool call completed.

அடிப்படை flow:
`invoke` -> full result wait
`stream` -> generator of events, yield as soon as partial state ready

Producer-consumer மாதிரி. Graph runner produce events, your API layer consume and forward to client via Server-Sent Events or WebSocket.

## 4. Architectural Reasoning

Streaming எப்போது useful?

* User-facing chat/agent UI இருந்தால். Perceived latency குறைக்க.
* Long-running multi-step orchestration இருந்தால். Progress visibility தேவை.
* Debugging / observability தேவைப்பட்டால். எந்த node எப்போது fail ஆனது என்று தெரியும்.
* Backpressure handle பண்ண வேண்டுமென்றால். Client slow ஆக இருந்தால் buffer பண்ணலாம்.

Alternatives:
* **Polling:** Client கொஞ்சம் கொஞ்சம் GET பண்ணும். Inefficient, latency அதிகம்.
* **Fire-and-forget:** Job queue-க்கு போட்டுவிட்டு result பின்னால் email அனுப்ப. User experience மோசம்.

Architect முடிவு: Real-time interaction தேவை என்றால் streaming தேர்வு. But it adds complexity to state management.

## 5. Trade-offs

**Latency vs Complexity:** Time to first token குறையும், ஆனால் API layer, client handling, reconnection logic சேர்க்க வேண்டும்.

**State consistency:** Partial state expose ஆகும். Client incomplete data பார்க்கலாம். UI-ல optimistic rendering handle பண்ண வேண்டும்.

**Ordering & backpressure:** Events நிறைய வரும். Client slow ஆனால் buffer overflow ஆகும். LangGraph-ல streaming என்பது in-order guaranteed, ஆனால் network drop ஆனால் replay இல்லை.

**Cost & observability:** Streaming ஆனால் connection open இருக்கும். Idle connection cost, load balancer timeout settings மாற்ற வேண்டும்.

Failure mode: Client disconnect ஆனாலும் graph continue ஆகுமா? நீங்கள் stream-ஐ separate from execution வைக்க வேண்டும். அப்போதான் client reconnect செய்தாலும் latest state கிடைக்கும்.

## 6. Practical Example

Enterprise support agent.

Flow: `classify -> retrieve_docs -> generate_answer -> validate`

நீங்கள் streaming use பண்ணாமல் இருந்தால், user 12 seconds கழித்து முழு answer பார்ப்பார்.

Streaming `UPDATES` mode-ல:
1. Node `classify` complete ஆனதும் event: `Intent = billing`
2. UI-ல "புரிந்துகொண்டேன்: billing query"
3. Node `retrieve_docs` start ஆகும் event வரும்
4. Tokens stream ஆகி UI-ல typewriter effect-ல answer வரும்
5. `validate` node fail ஆனால் உடனே UI-ல error banner வரும்

இதனால் user trust அதிகரிக்கும், abandoned rate குறையும்.

## 7. Reasoning Challenge

உங்களிடம் LangGraph agent இருக்கு. 3 nodes: `search`, `summarize`, `answer`. 500 concurrent users chat பண்ணுகிறார்கள். ஒவ்வொரு user-க்கும் streaming தேவை. ஆனால் நீங்கள் serverless function use பண்ணுகிறீர்கள். Function timeout 60 seconds.

Streaming வைத்தால் connection 30-40 sec open இருக்கும். Serverless cold start + connection keep-alive problem வரும்.

இங்கே என்ன architecture தேர்வு செய்வீர்கள்? WebSocket gateway + persistent worker vs Server-Sent Events with short-lived functions? எதை எதுக்காக தேர்வு செய்வீர்கள்?

## 8. Key Takeaways

* Streaming என்பது performance optimization அல்ல, user perception மற்றும் observability க்கான architectural choice.
* LangGraph-ல node-level updates stream பண்ணுவது orchestration visibility-க்கு மிக முக்கியம்.
* Streaming சேர்த்தால் state partial exposure, backpressure, reconnection பிரச்சனைகள் வரும். அவற்றை consciously design பண்ண வேண்டும்.
* Execution-ஐ streaming-லிருந்து decouple பண்ணுங்கள். Graph run ஆகும், streaming என்பது view layer.
