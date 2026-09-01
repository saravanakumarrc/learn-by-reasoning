# AI gateway

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.1 — Enterprise patterns

## 1. Problem

உங்கள் enterprise-ல 5 teams இருக்கு. எல்லாரும் LLM use பண்ண ஆரம்பிச்சிட்டாங்க.

- Team A: Customer support chatbot
- Team B: Internal RAG for knowledge base
- Team C: Code assistant for developers
- Team D: Finance summarization agent
- Team E: Marketing copy generation

எல்லாரும் நேரடியா OpenAI, Anthropic, Azure OpenAI, local model nu திறந்து call பண்ணுறாங்க.

என்ன problem வரும்?

1. API key எல்லா service-லயும் hardcode ஆகி இருக்கு. Rotation பண்ணனும்னா பயங்கரம்.
2. Cost tracking இல்லை. யாரு எவ்வளவு token use பண்றாங்கன்னு தெரியாது.
3. One model down ஆனா அந்த service முழுக்க down.
4. Prompt injection, PII leakage, data retention policy யார் enforce பண்றாங்க?
5. Rate limit, retry, timeout எல்லாம் ஒவ்வொரு team-ம் தனியா implement பண்றாங்க.

இது spaghetti integration ஆகிடும். Security, cost, governance எல்லாம் கட்டுப்பாடு இல்லாம போகும்.

இந்த pain point தான் AI gateway தேவைப்படுத்துகிறது.

## 2. Mental Model

AI gateway என்பது **உங்கள் applications-க்கும் LLM providers, model fleet-க்கும் இடையில் இருக்கும் ஒரு centralized control plane**.

ஒரு API router + policy enforcement point + observability layer மாதிரி நினைக்கவும்.

அனைத்து AI calls-ம் gateway வழியாக போகும். Gateway தான்:

- Authentication & authorization
- Routing to right model
- Rate limiting & quota
- Cost management
- Logging & audit
- Prompt sanitization & guardrails
- Fallback / retry logic

அனுமதிக்கும்.

ஒரு reverse proxy போல, ஆனால் AI-specific logic உடன்.

## 3. How It Works

Request flow simple:

`App -> AI Gateway -> Router/Policy -> Model Provider -> Gateway -> App`

Gateway இதை செய்கிறது:

**Routing:** Request-ன் context பார்த்து model தேர்வு செய்யும். 
`low-latency summarization` -> small fast model. 
`complex reasoning` -> large model.

**Policy enforcement:** PII detection, prompt injection filter, allow-list domains. Non-compliant request block.

**Caching & deduplication:** Same prompt 10 seconds முன் வந்திருந்தால் cache hit கொடு. Cost save.

**Observability:** Every request-க்கு `user_id, team_id, model, tokens, latency, cost, prompt, response` log ஆகும். இது audit & billing க்கு முக்கியம்.

**Resilience:** Provider down என்றால் automatic fallback to secondary provider or local model. Retry with exponential backoff.

## 4. Architectural Reasoning

AI gateway useful ஆகும் போது:

- **Multiple models/providers** இருக்கும் போது. Vendor lock-in தவிர்க்க.
- **Governance தேவை** இருக்கும் போது. Enterprise data compliance.
- **Cost control** தேவை போது. Token usage per team track பண்ணணும்.
- **Latency SLO** முக்கியம். Smart routing, caching.

Alternatives என்ன?

1. **Direct provider call:** Small startup க்கு OK. Team 1-2. Scale ஆனதும் chaos.
2. **Service mesh with custom filters:** Overkill, AI-specific logic இல்லை.
3. **Per-team SDK wrapper:** Duplication, inconsistent policy.

Gateway தேர்வு செய்யும் போது reason:

> "நாம் model-ஐ abstract பண்ணி, policy-ஐ centralize பண்ண வேண்டும். App team-கள் business logic மட்டும் பார்க்க வேண்டும், provider details கவலைப்படக்கூடாது."

## 5. Trade-offs

**Centralization vs Latency:** Gateway ஒரு extra hop. 10-30ms add ஆகும். Edge deployment or regional gateway-ல் mitigate பண்ணலாம்.

**Control vs Complexity:** Gateway operation, scaling, high availability தேவை. Gateway itself single point of failure ஆகும். Multi-region active-active தேவை.

**Flexibility vs Consistency:** Too strict policy innovation block பண்ணும். Too loose policy security risk. Balance தேவை.

**Cost visibility vs Overhead:** Logging every prompt/response storage cost அதிகம். PII masking, sampling தேவை.

Failure mode முக்கியம்: Gateway down ஆனால் அனைத்து AI features down. Circuit breaker, graceful degradation must.

## 6. Practical Example

Enterprise RAG + Agent platform.

Architecture:

`User App -> AI Gateway -> Router`

Router rules:
- `team = finance, sensitivity = high` -> route to private Azure OpenAI deployment, enable PII redaction, log to secure store.
- `team = support, prompt_type = summarization` -> route to cheap small model, cache enabled.
- `model = gpt-4, error rate >5%` -> fallback to claude-3.

Gateway also does:
- Prompt template injection: System prompt add பண்ணி brand voice enforce.
- Cost budget per team per day. Limit exceed ஆனால் block.
- Streaming response log, but redact credit card numbers.

இதனால் App team-க்கு code மாற்றம் zero. Only gateway base URL மாற்றம்.

## 7. Reasoning Challenge

உங்களிடம் 3 providers இருக்கு: OpenAI, Anthropic, self-hosted Llama.

Requirement:
1. Latency < 800ms for chat.
2. Cost per 1M tokens < $2 for non-critical traffic.
3. Sensitive data never leaves VPC.
4. Replay & audit for compliance.

இந்த constraints-க்கு gateway routing policy எப்படி design பண்ணுவீர்கள்? Model selection, fallback, data classification எப்படி handle பண்ணுவீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

- AI gateway என்பது integration point அல்ல, **governance and control plane**.
- Model abstraction & policy centralization தான் முக்கிய value.
- Cost, security, reliability ஆகியவை gateway-ல் solve ஆகும், ஆனால் latency மற்றும் operational complexity கூடும்.
- Gateway இல்லாமல் scale ஆனால் chaos, cost leak, compliance risk வரும்.
