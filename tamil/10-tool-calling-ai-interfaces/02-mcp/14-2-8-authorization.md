# Authorization

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.8 — MCP

### 1. Problem

நீங்கள் ஒரு AI agent கட்டுகிறீர்கள். அந்த agent-க்கு MCP server மூலம் tool calling access கொடுக்கிறீர்கள். உதாரணமாக, `get_user_data`, `create_invoice`, `delete_record` போன்ற tools.

இப்போது கேள்வி: **எந்த user எந்த tool-ஐ எந்த resource-ல run பண்ணலாம்?**

Agent ஒரு proxy மாதிரி. Client request வந்ததும் agent tool-ஐ call பண்ணும். அந்த call-க்கு பின்னால் யார் உண்மையில் request பண்ணுகிறார்கள் என்பது மறைந்துவிடும்.

ஒரு customer support agent வந்து "என் order-ஐ cancel பண்ணுங்க" என்றால், அது agent வழியாக `delete_record` tool-ஐ தூண்டும். ஆனால் அந்த agent யாருக்காக பேசுகிறது? Alice-க்காகவா, Bob-க்காகவா? அந்த request-ஐ verify செய்யாமல் tool-ஐ run பண்ணினால் என்ன ஆகும்?

MCP server-கள் இன்று public internet-ல் expose ஆகிறது. Tool calling = remote code execution. Authorization இல்லாமல் இது direct security breach.

### 2. Mental Model

Authorization = **Who can do What on Which resource, Under which conditions**.

Authentication என்பது "நீ யார்?" Identity proof.
Authorization என்பது "நீ என்ன செய்ய அனுமதி உள்ளவன்?" Permission check.

MCP context-ல் இது மூன்று layer-ல் வரும்:

1. **Client → MCP Client**: User authenticated ஆ?
2. **MCP Client → MCP Server**: இந்த client-க்கு இந்த server-ஐ access செய்ய permission உள்ளதா?
3. **MCP Server → Tool Execution**: இந்த request-ல் வந்த user identity & scope-க்கு இந்த tool run ஆகலாமா?

Agent ஒரு middleman. அதனால் authorization context-ஐ propagate பண்ண வேண்டும். Agent request-ல் வந்த user identity-ஐ tool call-க்கு pass செய்ய வேண்டும்.

### 3. How It Works

MCP authorization-க்கு இப்போது common pattern OAuth 2.1 + capability-based scoping.

**Flow:**
Client login ஆகி access token பெறும். Token-ல் claims இருக்கும்: `sub=user_id`, `scope=tools:read,tools:write`, `tenant_id=acme`.

Agent இந்த token-ஐ MCP server-க்கு forward பண்ணும், மறைமுகமாக `Authorization: Bearer` header மூலமாக.

MCP server token-ஐ validate பண்ணி, request-ல் வந்த tool name & resource id-க்கு policy check செய்யும்.

Policy எப்படி இருக்கும்?
```
ALLOW user IF user.tenant_id == resource.tenant_id AND scope includes tools:write
DENY delete_record IF user.role != admin
```

Simple RBAC: Role Based Access Control.
More fine-grained: ABAC - Attribute Based Access Control. Example: user can read own orders only.

MCP spec-ல் `mcp-authorization` extension வழியாக token propagation support ஆகிறது. Server tool list-ஐ return பண்ணும் போதே user-க்கு தெரியும் permission என்ன என்பது.

### 4. Architectural Reasoning

ஏன் இது தேவை?

Tool calling AI interfaces-ல் agent க்கு பல tools access உண்டு. Agent ஒரே request-ல் பல tools-ஐ call பண்ணும். அந்த tools enterprise system-ஐ touch செய்யும்.

Constraint: Latency குறைவாக வேண்டும், ஆனால் security miss ஆகக்கூடாது.

Options:
1. **No auth on MCP server**: Dev environment-க்கு மட்டும். Production-ல் ஆபத்து.
2. **API Key per client**: Simple ஆனால் user-level audit இல்லை. Revoke பண்ண கஷ்டம்.
3. **OAuth + scoped tokens**: User identity propagate ஆகும், fine-grained control கிடைக்கும். Standard.

ஆர்கிடெக்ட் ஏன் OAuth தேர்வு செய்வார்? Because identity provider already உள்ளது, token lifecycle managed, audit trail கிடைக்கும்.

MCP server side-ல் authorization check-ஐ எங்கே வைக்க வேண்டும்?
Best: Server-ல் central policy engine. Tool handler-க்கு முன் check. இல்லையெனில் ஒவ்வொரு tool-லும் repeat ஆகும்.

### 5. Trade-offs

**Centralized vs Distributed policy**: Central policy engine clean ஆனால் latency சேர்க்கும். Distributed check fast ஆனால் consistency குறையும்.

**Scope granularity**: `tools:*` என்றால் simple. ஆனால் least privilege கிடைக்காது. Tool-level scope கொடுத்தால் management overhead அதிகம்.

**Token propagation complexity**: Agent request-ஐ forward பண்ணும் போது token leak ஆகாமல் பார்த்துக்கொள்ள வேண்டும். Agent itself compromised ஆனால் token misuse ஆகும்.

**Performance vs Security**: Every tool call-க்கு auth check செய்தால் latency + cost. Cache decision பண்ணலாம், ஆனால் cache invalidation முக்கியம்.

Failure mode: Token expire ஆனால் agent retry பண்ணி long-running operation-ஐ duplicate செய்யலாம். Idempotency + auth expiry handling தேவை.

### 6. Practical Example

Enterprise RAG + Agent system. User asks: "என் team-ன் Q3 sales report-ஐ generate பண்ணு".

Flow:
1. User logs in via IdP. Token-ல் `sub=user123`, `roles=analyst`, `team_id=sales-apac`.
2. Agent MCP client-க்கு token forward.
3. MCP server `generate_report` tool-ஐ list செய்யும். Policy check: analyst role can read sales data for own team only.
4. Agent tool-ஐ call பண்ணும், request payload-ல் `team_id=sales-apac` filter auto inject ஆகும்.
5. Server DB query run, result return.

இப்போது அதே user `delete_invoice` tool-ஐ call பண்ண முயற்சித்தால், scope-ல் இல்லாததால் server deny செய்யும். Audit log-ல் "user123 denied delete_invoice" record ஆகும்.

இது multi-tenant SaaS-ல் கட்டாயம்.

### 7. Reasoning Challenge

உங்களிடம் ஒரு MCP server உள்ளது. 1000+ internal tools expose செய்யப்பட்டுள்ளன. Agent pool பல teams பயன்படுத்துகிறது.

ஒரு team-ன் agent ஒரு tool-ஐ call பண்ணும் போது, அந்த tool வேறு tenant-ன் data-ஐ access செய்யக்கூடாது. Token propagation செய்யாமல் agent-ஐ trust பண்ணலாமா? அல்லது every tool call-க்கு user context enforce செய்ய வேண்டுமா? ஏன்?

நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்: API key per team or OAuth per user with ABAC? Cost & operability எப்படி balance பண்ணுவீர்கள்?

### 8. Key Takeaways

* Authorization என்பது identity-க்கு அடுத்த step. Tool calling-ல் user context propagate ஆகாவிட்டால் agent ஒரு security hole ஆகிவிடும்.
* MCP-ல் OAuth + scoped tokens + ABAC தான் production-ready pattern.
* Policy check-ஐ server side centralize செய்யுங்கள். Tool handler-ல் repeat பண்ணாதீர்கள்.
* Least privilege, auditability, revocation capability இவை architectural decision-ல் முக்கியம்.
