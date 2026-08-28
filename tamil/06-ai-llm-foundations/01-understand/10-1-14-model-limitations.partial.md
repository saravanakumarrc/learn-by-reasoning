# PARTIAL — Model limitations

> Generation was not accepted as complete.
> Reason: Ollama reported done_reason=length

## 1. Problem

நீங்கள் ஒரு LLM போட்டு agent பண்ணினீங்க. Support ticket வந்ததும் அது answer கொடுக்கணும். முதல் 10 conversation-ல் சூப்பரா work பண்ணுது. 

அப்புறம் ஒரு customer-க்கு 2 வருஷ data வேண்டி கேட்கிறார். அந்த conversation history-யே 80k tokens ஆகுது. Model context window முடிஞ்சு போகுது. அல்லது model திடீரென policy-யை தப்பா சொல்லுது, hallucination பண்ணுது. 

அல்லது simple arithmetic: `127 * 84 = ?` என்றால் சில நேரம் சரியா வரும், சில நேரம் தப்பா வரும்.

இந்த விஷயங்கள் ஏன் வருது? Model-க்கு limitation உண்டு. அதை புரிஞ்சுக்காம architecture போட்டா production-ல பெரிய failure வரும்.

## 2. Mental Model

LLM-ஐ perfect knowledge base + perfect reasoner ஆக நினைக்காதீங்க.

இது ஒரு **statistical pattern matcher** with finite memory.

Context window = அதோட working memory. அதுக்கு அப்புறம் எதையும் பார்க்காது.
Knowledge cutoff = அதுக்கு அப்புறம் நடந்த உலகம் தெரியாது.
Training data = அதுல இருக்குற noise-ஐயும் கத்துக்கிட்டிருக்கும்.

அதனால் model-ஆடு தெரிஞ்சது தான் கொடுக்கும். தெரியாததை கண்டுபிடிக்க முயற்சி பண்ணும்போது hallucination வரும்.

## 3. How It Works

**Context window and token limit.** Model ஒரே முறை பார்க்கக்கூடிய input size-க்கு limit உண்டு. 8k, 128k, 200k என மாறும். உங்கள் conversation, system prompt, tools description, RAG results எல்லாம் இதுக்குள்ள தான் வரணும். Overflow ஆனால் truncate ஆகும்.

**Attention decay.** Window-க்குள் இருந்தாலும், மிக நீளமான context-ல் மத்தியில் இருக்கும் information-க்கு attention குறைவு. Model முன்னாடி பின்னாடி இருக்குறதை அதிகம் நினைவில் வைத்திருக்கும்.

**Knowledge cutoff and hallucination.** Model-க்கு real-time world knowledge இல்லை. Training data-ல இல்லாத ஒன்றை கேட்டால், plausible sounding answer-ஐ generate பண்ணும். இது architectural risk.

**Reasoning precision.** LLM லாங்குவேஜ் distribution-ஐ கற்றுக்கொள்ளும், symbolic manipulation அல்ல. அதனால் code, math, structured data extraction-ல் non-deterministic errors வரும்.

**Cost / Latency.** Context size அதிகரிக்க அதிகரிக்க cost, latency linear-ல் உயரும். Throughput target-க்கு இது constraint ஆகும்.

## 4. Architectural Reasoning

Model limitation என்பதை workaround பண்ண வேண்டும், fix பண்ண முடியாது.

**Memory limitation -> Retrieval and summarization.** Context window குறைவு என்றால், conversation history-ஐ summarize பண்ணி, relevant chunks மட்டும் retrieve பண்ணி தர வேண்டும். RAG pipeline, vector database, embedding-based retrieval இங்கே வரும்.

**Knowledge cutoff -> Grounding.** Real-time data வேண்டுமெனில், model-ஐ மட்டும் நம்பாதீங்க. External tools, APIs, knowledge base-லிருந்து fetch பண்ணி prompt-ல inject பண்ணுங்க.

**Hallucination -> Validation layer.** Critical output-க்கு, model output-ஐ parser, schema validator, retrieval citation check மூலம் verify பண்ணுங்க. Financial, medical domain-ல இது must.

**Reasoning depth -> Decomposition.** சிக்கலான task-ஐ small steps-ஆக பிரித்து, tool use, agent loop மூலம் solve பண்ணுங்க. ReAct pattern, multi-agent workflow இங்கே உதவும்.

## 5. Trade-offs

**Bigger context vs cost and latency.** 128k window வாங
