# Compute

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.1.1 — Cloud fundamentals

### 1. Problem

உங்க company-க்கு ஒரு web app வேணும். On-prem-ல செய்யும்போது என்ன ஆகும்?

Server வாங்கணும், rack space, power, cooling, OS patch, hardware failure handle பண்ணணும். Traffic 10x ஆகும்னு தெரியல. Peak-க்கு capacity plan பண்ணி server வாங்கினா, 80% நேரம் அது idle-ல இருக்கும். Traffic sudden spike வந்தா புது server order பண்ணி வர 6-8 வாரம் ஆகும். Downtime வரும்.

இந்த pain-தான் cloud compute வந்ததுக்கு காரணம். **Hardware-ஐ own பண்ணாமல், compute-ஐ rent பண்ண** முடிந்தால் என்ன ஆகும்?

### 2. Mental Model

Cloud-ல compute என்பது CPU cycles + memory + network I/O கொண்ட ஒரு abstract resource. நீங்கள் server-ஐ own பண்ணவில்லை, time-க்கு தகுந்த மாதிரி **capacity-ஐ scale பண்ணி pay-per-use** பண்ணுகிறீர்கள்.

On-prem = capacity-ஐ முன்கூட்டியே buy பண்ணு, waste ஆகும்.
Cloud compute = capacity-ஐ on demand-ல எடு, use பண்ணினதுக்கு மட்டும் pay பண்ணு.

### 3. How It Works

Cloud provider உங்களுக்கு 3 levels-ல compute கொடுக்கிறார்:

**VM / Instance - IaaS:** Physical server-ஐ virtualize பண்ணி, ஒரு VM தருகிறார். OS, runtime, app எல்லாம் நீங்கள் manage பண்ணுவீர்கள். EC2, Compute Engine மாதிரி. Full control இருக்கும்.

**Container - managed compute:** VM-க்குள்ளே container orchestration. Kubernetes, ECS. நீங்கள் app-ஐ container image-ஆக package பண்ணுவீர்கள். Scheduling, scaling, self-healing provider கவனிப்பார்.

**Serverless / FaaS:** நீங்கள் function மட்டும் upload பண்ணுவீர்கள். AWS Lambda, Cloud Functions. Provider compute, scaling, patching எல்லாம் manage பண்ணுவார். நீங்கள் request-க்கு பேச்சு.

அடிப்படையில் compute எப்போதும் physical CPU/memory-தான், ஆனால் abstraction layer உயரும்போது operational burden குறையும்.

### 4. Architectural Reasoning

Compute model தேர்வு என்பது **control vs operability** trade-off.

* **Latency sensitive, custom kernel, GPU workloads** இருந்தால் VM / bare metal தேவை. Example: low-latency trading, ML training.
* **Microservices, 12-factor app** போன்ற standard workloads-க்கு container ஏற்றது. Team-க்கு deployment consistency வேண்டும், scaling logic தேவை.
* **Spiky, event-driven, short execution** workloads-க்கு serverless சிறந்தது. Traffic இல்லாத நேரம் cost zero. Cold start accept பண்ண முடியும்.

ஒரு architect கேட்க வேண்டியது: 
எவ்வளவு control வேண்டும்? Team size எவ்வளவு? Operational expertise உள்ளதா? Traffic pattern என்ன?

### 5. Trade-offs

**Cost predictability vs elasticity:** VM-ல reserved instance எடுத்தால் cost குறையும் ஆனால் flexibility குறையும். Serverless எல்லா நேரமும் elastic ஆனால் per-request cost அதிகம்.

**Control vs maintenance:** VM-ல நீங்கள் OS patch, security hardening எல்லாம் பார்க்கணும். Serverless-ல அது provider-ன் problem. ஆனால் debugging கடினம்.

**Cold start & vendor lock-in:** Serverless-ல function runtime, limits provider define பண்ணுவார். Portability குறையும். Container / VM-ல code எடுத்து வேறு cloud-க்கு move பண்ண எளிது.

**Failure modes:** VM crash ஆனால் instance replace ஆகும். Serverless-ல provider-ன் multi-AZ scaling உங்களுக்கு invisible. ஆனால் throttling, concurrency limits திடீரென problem ஆகும்.

### 6. Practical Example

ஒரு e-commerce app-க்கு Diwali sale-ல 10x traffic வரும். Normal days-ல 10 VM போதும், sale-ல 100 VM தேவை.

On-prem-ல 100 VM வாங்கி வைத்தால் வருடம் முழுக்க cost waste. Cloud-ல auto scaling group வச்சு, CPU >70
