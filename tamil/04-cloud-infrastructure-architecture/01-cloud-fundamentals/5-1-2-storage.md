# Storage

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.1.2 — Cloud fundamentals

## 1. Problem

உங்க app ஒரு VM-ல ஓடுது. User upload பண்ணும் photo, local disk-ல save பண்ணீங்க.

இப்போ என்ன ஆகும்?
* VM crash ஆனா data போயிடும்.
* Traffic double ஆனா disk full ஆகும்.
* New region-க்கு expand பண்ணணும், data எப்படி move பண்ணுவீங்க?
* 50 instances இருந்தா ஒவ்வொன்னும் தனித்தனியா disk வச்சுக்க முடியாது.

On-prem-ல storage = server-உடன் கட்டப்பட்ட physical disk. Cloud-ல அது work ஆகாது. Scale, durability, availability எல்லாம் வேற level-ல பேசணும்.

## 2. Mental Model

Cloud-ல storage-ஐ மூன்று access pattern-ஆல பார்க்கணும், capacity-ஆல இல்ல.

* **Object storage**: Files as objects with key + metadata. HTTP API வழியா get/put/delete.
* **Block storage**: Raw disk blocks. VM-க்கு attach பண்ணி local disk மாதிரி use பண்ணலாம்.
* **File storage**: Shared filesystem. Multiple services/VM-கள் ஒரே path-ல read/write பண்ணலாம்.

ஒன்று பெரிய மனப்பதிவு: Cloud storage durable and managed ஆக இருக்கும். Replication, failure handling, scaling provider பார்த்துக்குவான். நீங்க பார்க்க வேண்டியது consistency model, latency, cost, access pattern.

## 3. How It Works

Object storage எப்படி வேலை செய்யும்?

Client API call பண்ணி `PUT /bucket/key` அனுப்பும். Storage service அதை multiple AZ-களில் replicate பண்ணி, erasure coding வச்சு store பண்ணும். Read request வந்தா closest region-ல இருந்து serve ஆகும்.

Block storage என்பது VM-க்கு attach ஆகும் volume. IOPS, throughput கண்ட்ரோல் பண்ணலாம். Snapshot எடுக்கலாம். VM move ஆனாலும் volume detach/attach பண்ணலாம்.

File storage என்பது NFS/SMB மாதிரி network share. Multiple nodes common data வேண்டிய microservices-க்கு useful.

## 4. Architectural Reasoning

**எப்போ object storage?**
Immutable, large files, infrequent access, massive scale. User uploads, images, videos, backups, ML datasets, RAG embeddings artifacts.

**எப்போ block storage?**
Database volume, OS disk, performance-sensitive workload. Low latency random I/O வேண்டும். MySQL/Postgres data directory, application logs local.

**எப்போ file storage?**
Shared config, content repo, web assets multiple servers-க்கு. Legacy app migration, CI artifacts shared across pods.

Decision driver: access pattern, not file size.

> Write-once read-many = object
> Low-latency random read/write = block
> Concurrent shared read/write = file

## 5. Trade-offs

* **Durability vs Latency**: Object storage 11 9s durability கொடுக்கும், ஆனா latency 50-150ms. Block storage single-digit ms, ஆனா நீங்க backup strategy உருவாக்கணும்.
* **Consistency**: Object storage eventual consistency read-after-write சில நேரம் தாமதம் ஆகும். Database க்கு block storage தேவை.
* **Cost**: Object storage cheap per GB, PUT/GET request charge ஆகும். Block storage expensive ஆனா predictable performance.
* **Operability**: Managed storage = less ops. ஆனா vendor lock-in, egress cost வரும். Cross-region copy பண்ணும்போது network cost பெரிசு.

Failure mode: Object storage region down ஆனா multi-region replication இல்லைன்னா data inaccessible. Block storage AZ failure ஆனா attached volume inaccessible, VM crash.

## 6. Practical Example

E-commerce platform.

Product images: User upload → API gateway → S3 compatible object storage. CloudFront-ஆல cache பண்ணி serve. Metadata DB-ல URL மட்டும் store. Scale infinite, cost low.

Transactional DB: RDS with EBS volume. Low latency, consistent writes தேவை. Snapshot automate பண்ணி backup.

Shared CMS assets: EFS mount பண்ணி 3 web servers share பண்ணும். Deploy சமயம் config file update ஒரே இடத்தில்.

இங்கே மூன்று storage types ஒரே system-ல.

## 7. Reasoning Challenge

உங்க service-க்கு 10k requests/sec வருது. Each request ஒரு 1KB JSON config file-ஐ
