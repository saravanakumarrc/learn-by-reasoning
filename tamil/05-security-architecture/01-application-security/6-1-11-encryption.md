# Encryption

> **Learning Path:** Security Architecture
> **Section:** 6.1.11 — Application security

## Problem

உங்க application ல user data, payment info, internal secrets எல்லாம் இருக்கு. அது எப்போதும் safe-ஆ இருக்கணும்னு நினைக்கிறீங்க.

ஆனா நிஜம் என்ன?

- DB dump leak ஆகும். Hacker ஒருத்தர் DB access பண்ணிட்டா plain text-லயே data கிடைச்சிடும்.
- Network ல sniffing பண்ணா API request/response படிச்சிடலாம்.
- Logs, backups, message queue, third-party service ல data கசிஞ்சிடும்.
- Insider threat இருக்கும்.

Compliance லயும் audit லயும் கேட்பார்கள்: data at rest encrypt ஆகியிருக்கா? in transit encrypt ஆகியிருக்கா?

இதுதான் encryption தேவைப்படுற painful problem.

## Mental Model

Encryption என்பது data-வை unreadable ஆக்குவது மட்டுமல்ல. அது **access control** மாதிரி.

Lock + Key மாதிரி நினைச்சுக்கோங்க. Data ஒரு பெட்டி. Key இல்லாம பெட்டியை திறக்க முடியாது.

முக்கியமானது lock அல்ல, **key-யை யார் வைத்திருக்கிறார்கள், எப்படி manage பண்ணுறீங்க** என்பதுதான்.

## How It Works

Application security ல encryption இரண்டு இடத்தில் வரும்.

**1. Data in transit**
Service to service call, client to server call. இங்கே TLS/HTTPS பயன்படுத்துவோம். TLS என்பது asymmetric encryption + symmetric encryption combo.

Client/server ஆரம்பத்தில் public key மூலம் symmetric session key exchange பண்ணும். அதுக்குப் பிறகு data transfer fast ஆக symmetric encryption ல நடக்கும்.

இதன் பொருள்: network ல packet capture பண்ணினாலும் data plain text இல்லை.

**2. Data at rest**
DB, disk, backup, S3 object, secrets file. இங்கே data save ஆகும் முன் encrypt பண்ணி வைக்கணும்.

Symmetric encryption like AES-256 பொதுவா பயன்படுத்துவோம். Fast, bulk data க்கு நல்லது.

Asymmetric encryption like RSA/ECC பயன்படுத்துவது key exchange மற்றும் digital signature க்கு. Data encrypt பண்ண பெரிய overhead.

Application ல encrypt/decrypt பண்ணும் போது key எங்க இருக்கு? App code ல hardcode பண்ண கூடாது. KMS, Vault போன்ற key management service பயன்படுத்துவோம்.

## Architectural Reasoning

Encryption எல்லா data-க்கும் வேண்டாம்.

முதலில் data classification பண்ணுங்க:
- Public, Internal, Confidential, Restricted.

Confidential மேல் தான் encryption apply பண்ணுங்க. PAN, Aadhaar, password, API keys, PII.

Architect ஆக முடிவு எடுக்கும் போது கேள்விகள்:
- Data எங்க travel பண்ணுது? Network boundary இருக்கா?
- Data leak ஆனால் impact என்ன? Regulatory fine வருமா?
- Performance impact acceptable-ஆ? AES encryption CPU ல cheap ஆனாலும் high throughput system ல overhead கணக்கிடணும்.
- Key rotate பண்ண முடியுமா? Key lost ஆனால் data மீட்க முடியாது.

TLS for in transit almost mandatory. At rest encryption ஐ DB level, filesystem level, application level என மூன்று layer ல செய்யலாம். Application level தரும் control அதிகம், ஆனால் complexity அதிகம்.

## Trade-offs

**Security vs Operability.** Encryption strong ஆக இருந்தால் key management complex ஆகும். Key lost = data lost.

**Performance vs Protection.** Every encrypt/decrypt CPU cycle எடுக்கும். High read/write path ல premature encryption பண்ணினால் latency increase ஆகும்.

**Centralized vs Decentralized key.** Central KMS simple, single point of failure + availability dependency. Local key management resilient ஆனால் rotation nightmare.

**Compliance vs Practicality.** Compliance சொல்லும் encrypt all PII. ஆனால் search, indexing, analytics செய்யும் போது encrypted data usable இல்லை. அதனால் tokenization, field-level encryption போன்ற hybrid approaches தேவைப்படும்.

Failure mode: key rotation செய்யாமல் விட்டால் key leak ஆனால் பழைய data எல்லாம் expose ஆகும். Backup ல old key இருந்தால் backward compatibility கவனிக்கணும்.

## Practical Example

ஒரு fintech app. User PAN, card token store பண்ணணும்.

DB-ல PAN column plain text வைக்காமல் application level ல encrypt பண்ணி store பண்ணுங்க. Key KMS ல வைத்து
