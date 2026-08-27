# CronJobs

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.9 — Kubernetes

## 1. Problem

VM-ல இருந்தீங்கன்னா `crontab -e` போட்டு `2 * * * * /script.sh` வச்சிட்டு போயிடலாம். Node ஒன்னு crash ஆனாலும் ஒரு node லயே ஓடும்.

Kubernetes-க்கு வந்ததும் பிரச்சனை வருது. Cluster-ல pods எங்கேயும் schedule ஆகலாம். Node down ஆகலாம். Scale up/down ஆகும். நீங்க ஒரு specific node-ல cron வச்சா அது **pet** மாதிரி ஆகுது. Pod மாதிரி manage பண்ண முடியாது. Logs எங்கே? Retry எப்படி? Monitoring எப்படி?

உங்களுக்கு தேவை: *time based* trigger ஆனாலும், அது Kubernetes-ன் lifecycle-க்குள்ள வரணும். Pod ஆக ஓடணும். Fail ஆனா restart policy இருக்கணும். History தெரியணும்.

அதான் CronJob வந்தது.

## 2. Mental Model

CronJob ஒரு daemon இல்லை. இது ஒரு **controller**.

`CronJob` object-ஐ Kubernetes API server-ல create பண்ணுறீங்க. CronJob controller வினாடிக்கு ஒரு தடவை கடிகாரத்தை பார்க்குது. Schedule match ஆனா ஒரு `Job` create பண்ணுது. அந்த Job ஒன்னு அல்லது அதிகமான Pod-களை spawn பண்ணுது. Job முடிஞ்சதும் Pod terminate.

மனசுல வச்சுக்கோங்க: **Schedule → Job → Pod → Done**. CronJob தானே ஓடிக்கிட்டு இருக்கு, ஆனா work எப்பவும் ephemeral.

## 3. How It Works

CronJob manifest-ல முக்கியமான fields:

* `schedule`: standard cron expression. `0 2 * * *` = தினமும் 2 AM
* `concurrencyPolicy`: `Allow`, `Forbid`, `Replace`. முந்தைய run முடியலைன்னா புதுசு ஓடுமா?
* `startingDeadlineSeconds`: schedule miss ஆனா எவ்வளவு நேரம் கழித்தும் run பண்ணக்கூடாது
* `jobTemplate`: எந்த container image, env, resources

Controller ஓடும் போது:

```mermaid
graph LR
A[CronJob Controller] -->|schedule matches| B[Job]
B --> C[Pod]
C -->|Success/Fail| D[Job status updated]
```

Pod success ஆனா Job complete ஆகும். Fail ஆனா `backoffLimit` படி retry.

## 4. Architectural Reasoning

CronJob useful ஆகும் போது:

* Work தெளிவா time bound. "ஒவ்வொரு நாளும் 3 AM-க்கு DB backup எடு". Event driven இல்லை.
* Work short to medium duration, முடிஞ்சதும் போதும். Long running daemon தேவை இல்லை.
* Idempotent ஆக இருக்கணும். ஏன்னா retry வரலாம்.

எப்போ choose பண்ணக்கூடாது:

* Work load dependent. Traffic அதிகமானா அப்போதான் run பண்ணணும் → queue / KEDA.
* Exactly-once guarantee கடுமையா வேணும் மற்றும் distributed lock தேவை → external scheduler.
* Millisecond precision தேவை → CronJob-ன் controller sync loop seconds level தான்.

Alternative: External cron service வச்சு Kubernetes API-க்கு call பண்ணுறது. அது complex, observability குறையும்.

## 5. Trade-offs

* **Simplicity vs Control**: CronJob setup எளிது. ஆனா backoff, retry, alerting Job level-ல மட்டும் தான். Advanced workflow வேண்டும்னா Argo Workflows போன்றது பார்க்கணும்.
* **Overlapping runs**: Default-ல concurrency allow. Job 30 mins ஆகுது, schedule 15 mins interval-ன்னா overlap ஆகும். `concurrencyPolicy: Forbid` வச்சா skip ஆகும். இது silent data loss மாதிரி ஆகலாம்.
* **Time zone & missed runs**: CronJob controller UTC-ல ஓடும். `timeZone` field recent Kubernetes-ல வந்திருக்கு. Node failure time-ல schedule miss ஆனா `startingDeadlineSeconds` க்கு அப்புறம் skip.
* **Observability**: Job history Kubernetes-ல தங்கும். நீங்க retention manage பண்ணணும். மாறாக systemd cron-ல log file rotate automatic.

Failure mode: Job create ஆனா Pod pending ஆகி நிற்கும். Resource quota இல்லாம. இதை நீங்க capacity planning-ல handle பண்ணணும்.

## 6. Practical Example

Enterprise-ல nightly sales aggregation:

* `sales-aggregator-cronjob` `0 1 * * *` schedule.
* JobTemplate 2 replicas, resource request 1 CPU / 2
