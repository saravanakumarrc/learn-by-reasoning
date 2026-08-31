# Enterprise MCP architecture

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.10 — MCP

## 1. Problem

உங்களிடம் ஒரு enterprise environment இருக்கு. 20-30 internal tools இருக்கு: CRM, ERP, ticketing system, internal knowledge base, billing API, HR service.

ஒரு AI agent அல்லது LLM இதையெல்லாம் use பண்ணணும். Tool calling செய்யணும்.

இப்போ என்ன பிரச்சனை?

* ஒவ்வொரு tool-க்கும் ஒவ்வொரு authentication, rate limit, schema வேறு.
* Agent code-ல நேரடியா API client எழுதினால், ஒவ்வொரு முறையும் tool மாறினால் agent-ஐ redeploy பண்ண வேண்டும்.
* Security team கேட்கும்: "எந்த agent எந்த data-க்கு access பண்ணுது? Audit எங்கே?"
* Dev team கேட்கும்: "என் service-ஐ LLM எப்படி call பண்ணும்? நான் change பண்ணினால் எல்லா agents-ஐயும் break பண்ணிடுவேன்."

இது integration spaghetti. Every new AI use-case = new custom integration.

## 2. Mental Model

MCP = Model Context Protocol.

இதன் core idea: **Tools-க்கும் AI-க்கும் இடையில் ஒரு standard adapter layer வைப்போம்.**

Service side-ல ஒரு MCP Server run பண்ணுவோம். அது உங்கள் internal API-களை wrap பண்ணி, standard format-ல tools-ஐ expose பண்ணும்.

Agent side-ல MCP Client இருக்கும். அது அந்த standard format-ஐ புரிந்து, tool discovery, call, schema validation செய்யும்.

அதாவது: Service team அவர்கள் MCP server-ஐ maintain பண்ணுவார்கள். AI team agent-ஐ maintain பண்ணுவார்கள். Interface contract ஒன்றே.

## 3. How It Works

Enterprise-ல MCP architecture மூன்று layer-கள் வைத்து வேலை செய்கிறது.

**MCP Server per domain / per service**
ஒவ்வொரு business domain-க்கும் ஒரு server. உதாரணமாக `crm-mcp-server`, `billing-mcp-server`. இது உள்ளே உங்கள் existing REST/gRPC API-ஐ call செய்யும். Outside-க்கு இது `tools`, `resources`, `prompts` என்ற MCP primitives-ஐ expose பண்ணும்.

**MCP Gateway / Router**
Enterprise-ல நேரடியா அனைத்து servers-ஐயும் agent-க்கு திறக்க முடியாது. Gateway இருக்கும்.

* Authentication & Authorization: mTLS, OAuth2, service mesh identity.
* Tool registry: எந்த server எந்த tools கொடுக்கிறது என்ற catalog.
* Rate limiting, auditing, PII filtering.
* Versioning: server v1, v2 இருந்தால் routing rule.

**MCP Client in Agent**
Agent framework e.g., LangGraph, LlamaIndex, your own orchestrator. Client connects to gateway, discovers tools dynamically, tool schema படித்து, LLM-க்கு tool calling செய்யும்.

Flow:
Agent → Gateway → AuthZ check → CRM MCP Server → Internal CRM API → Response → Gateway → Agent

## 4. Architectural Reasoning

இது எப்போது useful?

* நீங்கள் multiple agents / multiple teams க்கு same internal tools-ஐ expose பண்ண வேண்டும்.
* Tool set அடிக்கடி மாறும், ஆனால் agent logic-ஐ மாற்றாமல் இருக்க வேண்டும்.
* Central governance, audit, policy enforcement தேவை.

Alternatives?

* **Direct API integration:** Agent code-ல நேரடியா SDK எழுதுவது. Fast start, but coupling high.
* **API Gateway + custom schema:** Standard REST, ஆனால் LLM-க்கு tool semantics தெரியாது. Prompt engineering burden.
* **Service Mesh with sidecar adapters:** Works, ஆனால் AI-specific concerns like tool discovery, schema versioning missing.

ஏன் MCP?

Because it gives you **decoupling + standard contract** between AI consumption and backend services. Service team can evolve API without breaking agents, as long as MCP schema stable.

## 5. Trade-offs

* **Latency:** Extra hop - Agent → Gateway → Server → Internal API. Each call adds 20-100ms. For chat, ok. For real-time trading, not ok.
* **Complexity & Ops:** இன்னொரு layer maintain பண்ண வேண்டும். Server crashes, schema drift, versioning issues வரும்.
* **Security surface:** Gateway is critical. If compromised, attacker gets tool access to entire enterprise. Strong authz, least-privilege, audit mandatory.
* **Tool sprawl:** எல்லோரும் server வைத்து tools expose பண்ண ஆரம்பித்தால், 500 tools ஆகிவிடும். Agent confused ஆகும். Need governance, naming convention, deprecation policy.

Failure modes:

* Server down → agent blind spot. Need health checks, fallback tools.
* Schema mismatch → LLM hallucinate wrong parameters. Need strict validation at gateway.
* Sensitive data leakage via tool output. Need output filtering / redaction layer.

## 6. Practical Example

Enterprise support agent.

User: "என் invoice #12345 status என்ன? நேற்று payment செய்தேன்."

Agent flow:

1. Client connects to MCP Gateway with user JWT.
2. Gateway authorizes: this user can access `billing.read_invoice` and `crm.read_customer`.
3. Agent discovers tools: `get_invoice`, `get_payment_history`.
4. LLM decides call `get_invoice` with invoice_id=12345.
5. Gateway routes to `billing-mcp-server`. Server calls internal Billing API with service token, returns sanitized data.
6. Agent sees payment pending, calls `get_payment_history`.
7. Result synthesized to user.

Billing team அடுத்த வாரம் API v2 க்கு மாறினால், அவர்கள் மட்டும் MCP server-ஐ update செய்ய வேண்டும். Agent code மாறாது.

## 7. Reasoning Challenge

உங்களிடம் finance domain-க்கு 3 teams இருக்கு: Billing, Accounts Payable, Treasury. ஒவ்வொருவரும் தனித்தனி MCP server வைத்திருக்கிறார்கள்.

ஒரு CFO agent தயாரிக்கிறீர்கள். அது "Q3 cash flow summary" கேட்டால் மூன்று servers-ஐயும் தொடர்பு கொள்ள வேண்டும்.

இங்கே Gateway-ல என்ன policies வைப்பீர்கள்? Tools எப்படி organize பண்ணுவீர்கள்? Agent ஒரே call-ல தகவல் எடுக்க முடியாமல் போனால் latency அதிகரிக்கும். இதை எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

* MCP என்பது AI agents க்கும் enterprise tools க்கும் இடையே standard contract கொடுக்கும் adapter layer.
* Gateway = control plane for authz, audit, routing, versioning.
* Decoupling வரும், ஆனால் latency, ops complexity, security surface கூடும்.
* Tool governance இல்லாமல் MCP வெறும் integration mess-ஆக மாறும்.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியும்.
