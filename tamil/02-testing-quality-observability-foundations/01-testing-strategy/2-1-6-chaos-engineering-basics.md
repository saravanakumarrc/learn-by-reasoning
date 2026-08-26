# Chaos engineering basics

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.1.6 — Testing strategy

# Chaos engineering basics

## 1. Problem

நீங்கள் ஒரு distributed system கட்டினீர்கள். 20 microservices, API gateway, message queue, database, cache. Staging-ல load test பண்ணினீர்கள். Integration tests pass. Production-க்கு release பண்ணிய 2 மணி நேரத்தில் ஒரு service slow ஆகி, அதை depend பண்ணும் service-கள் timeout ஆகி, retry storm ஆரம்பித்து, எல்லாம் down.

இது ஏன் நடந்தது? ஏனென்றால் நீங்கள் failure-ஐ design பண்ணவில்லை. நீங்கள் happy path மட்டுமே test பண்ணினீர்கள்.

Production-ல network packet loss, node crash, disk full, latency spike, dependency outage எப்போதும் வரும். இதை reproduce பண்ணி test பண்ண முடியுமா? முடியாது. அதனால் நீங்கள் கற்றுக்கொள்வது: system எப்படி fail ஆகும் என்பது உங்களுக்கு தெரியாது.

Chaos engineering வருவது இங்கே தான்.

## 2. Mental Model

Chaos engineering = உங்கள் system-ஐ intentional-ஆக break பண்ணி, அது எப்படி react பண்ணுகிறது என்பதை பார்ப்பது.

இது testing அல்ல. இது learning. Hypothesis ஒன்றை வைத்து, controlled failure inject பண்ணி, steady state மாறுகிறதா என்று பார்க்கிறோம்.

Analogy: கார் ஓட்டும்போது brake fail ஆகும் என்பதை சாலையில் தான் தெரியும். நீங்கள் garage-ல brake-ஐ cut பண்ணி பார்க்க மாட்டீர்கள். Production தான் real road.

## 3. How It Works

ஒரு chaos experiment 4 படிகள்:

**Hypothesis:** நம்முடைய checkout service 50% latency increase ஆனாலும், error rate 1%க்குள் இருக்கும். Order success விகிதம் maintain ஆகும்.

**Steady state define:** Normal production-ல p95 latency < 200ms, error rate < 0.1%, throughput ~ 1000 RPS.

**Experiment:** Production-ல, limited blast radius-ல, ஒரு pod-ஐ kill பண்ணுவது. அல்லது network latency inject பண்ணுவது. அல்லது dependency service-க்கு traffic-ஐ throttle பண்ணுவது.

**Observe & verify:** Metrics, logs, traces-ல steady state maintain ஆகிறதா? Alert trigger ஆகிறதா? Cascading failure வருகிறதா?

Experiment fail ஆனால், அது தான் value. அங்கே தான் உங்கள் resilience gap தெரியும்.

Tools இதை automate பண்ணும்: Chaos Mesh, LitmusChaos, Gremlin, AWS Fault Injection Simulator. Netflix-ன் Chaos Monkey போன்றவை pod kill பண்ணி start ஆனது.

## 4. Architectural Reasoning

Chaos engineering useful ஆகும் போது:

* System distributed ஆகி, dependencies அதிகம் ஆகும்போது
* Availability, reliability SLA critical ஆகும்போது, financial transaction, payment, booking
* Team retry, timeout, circuit breaker, bulkhead போன்ற resilience patterns implement பண்ணியிருக்கிறது, ஆனால் அது உண்மையில் வேலை செய்கிறதா என்று தெரியவில்லை

Alternatives என்ன? 
* Chaos இல்லாமல், game day exercises: manual drill. Costly, not repeatable.
* Only synthetic monitoring: failure simulate பண்ணாது.
* Wait for real incident: அது learning ஆனால் expensive.

Architect choose பண்ணும்போது பார்ப்பது: blast radius control, automated rollback, observability maturity. Metrics, tracing இல்லாமல் chaos பண்ணுவது blind.

## 5. Trade-offs

**Risk vs Learning.** Production-ல failure inject பண்ணுவது real customer impact தரலாம். அதனால் start small, canary region, off-peak hours.

**Complexity.** Chaos platform setup, experiment design, steady state definition time எடுக்கும். Small team-க்கு overkill.

**False confidence.** Experiment pass ஆனாலும், அது எல்லா failure mode-ஐயும் cover பண்ணாது. Chaos engineering exhaustive அல்ல.

**Culture.** Engineers blame culture இருந்தால் யாரும் experiment run பண்ண மாட்டார்கள். Blameless postmortem முக்கியம்.

Most important failure mode: experiment itself
