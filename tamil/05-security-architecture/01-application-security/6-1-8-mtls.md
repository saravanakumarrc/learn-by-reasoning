# mTLS

> **Learning Path:** Security Architecture
> **Section:** 6.1.8 — Application security

## 1. Problem

உங்க company-ல 50+ microservices இருக்கு. எல்லாம் Kubernetes-ல ஓடுது. Service A, Service B-ஐ HTTPS வழியா call பண்ணுது.

TLS இருக்கு, அதனால connection encrypted. ஆனா யார் call பண்ணுறாங்கன்னு server-க்கு உறுதியா தெரியுமா?

Regular TLS-ல server தான் certificate காட்டும். Client யாருன்னு verify பண்ண மாட்டேங்குது. Network-க்குள்ளயே ஒரு compromised pod இருந்து அல்லது insider இருந்து யாரும் அதே internal API-ஐ அழைக்கலாம்.

அப்புறம் அந்த call legitimate-ஆ, அல்லது spoofed-ஆன்னு எப்படி differentiate பண்ணுவது?

இதுதான் mTLS வர காரணம்.

## 2. Mental Model

TLS = server-க்கு ID card காட்டுறது.
mTLS = இரண்டு பேரும் ஒருத்தருக்கு ஒருத்தர் ID card காட்டுறது.

Client-க்கும் server-க்கும் certificate இருக்கும். Handshake-ல இரண்டு பக்கமும் certificate present பண்ணி, CA verify பண்ணி, "நீ நீ தான்" என்று confirm பண்ணிக்கும்.

இது authentication, encryption இரண்டையும் கொடுக்கும். ஆனா key difference: trust ஒரு திசையில் இல்லை, இரண்டு திசையிலும்.

## 3. How It Works

Standard TLS handshake-ல server cert காட்டும். mTLS-ல client-ம் cert காட்ட வேண்டும்.

1. ClientHello போகும்
2. Server Hello + server certificate கொடுக்கும்
3. Client certificate request வரும்
4. Client தன்னோட certificate + private key proof கொடுக்கும்
5. இரண்டும் CA-வை trust பண்ணும் common root-ஆல verify பண்ணிக்கும்
6. Session keys establish ஆகும்

Certificate-ல identity இருக்கும்: service name, namespace, maybe SPIFFE ID. CA தான் issuing authority.

Service mesh-ல இது transparent ஆக handle ஆகும். Sidecar proxy handshake பண்ணும், app code மாற்ற தேவையில்லை.

## 4. Architectural Reasoning

mTLS useful ஆகும் போது:

* **Zero trust network** வேண்டும். Network perimeter-ல trust பண்ண முடியாது. Every hop verify வேண்டும்.
* Service-to-service communication sensitive. Payment, fraud, PII data access.
* Internal API-ஐ public internet-க்கு expose பண்ணாமல், private network-லயே run பண்ணும்போது அதை secure access control வேண்டும்.

Alternatives என்ன?

* Network-level firewall + IP whitelist. ஆனா IP spoof பண்ணலாம், pod restart-ல IP மாறும்.
* API key / bearer token. Revoke பண்ண கஷ்டம், leak ஆனால் rotate பண்ண வேண்டும், secret management overhead.
* Service mesh without mTLS: encryption இல்லை, eavesdropping possible.

எனவே architect-க்கு mTLS என்பது identity-based authentication, encryption கலந்த solution.

## 5. Trade-offs

**Certificate lifecycle management.** Certificates expire. Rotate பண்ண வேண்டும். 1000 pods-க்கு manual பண்ண முடியாது. Automated CA, cert-manager, SPIFFE/SPIRE போன்ற infrastructure தேவை.

**Operational complexity.** Trust anchor ஒன்னு உடைஞ்சா whole mesh down. CA compromise ஆனால் disaster. Certificate revocation real-time handle பண்ண வேண்டும்.

**Performance overhead.** Handshake CPU intensive. Connection reuse, session resumption, TLS 1.3 உபயோகித்து overhead குறைக்கலாம். Still latency-க்கு கொஞ்சம் கூடும்.

**Debugging கஷ்டம்.** Connection fail ஆனால் reason certificate validation fail ஆ? Expired? Wrong SAN? Wrong trust bundle? Observability தேவை.

Every solution creates new problem. mTLS trust boundary-ஐ service identity-க்கு மாற்றும், ஆனா PKI-யை reliable ஆக run பண்ண வேண்டும்.

## 6. Practical Example

Enterprise banking: `payment-service` -> `fraud-detection-service`

இரண்டும் same namespace-ல இல்லை, different teams own பண்ணுறாங்க.

Istio service mesh mTLS enforce பண்ணியிருக்கு. `payment-service` pod start ஆகும்போது sidecar-க்கு SPIFFE certificate issue ஆகும்: `spiffe://bank.internal/ns/payments/sa/payment-service`

`fraud-detection-service` அந்த request வரும்போது certificate verify பண்ணும்: identity match ஆகுதா? Certificate valid ஆ? CA trust ஆகுதா?

ஒரு attacker `payment-service` name spoof பண்ணி request அனுப்பினாலும் certificate இல்லாமல் handshake fail ஆகும். Network access இருந்தாலும் போதாது.

Audit log-ல who called whom என்பது certificate identity-ல தெரியும்.

## 7. Reasoning Challenge

உங்களிடம் public facing API gateway இருக்கு, அதுக்கு பின்னால 20 internal services. External clients gateway-ஐ மட்டும் access பண்ணும். Internal traffic-க்கு mTLS வேண்டுமா? Gateway-ல இருந்து backend-க்கு token-based auth போதுமா?

என்ன threat model பார்க
