# Tools

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.5 — MCP

### 1. Problem

உங்க AI agent-க்கு வெளி world உடன் பேச வேண்டும். Database-ஐ query பண்ணனும், file system-ல read/write பண்ணனும், internal tools, third-party APIs call பண்ணனும்.

இப்போ பிரச்சனை என்ன?

ஒவ்வொரு tool-க்கும் ஒரு custom integration எழுதுறீங்க. ஒரு LLM provider மாறினாலும், agent framework மாறினாலும், அதே integration மறுபடியும் மாற்ற வேண்டும்.

Agent-க்கு "என்ன tools உள்ளன, அது எப்படி use பண்ணுவது" என்று தெரிய வேண்டும். ஆனால் tool implementer-க்கும் agent builder-க்கும் ஒரு common contract இல்லை.

இதனால் vendor lock-in, duplicate work, security sprawl. ஒரு service team ஒரு tool build பண்ணினால், ஒவ்வொரு agent team-மும் அதை தனியாக consume பண்ண வேண்டியிருக்கு.

> What problem became painful enough? Tool integration chaos and lack of standard interface between LLM agents and external capabilities.

### 2. Mental Model

MCP = Model Context Protocol.

இது LLM agent-க்கும் external tools-க்கும் இடையே ஒரு standard socket போன்றது.

Tool provider ஒரு MCP server-ஐ expose பண்ணுவார். Agent client அதனுடன் connect ஆகி, tools list, schema, call பண்ணுவார்.

அனாலஜி: USB-C. Device என்ன charger-ஐயும், monitor-ஐயும் connect பண்ணலாம். ஒரே port, ஒரே protocol. MCP க்கு tool-க்கு USB-C போல.

### 3. How It Works

MCP ஒரு protocol, implementation language agnostic.

Basics:

* **Transport**: stdio, SSE, HTTP. Local tools-க்கு stdio, remote-க்கு SSE/HTTP.
* **Server**: Tool capabilities-ஐ expose பண்ணும் process. `tools/list`, `tools/call` என்ற JSON-RPC methods.
* **Client**: Agent host. Server-ஐ discover பண்ணி, tools-ஐ invoke பண்ணும்.
* **Resources & Prompts**: Tools மட்டுமல்ல, context data மற்றும் reusable prompts-ஐயும் expose பண்ணலாம்.

Flow:
1. Agent MCP client start ஆகும்.
2. Server-ஐ connect பண்ணி capability handshake.
3. Agent `tools/list` கேட்கும். Server JSON schema-டோடு tool definitions தரும்.
4. LLM அந்த schema பார்த்து reasoning பண்ணி `tools/call` decision எடுக்கும்.
5. Client server-க்கு call அனுப்பும், result-ஐ LLM-க்கு திருப்பி கொடுக்கும்.

No custom SDK per tool. ஒரே protocol.

### 4. Architectural Reasoning

**When useful?**

* Multi-agent system where tools frequently change
* Internal platform teams tools-ஐ expose செய்து, multiple AI apps consume பண்ண வேண்டும்
* You want tool discovery and versioning decoupled from agent code
* Security boundary clear வேண்டும்: tool access audited, scoped

**Constraint it addresses:** Integration complexity and coupling.

Alternatives:
* Direct API integration in agent code: tight coupling, high maintenance
* Function calling with hard-coded schemas: works for one LLM, brittle
* Custom middleware per provider: scales poorly

MCP-ஐ தேர்ந்தெடுக்கும் architect இதை பார்க்கிறார்: tool ecosystem ஐ productize பண்ண வேண்டும், not one-off integration.

### 5. Trade-offs

* **Standardization vs Flexibility:** Protocol limits how exotic a tool can be. Real world tools often need streaming, auth, long-running tasks. MCP handles basic patterns, complex patterns need extensions.
* **Latency:** Extra hop via MCP server. Local stdio fine, remote SSE adds network roundtrip.
* **Security surface:** Server-ஐ expose பண்ணினால், tool என்பது agent-க்கு remote code execution gateway ஆகும். Authentication, authorization, rate limiting, input validation critical.
* **Operational complexity:** Now you run and monitor MCP servers. One more moving part. Health checks, versioning, schema drift.

Failure modes:
* Schema mismatch → LLM calls wrong parameter
* Server down → agent blind
* Tool side effects non-idempotent → duplicate calls on retry

### 6. Practical Example

Enterprise support agent.

MCP server 1: CRM DB read-only. Tools: `get_customer_tickets`, `get_order_history`.
MCP server 2: Internal Knowledge Base. Tool: `search_docs`.
MCP server 3: Slack. Tool: `post_message_to_channel`.

Agent client connects to all three servers at startup. LLM user query "Ravi Kumar-க்கு last 3 orders என்ன status?" என்றால், agent tools list-ஐ பார்த்து `get_customer_tickets` + `get_order_history` call பண்ணும். Result-ஐ synthesize பண்ணி answer தரும்.

New tool வந்தால், e.g., Billing API, you just deploy new MCP server with schema. Agent auto discover பண்ணி use பண்ண ஆரம்பிக்கும். Agent code மாற்ற தேவையில்லை.

### 7. Reasoning Challenge

உங்களிடம் ஒரு financial agent இருக்கு. அது trading tool-ஐ call பண்ண வேண்டும். Tool call 2 seconds எடுக்கும், மற்றும் side effect உண்டு. Agent retry logic உள்ளது.

MCP மூலம் இந்த tool-ஐ expose பண்ண வேண்டும். 
என்ன architectural safeguards வைப்பீர்கள்? Idempotency, auth, timeout, user confirmation எப்படி handle பண்ணுவீர்கள்? MCP server-ஐ agent-இலிருந்து எப்படி isolate பண்ணுவீர்கள்?

### 8. Key Takeaways

* MCP tool integration-ஐ standardize பண்ணும், agent-ஐ tools-லிருந்து decouple பண்ணும்.
* Problem solve பண்ணுவது: duplicate integrations, vendor lock-in, discovery chaos.
* Trade-off: standardization gain க்கு பதிலாக operational overhead, security boundary, latency add ஆகும்.
* Architect முடிவு: tool ecosystem ஐ productize பண்ண வேண்டுமா? அப்போது MCP மதிப்புள்ளது.
