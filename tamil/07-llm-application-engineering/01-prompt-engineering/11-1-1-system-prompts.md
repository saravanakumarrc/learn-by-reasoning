# System prompts

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.1 — Prompt engineering

## 1. Problem

நீங்கள் ஒரு LLM-ஐ API மூலம் கூப்பிடுகிறீர்கள். அதே model, அதே temperature, ஆனால் ஒரு நாள் output சரியாக வருகிறது, மறுநாள் ஹல்லுசினேட் செய்கிறது. ஒரு agent-ல் tool call சரியாக வரவில்லை. JSON format மீறுகிறது. Tone மாறிக்கொண்டே இருக்கிறது.

இதற்கு காரணம் prompt மட்டும் அல்ல. **Model-க்கு context இல்லாமல், role இல்லாமல், constraints இல்லாமல் நீங்கள் கேள்வி கேட்கிறீர்கள்.** ஒவ்வொரு request-லும் நீங்கள் அதே background-ஐ மீண்டும் சொல்ல முடியாது.

இந்த pain தான் system prompt தேவைப்படுவதற்கு காரணம்.

## 2. Mental Model

System prompt என்பது LLM-க்கான **operating instructions**. User prompt என்பது அந்த கணம் நீங்கள் கேட்கும் task.

System prompt = யார் நீ, எப்படி நடக்கணும், என்ன rules follow பண்ணணும், என்ன output format வேணும்.

அது ஒரு **base context** போல. User prompt அதன் மேல் வரும் request.

Analogy: ஒரு service-க்கு configuration file இருக்கிறது. அதில் default behavior, policies இருக்கும். ஒவ்வொரு request-க்கும் அதே config-ஐ மீண்டும் அனுப்ப தேவையில்லை.

## 3. How It Works

LLM inference-ல் ஒரு single conversation என்பது ஒரு sequence of messages. System message முதலில் வரும். அது highest priority context.

Model அதை internalize செய்து, user messages-க்கு பதிலளிக்கும் போது அந்த framing-ஐ பயன்படுத்தும்.

System prompt பொதுவாக கொண்டிருக்கும்:

* **Role & Identity:** "நீ ஒரு senior software architect..."
* **Task boundaries:** என்ன செய்ய வேண்டும், என்ன செய்யக்கூடாது
* **Output constraints:** JSON only, no hallucination, cite sources
* **Reasoning style:** step-by-step, concise
* **Safety & compliance:** PII handling, refusal policy

இது ஒவ்வொரு request-லும் repeat ஆகாமல், model-ஐ consistent behavior-க்கு anchor செய்கிறது.

## 4. Architectural Reasoning

System prompt எப்போது useful?

* Production agent / RAG pipeline / API service-ல் consistency வேண்டும் போது
* Multiple users ஒரே model-ஐ பயன்படுத்தும் போது, behavior ஒன்றாக இருக்க வேண்டும்
* Output format strict இருக்க வேண்டும், downstream parser உள்ள போது
* Team-ல் prompt ownership தேவை, versioning தேவை

Alternatives:

* **User prompt only:** quick experiments-க்கு சரி. Production-க்கு brittle.
* **Few-shot in user prompt:** உதாரணங்கள் தரலாம், ஆனால் token cost அதிகம், drift ஆகும்.
* **Fine-tuning:** behavior permanent ஆக மாற்ற வேண்டும் என்றால். Costly, slow iteration.

Decision logic: Behavior ஒரு சில வாரங்களுக்கு மாறும், அடிக்கடி iterate செய்யணும் → system prompt. Behavior stable, domain-specific knowledge deep → fine-tuning or system prompt + RAG.

## 5. Trade-offs

**Consistency vs Flexibility:** Strong system prompt = predictable output. ஆனால் model too rigid ஆகி creative tasks-ல் மோசமாகும்.

**Control vs Prompt leakage:** System prompt-ல் உள்ள instructions user-க்கு தெரியக்கூடாது. Model sometimes system content-ஐ output-ல் repeat செய்யும். Redaction தேவை.

**Centralization vs Personalization:** ஒரே system prompt எல்லாருக்கும். Per-user / per-tenant customization வேண்டும் என்றால் system prompt dynamic ஆக build செய்ய வேண்டும். அது complexity.

**Token cost:** System prompt ஒவ்வொரு request-லும் context window-ல் உள்ளது. Long system prompt = higher cost, latency.

Failure mode: System prompt too vague → model drifts. Too strict → model refuses valid requests. System prompt conflict with user prompt → unpredictable behavior.

## 6. Practical Example

Enterprise support agent.

System prompt:
> "நீ ஒரு enterprise IT support assistant. நீ user-க்கு troubleshooting steps கொடுக்க வேண்டும். ஒவ்வொரு பதிலும் JSON format-ல் வர வேண்டும்: {steps: [...], escalation_needed: bool}. Company policy: PII collect பண்ணக்கூடாது. Unknown என்றால் admit செய்ய வேண்டும், hallucinate பண்ணக்கூடாது."

User prompt: "My laptop won't connect to VPN"

Model system instructions-க்கு ஏற்ப structured steps கொடுக்கும், JSON திரும்பும், downstream ticketing system parse செய்யும்.

இங்கே system prompt இல்லாமல் ஒவ்வொரு user-க்கும் tone, format மாறும். Automation break ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் multi-tenant SaaS chatbot உள்ளது. ஒரே model, ஆனால் Tenant A-க்கு strict compliance tone வேண்டும், JSON output வேண்டும். Tenant B-க்கு casual tone வேண்டும், free text வேண்டும்.

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? System prompt-ஐ எப்படி manage செய்வீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

* System prompt என்பது model-க்கான base operating policy, user prompt என்பது task
* Consistency, format enforcement, safety-க்கு system prompt தேவை
* Too long or too rigid system prompt கூட problem உருவாக்கும்
* Production-ல் system prompt-ஐ version செய்யவும், test செய்யவும், observe செய்யவும்
