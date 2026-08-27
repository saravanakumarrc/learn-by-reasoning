# Data governance

> **Learning Path:** Data Architecture
> **Section:** 4.2.14 — Data architecture

## 1. Problem

உங்கள் company-ல 200+ tables இருக்கு. Sales team ஒரு customer revenue-ஐ ஒரு வழியில் கணக்கிடுகிறது, Finance team இன்னொரு வழியில். Marketing-க்கு தெரியாது PII data எங்கே store ஆகியிருக்கு. ஒரு feature launch பண்ணும்போது, data source-ன் owner யார் என்றே தெரியவில்லை. 

இதனால் என்ன ஆகிறது? Wrong decision, duplicate pipelines, compliance breach, மற்றும் trust இழப்பு. Data இருக்கிறது, ஆனால் *யார் use பண்ணலாம், எப்படி, எந்த quality-ல* என்று தெரியவில்லை.

Data governance இதற்கு வருவதற்கு முன், problem painful ஆகி இருக்கும்: data sprawl, unknown lineage, quality issues production-ல வெடிக்கிறது, audit-ல fail ஆகிறது.

## 2. Mental Model

Data governance என்பது data-க்கான traffic rules + property registry.

ஒரு city-ல roads இருந்தால் மட்டும் போதாது. Ownership, speed limit, who can drive, log book வேண்டும். அதுபோல data-க்கு:

* **Ownership** யார்? Data Steward யார்?
* **Definition** என்ன? Meaning ஒன்றுதானா?
* **Access** யாருக்கு? PII, financial data-க்கு policy என்ன?
* **Quality & Lineage** எங்கிருந்து வந்தது, எப்படி மாறியது?

Governance என்பது control அல்ல, trust உருவாக்குவது.

## 3. How It Works

Architecture-ல governance என்பது central policy + distributed enforcement.

**Data Catalog + Metadata layer:** schema, description, owner, tags like PII, sensitive. இதுதான் source of truth.

**Lineage:** source system → ingestion → transformation → warehouse → BI/dashboard. ஒரு column மாறினால் யார் impact ஆவார்கள் என்று trace செய்ய வேண்டும்.

**Policies as code:** access control, retention, masking, classification. இதை data platform-ல enforce செய்ய வேண்டும்.

**Quality contracts:** data producer ஒரு SLA கொடுக்கிறார். completeness, freshness, uniqueness check-கள் automated.

```
Producer Service --> Data Catalog --> Policy Engine
        |                |                |
        v                v                v
   Data Lake / Warehouse   Lineage Graph   Access Masking / Audit
        |
        v
   Consumer / BI / ML
```

Governance tools இல்லாமல், இது manual spreadsheet-ல நடக்கும்.

## 4. Architectural Reasoning

எப்போது தேவை?

* Multiple teams same data-ஐ use பண்ணும்போது
* Regulatory compliance உள்ளது: GDPR, PCI-DSS, SOC2
* AI/RAG pipelines உள்ளது, training data quality முக்கியம்
* Data mesh அல்லது federated ownership model இருக்கும்போது

Constraint அது address பண்ணுவது: **trust, consistency, compliance**.

Options:
* **Centralized governance**: single team owns all policies. Simple, but bottleneck, slow.
* **Federated / Domain-owned**: each domain-க்கு steward, central platform provides tools. Scale ஆகும், but consistency கடினம்.

Architect choose பண்ணுவது team size, data criticality, compliance pressure பார்த்து. பெரும்பாலும் hybrid: central policy framework, domain-level stewardship.

## 5. Trade-offs

**Speed vs Control:** Strict approval workflow agile development-ஐ slow பண்ணும். Too loose என்றால் data chaos.

**Centralization vs Autonomy:** Central team enforce consistency, ஆனால் domain context இல்லாமல் bad policy உருவாகும்.

**Automation vs Manual:** Catalog auto-discovery + lineage extraction செய்யலாம், ஆனால் business definition, owner assignment manual தான். Automation இல்லாமல் catalog stale ஆகும்.

**Failure modes:** Ownership not defined → nobody fixes quality. Policy only documented, not enforced → audit fail. Lineage broken → incident-ல root cause கண்டுபிடிக்க முடியாது.

## 6. Practical Example

Enterprise bank-ல customer 360 view build செய்ய வேண்டும்.

Core banking, CRM, risk systems வெவ்வேறு teams own செய்கின்றன. Data governance இல்லாமல், engineers நேரடியாக production table-ல query அடிக்கிறார்கள், PII leak ஆகிறது.

Governance approach:
* Data catalog-ல `customer_id` standard definition, owner = CRM domain steward.
* PII tag உள்ள columns auto-mask ஆகும் non-production environment-ல.
* Lineage graph மூலம், core banking schema change வந்தால் downstream dashboards alert ஆகும்.
* Quality contract: customer table freshness < 1 hour, null rate < 0.1%.

Result: new team join ஆனாலும் safe access, audit ready, incident response fast.

## 7. Reasoning Challenge

உங்களிடம் 3 domains உள்ளது: Marketing, Risk, Product. ஒவ்வொன்றும் தனது data pipeline build செய்கிறது. CEO compliance team GDPR delete request-க்கு 30 நாளில் response வேண்டும் என்கிறார். 

Central governance team-ஐ உருவாக்கலாமா, அல்லது ஒவ்வொரு domain-க்கும் steward கொடுத்து self-govern செய்ய சொல்லலாமா? என்ன trade-off வரும்? Policy enforcement எப்படி design செய்வீர்கள்?

## 8. Key Takeaways

* Governance என்பது documentation அல்ல, enforceable policy + ownership ஆகும்.
* Data catalog + lineage இல்லாமல் scale செய்ய முடியாது.
* Central framework + federated stewardship தான் பெரும்பாலும் work ஆகும்.
* Quality மற்றும்
