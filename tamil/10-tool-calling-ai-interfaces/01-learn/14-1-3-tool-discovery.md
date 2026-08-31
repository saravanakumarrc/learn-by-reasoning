# Tool discovery

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.3 — Learn

## 1. Problem

உங்களிடம் ஒரு LLM agent இருக்கு. அது user request வாங்கி, plan பண்ணி, action எடுக்கணும். 

சிக்கல் என்ன? Agent-க்கு எந்த tool use பண்ணனும், எப்போ use பண்ணனும், எப்படி call பண்ணனும் என்று தெரியாது.

இப்போ நீங்கள் ஒரு fixed list of tools கொடுக்கிறீர்கள். `get_weather`, `send_email`, `search_db`. User கேட்கிறார்: *"நேற்று Chennai-ல என்ன weather இருந்தது, அதை என் boss-க்கு mail பண்ணு"*. Agent-க்கு இது இரண்டு tools தேவை.

ஆனால் user கேட்கிறார்: *"நேற்று எனக்கு வந்த payment-களை Slack-ல summary போடு"*. Agent-க்கு `get_payments`, `slack_post` tools தெரியுமா? அது dynamic-ஆ grow ஆகும்.

Fixed list வைத்தால்:

* New tool வந்தால் model re-train / re-prompt வேண்டும்
* Tool name தெரியாது என்றால் hallucinate பண்ணும்
* Tool overload ஆகும் - 200 tools கொடுத்தால் model confuse ஆகும்

இந்த pain தான் **tool discovery**-ஐ உருவாக்கியது. Agent தானாக தேவையான tool-ஐ கண்டுபிடித்து, use பண்ண வேண்டும்.

## 2. Mental Model

Tool discovery என்பது **capability catalog + search + selection**.

உங்களிடம் ஒரு tool registry இருக்கு. ஒவ்வொரு tool-ம் என்ன செய்யும், என்ன input எடுக்கும், என்ன output தரும் என்ற metadata உள்ளது.

Agent user intent-ஐ புரிந்து கொண்டு, அதற்கு பொருத்தமான tool-களை search பண்ணி, select பண்ணி call பண்ணும்.

இது ஒரு mini RAG problem போல. Tool descriptions ஒரு vector DB-ல இருக்கும். User query-யை embed பண்ணி, relevant tools-ஐ retrieve பண்ணுவது.

## 3. How It Works

Basic flow:

1. **Describe**: ஒவ்வொரு tool-க்கும் machine-readable description + natural language description. `name`, `description`, `parameters`, `examples`.
2. **Index**: Descriptions-ஐ embeddings-ஆ மாற்றி vector database-ல் store பண்ணு.
3. **Query**: User request வந்ததும், intent-ஐ extract பண்ணி embed பண்ணு.
4. **Retrieve**: Top-K tools-ஐ similarity search மூலம் கண்டுபிடி.
5. **Filter & Rank**: Parameters availability, access control, cost பார்த்து filter பண்ணு.
6. **Call**: Selected tool-களை LLM-க்கு context-ஆ கொடுத்து call பண்ணு.

Advanced version-ல் agent தான் search query generate பண்ணும், iterative refinement பண்ணும். *"I need payment data"* -> search *"get payments"* -> not enough -> search *"get payments by date"*.

## 4. Architectural Reasoning

இது useful ஆகும் போது:

* **Tool catalog பெரிதாக இருக்கும்** - 50+ tools, மனிதன் list பண்ண முடியாது
* **Tools dynamic-ஆ add/remove ஆகும்** - third-party integrations, internal microservices
* **Multi-domain agent** - finance, HR, support ஒரே agent

Alternatives:

* **Static tool list**: சிறிய system-க்கு fine. 10-15 tools வரை.
* **LLM internal knowledge**: Model தெரிந்த tool names-ஐ guess பண்ணும். Unreliable.
* **Manual routing**: Human ops team route பண்ணும். Slow.

நீங்கள் tool discovery தேர்வு செய்யும் போது உங்கள் constraint என்ன?

* Latency: search add ஆகும் 50-200ms
* Accuracy: wrong tool select ஆனால் costly
* Operability: tool registry maintain பண்ண வேண்டும்

## 5. Trade-offs

**Recall vs Precision**: Top-K அதிகம் எடுத்தால் recall அதிகம், ஆனால் LLM confuse ஆகும். Top-K குறைவாக இருந்தால் miss ஆகும்.

**Freshness vs Cost**: Tool catalog அடிக்கடி update ஆகும். Embedding re-index cost உள்ளது.

**Generic description vs Specific**: Description too generic ஆனால் irrelevant tools வரும். Too specific ஆனால் query match ஆகாது.

**Failure mode**: Model hallucinate பண்ணி non-existent tool name generate பண்ணலாம். அதை guard பண்ண tool registry-ல validate செய்ய வேண்டும்.

Security trade-off: Agent எந்த tool-ஐயும் discover பண்ணலாம். அதனால் access control filter critical. `delete_user` tool ஒரு normal user agent-க்கு தெரியக்கூடாது.

## 6. Practical Example

Enterprise support agent.

Tools: 120 internal tools. `create_jira_ticket`, `query_salesforce`, `fetch_k8s_logs`, `post_slack`, `send_email`, `refund_payment`, ...

User: *"நேற்று Mumbai region-ல நம்ம payment gateway error rate அதிகமா இருந்துச்சா? இருந்தா SRE team-க்கு Slack alert அனுப்பு"*

Agent:

* Intent: check error rate + conditional alert
* Tool discovery search: *"payment gateway error rate by region"* -> `get_gateway_metrics`
* Search: *"send slack alert to SRE"* -> `post_slack_message`
* Retrieve both, call sequentially.

இங்கே agent fixed list-ஐ பார்க்காமல், 120 tools-ல இருந்து 2 relevant tools-ஐ தானாக கண்டுபிடித்தது.

Implementation note: Tool descriptions-ல examples வைக்கவும். `get_gateway_metrics` description-ல *"Example: get error rate for payment gateway in Mumbai for last 24h"* என்று இருந்தால் match துல்லியமாக இருக்கும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு multi-tenant SaaS agent இருக்கு. ஒவ்வொரு tenant-க்கும் தனித்தனி tools இருக்கு. Tenant A-க்கு `send_sms_twilio`, Tenant B-க்கு `send_sms_sns`. ஒரே agent model எல்லா tenant-க்கும் use பண்ணப்படுகிறது.

User query வந்ததும் tool discovery எப்படி design பண்ணுவீர்கள்? Tenant context-ஐ எப்போ add பண்ணுவீர்கள்? Tool search-க்கு முன்னா அப்புறமா?

## 8. Key Takeaways

* Tool discovery = tool catalog-ல search + rank செய்து relevant tools-ஐ agent-க்கு கொடுப்பது
* Fixed tool list scale ஆகாது. Dynamic catalog + retrieval தான் long term solution
* Description quality = discovery quality. Good metadata, examples, parameters முக்கியம்
* Discovery இல்லாமல் agent blind. Discovery மட்டும் போதாது. Access control, validation கண்டிப்பாக வேண்டும்
