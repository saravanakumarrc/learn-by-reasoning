# Prompts

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.6 — MCP

## 1. Problem

உங்களிடம் ஒரு AI agent இருக்கு. அது LLM use பண்ணுது. Agent-க்கு real world-ல data தேவை: database query பண்ணணும், file read பண்ணணும், weather API call பண்ணணும், internal CRM-ல customer தேடணும்.

இதுவரை என்ன பண்ணுவீங்க? Agent code-க்குள்ளேயே ஒவ்வொரு tool-க்கும் hard-code பண்ணுவீங்க. New tool வந்தா code change, redeploy, test, release.

இப்போ 5 different teams 5 different tools build பண்ணுது. Agent team எப்போவும் wait பண்ணனும். Tool schema மாறினாலும் agent break ஆகும்.

What goes wrong? **Tight coupling, vendor lock-in, no standard interface.**

இந்த pain தான் MCP-க்கு காரணம்.

## 2. Mental Model

MCP = Model Context Protocol. 

Simple mental model: **LLM-க்கும் tools-க்கும் இடையே ஒரு standard socket.**

எப்படி USB-C எல்லா device-க்கும் common port கொடுத்ததோ, அதே மாதிரி MCP எல்லா AI client-க்கும் எல்லா tool/server-க்கும் common protocol கொடுக்குது.

Agent asks: "என்ன tools உன்னிடம் இருக்கு?"
MCP server answers: list of tools, அவங்க input schema, description.

Agent chooses tool, MCP protocol-ல request அனுப்புது. Server execute பண்ணி result திருப்பி அனுப்புது.

No custom integration per tool.

## 3. How It Works

MCP இரண்டு முக்கிய pieces:

**MCP Client** - LLM host-ல இருக்கும். Claude Desktop, Cursor, VS Code, custom agent framework. இது agent-ன் request-ஐ handle பண்ணி MCP server-க்கு forward பண்ணும்.

**MCP Server** - ஒவ்வொரு tool-க்கும் ஒரு lightweight server. Local process ஆக இருக்கலாம், அல்லது remote HTTP server ஆக இருக்கலாம்.

Communication: stdio, SSE, HTTP. JSON-RPC based.

Flow:
1. Client server-ஐ discover பண்ணுது
2. `tools/list` call பண்ணி available tools எடுக்குது
3. LLM decides which tool call பண்ணனும்
4. Client `tools/call` request அனுப்புது
5. Server tool execute பண்ணி result திருப்பி தருது
6. LLM result-ஐ use பண்ணி next step decide பண்ணுது

Context, resources, prompts என்று மூன்று capabilities இருக்கு. ஆனால் architect-க்கு முக்கியம் tools.

## 4. Architectural Reasoning

MCP useful ஆகும் போது:

* Multiple tools from different teams, different lifecycles
* Tools dynamic-ஆ add/remove ஆகணும்
* Agent-க்கு tool discovery தேவை
* Standard contract வேணும், not custom SDK per tool

Constraints it solves:
* **Coupling**: Agent code-ல tool integration இல்லை
* **Discoverability**: Agent run time-ல tools list பண்ண முடியும்
* **Interoperability**: Different clients same server use பண்ணலாம்

Alternatives:
* Direct function calling / tool calling via OpenAI API - works, ஆனால் vendor specific, custom integration
* Custom REST gateway per tool - works, ஆனால் schema management, auth handling manual
* Agent framework internal registry - team size small இருக்கும் வரை okay

MCP choose பண்ணுவது ஏன்? Standardization cost-ஐ pay பண்ணி long term coupling-ஐ குறைக்க.

## 5. Trade-offs

**Pros**
* Decoupling: Tool team agent team-ஐ block பண்ணாது
* Reuse: ஒரே MCP server பல clients-க்கு work ஆகும்
* Rapid iteration: Server update ஆனாலும் agent redeploy தேவையில்லை

**Cons / Trade-offs**
* **Latency**: Extra hop, serialization. Local stdio okay, remote HTTP add network roundtrip
* **Security boundary**: MCP server என்ன access கொடுக்குதுன்னு trust வேணும். Agent தப்பான tool call பண்ணா data leak ஆகும். Authentication, authorization, scope control முக்கியம்
* **Error handling**: Server down ஆனால் agent stuck. Retry, timeout, fallback தேவை
* **Schema drift**: Tool description மாறினால் LLM hallucinate பண்ணும். Versioning தேவை
* **Complexity**: Small system-க்கு overkill. 2-3 tools இருந்தா direct integration எளிது

Failure mode: MCP server crash ஆனால் agent-க்கு tool unavailable. Agent should degrade gracefully, not fail completely.

## 6. Practical Example

Enterprise support agent.

Agent needs: CRM search, Ticket create, Knowledge base search, Slack notify.

4 different teams own these.

Without MCP: Agent repo-ல 4 integrations hard-coded. Each team release பண்ணும் போது agent team-ஐ involve பண்ணனும்.

With MCP:
* CRM team runs MCP server exposing `crm_search_customer`, `crm_update_ticket`
* KB team runs MCP server exposing `kb_search`
* Slack team runs MCP server exposing `slack_send_message`

Agent client starts, discovers 4 servers, gets tools list. User asks "Customer 12345-ன் last 3 tickets என்ன?"

LLM reasons: first `crm_search_customer` call பண்ணனும். Calls via MCP. Result வந்ததும் next tool decide பண்ணும்.

New tool வந்தா? `billing_check` MCP server deploy பண்ணினால் போதும். Agent automatically sees it. Zero code change.

## 7. Reasoning Challenge

உங்களிடம் internal AI agent இருக்கு. அது production database-க்கு direct access கொடுக்கும் MCP server உடன் connect ஆகி இருக்கு.

Security team கேட்குது: agent தவறுதலாக `DROP TABLE` போன்ற destructive query run பண்ணலாம்.

இந்த architecture-ல என்ன risk இருக்கு? MCP protocol level-ல என்ன controls போடுவீங்க? Tool design level-ல எப்படி mitigate பண்ணுவீங்க?

## 8. Key Takeaways

* MCP = LLM-க்கும் tools-க்கும் standard interface. Integration cost-ஐ குறைக்க.
* Tool discovery + schema contract தான் core value, not protocol magic.
* Decoupling கொடுக்கும், ஆனால் latency, security, operational complexity சேர்க்கும்.
* Small, stable toolset-க்கு MCP overkill. Large, multi-team, evolving ecosystem-க்கு மதிப்பு.
* Architect decision: Standardize early if you expect >3 teams and frequent tool churn.
