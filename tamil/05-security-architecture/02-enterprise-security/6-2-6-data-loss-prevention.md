# Data loss prevention

> **Learning Path:** Security Architecture
> **Section:** 6.2.6 — Enterprise security

## 1. Problem

உங்க company-ல customer PII, payment data, internal source code, M&A documents இருக்கு. இதை lose பண்ணினால் fine வரும், reputation போகும், customer trust போகும்.

உண்மையான pain என்ன தெரியுமா? Data திருடப்படுவது மட்டும் இல்லை. **நேர்மையான engineer கூட தெரியாமல் data leak பண்ணிடுவது.**

ஒரு developer log-ல customer Aadhaar number print பண்ணிட்டார். அது public log aggregator-க்கு போய் விட்டது.
Sales team ஒரு confidential pricing sheet-ஐ personal Gmail-க்கு forward பண்ணினார்.
Engineer S3 bucket-ஐ public read செய்து வைத்தார்.
இவை எல்லாம் malicious attack அல்ல. Human error + lack of control.

இங்கே வரும் கேள்வி: **Data எங்கே போகிறது என்பதை நாம் எப்படி பார்க்க முடியும், எப்போது தடுக்க முடியும்?**

## 2. Mental Model

Data loss prevention என்பது firewall அல்ல. Firewall external attacker-ஐ தடுக்கும். DLP என்பது **உள்ளே இருக்கும் data வெளியே போகாமல் பார்த்துக்கொள்வது.**

மூன்று states இருக்கு:

* **Data at rest** - database, file share, laptop, S3 bucket
* **Data in use** - application memory, editor, email compose window
* **Data in motion** - email, API call, file upload, copy-paste, Slack message

DLP இவற்றை classify பண்ணி, policy வைத்து, inspect பண்ணி, action எடுக்கும். Think of it as a data-aware gatekeeper.

## 3. How It Works

Core loop மூன்று விஷயம்:

**1. Classify** 
Sensitive data எது என்று தெரிய வேண்டும். Regex patterns, keywords, ML-based classification, metadata tags. Credit card number = 16 digits + Luhn check. PII = name + phone combo.

**2. Policy**
Who can access what, where can it go. Eg: PII data can leave only via approved DLP gateway, personal email-க்கு அனுப்பக்கூடாது, public internet-க்கு upload தடை.

**3. Inspect & Act**
Channel-ல intercept பண்ணி inspect செய்யும். Action: allow, block, quarantine, encrypt, redact, alert.

Typical enforcement points:
* **Network DLP** - proxy, egress gateway, inspect outbound traffic
* **Endpoint DLP** - laptop agent, USB block, screenshot prevention, clipboard control
* **Cloud/SaaS DLP** - CASB for Gmail, Slack, Drive, Salesforce
* **API/Storage DLP** - scan bucket uploads, database DML hooks

## 4. Architectural Reasoning

DLP தேவைப்படுவது எப்போது?

உங்களுக்கு compliance தேவை இருக்கும் போது - GDPR, PCI-DSS, HIPAA. Audit-ல "எப்படி data leak ஆகாமல் தடுக்கிறீர்கள்?" என்று கேட்பார்கள்.

முக்கிய constraint இது: **Visibility இல்லாமல் control இல்லை.** நீங்கள் data flow தெரியாமல் policy போட முடியாது.

Alternatives என்ன?
* Pure encryption: data secure ஆகும், ஆனால் leak ஆனாலும் leak ஆகும், misuse தடுக்காது
* Access control மட்டும்: who can read தெரியும், where they copy paste பண்ணுவார்கள் தெரியாது
* Training alone: works until human error

DLP ஏன் choose பண்ணுவது? Because you need **context-aware enforcement**. Data என்ன, user யார், destination எது என்பதை பார்த்து முடிவு.

## 5. Trade-offs

**Visibility vs Privacy.** DLP inspect பண்ண வேண்டும் என்றால் content read பண்ண வேண்டும். அது employee privacy கேள்வி எழுப்பும். Over-inspect பண்ணினால் trust போகும்.

**False positive vs False negative.** Credit card regex அடித்தால் random 16-digit number-க்கும் alert வரும். Too strict ஆனால் users frustrate ஆகி work-around பண்ணுவார்கள். Too loose ஆனால் leak நடக்கும்.

**Friction vs Security.** Block personal email transfer என்றால் sales team productivity பாதிக்கும். Architect-க்கு இங்கே trade-off பண்ண வேண்டும்.

**Operability.** DLP rules maintain பண்ண வேண்டும், classification taxonomy update பண்ண வேண்டும், false positives tune பண்ண வேண்டும். இது dedicated team இல்லாமல் fail ஆகும்.

Failure mode முக்கியம்: DLP bypass ஆகலாம். Eg: user data-ஐ screenshot எடுத்து phone-ல photo எடுத்து WhatsApp செய்வது. அதற்கு endpoint DLP + culture needed.

## 6. Practical Example

Enterprise with Gmail, Slack, S3.

Architecture:
User uploads file to Drive -> CASB intercepts -> DLP scans content -> finds PAN card number -> policy says PII cannot go to personal account -> block and alert security.

Network egress: All outbound traffic goes via proxy with DLP inspection. Upload to dropbox.com with internal source code -> quarantine.

Endpoint: Developer laptop agent blocks copy-paste of classified documents to non-approved apps.

Result: Leak surface குறையும். Audit trail கிடைக்கும்.

## 7. Reasoning Challenge

உங்களிடம் 2000 engineers உள்ளனர். GitHub Enterprise, Slack, Jira, GDrive உள்ளன. Customer PII மட்டும் தடுக்க வேண்டும். False positive காரணமாக daily 500 alerts வருகிறது. Security team overwhelmed.

இங்கே என்ன மாற்றம் செய்வீர்கள்? Policy-ஐ தளர்த்துவீர்களா, classification-ஐ மேம்படுத்துவீர்களா, அல்லது enforcement point-ஐ ம
