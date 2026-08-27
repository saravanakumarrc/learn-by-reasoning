# Identity boundaries

> **Learning Path:** Security Architecture
> **Section:** 6.2.4 — Enterprise security

## Problem

உங்கள் enterprise-ல ஒரு single corporate AD இருக்கு. அதே AD-ஐயே internal apps, SaaS tools, partner portal எல்லாத்துக்கும் use பண்றீங்க. ஒரு employee ஒரு தடவை login பண்ணா, அந்த identity எல்லா system-லயும் propagate ஆகுது.

இப்போ business grow ஆகுது. New acquisition வந்துச்சு, அவங்களுக்கு தனி IdP. Customers-க்கு தனி identity domain. Partner-கள் தங்கள் own identity system-ஐ கொண்டு வர்றாங்க.

இதுல என்ன வரும்? One identity breach ஆனால் lateral movement முழு enterprise-க்கும் போயிடும். ஒரு customer identity தவறாக internal HR system-க்கு access பண்ணிடும். ஒரு partner-க்கு தேவையானதை விட அதிக privileges கொடுத்துட்டோம்.

"Network perimeter safe" என்று நினைச்சோம், ஆனால் identity தான் உண்மையான boundary ஆக மாறியிருக்கு.

## Mental Model

Identity boundary என்பது network firewall அல்ல. இது **"இந்த identity claim-ஐ இங்கே நம்பலாமா?"** என்று முடிவு செய்யும் logical checkpoint.

உதாரணத்துக்கு airport immigration போல. உள்ளே வந்தவுடன் நீங்கள் நாட்டு சட்டத்துக்கு உட்பட்டவர். அதே மாதிரி, ஒரு service boundary-க்குள் நுழையும் identity, அந்த boundary-க்கு specific claims, audience, lifetime, trust assumptions கொண்டதாக இருக்க வேண்டும்.

Boundary-க்கு வெளியே: verify, authenticate, map.
Boundary-க்குள்: authorize based on local policy.

## How It Works

ஒரு identity boundary-க்கு மூன்று வேலைகள்:

1. **Verification**: Token-ஐ validate பண்ணுவது. JWT signature check, issuer check, expiry, audience. OIDC/OAuth2 flow-ல IdP தான் source of truth.
2. **Translation / Mapping**: வெளி identity-ஐ உள்ள local principal-க்கு map பண்ணுவது. e.g., partner IdP-ல `partner_user_123` -> உங்கள் tenant-ல `external_user` with limited roles.
3. **Enforcement**: Boundary-ல policy decision point வைத்து, `allow/deny` முடிவு செய்வது. இது zero trust-ன் core.

Implementation-ல இது gateway, API gateway, service mesh sidecar, அல்லது dedicated IAM proxy-வில் நடக்கும். முக்கியம்: identity data boundary-க்குள் leak ஆகக்கூடாது. Claims மட்டும் propagate ஆகணும்.

## Architectural Reasoning

Identity boundary எப்போது useful?

* **Multiple trust domains**: employees, customers, partners, workloads. ஒவ்வொன்றுக்கும் trust level வேறு.
* **Multi-tenant SaaS**: Tenant A-ன் admin Tenant B-க்கு access பண்ணக்கூடாது. Tenant isolation என்பது identity boundary தான்.
* **B2B federation**: SAML/OIDC federation பண்ணும்போது, நீங்கள் partner IdP-யை முழுசா trust பண்ண முடியாது. Claims transformation மூலம் boundary வைக்கிறீங்க.
* **Workload identity**: Human identity vs service principal identity. Kubernetes workload-க்கு separate identity boundary வேண்டும், long-lived credentials வேண்டாம்.

Alternative என்ன? Single global identity. அது simple ஆனால் blast radius huge. மற்றொன்று: every service does its own auth. அது operational nightmare.

Architect-ஆக நீங்கள் முடிவு செய்ய வேண்டியது: எங்கே boundary வைக்கிறோம்? எந்த level-ல verify பண்ணுகிறோம்? Token lifetime எவ்வளவு? Cross-boundary access-க்கு explicit federation agreement உண்டா?

## Trade-offs

**Centralize vs Federate**: Central IdP simple, consistent audit. ஆனால் single point of failure, acquisition-களை integrate பண்ண கஷ்டம். Federated boundaries flexible, ஆனால் mapping complexity, claim consistency குறையும்.

**Security vs Lat
