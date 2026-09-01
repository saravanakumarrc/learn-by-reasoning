# Prompt changes

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.4 — AI-specific monitoring

## 1. Problem

உங்கள் production-ல ஒரு RAG agent இருக்கு. கடந்த வாரம் average latency 800ms, good. இந்த வாரம் 2.3s ஆகிவிட்டது. Cost per query கூடியிருக்கு. User satisfaction குறைந்திருக்கு.

என்ன மாறியது?

- Model version மாறினதா?
- Prompt template மாறினதா?
- Retrieval top-k மாறினதா?
- System prompt-ல ஒரு வரி சேர்ந்ததா?

Traditional monitoring சொல்லும்: CPU, memory, latency, error rate. ஆனால் **ஏன்** latency அதிகரித்தது என்று சொல்லாது.

AI system-ல, output quality, cost, latency மூன்றும் ஒரே root cause-இலிருந்து வரலாம்: **prompt change**.

Prompt ஒரு small string change. ஆனால் அது token usage, reasoning steps, retrieval behavior, hallucination rate எல்லாவற்றையும் மாற்றிவிடும்.

இதை catch பண்ணாமல் விட்டால், production regression invisible-ஆக இருக்கும்.

## 2. Mental Model

Prompt என்பது code மாதிரி. Code deploy பண்ணும்போது versioning, diff, rollback இருக்கு. Prompt-க்கும் அதே தேவை.

AI-specific monitoring-ல் prompt changes என்பது:

> **Prompt என்பது configuration + code ஆகும். அதன் change ஒரு deployment event.**

அதை track பண்ண வேண்டும், அதன் impact-ஐ measure பண்ண வேண்டும், அது revert செய்ய முடிய வேண்டும்.

## 3. How It Works

Prompt changes-ஐ monitor பண்ண, மூன்று layer தேவை.

**Prompt Registry / Versioning**
ஒவ்வொரு prompt template-க்கும் stable ID + version. System prompt, user prompt, few-shot examples, tools description எல்லாம் சேர்த்து hash செய்து version ஆக்கு.

**Execution Telemetry**
ஒவ்வொரு LLM call-க்கும் log பண்ணு:
- prompt_version_id
- prompt_hash
- input_tokens, output_tokens
- model_id, temperature
- retrieval context used
- latency, cost
- output quality signals: user rating, guardrail hit, factuality score

**Correlation**
Prompt version change ஆன நேரத்தை, metrics drift-உடன் correlate செய். Dashboard-ல ஒரு line: prompt v3 deployed at 14:32, latency spike at 14:35.

Simple architecture:

```mermaid
graph LR
    App -> PromptStore[(Prompt Registry)]
    App -> LLM
    App -> Telemetry[(Trace + Prompt Version)]
    Telemetry -> Dashboard
    Telemetry -> Alert
```

## 4. Architectural Reasoning

இது useful ஆகும் போது?

- Prompt engineering iterative ஆக நடக்கிறது. A/B test பண்ணுகிறீர்கள்.
- Multiple teams same prompt library-ஐ use செய்கிறார்கள்.
- Compliance / audit தேவை. "எந்த prompt-உடன் இந்த output வந்தது?" என்று கேட்கலாம்.

Alternatives:
- Manual spreadsheet. Fail.
- Git only. Prompt file மாற்றம் தெரியும், ஆனால் production-ல எந்த version run ஆகிறது என்று தெரியாது.
- LLM provider logs only. Prompt content இல்லை, hash இல்லை.

Architect choose பண்ணுவான் prompt registry + telemetry coupling, because prompt change என்பது silent deployment.

## 5. Trade-offs

**Observability vs PII risk**
Prompt-ல user input இருக்கும். Logging செய்தால் data leakage risk. Trade-off: mask PII, log only prompt template id, not full rendered prompt with user data. அல்லது separate secure store.

**Granularity vs Cost**
ஒவ்வொரு call-க்கும் full prompt log செய்வது expensive. Sampling + critical paths மட்டும் full capture.

**Version pinning vs agility**
Strict version pinning safe. ஆனால் prompt engineer fast iterate விரும்புவார். Trade-off: canary release for prompts, 5% traffic to v2.

**False correlation**
Latency அதிகரித்தது prompt change-ல் இருந்து இல்லை, model provider outage இருந்து இருக்கலாம். Prompt version என்பது ஒரு dimension மட்டுமே. Multi-variate analysis தேவை.

## 6. Practical Example

Enterprise support chatbot. System prompt v1: "Answer concisely in 2 sentences."

Product team v2 deploy பண்ணினார்கள்: "Answer with step-by-step reasoning, cite sources."

Metrics:
- v1: avg output tokens 120, latency 900ms, user satisfaction 4.2
- v2: avg output tokens 380, latency 2.1s, cost 3.2x, satisfaction 4.0

Prompt change tracking இல்லாமல் இருந்தால், team நினைத்திருப்பார்கள் model slow ஆகிவிட்டது. Prompt version dashboard-ல் clear ஆக தெரியும்: token count jump prompt v2-உடன் correlate ஆகிறது.

இங்கே decision: step-by-step quality தேவையா? அல்லது cost/latency accept பண்ணலாமா? Trade-off explicit ஆகிறது.

## 7. Reasoning Challenge

உங்கள் RAG system-ல prompt template v5 deploy செய்தீர்கள். 30 நிமிடம் கழித்து, hallucination rate 2% லிருந்து 9% ஆக உயர்ந்தது. Retrieval results same. Model same.

என்ன check பண்ணுவீர்கள்? Prompt change-இல் என்ன elements இருக்கலாம் இந்த regression-க்கு காரணம்? Rollback பண்ணலாமா, அல்லது prompt-ஐ fix பண்ணி v5.1 deploy பண்ணலாமா?

## 8. Key Takeaways

- Prompt என்பது deployment artifact. Version it, hash it, track it.
- Prompt version + telemetry correlate பண்ணாமல் AI regression-ஐ debug செய்ய முடியாது.
- Small prompt change = large cost/latency/quality impact. Monitor it like code.
- Observability needs privacy handling and sampling trade-offs.
