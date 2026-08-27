# Resource limits

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.12 — Kubernetes

## Problem

உங்க Kubernetes cluster-ல ஒரே node-ல 20 pods ஓடுது. எல்லாம் normal-ஆ இருக்கு. திடீர்னு ஒரு service-ல traffic spike வந்தது. அந்த pod முழு node CPU-வையும், memory-யையும் எடுத்துக்குது.

என்ன ஆகும்?
மற்ற 19 pods slow ஆகும், API latency spike ஆகும், database connection pool drain ஆகும். Node-ல memory pressure வந்து kernel OOM killer random pod-ஐ kill பண்ணும். யாருடைய pod என்று தெரியாமல் production incident ஆகும்.

இது noisy neighbor problem. ஒரு tenant முழு shared resource-ஐயும் எடுத்துக்கும் போது cluster-ன் stability போய்விடும். இதை தடுக்கவே resource limits தேவை.

## Mental Model

Node-ல resources finite. CPU, memory ஒரு shared pool. 

Kubernetes-ல இரண்டு concept இருக்கு:
* **requests**: scheduler-க்கு சொல்லும் "இதுவாவது தேவை" என்ற guarantee. Pod இதற்கு கீழ் இருந்தால் schedule ஆகும்.
* **limits**: hard cap. Pod இதை தாண்டினால் throttle அல்லது kill.

அதாவது requests = reservation, limits = ceiling. Hotel room book பண்ணும்போது minimum guarantee vs maximum allowed என்பது போல.

## How It Works

Pod spec-ல resources set பண்ணுறோம்:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

Scheduler node selection செய்ய requests-ஐ பார்க்கும். Node-ல போதுமான allocatable CPU/memory இருந்தால் மட்டுமே pod schedule ஆகும்.

Pod ஓட ஆரம்பித்த பிறகு:
* **CPU**: CFS quota மூலம் enforce ஆகும். Limit தாண்டினால் throttling ஆகும். Pod slow ஆகும் ஆனால் kill ஆகாது.
* **Memory**: Limit தாண்டினால் kernel OOM killer உடனே pod-ஐ kill பண்ணும். `OOMKilled` status வரும்.

இது ஒரு pod-ன் failure-ஐ மற்ற pods-க்கு spread ஆகாமல் தடுக்கும்.

## Architectural Reasoning

இது useful ஆகும் எப்போது?

Cluster multi-tenant ஆக இருக்கும் போது, அல்லது one node-ல mixed criticality services ஓடும் போது. Payment service, recommendation service ஒரே node-ல இருக்கக்கூடாது என்று isolation வேண்டும்.

Constraint: availability vs utilization. Limits இல்லாமல் utilization அதிகம், ஆனால் stability குறைவு. Limits strict ஆக்கினால் stability அதிகம், ஆனால் cost / waste அதிகம்.

Alternatives என்ன?
* Node level isolation: dedicated node pool per workload. வேலை செய்யும், ஆனால் cost அதிகம்.
* Over-provisioning: எல்லாம் separate node. Operational complexity அதிகம்.
* Resource limits + proper requests: best balance for shared clusters.

Architect choose பண்ணும்போது கேட்க வேண்டியது: இந்த workload burst ஆகுமா? Steady ஆ? Memory usage predictable ஆ? CPU bound ஆ? Memory bound ஆ?

## Trade-offs

**1. Requests vs Limits gap**
Requests low வச்சு limits high வச்சா packing efficient ஆகும், ஆனால் node-ல actual usage spike வந்தால் contention வரும். Requests = limits வச்சா waste ஆகும் ஆனால் predictable.

**2. CPU throttling vs latency**
CPU limit வைத்தால் pod burst-ஐ முழுவதும் பயன்படுத்த முடியாது. Throttling ஆனால் request latency spike ஆகும். High QPS service-க்கு இது பிரச்சனை.

**3. Memory limit = kill risk**
Memory limit தாண்டினால் immediate kill. App memory leak இருந்தால் crash loop வரும். Limits இல்லாமல் இருந்தால் node ஒட்டுமொத்தமாக crash ஆகும். இது trade-off: pod level failure vs node level failure.

**4. Cost vs reliability**
Strict limits + headroom வைத்தால் cluster stable ஆகும், ஆனால் cloud bill அதிகம். Under-provision பண்ணினால் noisy neighbor incidents வரும்.

## Practical Example

Enterprise API gateway + worker pods.

Gateway: low latency தேவை, CPU burst தேவை. Requests 1 CPU, Limits 2 CPU. Memory requests = limits, 1Gi. Throttling குறைவாக இருக்க வேண்டும்.

Worker: batch job, processing speed flexible. Requests 500m CPU, Limits 1 CPU. Memory requests 1Gi, Limits 2Gi. Memory spike handle பண்ணலாம், peak time-ல kill ஆக கூடாது.

Scheduler இதை பார்த்து node-ல fit பண்ணும். Gateway pod-ஐ kill பண்ணாமல், worker pod-ஐ limit-ல throttle / kill பண்ணி node-ஐ protect பண்ணும்.

## Reasoning Challenge

உங்களிடம் 3 node cluster இருக்கு. ஒவ்வொரு node-ம் 16 CPU, 64 Gi memory. 40 microservices ஓடுகின்றன. சில services steady, சில bursty.

நீங்கள் resource requests set பண்ணினால் total requested resources 80% node capacity-க்கு மேல் போகிறது. Limits set பண்ணாமல் இருக்கிறீர்கள். Traffic spike வந்தால் என்ன ஆகும்? 

Limits set பண்ண வேண்டுமா, requests குறைக்க வேண்டுமா, அல்லது node autoscaling / dedicated node pool தேவையா? எந்த trade-off-ஐ நீங்கள் accept பண்ணுவீர்கள்? ஏன்?

## Key Takeaways

* Resource limits noisy neighbor-ஐ தடுத்து cluster stability கொடுக்கும். Requests scheduling guarantee, limits enforcement cap.
* CPU limit = throttling, Memory limit = OOM kill. இரண்டின் failure mode வேறு.
* Requests = limits என்றால் predictable ஆனால் waste. Gap விட்டால் efficient ஆனால் contention risk.
* Limits இல்லாத cluster production-
