# Authentication

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.10 — 2. API engineering

## 1. Problem

உங்களிடம் ஒரு API இருக்கு. Mobile app, web app, third-party partner எல்லாரும் அதை call பண்றாங்க. HTTP stateless. ஒவ்வொரு request-உம் தனியா வருது.

இங்கே core question என்ன?

> இந்த request-ஐ அனுப்புறது யார்?

இதை தெரியாம service ஒன்னும் செய்ய கூடாது. Database-ஐ மாற்றுவது, payment செய்வது போன்ற actions எல்லாம் identity இல்லாம நடக்கக்கூடாது.

ஒரு single monolith-ல session cookie வச்சு வேலை ஆயிடும். ஆனால் distributed system-ல 50 services, API Gateway, multiple clients இருக்கும்போது **who is calling me** என்பது painful ஆகும்.

## 2. Mental Model

Authentication = prove who you are.

Authorization = what you are allowed to do.

Passport check பண்ணுறது authentication. அந்த passport-ல என்ன visa இருக்கு என்பது authorization.

Engineer-க்கு முக்கியம்: Authentication is a proof mechanism, not a storage mechanism.

## 3. How It Works

Flow எப்போதும் இதே:

1. **Client credentials present பண்ணும்** - username/password, API key, client certificate, token.
2. **Auth service verify பண்ணும்** - credential valid தானா என்று check.
3. **Proof issue பண்ணும்** - verify ஆனதும் அடுத்த request-களுக்கு ஒரு proof கொடுக்கும்.
4. **Each request-ல proof attach பண்ணும்** - client அதை Authorization header-ல அனுப்பும்.
5. **Service proof validate பண்ணும்** - signature, expiry, issuer check.

Stateless API-க்கு இது முக்கியம். Server ஒவ்வொரு request-க்கும் DB போய் "யார் இது?" என்று கேட்க முடியாது.

## 4. Architectural Reasoning

Constraint என்ன?

* **Stateless scale:** Service instances எத்தனை வேண்டுமானாலும் scale ஆகணும்.
* **Distributed trust:** Service A service B-ஐ call பண்ணும்போது அதுவும் authenticate ஆகணும்.
* **Different client types:** Human user vs machine-to-machine.

Options:

**Session cookie + server-side session store**
Simple, revocation easy. ஆனால் session store shared ஆக வேண்டும். API Gateway-க்கு அப்பால் scale பண்ணும்போது sticky session அல்லது central store தேவை. Microservices cross-domain பிரச்சனை.

**API Key**
Machine-to-machine-க்கு நல்லது. Long-lived secret. ஆனால் rotate பண்ணுவது கஷ்டம், scope fine-grained கிடையாது, leak ஆனால் revoke பண்ணும் வரை access இருக்கும்.

**JWT / OIDC token**
Stateless verification. Signature check போதும், DB hit இல்லை. Distributed system-ல ideal. Mobile app, SPA-க்கு standard.

**mTLS**
Service-to-service-க்கு strong identity. Certificate manage பண்ண வேண்டும்.

Architect decide பண்ணுவது constraint பார்த்து. Human user facing external API → OAuth2 + JWT. Internal service mesh → mTLS. Partner integration → API Key or mTLS.

## 5. Trade-offs

* **Stateless vs Revocation:** JWT stateless, fast. ஆனால் token expire ஆகும் வரை revoke செய்ய முடியாது. Short TTL + refresh token pattern, அல்லது token blacklist / denylist வைத்து state மீண்டும் வரும்.
* **Secret management:** API key அல்லது private key leak ஆனால் பாதிப்பு பெரியது. Rotation, vault, least privilege முக்கியம்.
* **Complexity vs Security:** OAuth2/OIDC powerful ஆனால் complexity அதிகம். சில internal tools-க்கு அது over-engineering.
* **Failure modes:** Token theft → attacker impersonate பண்ணுவான். Clock skew → token validation fail. Missing signature verification → forgery.

## 6. Practical Example

Enterprise fintech API.

Mobile app user login பண்ணும். Auth service password verify பண்ணி, access token 15 min TTL, refresh token 7 days கொடுக்கும். Access token JWT, signed by Auth service private key.

API Gateway ஒவ்வொரு request-க்கும் JWT signature verify பண்ணி, claims read பண்ணி downstream service-க்கு pass பண்ணும். Service-க்கு DB hit இல்லை.

Internal microservices service-to-service call பண்ணும்போது mTLS use பண்ணும். API key இல்லை.

Partner bank integration-க்கு dedicated API key + IP whitelist + rate limit.

இங்கே authentication layer centralized, services stateless.

## 7. Reasoning Challenge

உங்களிடம் 20 microservices இருக்கு. எல்லாம் internal network-ல. சில services external mobile clients-க்கு expose ஆகும். Mobile users
