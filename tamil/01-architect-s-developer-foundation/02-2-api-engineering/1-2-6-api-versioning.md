# API versioning

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.6 — 2. API engineering

### 1. Problem

நீங்க ஒரு public API வச்சிருக்கீங்க. 200 mobile apps, 30 internal services அதை consume பண்ணுது. Business-க்கு தேவைப்பட்டு response schema-ல ஒரு field-ஐ rename பண்ணணும், ஒரு parameter-ஐ mandatory ஆக்கணும்.

அப்படி மாத்தினீங்கன்னா என்ன ஆகும்? Existing client-கள் crash ஆகும், data loss ஆகும், support ticket flood ஆகும். அதனால change பண்ண முடியாம stuck ஆகிடுறீங்க.

இதுதான் **breaking change**-ன் cost. API என்பது contract. நீங்க deploy பண்ணும்போது contract-ஐ மாத்தக் கூடாது. ஆனா business evolve ஆகணும். இந்த tension-க்கு தீர்வுதான் API versioning.

### 2. Mental Model

API versioning = **ஒரே service-க்கு பல contracts-ஐ ஒரே சமயத்தில் run பண்ணுறது**.

நீங்க ஒரு restaurant-ல menu-வை update பண்றீங்க. பழைய customers பழைய dish name-ல order பண்ணுவாங்க. புதுசா வருபவங்க புது menu-வை பார்ப்பாங்க. Kitchen இரண்டையும் புரிஞ்சு cook பண்ணணும். அதுதான் versioning.

### 3. How It Works

Version-ஐ signal பண்ண 3 common வழிகள்:

**URL path versioning** - மிக common, explicit.
`/api/v1/orders` → `/api/v2/orders`

**Header versioning**
`Accept: application/vnd.company.v2+json`

**Query param**
`/api/orders?version=2`

Architect-க்கு URL path-தான் readable, cache-friendly, observable ஆக இருக்கும். Header/Query அதிக flexibility கொடுக்கும் ஆனால் மறைவாக இருக்கும்.

Implementation-ல பொதுவாக:
- v1, v2 ஆக separate handler/router-ல map பண்ணுறோம்
- Core business logic shared, presentation layer version-specific ஆக இருக்கும்
- Request வரும்போது version identify பண்ணி route பண்ணுவோம்

### 4. Architectural Reasoning

Versioning தேவைப்படும் constraints:

- **External clients நீங்க control பண்ண முடியாது**. Mobile app update slow, enterprise integration slow.
- **Backward compatibility-ஐ long time maintain பண்ணணும்**.
- **Breaking change unavoidable** - field remove, type change, auth flow change.

Alternatives:

- Never break? அதாவது add-only changes, deprecate but never remove. சில internal systems-க்கு போதும். Scale ஆனால் schema குப்பை ஆகும்.
- Force upgrade? Mobile app mandatory update. User churn, ops risk.
- Versioning.

எப்போ choose பண்ணுவது:
Public API, multi-tenant SaaS, long-lived integrations → versioning must.
Internal service, same team owns producer & consumer, deploy together → versioning may be overkill. Contract test + coordinated deploy போதும்.

### 5. Trade-offs

**Maintain multiple versions** = code complexity + test matrix + infra cost. ஒவ்வொரு version-க்கும் bug fix, security patch போடணும்.

**Version sprawl**. v1, v2, v3 எல்லாம் 3 வருஷம் நிற்கும். Team அளவு பெருசாகும்போது operability கஷ்டம்.

**Client confusion**. எந்த version use பண்ணணும்? Documentation clear இல்லைன்னா support cost ஏறும்.

**Deprecation & Sunset** முக்கியம். Versioning இல்லாமல் versioning-ஐ manage பண்ணுறது இல்லை. நீங்க v1-ஐ எப்போ close பண்ணுவீங்கன்னு communicate பண்ணணும், telemetry வச்சு usage track பண்ணணும்.

Failure mode: Version header miss ஆனால் default version எது? Silent default பண்ணினா future breaking ஆகும். Explicit 400 error தருவது safe.

### 6. Practical Example

Payment service `POST /v1/payments`. v1-ல `amount` integer cents-ல வாங்குது.

New requirement: international payments, decimals தேவை. v2-ல `amount` string with currency.

நீங்க என்ன பண்றீங்க?
- `/v1/payments` அப்படியே விடுறீங்க. Existing merchants break ஆகக் கூடாது.
- `/v2/payments` புது schema வச்சு rollout பண்றீங்க.
- Gateway layer-ல version router: v1 → legacy adapter → core, v2 → new adapter → core.
- Telemetry-ல v1 usage track பண்றீங்க. 6 months கழித்து <5% usage ஆனதும் deprecate notice அனுப்புறீங்க, 12 months-ல sunset.

இதனால producer free-ஆ evolve பண்ணலாம், consumer control-ல migrate பண்ணலாம்.

### 7. Reasoning Challenge

உங்க company-க்கு internal `User Service` இருக்கு. 12 microservices அதை call பண்ணுது, எல்லாம் same repo team-ல இருக்கு. நீங்க response-ல `email_verified` field-ஐ remove பண்ணணும், இனி `verification_status` enum வச்சிருக்கீங்க.

Versioning பண்ணுவீங்களா? இல்லை breaking change அனுமதிப்பீங்களா? ஏன்? Cost என்ன?

### 8. Key Takeaways

- API versioning solves **contract stability** problem, not code organization problem.
- Version = support cost. Every version you keep, you own forever until sunset.
- URL path versioning is explicit and operable for most systems.
- Design for deprecation from day one: telemetry, sunset policy, communication.
- Version only when you cannot coordinate deploy with consumers.
