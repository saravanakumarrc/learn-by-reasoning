# Tenant-specific agents

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.2.5 — Multi-tenancy

## 1. Problem

உங்களிடம் ஒரு Enterprise AI platform இருக்கு. 10 different customers - bank, hospital, retail chain. எல்லாரும் ஒரே platform-ஐ use பண்ணுறாங்க.

Bank-க்கு compliance முக்கியம். Audit log வேணும். Data ஒரு region-ல மட்டும் இருக்கணும்.

Hospital-க்கு PHI data leakage ஆகக்கூடாது. Model prompts sensitive.

Retail-க்கு 1000 stores-ல இருந்து real-time inventory query வேணும்.

ஒரே generic agent-ஐ எல்லாருக்கும் கொடுத்தால் என்ன ஆகும்?

* Prompt-ல ஒரு tenant-ன் data மற்ற tenant-க்கு leak ஆகும்.
* One tenant-ன் bad prompt அல்லது high traffic மற்றவர்களை slow ஆக்கும்.
* Custom business logic, tone, tools, guardrails எல்லாம் mix ஆகும்.
* Billing, usage, access control track பண்ண முடியாது.

இங்கே வரும் pain point: **Isolation vs Reuse**. Shared infrastructure வேணும், ஆனால் tenant boundary strict-ஆ இருக்கணும்.

## 2. Mental Model

Tenant-specific agent என்பது ஒரு logical agent instance ஆகும், ஆனால் அது **one tenant-க்கு மட்டும்** configure ஆனது.

அதாவது same code base, same orchestration engine, ஆனால்:

* தனித்தனி configuration
* தனித்தனி tools & data access
* தனித்தனி policy & guardrails
* தனித்தனி observability & billing

Shared core, isolated context.

அனாலஜி: ஒரு bank-ல எல்லாருக்கும் ஒரே ATM software. ஆனால் ஒவ்வொரு customer-க்கும் தனித்தனி account, PIN, limits.

## 3. How It Works

Architecture-ல மூன்று layer இருக்கு:

**Tenant Router / Gateway**
Incoming request வரும்போது tenant ID extract பண்ணும். API key, subdomain, JWT claim எதாவது use பண்ணி. அதன் பின் request-ஐ அந்த tenant-ன் agent config-க்கு route பண்ணும்.

**Tenant Config Store**
Every tenant-க்கு ஒரு config object:

* `system_prompt` + brand tone
* `allowed_tools`: which tools can call
* `data_scope`: which vector DB / database collections அணுகலாம்
* `policy_rules`: PII masking, compliance checks
* `model_params`: temperature, model tier
* `rate_limit & quota`

**Agent Runtime**
Runtime engine ஒன்றே இருக்கலாம். ஆனால் execution context tenant-specific ஆக build ஆகும். Tool call செய்யும் முன் data access filter apply ஆகும். Logs tenant-isolated ஆக write ஆகும்.

```
User -> Tenant Router -> Tenant Config Load -> Agent Runtime
                         |               |                |
                         v               v                v
                    Auth / Audit    Data Isolation    Tool Guardrails
```

## 4. Architectural Reasoning

Tenant-specific agent எப்போது தேவை?

* Multi-tenant SaaS AI product இருக்கும்போது
* Compliance தேவை isolation
* ஒவ்வொரு customer-க்கும் different knowledge base, workflows
* Usage-based billing தேவை

Alternatives என்ன?

1. **Single shared agent + prompt tagging**: Cheap, ஆனால் data leakage risk high. No isolation.
2. **Fully separate deployment per tenant**: Maximum isolation, ஆனால் cost & ops nightmare.
3. **Tenant-specific agent on shared runtime**: Sweet spot. Code reuse + logical isolation.

Architect choose பண்ணுவார் because:

* Scale பண்ண வேண்டும், 100+ tenants.
* Operational complexity குறைக்க வேண்டும்.
* Compliance audit பாஸ் செய்ய வேண்டும்.

## 5. Trade-offs

**Isolation vs Cost**: ஒவ்வொரு tenant-க்கும் தனி vector DB, model instance வைக்கலாம். Perfect isolation, ஆனால் cost explode ஆகும். Shared DB with row-level security + tenant_id filter common.

**Customization vs Maintainability**: ஒவ்வொரு tenant-க்கும் custom prompt / tools கொடுக்கலாம். ஆனால் version control, testing கடினம். Config-as-code + template system தேவை.

**Latency**: Config load, policy check ஒவ்வொரு request-லும் செய்தால் latency add ஆகும். Cache tenant config in memory, short TTL.

**Failure mode**: ஒரு tenant-ன் malformed prompt அல்லது runaway tool loop மற்ற tenants-ஐ affect பண்ணக்கூடாது. Per-tenant rate limiting, timeout, circuit breaker தேவை.

Security trade-off: Prompt injection ஒரு tenant-ல இருந்து மற்ற tenant data-வை access செய்ய முயற்சிக்கலாம். Tool output filtering + strict data scope enforcement முக்கியம்.

## 6. Practical Example

Enterprise support agent.

Bank tenant A:
* Data source: internal KB, customer accounts DB read-only view
* Tools: get_account_summary, create_ticket
* Guardrail: no disclosure of other customer data, mandatory audit log
* Model: GPT-4 with low temperature

Retail tenant B:
* Data source: product catalog vector DB, inventory service
* Tools: search_products, check_stock
* Guardrail: price info public only
* Model: cheaper model, higher temperature for creative responses

Same agent runtime, ஆனால் request வரும்போது tenant ID-யை base செய்து config load ஆகும். Logs separate, billing metered.

## 7. Reasoning Challenge

உங்களிடம் 200 tenants இருக்கு. 80% tenants small, 20% enterprise.

Enterprise tenants demand dedicated model instance + data residency in EU.

Small tenants fine with shared model.

ஒரே agent runtime use பண்ணி, ஆனால் tenant-specific isolation எப்படி design பண்ணுவீர்கள்? Shared vs dedicated resources எங்கே draw பண்ணுவீர்கள்? Cost, latency, compliance எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Tenant-specific agent என்பது isolation-க்கான architecture pattern, feature அல்ல.
* Shared runtime + isolated config, data scope, tools, policy = practical multi-tenancy.
* Data leakage, noisy neighbor, compliance இவைதான் main drivers.
* Every customization adds operational cost. Template + config-as-code மூலம் manage பண்ணுங்கள்.
* Observability must be tenant-aware from day one, இல்லைன்னா debugging impossible.
