# Data classification

> **Learning Path:** Security Architecture
> **Section:** 6.2.5 — Enterprise security

# Data classification

## 1. Problem

உங்க enterprise-ல data எங்கே எங்கே இருக்கு தெரியுமா? Production database-ல, object storage-ல, data lake-ல, employee laptop-ல, Slack-ல, third-party SaaS-ல. ஒரு developer backup எடுத்து personal S3 bucket-ல வச்சுட்டார். Marketing team customer list-ஐ Google Sheet-ல share பண்ணியிருக்காங்க.

இப்போ breach ஆனால் என்ன ஆகும்? எல்லா data-யும் same level-ல protect பண்ணுவீங்களா? அது cost ஆகும். எதையும் protect பண்ணாம விடுவீங்களா? அது risk.

உண்மையில் problem இது: **நமக்கு data-யின் sensitivity தெரியாததால், security control-ஐ எங்கே apply பண்ணணும்னு தெரியல**. Over-protect பண்ணினா developer productivity drop. Under-protect பண்ணினா GDPR, PCI DSS fine வரும், breach ஆனால் reputation loss.

Data classification தேவைப்படுவது இந்த confusion-ஐ clear பண்ண.

## 2. Mental Model

Data classification என்பது data-க்கு ஒரு label கொடுப்பது. அந்த label சொல்லும்: இந்த data எவ்ளோ sensitive, யார் access பண்ணலாம், எப்படி store பண்ணணும், எப்படி transmit பண்ணணும், எப்படி delete பண்ணணும்.

Mental model simple: **Impact-based labeling**.

Public < Internal < Confidential < Restricted

அல்லது regulatory driven: PII, PHI, PCI, IP.

Label ஒன்னு data-வோடு attach ஆகும்போது, அதுக்கு policy automatic-ஆ apply ஆகும். Architect-க்கு இது system boundary தீர்மானிக்க உதவும்.

## 3. How It Works

Classification ஒரு manual policy மட்டும் இல்ல. அது 3 layer-ல work ஆகும்.

**1. Policy definition:** Business + Legal + Security சேர்ந்து categories define பண்ணுவாங்க. உதாரணமாக:
- Public: marketing website content
- Internal: org chart, internal wiki
- Confidential: customer PII, financial reports
- Restricted: source code secrets, encryption keys, salary data

ஒவ்வொரு category-க்கும் handling rules இருக்கும்: encryption at rest & in transit, access control model, retention, logging, DLP.

**2. Discovery & labeling:** Data எங்க இருக்குன்னு கண்டுபிடிச்சு label போடணும். Manual tagging work ஆகாது. Data classification tool, scanner, metadata service use பண்ணி pattern match பண்ணுவோம். PII regex, credit card pattern, file header.

**3. Enforcement:** Label பார்த்து control apply ஆகணும். Access control policy, encryption policy, network segmentation, data loss prevention rule எல்லாம் classification label-ஐ பார்த்து trigger ஆகும்.

இது continuous process. Data create ஆகும்போது classify பண்ணு, move ஆகும்போது label travel பண்ணணும்.

## 4. Architectural Reasoning

Classification useful ஆகும் போது?

* Compliance இருக்கும் போது: GDPR-ல PII-க்கு right to erasure, PCI-ல card data-க்கு strict scope.
* Data sprawl இருக்கும் போது: 100+ services, data everywhere.
* Zero Trust implement பண்ணும்போது: access decision-க்கு context தேவை.

Architect என்ன தீர்மானிக்கிறார்?

* எத்தனை categories வேண்டும்? 3-4 categories best. Too many என்றால் engineer confuse ஆகுவான், mis-label ஆகும்.
* Classification centralized ஆ? Decentralized ஆ? Central policy + automated enforcement scalable.
* Label எங்க store பண்ணுவது? Data object metadata-ல, data catalog-ல, separate classification service-ல.

Alternative: everything encrypt பண்ணிட்டா போதுமா? இல்லை. Encryption solves confidentiality மட்டும். Audit, retention, sharing rules, DLP, backup scope எல்லாம் classification இல்லாமல் decide பண்ண முடியாது.

## 5. Trade-offs

**Granularity vs Usability:** More categories = more accurate control. ஆனால் developer எந்த label போடுவதுன்னு தெரியாமல் தடுமாறுவார். 4 levels போதும்.

**Automation vs Accuracy:** Auto classification fast, ஆனால் false positive/negative வரும். Regex-ல credit card போல இருக்கும் random number-ஐ PII ஆக mark பண்ணிடும். Human review loop தேவை.

**Consistency vs Speed:** Strict classification means every new data asset review வேண்டும். அது velocity-ஐ slow பண்ணும். ஆனால் skip பண்ணினால் shadow data create ஆகும்.

**Scope reduction vs operational complexity:** Restricted data-ஐ separate VPC, KMS key, tighter logging பண்ணலாம். அது security improve பண்ணும். ஆனால் cost, latency, ops overhead increase ஆகும்.

Failure mode: Mis-classification. Confidential data-ஐ Public ஆக label பண்ணினால் DLP block ஆகாது, leak ஆகும். Over-classification பண்ணினால் legitimate access block ஆகி business impact வரும்.

## 6. Practical Example

Enterprise bank. 

Data catalog scan பண்ணி கண்டுபிடித்தது:
- Customer KYC documents -> Restricted
- Transaction logs -> Confidential
- Marketing newsletter list -> Internal
- Product brochure -> Public

Policy: Restricted data must be encrypted with customer-managed KMS key, access via just-in-time approval, store only in private VPC, no internet egress. Confidential data must be encrypted, access via RBAC + MFA, retention 7 years.

Developer new microservice build பண்ணும்போது, data classification label API-ல query பண்ணி, அதுக்கு ஏற்ற encryption, logging, network policy auto apply ஆகும். Data share பண்ண வேண்டும் என்றால் DLP check பண்ணி label mismatch இருந்தால் block பண்ணும்.

Result: audit-க்கு evidence ready. Breach ஆனால் impact scope தெரியும். Cost குறையும், ஏனெனில் Public data-க்கு expensive control வேண்டாம்.

## 7. Reasoning Challenge
