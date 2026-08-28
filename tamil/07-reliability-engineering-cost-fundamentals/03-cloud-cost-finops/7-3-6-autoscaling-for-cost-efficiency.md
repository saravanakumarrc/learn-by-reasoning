# Autoscaling for cost efficiency

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.3.6 — Cloud cost / FinOps

## 1. Problem

நீங்கள் ஒரு SaaS product-ஐ cloud-ல run பண்ணுறீங்க. Traffic weekday morning-ல low, evening-ல peak, weekend-ல வேற மாதிரி. Black Friday-ல 10x spike வரும்.

இப்போ இரண்டு மோசமான வழிகள் மட்டுமே இருக்கு:

* Peak-க்கு ஏத்தபடி capacity over-provision பண்ணுவது. Bill முழுக்க waste. Idle node-கள் 70% நேரம் காத்திருக்கும்.
* Peak-க்கு ஏத்தபடி provision பண்ணாமல் இருப்பது. Latency spike, error rate increase, customer impact.

FinOps-ல முதல் பிரச்சனை cost waste. இரண்டாவது reliability problem.

இதை தீர்க்க தான் autoscaling வந்தது. Capacity-ஐ demand-க்கு ஏத்த மாதிரி dynamic-ஆ adjust பண்ணுவது.

## 2. Mental Model

Autoscaling என்பது thermostat மாதிரி.

Room temperature high ஆனால் AC கூடுதல் cool பண்ணும். Low ஆனால் குறைக்கும்.

System-ல load அதிகமானால் pods / instances கூட்டுவது. Load குறைந்தால் குறைப்பது.

Goal இரண்டு விஷயம்: **availability maintain பண்ணணும், cost waste பண்ணக்கூடாது.**

## 3. How It Works

Core loop மூன்று step:

**Measure → Decide → Act**

*Measure:* metrics collect பண்ணுறோம். CPU utilization, memory, request rate / RPS, queue length, latency p95, custom business metric.

*Decide:* scaling policy trigger ஆகுமா என்பதை பார்க்கிறோம். உதாரணமாக Kubernetes HPA-ல `target CPU 60%`. Current average 75% என்றால் replica count கூட்டு.

*Act:* scale up / scale down பண்ணுறோம். Horizontal scaling என்றால் more pods/instances add பண்ணுவது. Vertical scaling என்றால் existing instance-க்கு CPU/memory கூட்டுவது.

இதில் cool down period முக்கியம். Scale up பண்ணிய உடனே அதை scale down பண்ணக்கூடாது. Oscillation avoid பண்ண. HPA-ல scale up cool down ~30 sec, scale down ~300 sec default மாதிரி.

Cloud native-ல இது autoscaler service handle பண்ணும். AWS Auto Scaling Group, GCP MIG, Kubernetes HPA + Cluster Autoscaler.

## 4. Architectural Reasoning

எப்போ autoscaling useful?

* Workload variable. Traffic daily/weekly pattern உண்டு.
* Request fast scale up ஆகணும். User-facing API.
* Cost sensitive. Idle capacity வைக்க முடியாது.

எப்போ கவனமாக இருக்கணும்?

* Cold start latency high. New pod/instance boot ஆக 30-60 sec ஆகும். User request-க்கு immediate response தேவைப்பட்டால் warm pool வைக்க வேண்டும்.
* Statefull workloads. Database replica scale up/down tricky.
* Scale event-க்கு cost அதிகம். Frequent scale up/down பண்ணினால் API call cost, operational overhead வரும்.

Alternatives:
* Over-provision + reserved instances. Predictable workload-க்கு சரி.
* Scheduled scaling. Known peak-க்கு முன்னாடியே scale up பண்ணுவது. Cost efficient, but unexpected spike-க்கு fail ஆகும்.
* Over-provision small buffer + autoscaling for spike.

Decision point: scaling signal எது? CPU மட்டும் போதாது. CPU low ஆக இருந்தாலும் thread pool full ஆகி latency spike ஆகலாம். RPS, queue depth, latency p95 போன்ற application-level metric சரியான signal கொடுக்கும்.

## 5. Trade-offs

**Cost vs Latency.** Scale up late பண்ணினால் cost save ஆகும், ஆனால் latency spike. Scale early பண்ணினால் cost அதிகம். இதுதான் core trade-off.

**Stability vs Responsiveness.** Aggressive scaling policy quick react பண்ணும், ஆனால் oscillation வரும். Conservative policy stable ஆக இருக்கும், ஆனால் spike-ல தாமதம்.

**Complexity vs Operability.** Autoscaling setup simple ஆக தோன்றும். Real-ல metric selection, cool down tuning, scale up/down limit, max replicas, node pool sizing, cost anomaly handling எல்லாம் operational burden.

Failure modes:
* Metric lag. Cloud metric 1 min interval. Spike-க்கு react பண்ண 2-3 min தாமதம். அதுக்குள்ள service down.
* Scale up bottleneck. Node autoscaler-க்கு new node provision ஆக 2-5 min ஆகும். HPA pod scale பண்ணினாலும் node இல்லாமல் pending-ல தங்கும்.
* Throttling. Too fast scaling-ல API rate limit hit ஆகும்.

## 6. Practical Example

E-commerce API, normal RPS 2000, flash sale-ல 20000 RPS.

Architecture: API service behind load balancer, deployed on Kubernetes. HPA based on RPS per pod and latency p95.

Normal-ல 10 pods run ஆகும். RPS per pod ~200. Sale start ஆனதும் latency p95 400ms-க்கு மேல போகுது. HPA target p95 <200ms என set பண்ணியிருக்கோம்.

HPA scale up trigger ஆகி 20 pods-க்கு scale up பண்ணுது. Cluster Autoscaler new node provision பண்ணுது. Warm pool-ல 2 node ready ஆக இருக்கு, cold start reduce பண்ண.

Sale முடிந்ததும் traffic drop. Scale down cool down 5 min வரை wait பண்ணி slow-ஆ pods reduce பண்ணுது. Night time-ல scheduled scale down to 4 pods.

Result: Peak handle ஆகும், idle cost குறையும். Bill 30-40% குறையும் compared
