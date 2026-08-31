# Authentication

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.7 — MCP

## 1. Problem

MCP server-களை tool calling-க்கு expose பண்ணும்போது ஒரு பெரிய கேள்வி வரும்: யார் இந்த tool-ஐ call பண்ணலாம்? 

ஒரு AI agent client-ல இருந்து MCP server-க்கு request வருது. அந்த request உண்மையா உன் user-டதா? அல்லது spoof பண்ணப்பட்டதா? Server ஒரு database write, payment, internal API call மாதிரி sensitive tool-களை வச்சிருந்தா, authentication இல்லாமல் யார் வேணும்னாலும் அதை trigger பண்ண முடியும்.

Tool Calling & AI Interfaces path-ல, MCP என்பது ஒரு interface protocol. Interface இருந்தால், identity முக்கியம். இல்லைன்னா trust boundary முற்றிலும் காணாமல் போகும்.

## 2. Mental Model

Authentication = **"Who are you?"** என்பதை verify பண்ணுவது.

MCP-ல இரண்டு பக்கம் இருக்கு:

1. **Client authentication**: Agent/client-ஐ server அடையாளம் காணும். இது token, API key, OAuth மூலம் நடக்கும்.
2. **User delegation**: Agent behalf-ல user-ன் permission-ஐ server பார்க்கும். Agent-க்கு user context தெரியும், அதை server-க்கு prove பண்ண வேண்டும்.

மனதில் வைக்க வேண்டிய model: MCP connection என்பது ஒரு trusted channel அல்ல. Network-ல வரும் எந்த request-உம் untrusted. Server எப்போதும் **verify then trust** பண்ண வேண்டும்.

## 3. How It Works

MCP spec-ல built-in auth முழுமையாக கட்டாயமில்லை. Transport-க்கு பொறுத்து authentication வருகிறது.

**stdio transport**: Local process. Usually same machine trust. Authentication குறைவு.

**SSE / HTTP transport**: Remote. இங்கே auth தேவை.

Practical pattern:
Client → HTTP request with `Authorization: Bearer <token>` → MCP server validates token → tool execution.

Token எப்படி வரும்?
* Static API key: Simple, rotate பண்ண வேண்டும்.
* OAuth 2.0 / OpenID Connect: User identity + scope-based access. Enterprise-க்கு இதுவே standard.
* mTLS: Service-to-service trust.

MCP server tool list-ஐ return பண்ணும்போதும், tool call execute பண்ணும்போதும், same auth check apply ஆகும். Auth pass ஆனால் மட்டுமே tool metadata expose ஆகும்.

## 4. Architectural Reasoning

**When does auth become painful?**

* Multiple clients same MCP server-ஐ use பண்ணும்போது.
* Multi-tenant setup: Customer A-க்கு tool X தெரியும், Customer B-க்கு தெரியக்கூடாது.
* Agent orchestrator different teams own பண்ணும்போது.

**Constraint**: Latency. Auth check ஒவ்வொரு tool call-க்கும் செய்ய வேண்டும். Token validation fast இருக்க வேண்டும். அதனால் JWT with local verification பொதுவாக பயன்படுத்தப்படுகிறது.

**Alternatives**:
* No auth: Dev/test மட்டும்.
* Network-level auth: VPN / private network. Simple ஆனால் fine-grained control இல்லை.
* API Gateway in front of MCP: Gateway auth பண்ணி, internal header pass பண்ணும். Operability எளிது.

Architect choose பண்ணும்போது கேட்க வேண்டியது: **Who needs to prove who they are?** Client identity மட்டுமா, end user identity வேண்டுமா? Scope மட்டும் போதுமா, audit trail வேண்டுமா?

## 5. Trade-offs

* **Security vs Latency**: Token introspection remote call செய்தால் secure ஆனால் slow. Local JWT verify fast ஆனால் revocation சிக்கல்.
* **Simplicity vs Granularity**: API key simple. OAuth complex ஆனால் user-level delegation, scope, revocation தரும்.
* **Centralized vs Decentralized auth**: Auth service centralize பண்ணினால் operational burden குறையும், single point of failure வரும்.
* **Stateless vs Stateful**: Stateless token scale easy. Stateful session revocation easy.

Failure mode: Token leak ஆனால் attacker எல்லா tools-ஐயும் call பண்ண முடியும். அதனால் short expiry + refresh token + scope restriction முக்கியம்.

## 6. Practical Example

Enterprise RAG system: Internal MCP server வைத்திருக்கிறது. Tools: `search_internal_docs`, `create_jira_ticket`, `run_sql_readonly`.

Three clients: Customer support agent, Developer agent, Finance agent.

Architect decision:
MCP server behind API Gateway. Gateway OAuth2 client credentials flow use பண்ணி client authenticate பண்ணும். Token-ல `client_id` + `scopes` இருக்கும்.

Support agent-க்கு scope `docs:read` மட்டும். Developer agent-க்கு `docs:read, jira:write`. Finance agent-க்கு `docs:read, sql:readonly`.

Server tool call வரும்போது, token validate பண்ணி, requested tool-க்கு scope match ஆகிறதா என்று check பண்ணும். Match இல்லைன்னா 403.

Audit log-ல `who called what tool with which user context` store பண்ணும்.

இதனால் ஒரு agent compromise ஆனாலும் blast radius குறைவு.

## 7. Reasoning Challenge

உங்களிடம் ஒரு public MCP server இருக்கு. 100+ third-party AI apps அதை consume பண்ணும். சில tools read-only, சில tools write. Rate limit வேண்டும். Token revocation immediate ஆக வேண்டும்.

நீங்கள் static API key use பண்ணலாமா? OAuth with introspection use பண்ணலாமா? JWT with short expiry + revocation list use பண்ணலாமா?

எந்த architecture தேர்வு செய்வீர்கள்? Latency, revocation, operational complexity எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* MCP server-க்கு auth என்பது optional spec, ஆனால் production-ல mandatory.
* Auth question எப்போதும் **who** மற்றும் **what can they do** என்பதே.
* Client authentication வேறு, user delegation வேறு. Tool calling-ல இரண்டும் mix ஆகும்.
* Every auth decision creates trade-off between security, latency, operability. Short-lived token + scope + gateway pattern பெரும்பாலும் போதுமானது.
