# Security

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.9 — MCP

## 1. Problem

நீங்கள் ஒரு LLM agent-ஐ build பண்ணிட்டீர்கள். அது Tool Calling மூலம் external tools-ஐ use பண்ண வேண்டும். Database query, file read, payment gateway, internal API எல்லாம்.

ஒரு பிரச்சனை: AI model-க்கு நேரடியாக tool access கொடுத்தால் என்ன ஆகும்?

Model ஒரு prompt-ல இருந்து instruction எடுத்துக்கிட்டு, user-க்கு தேவையில்லாத tool-ஐ call பண்ணலாம். Sensitive data-வை leak பண்ணலாம். Unauthorized action எடுக்கலாம்.

இப்போது tool-களை expose பண்ணும் layer தேவை. அந்த layer என்ன tools available, யாருக்கு access, எப்படி authenticate, எப்படி authorize, எப்படி audit என்பதை கட்டுப்படுத்த வேண்டும்.

MCP - Model Context Protocol - இந்த gap-ஐ solve பண்ண வந்தது. ஆனால் protocol வந்தாலும் security problem மறைந்துவிடாது. Tool access-ஐ safe-ஆக கொடுப்பது architect-ன் பிரச்சனை.

> What problem became painful enough? Agent-கள் வளர்ந்தால், tools எண்ணிக்கை அதிகரிக்கும். ஒவ்வொரு client-க்கும் ஒவ்வொரு permission set. ஒரு central security model இல்லாமல் chaos ஆகும்.

## 2. Mental Model

MCP client = AI agent / LLM host
MCP server = Tool provider

Client server-ஐ connect பண்ணி list tools, call tools பண்ணும்.

Security-ல மூன்று layer நினைக்கவும்:

**Transport security** - Connection safe-ஆ இருக்கா? TLS?
**Authentication** - யார் connect பண்ணுகிறார்கள்?
**Authorization** - இந்த client-க்கு எந்த tool-ஐ call பண்ண அனுமதி இருக்கு?

ஒரு bank-ல teller-க்கு vault key கொடுக்க மாட்டீர்கள். அதே logic.

## 3. How It Works

MCP itself security protocol அல்ல. அது transport + auth extension-ஐ support பண்ணும்.

Typical secure MCP setup:

`LLM App -> MCP Client -> Auth Proxy / Gateway -> MCP Server`

Gateway-ல ஆகும் வேலை:

* Client identity verify பண்ணுது - API key, OAuth token, mTLS
* Tool allow-list check பண்ணுது - இந்த client-க்கு இந்த tool மட்டும்
* Input validation & output sanitization பண்ணுது
* Audit log எழுதுது

MCP server-க்குள் ஒவ்வொரு tool-க்கும் schema இருக்கும். Gateway அதை inspect பண்ணி policy enforce பண்ணும்.

## 4. Architectural Reasoning

MCP security எப்போது தேவை?

* Multiple tenants share same tool servers
* Tools sensitive operations பண்ணும் - DB write, payment
* Tools external exposure ஆகும் - remote MCP server
* Compliance audit தேவை

Alternative என்ன?

**Direct tool integration**: LLM app-ல tool logic embed பண்ணுவது. Small scale-ல work ஆகும். Tools அதிகமானால் code மெச்சுப்பிழப்பாகும். Security policy centralize பண்ண முடியாது.

**API Gateway pattern**: Traditional REST gateway + auth. Works but LLM-க்கு tool discovery dynamic-ஆ தேவை. MCP அதை standardize பண்ணுகிறது.

Architect choose MCP + gateway when tool ecosystem grow பண்ண வேண்டும், different teams tools publish பண்ண வேண்டும், and security policy centralize பண்ண வேண்டும்.

## 5. Trade-offs

**Trust boundary expand ஆகிறது**: Model output-ஐ blind-ஆ trust பண்ண முடியாது. Prompt injection மூலம் model malicious tool call generate பண்ணலாம். Gateway input validation critical.

**Latency**: Auth check, policy evaluation, audit log எல்லாம் request path-ல add ஆகும். High throughput tool-க்கு caching auth decision பயன்படும்.

**Complexity vs safety**: Simple local MCP server-க்கு auth இல்லாமல் இருக்கலாம். ஆனால் production-ல network-ல expose ஆனதும் auth mandatory.

**Least privilege hard to maintain**: Tool allow-list per client dynamic-ஆ மாறும். Policy as code, versioned config வேண்டும். இல்லாவிட்டால் drift ஆகும்.

Failure mode: Gateway down ஆனால் all tool access stop ஆகும். High availability design வேண்டும். Fail-open செய்யக்கூடாது.

## 6. Practical Example

Enterprise RAG agent. Employees ask internal docs, run SQL, create Jira tickets.

Architecture:

`Employee -> LLM App -> MCP Client -> Auth Gateway -> [Doc MCP Server, SQL MCP Server, Jira MCP Server]`

Gateway policy:

* Engineering team: SQL read-only, Jira create allowed
* Sales team: Doc read only, SQL no access
* Everyone: Doc read allowed

Client authenticate via OAuth token from corporate IdP. Gateway token validate பண்ணி tenant + team extract பண்ணும். Tool call முன் policy engine check பண்ணும். Tool name + arguments audit log-ல save ஆகும்.

SQL server tool `run_query` accept பண்ணும். Gateway argument-ல `DROP TABLE` இருந்தால் block பண்ணும். Output-ல PII இருந்தால் mask பண்ணும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு public MCP server இருக்கு, அது customer data read பண்ணும். 100+ internal agents connect பண்ண வேண்டும். Some agents production, some dev. Network-ல exposed.

இங்கே auth, authorization, transport என்ன தேர்வு செய்வீர்கள்? Gateway fail-open ஆகவா இல்லை fail-closed ஆகவா இருக்க வேண்டும்? ஏன்?

## 8. Key Takeaways

* MCP protocol-ஐ secure பண்ணுவது transport + authentication + authorization layers மூலம் தான், protocol மட்டும் அல்ல
* Tool access-ஐ central gateway மூலம் control பண்ணுவது auditability, least privilege, input validation-க்கு கட்டாயம்
* Model output-ஐ trusted input-ஆ consider பண்ணாதீர்கள். Prompt injection always possible
* Security decision-ல fail-closed தான் default. Availability-க்காக safety-ஐ sacrifice பண்ணாதீர்கள்
