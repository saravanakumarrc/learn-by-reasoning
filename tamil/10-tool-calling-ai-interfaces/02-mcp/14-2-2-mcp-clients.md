# MCP clients

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.2 — MCP

## 1. Problem

உங்களிடம் ஒரு LLM application இருக்கு. அது user-க்கு பதில் சொல்லணும். ஆனால் பதில் சொல்ல அது database-ல data எடுக்கணும், file system-ல file படிக்கணும், Slack-க்கு message அனுப்பணும், internal API-க்கு call பண்ணணும்.

இதை எப்படி செய்வீங்க?

இப்போது பெரும்பாலான teams இப்படி செய்கிறார்கள்:
LLM app-க்குள்ளயே ஒவ்வொரு tool-க்கும் hardcoded integration வைக்கிறார்கள். ஒரு tool வந்தால் code மாற்றம், deploy, test.

பிரச்சனை என்ன?
* App-ஐ விரிவாக்க முடியாது. New tool வந்தால் app-ஐ மீண்டும் பில்ட் பண்ண வேண்டும்.
* Tool-கள் வெவ்வேறு teams-ல் இருக்கும். ஒவ்வொரு tool-க்கும் API contract வேறுபடும்.
* LLM-க்கு "இந்த tool என்ன செய்யும், எப்படி call பண்ணுவது" என்று தெரிய வேண்டும். அந்த knowledge-ஐ எங்கே வைப்பது?
* Security, authentication, rate limiting ஒவ்வொரு tool-க்கும் தனியாக handle பண்ண வேண்டும்.

இந்த pain point வந்த பிறகுதான் MCP clients என்ற concept வருகிறது.

## 2. Mental Model

MCP = Model Context Protocol. இது LLM-க்கும் external tools-க்கும் ஒரு standard handshake.

நினைத்துக்கொள்ளுங்கள்: LLM என்பது ஒரு user. MCP client என்பது அந்த user-க்கான personal assistant. அந்த assistant-க்கு ஒரு toolbox இருக்கு. ஒவ்வொரு tool-ம் MCP server-ல் run ஆகிறது.

Client-ன் வேலை:
1. LLM-இல் இருந்து tool call intent-ஐ புரிந்துகொள்ளுதல்
2. எந்த MCP server-க்கு போக வேண்டும் என்பதை முடிவு செய்தல்
3. Tool call-ஐ சரியான server-க்கு forward செய்தல்
4. Result-ஐ LLM-க்கு திருப்பி கொடுத்தல்

MCP client = connector + router + session manager.

## 3. How It Works

ஒரு typical flow:

1. LLM ஒரு prompt-ஐ பெறுகிறது. `Get the latest order for customer 123 and send summary to Slack`
2. LLM தனது tool list-ல் இருந்து `get_order` மற்றும் `send_slack_message` தேவை என்பதை முடிவு செய்கிறது.
3. MCP client இந்த tool calls-ஐ intercept செய்கிறது.
4. Client, `get_order` tool எந்த MCP server-ல் இருக்கிறது என்பதை தெரிந்து, அந்த server-க்கு JSON-RPC call அனுப்புகிறது.
5. Server tool-ஐ execute செய்து result திருப்பி அனுப்புகிறது.
6. Client result-ஐ LLM-க்கு கொடுக்கிறது. LLM அடுத்த step-க்கு செல்கிறது.

MCP client வைத்திருக்கும் தகவல்:
* Server discovery: எந்த server எந்த tools-ஐ expose செய்கிறது
* Capability schema: tool name, parameters, description
* Session state: authentication token, transport connection

Transport வழக்கமாக stdio, SSE, அல்லது HTTP.

## 4. Architectural Reasoning

MCP client useful ஆகும் போது:
* நீங்கள் ஒரு LLM app-ல் பல tools-ஐ plug-and-play செய்ய விரும்பும்போது
* Tools வெவ்வேறு teams-ல் owned ஆக இருக்கும்போது
* Tool inventory அடிக்கடி மாறும், runtime-ல் add/remove ஆக வேண்டும்

Alternatives:
* Direct function calling with hardcoded SDKs: simple ஆனால் tightly coupled
* REST API gateway with manual mapping: flexible ஆனால் LLM-க்கு tool schema தெரியாது
* Agent framework with built-in tools: fast ஆனால் vendor lock-in

MCP client-ஐ தேர்வு செய்வது ஏன்?
* Decoupling: LLM app tool implementation-ஐ தெரிந்து கொள்ள வேண்டாம்
* Standard interface: Server side மட்டும் MCP-க்கு conform ஆக வேண்டும்
* Reusability: அதே MCP server-ஐ பல clients பயன்படுத்தலாம்

## 5. Trade-offs

**Complexity moves to client.** Client-க்கு discovery, routing, auth management, error retry போன்ற logic வரும். App simple ஆகும், client heavy ஆகும்.

**Latency adds up.** LLM -> Client -> Server -> Client -> LLM. Network hop அதிகம். Timeout மற்றும் retry strategy முக்கியம்.

**Trust boundary.** Client பல servers-க்கு connect ஆகிறது. ஒரு compromised server மூலம் LLM-க்கு malicious data வரலாம். Input validation, sandboxing தேவை.

**Session state.** MCP servers stateless ஆக இருக்கலாம், ஆனால் client session, token refresh, connection pooling manage செய்ய வேண்டும். Scale ஆகும்போது connection limit பிரச்சனை.

## 6. Practical Example

Enterprise RAG + Action Agent.

உங்களிடம் internal knowledge base, CRM, Jira, Slack tools உள்ளன. ஒவ்வொன்றும் தனித்தனி team-ல் உள்ளன.

நீங்கள் ஒரு MCP client-ஐ agent host-ல் வைக்கிறீர்கள். Start time-ல் client அனைத்து MCP servers-ஐ discover செய்கிறது:
* `knowledge-mcp-server` -> search_docs tool
* `crm-mcp-server` -> get_customer tool
* `jira-mcp-server` -> create_ticket tool

User கேட்கிறார்: `Customer 456-க்கு last order எது? அதுக்கு ticket create பண்ணு`

LLM tool plan செய்கிறது. Client routing செய்கிறது. CRM server-க்கு call போகிறது, result வந்தவுடன் Jira server-க்கு call போகிறது. App code-ல் எந்த server URL-ம் hardcode இல்லை. New tool வந்தால் server-ஐ add செய்தால் போதும்.

## 7. Reasoning Challenge

உங்களிடம் 20 MCP servers உள்ளன. அவை எல்லாம் different latency-ல் respond செய்கின்றன. சில servers slow ஆக இருக்கின்றன. LLM-க்கு tool call-ன் முடிவு காத்திருக்க வேண்டும்.

Client-ல் என்ன design செய்வீர்கள்? Timeout, retry, fallback, parallel calls எப்படி handle பண்ணுவீர்கள்? Tool call-ஐ fail ஆனால் LLM-க்கு என்ன signal கொடுப்பீர்கள்?

## 8. Key Takeaways

* MCP client என்பது LLM-க்கும் MCP servers-க்கும் இடையே உள்ள router + session manager.
* Problem solve செய்வது: tool integration-ஐ app code-ல் இருந்து decouple செய்தல்.
* Client design decisions: discovery, routing, auth, error handling, latency management.
* Every new abstraction adds hop latency and trust surface. Operability cost-ஐ underestimate பண்ணாதீர்கள்.
