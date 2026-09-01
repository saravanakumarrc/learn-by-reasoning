# Tenant-specific policies

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.2.4 — Multi-tenancy

## 1. Problem

ஒரு Enterprise AI platform-ல் ஒரே infrastructure-ல் 50+ tenants இருக்காங்க. ஒரு tenant-க்கு finance domain data, இன்னொருத்தருக்கு healthcare data. 

அனைவருக்கும் ஒரே policy வைத்தால் என்ன ஆகும்?
- Healthcare tenant-க்கு HIPAA compliance தேவை, data retention 7 years.
- Finance tenant-க்கு PII masking கண்டிப்பாக வேண்டும், audit log immutable ஆக இருக்க வேண்டும்.
- Start-up tenant-க்கு cost குறைவாக இருக்க வேண்டும், model access limited.

ஒரே global policy என்றால் ஒன்று over-restrictive ஆகும், அல்லது ஒன்று too permissive ஆகும். 

What goes wrong if we don't have tenant-specific policies? Data leak, compliance violation, cost blow up, மற்றும் support tickets explode.

## 2. Mental Model

Multi-tenancy என்பது ஒரே platform share பண்ணுவது. Tenant-specific policies என்பது **ஒவ்வொரு tenant-க்கும் அதன் own ruleset** கொடுப்பது.

Think of it like an apartment building. Building-க்கு common rules உண்டு. ஆனால் ஒவ்வொரு tenant-க்கும் lease agreement வேறுபடும். யாருக்கு pet allowed, யாருக்கு sublet allowed, என்ன insurance வேண்டும்.

Platform level-ல் base guardrails இருக்கும். Tenant level-ல் overrides and extensions இருக்கும்.

## 3. How It Works

Policy evaluation என்பது request வரும்போது context-ஐ பார்த்து decision எடுப்பது.

Request flow:
`User -> Auth -> Tenant Resolution -> Policy Engine -> Decision`

Tenant Resolution-ல் tenant_id extract ஆகும். அதன் பின் policy engine அந்த tenant-க்கான policy bundle-ஐ load பண்ணும்.

Policy bundle என்பது typically:
- **Access Control**: யார் என்ன model/resource access பண்ணலாம்
- **Data Governance**: data residency, retention, encryption requirements
- **Usage & Cost**: rate limits, quota, allowed models, max tokens per day
- **Safety & Compliance**: PII redaction, prompt filtering, audit logging level
- **Feature Flags**: RAG source access, agent tool allowlist

Policy store-ல் இது versioned JSON/YAML or Rego/OPA policy ஆக இருக்கும். Evaluation fast ஆக இருக்க வேண்டும், so cache பண்ணுவோம். Change ஆனால் cache invalidate.

## 4. Architectural Reasoning

When does this become useful?
ஒரே platform-ல் multiple business units / customers இருக்கும் போது.

Constraint it addresses: Isolation without physical isolation. Cost efficiency + compliance.

Alternatives:
1. **Single global policy**: Cheap to build, ஆனால் business needs-ஐ meet பண்ணாது.
2. **Separate deployment per tenant**: Full isolation, ஆனால் cost, operability nightmare.
3. **Tenant-specific policies on shared infra**: Sweet spot.

Architect choose பண்ணும் reason:
- Compliance boundary தேவை. Healthcare tenant data EU-ல் மட்டும் இருக்க வேண்டும்.
- Commercial differentiation. Enterprise tenant-க்கு higher rate limit, dedicated model.
- Risk containment. ஒரு tenant-ல் abuse ஆனால் மற்றவரை affect பண்ணக்கூடாது.

Decision flow:
Base policies -> Tenant overrides -> User role overrides.

## 5. Trade-offs

**Flexibility vs Complexity**
ஒவ்வொரு tenant-க்கும் custom policy வைத்தால் policy matrix explode ஆகும். Testing, audit செய்வது கடினம். Versioning முக்கியம்.

**Performance vs Freshness**
Policy evaluation per request costly. Cache பண்ணினால் policy change propagation delay வரும். Stale policy risk உண்டு.

**Central control vs Tenant autonomy**
Platform team base guardrails set பண்ணும். Tenant admin-க்கு self-service policy change கொடுத்தால் misuse risk. Who can change what? RBAC needed for policies itself.

**Observability**
எந்த tenant எந்த policy violation-ல் hit ஆகிறது என்பதை log பண்ண வேண்டும். இல்லை என்றால் debugging impossible.

Failure modes:
- Tenant resolution fail ஆனால் default deny பண்ண வேண்டும், default allow அல்ல.
- Policy engine down ஆனால் fail-open vs fail-closed decision critical.
- Policy conflict: tenant policy base policy-ஐ override பண்ண முடியுமா? Hierarchy clear ஆக இருக்க வேண்டும்.

## 6. Practical Example

Enterprise AI assistant platform. 3 tenants:

**Tenant A - Bank**
Policy: Data residency = in-country. PII redaction mandatory. Audit log immutable to S3 with 7 year retention. Allowed models = GPT-4o, Claude 3.5 only. Rate limit 1000 req/min. No external tools.

**Tenant B - Healthcare SaaS**
Policy: Data residency = EU. PHI detection + auto-redaction. Retention 7 years. Allowed models = all. Rate limit 500 req/min. RAG sources limited to tenant-owned vector DB only. Prompt injection filter strict.

**Tenant C - Internal R&D**
Policy: Data residency = any. No redaction. Rate limit 200 req/min. Allowed models = experimental models included. No audit retention.

All three share same API gateway, same model pool, same infra.

Request வரும்போது tenant_id-ல் இருந்து policy fetch ஆகி, request-ஐ allow/deny, transform, log பண்ணும். Tenant A-ன் request automatically PII mask ஆகும், Tenant C-ன் request அப்படியே போகும்.

## 7. Reasoning Challenge

உங்களிடம் 200 tenants உள்ளது. 20 tenants enterprise, மீதி SMB.

Enterprise tenants கேட்கிறார்கள்: "எங்கள் data எப்போதும் dedicated GPU pool-ல் மட்டுமே run ஆக வேண்டும்."

SMB tenants: "நாங்கள் spot instances use பண்ணி cost குறைக்க வேண்டும்."

ஒரே policy engine-ல் இதை எப்படி handle செய்வீர்கள்? Policy-ல் infrastructure placement rule வைக்கலாமா? அல்லது routing layer-ல் tenant class பிரித்து hard code பண்ணலாமா? Trade-off என்ன?

## 8. Key Takeaways

- Tenant-specific policies என்பது shared infra-ல் isolation-ஐ business rule level-ல் achieve பண்ணுவது
- Policy hierarchy clear ஆக இருக்க வேண்டும்: Base > Tenant > User
- Policy evaluation fast, versioned, auditable ஆக இருக்க வேண்டும்
- Every tenant customization adds operational complexity and testing surface
