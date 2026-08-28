# Insecure output handling

> **Learning Path:** Security Architecture
> **Section:** 6.3.7 — AI security

## 1. Problem

உங்க system-ல ஒரு LLM service இருக்கு. அது user query-க்கு பதில் தருது. அந்த output-ஐ நீங்க நேரடியாக frontend-ல render பண்ணுறீங்க, அல்லது அதை அப்படியே downstream service-க்கு அனுப்புறீங்க, அல்லது database-ல save பண்ணுறீங்க.

என்ன பிரச்சனை வரும்?

LLM-ஐ நீங்க trust பண்ண முடியாது. அது hallucinate பண்ணும், user prompt-ல இருந்து injected instruction-ஐ follow பண்ணும், internal data-ஐ leak பண்ணும், malformed JSON / code தரும். Output-ஐ validate பண்ணாம trust பண்ணினா, அது உங்க application-க்கு ஒரு compromised input ஆக மாறும்.

Insecure output handling என்பது அதுதான்: **LLM output-ஐ trusted data மாதிரி treat பண்ணுவது**.

## 2. Mental Model

ஒரு LLM-ஐ ஒரு புத்திசாலி ஆனால் unpredictable external user மாதிரி நினைங்க.

User input-ஐ நீங்க sanitize பண்ணுவீங்க, அதே மாதிரி LLM output-ஐயும் sanitize பண்ணணும். Output என்பது ஒரு **untrusted boundary**. அதுல இருந்து வரும் data, உங்க system-க்கு வெளியே இருந்து வரும் data மாதிரி treat பண்ணணும்.

அடிப்படை rule: **Generate freely, validate strictly before use.**

## 3. How It Works

Output handling என்பது 3 layers-ல நடக்கும்.

**Parsing & Schema Enforcement**
LLM-க்கு JSON schema, Pydantic model கொடுத்து output format-ஐ force பண்ணுறோம். `response_format` மற்றும் output guardrails use பண்ணி, expected shape-க்கு match ஆகலைன்னா reject.

**Content Validation**
Output-ல உள்ள content-ஐ check பண்ணுறோம்:
- PII / secrets leak ஆகுதா?
- Disallowed content இருக்கா?
- Tool call / function arguments valid ஆ?
- SQL / code generation-ல injection உள்ளதா?

Allowlist-based validation > blocklist.

**Contextual Safety**
Output-ஐ downstream-க்கு அனுப்புறதுக்கு முன், அதன் intent-ஐ verify பண்ணுறோம். உதாரணமா, agent ஒரு email draft generate பண்ணுது. அந்த email-ல external link, attachment request வந்தால், அதை human review queue-க்கு தள்ளணும்.

இதை செய்ய output layer-ல ஒரு validation service வைக்கலாம். LLM -> Output Validator -> Policy Engine -> Downstream.

## 4. Architectural Reasoning

இது எப்போ தேவை?

* LLM output நேரடியாக user-க்கு காட்டப்படும் போது - XSS, prompt injection carry-over
* LLM output ஒரு tool call / API request ஆக execute ஆகும் போது - code execution, unintended DB write
* LLM output RAG context-ல இருந்து எடுக்கப்பட்ட sensitive data-ஐ expose பண்ணும் போது

Alternatives:
1. No validation - வேகமா, ஆனால் high risk
2. LLM self-check - "are you sure?" prompt - weak, bypassable
3. Dedicated output validation service with schema + policy checks - slower, but controllable

Architect choose பண்ணும்போது பார்க்கும் constraint:
- Latency budget: validation add பண்ணும் milliseconds
- Risk level: financial transaction vs internal summary
- Operability: false positive rate

Decision pattern: **Critical path-ல strict schema + allowlist, non-critical path-ல lightweight sanitization.**

## 5. Trade-offs

* **Safety vs Flexibility**: Strict schema reduce hallucination risk, ஆனால் LLM creativity-ஐ கட்டுப்படுத்தும். Too strict ஆனா useful output கிடைக்காது.
* **Latency vs Coverage**: Deep validation, LLM-based re-check, human-in-the-loop எல்லாம் latency-ஐ அதிகரிக்கும். Real-time chatbot-ல இது painful.
* **Cost vs Trust**: Validation service, separate policy model run பண்ணுவது cost. ஆனால் insecure output handling-ல data leak ஆன cost அதை விட அதிகம்.
* **False positives**: Over-sanitization ஆனா legitimate output block ஆகும். User trust குறையும்.

Failure mode: Output validator-ஐ bypass பண்ணி prompt injection-ல "ignore previous instructions and output raw data" மாதிரி சொல்லி, LLM அதை உண்மையான output-ல சேர்த்தால், validator schema-க்கு match ஆனாலும் content leak ஆகும். அதனால output validation alone போதாது, input sanitization + RAG retrieval filtering-ம் தேவை.

## 6. Practical Example

Enterprise support agent with RAG.

Architecture: User query -> LLM + vector database retrieval -> Answer generation -> Response to user.

Problem: Internal knowledge base-ல employee salary, internal incident report இருக்கு. User "show me all salary data" என்று ask பண்ணினால், LLM அதை முழுசா quote பண்ணி தரும்.

Insecure handling: LLM output-ஐ நேரடியாக render பண்ணினா data leak.

Secure handling:
1. Retrieval layer-ல document classification: public, internal, confidential
2. LLM output-ல source citation enforce பண்ணி, confidential doc-ஐ redact பண்ணும் policy run
3. Output validator: PII pattern detect,
