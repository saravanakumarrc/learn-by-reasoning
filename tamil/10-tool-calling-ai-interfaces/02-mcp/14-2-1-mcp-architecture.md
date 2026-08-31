# MCP architecture

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.1 — MCP

## 1. Problem

உங்களிடம் ஒரு LLM agent இருக்கு. அது user கேள்விக்கு பதில் சொல்ல userக்கு மட்டும் போதாது. அது database-ஐ query பண்ணணும், file system-ல படிக்கணும், API-க்கு call பண்ணணும், internal tool-ஐ use பண்ணணும்.

இப்போ problem என்ன?

ஒவ்வொரு tool-க்கும் ஒரு custom integration எழுதணும். ஒரு tool புதுசா வந்தா, agent code-ஐ மாற்றணும், redeploy பண்ணணும். LLM provider மாறினா, tool calling format மாறும். ஒரே tool-ஐ 5 different agents use பண்ணனும்னா 5 தடவை wrapper எழுதணும்.

> What goes wrong? Integration sprawl. Tight coupling between agent logic and tools. No standard contract.

இந்த pain தான் MCP-ஐ பிறக்க வச்சது.

## 2. Mental Model

MCP = Model Context Protocol.

இது LLM-க்கும் external tools-க்கும் இடையில் ஒரு standard socket மாதிரி.

Agent ஒன்னு பேசுறது MCP client. Tool ஒன்னு பேசுறது MCP server. இடையில் ஒரு protocol, JSON-RPC over stdio / HTTP / SSE.

அனலஜி: USB-C. Phone, laptop, monitor எல்லாம் வெவ்வேறு. ஆனா cable ஒன்னு போதும். Tool என்பது peripheral, Agent என்பது host. MCP தான் cable spec.

## 3. How It Works

MCP ஒரு client-server model.

**MCP Server**: ஒரு tool / data source-ஐ expose பண்ணும். அது `tools`, `resources`, `prompts` ஐ list பண்ணும்.

`tools` = function call செய்யக்கூடியது. `get_user`, `create_invoice` மாதிரி.
`resources` = read-only data. file, DB row, URL.
`prompts` = reusable prompt template.

Server ஒரு manifest கொடுக்கும்: name, description, input schema.

**MCP Client**: Agent இருக்கும் இடம். அது server-ஐ discover பண்ணி connect ஆகும். LLM tool call செய்யணும்னா, client அதை MCP server-க்கு forward பண்ணும். Result-ஐ திரும்ப LLM-க்கு கொடுக்கும்.

Communication simple:
1. Client `tools/list` கேட்கும்
2. LLM அந்த list பார்த்து decide பண்ணும் எந்த tool use பண்ணனும்
3. Client `tools/call` செய்யும்
4. Server execute பண்ணி result திருப்பும்

Protocol transport agnostic. Local dev-ல stdio. Remote-ல HTTP + SSE.

## 4. Architectural Reasoning

MCP useful ஆகும் போது:

* Agent க்கு multiple heterogeneous tools தேவைப்படும் போது
* Tools frequently add / remove ஆகும் போது
* Same tool-ஐ multiple agents / LLM providers use பண்ணனும் போது
* You want tool discovery without code change

Constraint it addresses: Integration coupling and vendor lock-in.

Alternative என்ன?
* Direct tool calling with OpenAI function calling / Anthropic tools. ஆனா அது provider specific, custom integration.
* Custom REST API wrapper per tool. ஆனா schema, auth, retry எல்லாம் நீங்க manage பண்ணனும்.
* LangChain tools. Framework lock-in.

MCP choose பண்ணுவது ஏன்? Standardization. Tool provider ஒரு முறை MCP server build பண்ணினா, எந்த MCP client-ம் use பண்ணலாம்.

## 5. Trade-offs

**Decoupling vs Latency**: Standard protocol layer சேர்க்கும். Extra hop உண்டு. Local stdio fast. Remote HTTP add latency.

**Discovery vs Governance**: Tools auto discover ஆகும். ஆனா security ரொம்ப முக்கியம். Any server connect ஆனா sensitive operation செய்யலாம். Need auth, allowlist, scope.

**Simplicity vs Expressiveness**: MCP schema simple. Complex streaming, long-running tasks, multi-step workflows அதுக்கு extra handling தேவை.

**Failure modes**:
* Tool server crash ஆனா agent blind ஆகும். Client should have timeout + fallback.
* Schema mismatch: LLM hallucinate parameter. Server validation must be strict.
* Version drift: Server tool signature மாறினா, client cache outdated.

## 6. Practical Example

Enterprise support agent.

Agent-க்கு தேவை: CRM database read, internal knowledge base search, ticket creation API, Slack notify.

இல்லாமல்: Agent code-ல நாலு custom connectors.

MCP-ல: ஒவ்வொரு system-க்கும் ஒரு MCP server.

* `crm-mcp-server` exposes `get_customer`, `get_orders`
* `kb-mcp-server` exposes `search_docs`
* `zendesk-mcp-server` exposes `create_ticket`
* `slack-mcp-server` exposes `send_message`

Agent is MCP client. Startup-ல எல்லா server-ஐயும் connect பண்ணும், tools list collect பண்ணும். User query வரும் போது LLM decide பண்ணும்: "நான் முதல் customer தேடுவேன், பிறகு orders பார்ப்பேன்". Tool calls MCP வழியாக போகும்.

New tool வேண்டுமா? New MCP server deploy பண்ணு. Agent restart வேண்டாம், auto discover.

## 7. Reasoning Challenge

உங்களிடம் ஒரு financial agent இருக்கு. அது production-ல sensitive DB write செய்யும். நீங்கள் third-party MCP server-ஐ use பண்ணலாமா?

என்ன risks இருக்கு? MCP server-ஐ எப்படி trust பண்ணுவீர்கள்? Network transport-ல என்ன security controls வைப்பீர்கள்? Agent-க்கு tool call செய்ய permission model எப்படி வேண்டும்?

## 8. Key Takeaways

* MCP என்பது LLM-க்கும் tools-க்கும் இடையே standard contract, integration sprawl-ஐ குறைக்கிறது.
* Server = tool capability expose, Client = agent side. Discovery + schema driven.
* Decoupling கிடைக்கும், ஆனா latency, security, governance trade-off வரும்.
* Architect முடிவு: Tool ecosystem scale ஆகும்போது standardization மதிப்பு அதிகம்.
