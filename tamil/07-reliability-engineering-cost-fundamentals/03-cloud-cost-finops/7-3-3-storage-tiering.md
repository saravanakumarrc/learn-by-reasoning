# Storage tiering

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.3.3 — Cloud cost / FinOps

### 1. Problem

உங்கள் system 3 வருஷமா grow ஆகுது. User uploads, logs, backups, audit data எல்லாம் object storage-ல குவிஞ்சுடுச்சு. 50 TB ஆகிடுச்சு.

பில்லை பார்க்கும் போது ஷாக் ஆகுது. ஏன்னா எல்லாத்துக்கும் S3 Standard / SSD tier-ல தான் வச்சிருக்கீங்க. ஆனா உண்மையில் 90% data கடந்த 6 மாசமா யாரும் access பண்ணல. மாசத்துக்கு ஒரு தடவை ஒரு report-க்கு தேவைப்படும் backup, cold archive video, பழைய user profile.

இங்கே painful point என்ன? **Access pattern ஒரே மாதிரி இல்லை, ஆனால் cost ஒரே மாதிரி இருக்கு.** Hot data-க்கு தேவைப்படும் low latency-க்கு நீங்கள் cold data-க்கும் பணம் கொடுத்துட்டு இருக்கீங்க.

இதை தொடர்ந்தா FinOps கணக்கு முற்றிலும் break ஆகும்.

### 2. Mental Model

Storage tiering என்பது data-ன் temperature பார்த்து வைக்கும் இடத்தை மாற்றுவது.

Hot = இப்போதே தேவை, milliseconds-ல access வேண்டும்
Warm = அடிக்கடி இல்லை, ஆனால் மாசத்துக்கு ஒரு தடவை access ஆகலாம்
Cold / Archive = கிட்டத்தட்ட access இல்லை, compliance / audit-க்கு மட்டும்

நினைச்சுக்கோங்க library shelf மாதிரி. அடிக்கடி எடுக்கும் புத்தகம் reading table-ல வைக்கணும். ஒரு வருஷமா எடுக்காத புத்தகம் basement archive-க்கு போகலாம். Access செய்யணும்னா எடுக்க நேரம் ஆகும், ஆனா shelf space save ஆகும்.

### 3. How It Works

Cloud storage-ல இது lifecycle policy மூலம் automate ஆகுது.

S3-ல உதாரணமா:
Standard → Standard-IA → Glacier Instant → Glacier Deep Archive

ஒரு object create ஆனதும் Standard-ல இருக்கும். Policy சொல்லும்:
`90 நாள் access இல்லைனா IA-க்கு மாத்து, 365 நாள் ஆனா Glacier-க்கு மாத்து`

Tier move என்பது physically data move இல்லை, metadata + backend storage class மாற்றம். Retrieval செய்யும் போது tier-க்கு ஏற்ற minimum latency & retrieval fee வரும்.

Block storage / database-ல tiering வேற மாதிரி இருக்கும். EBS ல gp3 vs sc1 vs st1, அல்லது Postgres tablespace-ல hot table SSD, historical partition HDD / object storage-க்கு offload.

Intelligent Tiering option இருக்கு, access pattern monitor பண்ணி auto move பண்ணும். ஆனா monitoring cost உண்டு.

### 4. Architectural Reasoning

Tiering useful ஆகும் போது:
* Data volume பெருசா இருக்கு, ஆனா access pattern skewed
* Cost constraint தெளிவா இருக்கு, SLA hot data-க்கு மட்டும்
* Data retention compliance தேவை, delete பண்ண முடியாது

என்ன constraint address பண்ணுது? **Cost per GB vs latency SLA trade-off-ஐ decouple பண்ணுது.**

Alternatives:
* எல்லாம் ஒரே tier-ல வச்சுட்டு cost ஏற்றுக்கொள்ளுதல்
* Manual archival scripts
* Delete பண்ணிடுதல் - இது compliance risk

Architect ஏன் choose பண்ணுவார்? Hot path latency-ஐ protect பண்ணிக்கிட்டு, cold data-க்கு cost குறைக்க. பெரும்பாலான systems-ல 80/20 rule work ஆகும். 20% data 80% access.

### 5. Trade-offs

* **Latency vs Cost:** Glacier Deep Archive retrieval 12 மணி நேரம் வரை ஆகும். User-facing feature-க்கு இது acceptable இல்லை. Tiering என்பது latency budget-ஐ accept பண்ணி cost குறைக்கும் முடிவு.
* **Retrieval cost & egress:** Archive tier-ல இருந்து எடுக்கும் போது per GB retrieval fee உண்டு. திடீர்னு bulk restore தேவைப்பட்டா bill shock வரும்.
* **Transition cost & risk:** Tier move-க்கு API call cost, சில systems-ல early deletion fee. Policy misconfigure பண்ணி important data cold tier-க்கு போய் விட்டால் recovery slow.
* **Operational complexity:** அதிக tier = monitoring, lifecycle testing, restore drill. Team size சின்னதா இருந்தா overhead கூடும்.

Failure mode: Lifecycle policy `last accessed` base-ல இருந்தால், background job scan பண்ணாத object miss ஆகும். அல்லது metadata தான் hot, data cold.

### 6. Practical Example

Enterprise e-commerce platform. Orders, logs, user uploads.

* Hot: last 30 days orders, user profile, product catalog → S3 Standard / SSD, read latency < 50ms
* Warm: 31-180 days orders, application logs → S3 Standard-IA / S3 Infrequent Access
* Cold: > 180 days orders, yearly audit logs, raw video ads → Glacier Instant
* Deep Cold: 7 years retention for compliance, never access → Glacier Deep Archive

DB-ல partitioned table. `orders_
