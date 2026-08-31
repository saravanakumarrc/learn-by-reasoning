# MCP servers

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.3 — MCP

## 1. Problem

உங்களிடம் ஒரு LLM agent இருக்கு. அது user கேள்விக்கு பதில் சொல்ல வேண்டும்.

> "நேற்று நடந்த top 3 transactions-ஐ காட்டு"
> "இந்த customer-க்கு கடந்த மாத invoice PDF அனுப்பு"
> "Jira-ல open bugs எத்தனை?"

Agent-க்கு இதெல்லாம் செய்ய database, API, file system, ticketing tool access வேண்டும்.

ஒவ்வொரு tool-க்கும் agent-க்கு தனி integration எழுதினால் என்ன ஆகும்?

* ஒவ்வொரு LLM client-க்கும் tool logic repeat ஆகும்
* Auth, rate-limit, error handling எல்லாம் client-ல duplicate
* New tool வந்தால் agent code மாற்ற வேண்டும்
* Tool provider மாற்றினால் எல்லா agents-ஐயும் update செய்ய வேண்டும்

Pain point: **AI interface மற்றும் tool implementation இடையே tight coupling**.

இதை தீர்க்க தேவையானது ஒரு standard protocol.

## 2. Mental Model

MCP = Model Context Protocol.

அடிப்படை யோசனை simple: **Agent <-> Server என்ற separation**.

LLM client ஒரு standard way-ல tool-ஐ கேட்கும். MCP server ஒரு standard way-ல tool-ஐ expose செய்யும்.

இது USB-C போன்றது. Device மாறினாலும் cable standard அதே.

Agent-க்கு தெரியும்: `tools/list`, `tools/call` என்ற 2 calls.
Server-க்கு தெரியும்: அதே contract-ஐ implement செய்ய வேண்டும்.

இப்போது tool logic server-ல இருக்கு, agent generic ஆக இருக்கும்.

## 3. How It Works

MCP server என்பது ஒரு process, அது:

* `tools` expose செய்யும். ஒவ்வொரு tool-க்கும் name, description, input schema இருக்கும்.
* Agent `tools/list` கேட்டால் catalog தரும்.
* Agent `tools/call` செய்தால் server அந்த logic-ஐ run செய்து result திருப்பி தரும்.

Transport பொதுவாக stdio அல்லது HTTP + SSE. Authentication, resource, prompt என்ற extra capabilities உண்டு, ஆனால் core reasoning-க்கு tools முக்கியம்.

Flow:
`User -> LLM Client -> MCP Server -> Your DB/API -> Result -> LLM`

Server உங்கள் internal system-ஐ wrap செய்கிறது. Agent-க்கு internal details தெரிய வேண்டாம்.

## 4. Architectural Reasoning

எப்போது MCP server பயனுள்ளது?

* **Multiple agents, same tools**: Chatbot, coding agent, internal assistant எல்லாரும் ஒரே database tool-ஐ use பண்ண வேண்டும்.
* **Tool reuse across teams**: Data team ஒரு MCP server build செய்தால் product team agents எளிதாக consume செய்யலாம்.
* **Decoupling**: Tool owner server-ஐ evolve செய்யலாம், agent-ஐ touch செய்யாமல்.

Alternatives:
* Direct API integration in agent: fast for one-off, but duplicate.
* Custom tool registry per vendor: lock-in.
* Function calling with hardcoded tools: brittle.

MCP தேர்வு செய்யும் காரணம்: **standard interface, centralized tool governance**.

## 5. Trade-offs

**Standardization vs Flexibility**: MCP schema strict. Complex stateful workflows-க்கு awkward ஆகலாம். Custom protocol flexible, ஆனால் maintenance heavy.

**Latency**: Agent -> Server -> Backend என்ற extra hop. Network failure, timeout handle செய்ய வேண்டும். Retry logic முக்கியம்.

**Security & Trust**: Server-க்கு powerful access இருக்கும். Agent prompt injection மூலம் tool call trigger ஆகலாம். Server-ல authorization, input validation, rate limit கண்டிப்பாக வேண்டும். Never trust LLM output blindly.

**Operational Complexity**: ஒரு server down ஆனால் அதை depend செய்யும் எல்லா agents-ம் பாதிக்கும். Observability, logging, versioning தேவை.

## 6. Practical Example

Enterprise support agent.

Requirements: Customer data from Postgres, invoices from S3, tickets from Jira.

Architectural choice:
3 MCP servers build செய்யுங்கள்.

* `customer-mcp-server`: tools = `get_customer`, `list_recent_orders`
* `billing-mcp-server`: tools = `generate_invoice_pdf`, `send_invoice_email`
* `jira-mcp-server`: tools = `search_tickets`, `create_ticket`

LLM client இதை discover செய்து list செய்யும். User "என் கடைசி invoice அனுப்பு" என்றால் agent:
1. customer tool-ல ID கண்டுபிடி
2. billing tool-ல PDF generate
3. email tool-ல send

Tool logic server-ல இருப்பதால் agent simple ஆக இருக்கும். Billing team server-ஐ மாற்றினால் agent மாற்ற தேவையில்லை.

## 7. Reasoning Challenge

உங்களிடம் ஒரு internal RAG system இருக்கு. அது vector database-ல knowledge base search செய்கிறது. இப்போது 3 different agents: customer support chatbot, sales copilot, internal analyst assistant. எல்லாருக்கும் same search தேவை.

Option A: ஒவ்வொரு agent-லும் RAG code copy பண்ணுவது.
Option B: ஒரு `knowledge-mcp-server` உருவாக்கி `search_knowledge` tool expose செய்வது.

நீங்கள் B தேர்வு செய்தால் என்ன new problem வரும்? அதை எப்படி handle செய்வீர்கள்?

## 8. Key Takeaways

* MCP server என்பது tools-ஐ standardize செய்து agent-களுக்கு expose செய்யும் boundary.
* Problem solve செய்வது coupling அல்ல, reuse மற்றும் governance.
* Server-ல security, validation, observability மிக முக்கியம்.
* Every new hop = latency + failure mode. Trade-off accept செய்து தான் architecture தேர்வு செய்ய வேண்டும்.
