# Jobs

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.8 — Kubernetes

## 1. Problem

உங்க company-ல ஒவ்வொரு நாளும் இரவு 2 மணிக்கு billing report generate ஆகணும். Report generation என்பது finite work — data-ஐ read பண்ணி, aggregate பண்ணி, S3-ல file-ஆ save பண்ணி முடிந்துவிடும். ஒரு மணி நேரத்தில் முடியும்.

இதை நீங்கள் எப்படி orchestrate பண்ணுவீர்கள்?

Pod-ஐ manually create பண்ணி விட்டால், pod crash ஆனால் யார் restart பண்ணுவது? Deployment போட்டால் replica 1 pod எப்போதும் run ஆகும், வேலை முடிந்தும் pod idle-ஆ இருக்கும். Cron-ஐ node-ல வச்சு run பண்ணினால் node down ஆனால் job skip ஆகும்.

**Pain point:** வேலை முடிய வேண்டும், முடிந்ததும் நிற்க வேண்டும், fail ஆனால் தானாக retry ஆக வேண்டும், மற்றும் எத்தனை முறை success ஆக வேண்டும் என்பது தெரிந்திருக்க வேண்டும்.

இதற்குத்தான் Kubernetes-ல Job வந்தது.

## 2. Mental Model

Job = **ஒரு வேலையை முடிக்கும் controller**.

நீங்கள் ஒரு Job object-ஐ create பண்ணுகிறீர்கள். அது ஒன்று அல்லது பல Pod-களை உருவாக்கி, அவை வெற்றிகரமாக exit ஆகும் வரை கண்காணிக்கும். வேலை முடிந்ததும் Job complete ஆகும். Pod-கள் clean ஆகிவிடும்.

Deployment என்பது **long-running service-க்கு**. Job என்பது **finite batch work-க்கு**.

## 3. How It Works

Job controller continuous-ஆ Job object-ஐ watch பண்ணும்.

Job spec-ல முக்கியமானது:

* **completions**: எத்தனை successful Pod முடிவு வேண்டும். default 1.
* **parallelism**: ஒரு நேரத்தில் எத்தனை Pod run பண்ணலாம்.
* **backoffLimit**: fail ஆன Pod-ஐ எத்தனை முறை retry பண்ண வேண்டும்.
* **restartPolicy**: Job-க்கு `OnFailure` அல்லது `Never`. இது முக்கியம். Job வேலை முடிந்த பிறகு restart வேண்டாம்.

உதாரணமாக, 10 files-ஐ process பண்ண வேண்டும் என்றால் `completions: 10` மற்றும் `parallelism: 5` வைத்தால் 5 Pod-கள் ஒரே நேரத்தில் ஓடி, மொத்தம் 10 successful run ஆனதும் Job complete ஆகும்.

Pod exit code 0 என்றால் success, மற்றது failure. Controller அதை கணக்கில் வைத்து retry decide பண்ணும்.

## 4. Architectural Reasoning

Job எப்போது useful?

* **Batch / ETL**: Nightly data export, DB backup, report generation.
* **One-off migration**: Schema migration, data backfill.
* **Short-lived compute**: Video transcoding, ML training run, test execution.

Constraint-ஐ பாருங்கள்: Work is finite, idempotent ஆக இருக்கலாம், முடிந்ததும் resource வேண்டாம்.

Alternatives:

* **Deployment + Cron**: Long-running service cron job உள்ளே trigger பண்ணும். Service எப்போதும் run ஆகும், cost + operational complexity.
* **CronJob**: Job-ஐ schedule பண்ணும் controller. Job ஒரு run, CronJob recurring runs.
* **Manual Pod**: Operability இல்லை.

Architect decision: Work finite + needs retry + needs completion guarantee என்றால் Job. Recurring schedule வேண்டுமென்றால் CronJob.

## 5. Trade-offs

* **Retry
