# Backup strategies

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.2.3 — Disaster recovery & high availability

# Backup strategies

## 1. Problem

உங்க production database ஒரு நாள் காலையில் போய்விட்டது. Disk failure, accidental `DROP TABLE`, ransomware, அல்லது bad deployment. Data இல்லை.

இப்போது கேள்வி: எவ்வளவு தரவை திரும்ப கொண்டு வர முடியும்? எவ்வளவு நேரத்தில்?

இங்கே இரண்டு எண்கள் முக்கியம்: **RPO** - Recovery Point Objective, எவ்வளவு data loss ஏற்க முடியும். **RTO** - Recovery Time Objective, எவ்வளவு நேரத்தில் service திரும்ப வரணும்.

Backup இல்லாமல் இந்த இரண்டையும் கட்டுப்படுத்த முடியாது. Replication உயர் availability கொடுக்கும், ஆனால் தப்பு data replicate ஆகும். Backup தான் தவறு நடந்த பிறகு பழைய நிலைக்கு திரும்புவதற்கான வழி.

## 2. Mental Model

Backup என்பது point-in-time state-ஐ immutable ஆக சேமிப்பது.

ஒரு photo album மாதிரி. நீங்கள் தினமும் full photo எடுக்கலாம். அல்லது முந்தைய photo-விலிருந்து மாறியது மட்டும் எடுக்கலாம்.

முக்கியம்: backup எடுக்கும் போது application consistency தேவை. DB-ல் ஒரு transaction half-written இருக்கக்கூடாது. அதனால் snapshot, WAL, அல்லது freeze point தேவை.

## 3. How It Works

அடிப்படையில் மூன்று வகை:

**Full backup**: எல்லாவற்றையும் காப்பி. Simple, restore வேகம். ஆனால் size பெரியது, time எடுக்கும்.

**Incremental backup**: கடைசி backup-க்கு பிறகு மாறியது மட்டும். சிறிய size, வேகம். ஆனால் restore-க்கு full chain தேவை.

**Differential backup**: கடைசி full backup-க்கு பிறகு மாறியது. Incremental-ஐ விட restore எளிது, ஆனால் size வளரும்.

Practice-ல் hybrid தான் வேலை செய்யும். DB-கள் பெரும்பாலும் physical snapshot + WAL/transaction log streaming பயன்படுத்தும். PostgreSQL-ல் base backup + WAL archive = point-in-time recovery. MySQL-ல் Percona XtraBackup + binlog.

File system level-ல் EBS snapshot, LVM snapshot, ZFS snapshot போன்றவை block level copy-on-write செய்யும்.

3-2-1 rule ஒரு மனப்பதிவு: 3 copies, 2 different media, 1 offsite. இது ransomware மற்றும் site failure-க்கு பாதுகாப்பு.

## 4. Architectural Reasoning

Backup தேர்வு constraints-ஆல் முடிவாகிறது.

* **Data size & churn**: 5TB DB, தினமும் 200GB மாறினால் full daily செலவு அதிகம். Incremental + WAL தேவை.
* **RPO/RTO**: RPO 15 min வேண்டும் என்றால் continuous WAL shipping தேவை. RTO 1 hour வேண்டும் என்றால் backup warm copy, restore automation தேவை.
* **Consistency**: Running DB-ஐ backup எடுக்கும் போது crash-consistent போதுமா அல்லது application-consistent வேண்டுமா? Database snapshot lock பண்ண வேண்டும்.
* **Cost & operability**: S3 Glacier cheap ஆனால் restore slow. S3 Standard + IA வேறு trade-off.

Alternative: replication + PITR என்பது backup அல்ல. Replication lag இருக்கும், தப்பு replicate ஆகும். Backup என்பது immutable history.

## 5. Trade-offs

**Freshness vs cost**: அடிக்கடி backup எடுத்தால் RPO குறையும், storage & network cost அதிகரிக்கும்.

**Restore speed vs backup speed**: Incremental backup எடுப்பது வேகம், ஆனால் restore-க்கு chain rebuild தேவை. Full backup restore வேகம்.

**Consistency vs availability**: Online hot backup எடுக்கும் போது I/O impact வரும். Maintenance window-ல் full backup எடுத்தால் downtime இருக்கும்.

**Validation cost**: Backup எடுத்தோம் என்றால் போதாது. Restore test செய்ய வேண்டும். பல team-கள் backup எடுக்கிறார்கள், ஆனால் restore-ஐ test செய்வதில்லை. அது false safety.

Failure mode: backup storage-ஐயும் தாக்கும் ransomware, credentials leak ஆனால் backup delete ஆகும், backup corrupt ஆகும். அதனால் immutable bucket, versioning, separate credentials.

## 6. Practical Example

Enterprise e-commerce order DB, PostgreSQL 3TB.

Decision: Weekly full base backup Sunday இரவு, daily incremental via WAL archiving to S3 every 5 min. Retention: 30 days S3 Standard, 1 year S3 Glacier.

RPO ~5 min, RTO ~45 min for base restore + WAL replay.

Automation: Backup job Cron + monitoring. Restore drill மாதம் ஒரு முறை staging-ல் run. Backup validation checksum store.

Cost control: Full backup compress, deduplicate. WAL streaming-க்கு separate bucket with lifecycle policy.

இங்கே
