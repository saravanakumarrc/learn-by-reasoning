# Tool registry

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.7 — Enterprise patterns

## 1. Problem

Enterprise AI system-ல ஒரு agent இருக்கு. அது user query-க்கு பதில் கொடுக்கணும்.

ஒரு query-க்கு வெறும் LLM போதாது. சில நேரம் database-ல data வேணும், சில நேரம் API call பண்ணணும், சில நேரம் calculator பயன்படுத்தணும், சில நேரம் internal tool அல்லது legacy system-க்கு call பண்ணணும்.

பிரச்சனை என்ன?

Agent எந்த tool-ஐ எப்போது use பண்ணனும், அந்த tool எங்க இருக்கு, எப்படி authenticate பண்ணனும், input/output format என்ன, rate limit எவ்வளவு, எந்த version இப்போ active-ல இருக்கு — இதையெல்லாம் agent-க்கு தெரியணும்.

இப்போ ஒவ்வொரு agent-லயும் tools-ஐ hard-code பண்ணினால் என்ன ஆகும்?
New tool வந்தால் agent code change, redeploy. Tool schema மாறினால் எல்லா agent-ம் break ஆகும். Security policy மாறினால் அத்தனை இடத்துலயும் update.

Scale ஆன enterprise-ல 50+ tools இருக்கும். Finance, HR, CRM, billing, internal knowledge base. இதை கையால் manage பண்ண முடியாது.

இந்த pain தான் Tool registry-ஐ உருவாக்கியது.

## 2. Mental Model

Tool registry என்பது **tools-க்கான service catalog**.

ஒரு central place-ல எல்லா tools-உம் register ஆகி இருக்கும். Schema, capability, ownership, policy, endpoint, authentication — எல்லாம் ஒரே இடத்தில்.

Agent ஒரு query பார்த்தவுடன், registry-ஐ கேட்டு "இந்த task-க்கு என்ன tools available?" என்று தெரிந்து கொள்ளும். அப்புறம் அதை call பண்ணும்.

உதாரணத்துக்கு library catalogue மாதிரி. Book எங்க இருக்கு, எப்படி borrow பண்ணனும் என்று catalogue சொல்லும். Catalogue-ஐ மாற்றினால் library staff மாற்றினாலும் போதும், reader-கள் அதை பயன்படுத்துவார்கள்.

## 3. How It Works

Registry ஒரு metadata store + discovery service.

**Register:** Tool owner ஒரு manifest பதிவு செய்வார்.
Tool name, description, input schema, output schema, endpoint URL, auth method, rate limit, owner team, SLA, version.

**Discover:** Agent அல்லது orchestrator registry-ஐ query பண்ணும். Capability-based search: "SQL query execute பண்ண முடியுமா?", "customer data read access உண்டா?".

**Invoke:** Registry tool-ஐ point செய்யும். சில design-ல registry direct call பண்ணும், சில design-ல registry metadata மட்டும் கொடுத்து agent direct tool-க்கு call பண்ணும்.

**Govern:** Registry-ல policy enforcement இருக்கும். Who can call which tool, when, with what data. Audit log எல்லாம் இங்கே capture ஆகும்.

Versioning முக்கியம். Tool v1, v2 இருந்தால் agent எந்த version-ஐ use பண்ண வேண்டும் என்பதை registry decide பண்ணும்.

## 4. Architectural Reasoning

Tool registry useful ஆகும் போது:

* Multiple agents share same toolset.
* Tools அடிக்கடி add/remove/update ஆகும்.
* Governance, audit, cost control தேவை.
* Tools distributed teams-ல build ஆகும், central visibility வேண்டும்.

Alternative என்ன?

1. Hard-code in agent. Small, stable system-க்கு ok. Enterprise-ல maintainability nightmare.
2. Configuration file per agent. Better but still duplication, sync problem.
3. Service mesh / API gateway. Tools discover பண்ண உதவும், ஆனால் AI-specific metadata — capability description, LLM-friendly schema — இல்லை.

Registry-ஐ தேர்வு பண்ணினால் என்ன கிடைக்கும்?
Decoupling. Agent logic tool location-ல இருந்து தனிப்படும். Tool change ஆனால் agent மாறாது. Central governance possible.

## 5. Trade-offs

**Consistency vs Freshness.** Registry metadata stale ஆகலாம். Tool down ஆனால் registry உடனே தெரியுமா? Cache பண்ணினால் latency குறையும், ஆனால் stale risk. Cache TTL பற்றி முடிவு எடுக்கணும்.

**Central point of failure.** Registry down ஆனால் எந்த agent-மே tool discover பண்ண முடியாது. High availability, replication, read replicas வேண்டும்.

**Complexity.** Small system-க்கு registry overhead தேவையில்லை. Operational cost, schema management, versioning policy — இதெல்லாம் team-க்கு கற்றுக்கொடுக்கணும்.

**Security surface.** Registry-ல tool permissions இருக்கும். Registry compromise ஆனால் attacker எந்த tool-ஐயும் call பண்ணும் permission-ஐ திருடலாம். Strong auth, audit, least privilege முக்கியம்.

**Schema drift.** Tool output schema மாறினால் agent prompt engineering break ஆகும். Registry contract testing, validation pipeline வேண்டும்.

## 6. Practical Example

Enterprise RAG + agent system.

Tools:
* `postgres_query` — internal DB read
* `salesforce_get_account` — CRM API
* `billing_invoice_generate` — billing service
* `document_search` — vector database search
* `email_send` — internal mailer

ஒரு user கேட்கிறார்: "Last quarter-ல Acme Corp-க்கு எவ்வளவு invoice அனுப்பினோம்?"

Agent workflow:
1. Registry-ல "invoice" capability உள்ள tool தேடு → `billing_invoice_generate` + `salesforce_get_account` கிடைக்கும்.
2. Registry metadata-ல input schema பார்த்து parameters build பண்ணு: customer_id, quarter.
3. Policy check: Agent-க்கு billing read permission உண்டா? Registry audit log-ல record பண்ணு.
4. Call tool, result-ஐ combine பண்ணி user-க்கு answer.

இப்போ billing team tool endpoint மாற்றினால், registry-ல update பண்ணினால் போதும். Agent redeploy தேவையில்லை.

## 7. Reasoning Challenge

உங்களிடம் 3 teams இருக்கு: Finance, Support, Sales. ஒவ்வொரு team-மும் தங்கள் internal tools-ஐ build பண்ணுகிறார்கள். Agent platform common.

Requirement: 
* Tool-ஐ யார் build பண்ணினார்கள் என்று தெரிய வேண்டும்
* Tool use ஆனது எத்தனை முறை, cost என்ன என்று track பண்ண வேண்டும்
* Production tool மாற்றும்போது canary rollout வேண்டும்

இந்த constraints-க்கு registry design எப்படி இருக்க வேண்டும்? Discovery மட்டும் போதுமா? அல்லது invoke proxy பண்ண வேண்டுமா?

## 8. Key Takeaways

* Tool registry = tools-க்கான central catalog + governance layer, agent-க்கான discovery mechanism.
* Agent-ஐ tool location-ல இருந்து decouple பண்ணி maintainability, reuse, governance கொடுக்கும்.
* Registry-ஐ build பண்ணுவது consistency, freshness, availability, security trade-offs உருவாக்கும்.
* Small system-க்கு over-engineering, enterprise multi-agent system-க்கு essential.
