# Right-sizing

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.3.2 — Cloud cost / FinOps

## 1. Problem

உங்கள் service cloud-ல ஓடுது. ஆரம்பத்துல traffic கொஞ்சம். ஆனால் Black Friday, release, viral event போன்றவற்றுக்கு தயாராக 3x, 4x capacity வைத்து provision பண்ணியிருக்கீங்க.

Result என்ன? 80% நேரம் CPU 15-20%, memory 30% தான் use ஆகுது. Bill வரும்போது shock ஆகுது. இது over-provisioning.

மறுபுறம், சில team-கள் சிக்கனம் பார்க்க small instance எடுத்து விட்டுவிடுவார்கள். Traffic spike வந்ததும் latency spike, timeout, 5xx. Pager அடிக்கும். இது under-provisioning.

Right-sizing-ன் core problem இதுதான்: **நாம் capacity-ஐ actual workload-க்கு எப்படி match பண்ணுவது, over-pay பண்ணாமல், reliability-யும் கெடுக்காமல்?**

## 2. Mental Model

Right-sizing என்பது "சின்ன instance-க்கு மாறு" என்பது அல்ல. அது ஒரு continuous feedback loop.

> Actual utilization → requirement → instance type / count → cost & reliability → re-measure

நீங்கள் ஒரு car-க்கு fuel போடுவது போல. Tank-ஐ முழுசா நிரப்புவது waste. ஆனால் half empty-ல long trip போக முடியாது. Traffic pattern-க்கு ஏற்ப tank size மாற்றுவது தான் right-sizing.

## 3. How It Works

இதற்கு மூன்று pillars தேவை.

**Metrics:** CPU, memory, network, disk I/O, request latency, queue length, saturation. CloudWatch, Prometheus, etc. இதை 2-4 வாரம் collect பண்ணுங்கள். Peak மட்டும் பார்க்காதீர்கள். P95/P99 utilization பாருங்கள்.

**Workload pattern:** Steady state vs bursty. Day-night, weekday-weekend. Batch job இருக்கா? Traffic predictable-ஆ?

**Capacity headroom:** Production-ல 70-80% sustained utilization-க்கு மேல் போகாதே என்று rule வைக்கலாம். அதற்கு மேல் போனால் latency degrade ஆகும், autoscaling react பண்ண நேரம் வேண்டும்.

இதை வைத்து instance type மாற்றுவது, vCPU/memory ratio சரி செய்வது, node count மாற்றுவது நடக்கும்.

## 4. Architectural Reasoning

Right-sizing useful ஆகும் போது:

* Steady state load இருக்கும், ஆனால் provisioned capacity peak-க்கு ஏற்றது.
* Cost FinOps-ன் முக்கிய metric ஆக இருக்கும்.
* Service-ல SLA இருக்கும், அதனால் blind cut பண்ண முடியாது.

Alternatives:

* **Over-provision + autoscaling:** Simple, safe. ஆனால் baseline cost high.
* **Under-provision + aggressive autoscaling:** Cost குறைவு. ஆனால் cold start latency, scale-up delay, risk.
* **Right-size + autoscaling:** Baseline-ஐ lean-ஆக வைத்து, spike-க்கு autoscaling handle பண்ணும். இது balanced.

Architect-ஆக நீங்கள் கேட்க வேண்டியது: இந்த service-ன் latency SLO என்ன? Scale-up எவ்வளவு நேரம் எடுக்கும்? அந்த நேரத்தில் traffic எவ்வளவு tolerate பண்ண முடியும்?

## 5. Trade-offs

**Cost vs Headroom:** அதிக headroom வைத்தால் cost அதிகம், reliability அதிகம். குறைத்தால் cost குறையும், risk அதிகம்.

**Utilization vs Performance:** CPU 80%+ ஆனால் context switch, queueing latency அதிகரிக்கும். Memory pressure இருந்தால் GC pause அதிகரிக்கும்.

**Operational overhead:** Right-sizing continuous work. Metrics பார்க்க, analyze பண்ண, change பண்ண. Small team-க்கு இது overhead. ஆனால் ignore பண்ணினால் waste continue ஆகும்.

**Instance type lock-in:** Right-sized instance ஒரு workload-க்கு perfect. ஆனால் workload மாறினால் மீண்டும் tune பண்ண வேண்டும்.

Failure mode: Seasonal pattern miss பண்ணினால். உதாரணமாக monthly billing run. அந்த நாள் CPU spike ஆகும். அதை daily average-ல மறைத்து விட்டு downsize பண்ணினால் outage வரும்.

## 6. Practical Example

ஒரு payment API service. r5.xlarge 10 nodes-ல ஓடுது. 3 மாத metrics பார்த்தால்:

* Average CPU 22%, P95 45%
* Memory 40% steady
* Peak 2 மணி நேரம் மட்டும் Black Friday-ல 70%

Analysis சொல்கிறது: CPU bound அல்ல, memory bound அல்ல. vCPU/memory ratio mismatch இல்லை. Baseline 6 nodes போதும். Peak-க்கு autoscaling 4 nodes add.

Decision: Baseline-ஐ 10 → 6 ஆக குறைத்து, autoscaling policy-ஐ 60% CPU > 3 min என்று set பண்ணு.

Result: Monthly cost ~40% குறைந்தது. P99 latency same. Scale-up tested in staging.

இங்கே right-sizing autoscaling-ஐ replace பண்ணவில்லை. Baseline waste-ஐ குறைத்தது.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இருக்கும் message queue வாசிக்கும். அவர்கள் எல்லாரும் same event-ஐ process பண்ண வேண்டும், ஆனால் processing time வேறுபடும். நீங்கள் each consumer-க்கு dedicated large instance கொடுத்திருக்கீங்க. Average CPU 10% தான். Scale-up time 5 min. Queue backlog tolerate பண்ண முடியுமா?

இங்கே right-sizing மட்டும் போதுமா? இல்லை வேறு architectural change
