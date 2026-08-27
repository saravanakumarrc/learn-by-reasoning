# Authentication

> **Learning Path:** Security Architecture
> **Section:** 6.1.1 — Application security

## 1. Problem

உங்க system-ல ஒரு API இருக்கு. Web app, mobile app, partner-ஆல் call பண்ணப்படுது. ஒரு request வரும்போது அது யாருடையது என்று தெரியாமல் இருந்தால் business logic-ஐயும் trust பண்ண முடியாது.

HTTP stateless. ஒவ்வொரு request-ம் தனியாக வரும். User ஒரு முறை login பண்ணினால், அடுத்த 100 request-க்கும் அதே user தான் என்று எப்படி கண்டுபிடிப்பது?

Password-ஐ ஒவ்வொரு request-லும் அனுப்புவது வேலை செய்யாது. Network failure, retry, log leakage எல்லாம் பிரச்சனை.

இங்கே தான் Authentication தேவைப்படுகிறது. **Who are you?** என்று prove பண்ண வேண்டும்.

## 2. Mental Model

Authentication = identity prove பண்ணுவது.
Authorization = prove பண்ணிய பிறகு என்ன செய்ய அனுமதி உண்டு என்பது.

Authentication-ஐ ஒரு வீட்டு அடையாள அட்டை போல் நினைத்துக்கொள்ளுங்கள். Security guard ஒரு முறை ID-யை பார்த்து badge கொடுப்பான். அந்த badge தான் அடுத்த முறை prove ஆகும்.

Proof என்பது பொதுவாக:
* something you know - password, PIN
* something you have - device, OTP
* something you are - biometric

நாம் engineer-களாக அந்த proof-ஐ எப்படி safely carry பண்ணுவது, எவ்வளவு நேரம் valid, எப்படி revoke பண்ணுவது என்று முடிவு செய்ய வேண்டும்.

## 3. How It Works

Core flow எப்போதும் ஒன்று தான்:

1. **Verify credentials**: user-id + password / OTP வந்தால் auth service-ல verify பண்ணு.
2. **Issue proof**: verify ஆனால் session அல்லது token கொடு.
3. **Present proof**: client ஒவ்வொரு request-லும் அந்த proof-ஐ அனுப்பும்.
4. **Validate proof**: API gateway / service proof-ஐ validate பண்ணி request-ஐ allow பண்ணும்.

Proof-ஐ carry பண்ண இரண்டு பொதுவான வடிவங்கள்:

* **Session cookie**: Server-ல session store வைத்து cookie-ல session id கொடுக்கிறோம். ஒவ்வொரு request-லும் cookie வரும், server store-ல check பண்ணி user-ஐ தெரிந்துகொள்ளும்.
* **Stateless token**: Server user-ஐ verify பண்ணி signed JWT அல்லது opaque access token கொடுக்கும். Client அதை அடுத்த request-ல Authorization header-ல வைத்து அனுப்பும். Service token-ஐ signature மூலம் validate பண்ணிக்கொள்ளும், DB hit இல்லாமல்.

Refresh token pattern: access token குறுகிய காலம், refresh token நீண்ட காலம். Access token expire ஆனால் refresh token-உள் புதிய access token வாங்கிக்கொள்ளலாம்.

OAuth2 / OIDC இங்கே வருவது third-party access-க்கு. உங்கள் app-க்கு user-ஐ authenticate பண்ணுவதற்கு பதில் Google, Okta போன்ற identity provider-ஐ trust பண்ணுவது.

```mermaid
graph LR
Client -->|credentials| AuthService
AuthService -->|issue token| Client
Client -->|Authorization: Bearer token| API Gateway
API Gateway -->|verify signature / introspect| AuthService
API Gateway -->|allow| Microservice
```

## 4. Architectural Reasoning

**Monolith + browser** என்றால் session cookie + server-side session store போதும். Simple, revocation எளிது.

**Distributed microservices + mobile + web + third-party** என்றால் stateful session பிரச்சனை. ஒவ்வொரு service-க்கும் session store-ஐ share பண்ண வேண்டும் அல்லது sticky routing
