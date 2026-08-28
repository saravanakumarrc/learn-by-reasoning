# Reserved vs spot instances

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.3.1 — Cloud cost / FinOps

## Problem

உங்க company-ல cloud bill ஒவ்வொரு மாதமும் ஏறிக்கொண்டே போகிறது. On-demand instance எடுத்தால் மணிக்கு rate நிலையானது, ஆனால் scale பண்ணும்போது cost எகிறுகிறது.

ஒரு workload முழுக்க 24x7 ஓடுகிறது. உதாரணமாக API tier, database replica, background worker. இதுக்கு on-demand விலை கொடுத்துக்கொண்டே இருந்தால், ஒரு வருடத்தில் லட்சக்கணக்கில் வீணாகிறது.

மறுபுறம், நைட் batch job, CI/CD runner, dev/test environment போன்றவை இடைவிட்டு ஓடுகிறது. அதற்கு எப்போதும் high price கொடுப்பது வீண்.

இங்கே தான் கேள்வி வருகிறது: **predictable baseline workload-க்கு குறைந்த விலை எப்படி பெறுவது? மற்றும் unused capacity-ஐ எப்படி cheap-ஆக பயன்படுத்துவது?**

இதற்கு cloud provider கொடுக்கும் பதில் தான் Reserved Instances மற்றும் Spot Instances.

## Mental Model

Cloud capacity-ஐ வாங்குவதை வீடு வாடகைக்கு எடுப்பதுடன் ஒப்பிடுங்கள்.

**Reserved Instance = Long term lease.** 1-3 வருட commitment கொடுத்து, மாதாந்திர வாடகையை குறைத்துக்கொள்கிறீர்கள். Provider-க்கு predictable revenue வேண்டும், உங்களுக்கு discount வேண்டும்.

**Spot Instance = Serviced apartment vacancy.** Provider-க்கு தேவையில்லாத extra capacity இருந்தால் அதை market price-ல் விற்கிறார்கள். எப்போது demand அதிகரித்தாலும் உங்களை evict செய்யலாம்.

ஒன்று cost predictability க்கு, மற்றொன்று cost minimization க்கு.

## How It Works

**Reserved Instance:**
On-demand price-ஐ விட 30-70% வரை குறைவு. மூன்று வகை payment உண்டு: No Upfront, Partial Upfront, All Upfront. Commitment term 1 அல்லது 3 வருடம், Standard அல்லது Convertible.

நீங்கள் instance family, region, tenancy specify செய்து reserve வாங்குகிறீர்கள். அதே configuration உள்ள VM ஓடினால் discount apply ஆகும். Usage குறைந்தாலும் charge வரும்.

**Spot Instance:**
Provider-ன் unused capacity-ஐ real-time auction-ல் விற்கிறார்கள். Price on-demand-ஐ விட 60-90% குறைவாக இருக்கும். நீங்கள் max bid வைக்கிறீர்கள். Spot price உயர்ந்தாலோ capacity தேவைப்பட்டாலோ instance terminate ஆகும். AWS-ல் 2 minute warning வரும்.

## Architectural Reasoning

எந்த workload எதற்கு சரி என்பது availability requirement மற்றும் interruption tolerance-ஆல் முடிவாகிறது.

Reserved Instance பயன்படுத்துங்கள்:
- Baseline capacity எப்போதும் ஓட வேண்டும். API frontend, production DB, Kafka brokers போன்றவை.
- Cost predictability முக்கியம். FinOps budget lock செய்ய வேண்டும்.
- Workload size மாறாமல் இருக்கிறது.

Spot Instance பயன்படுத்துங்கள்:
- Fault-tolerant, stateless, retry செய்யக்கூடிய jobs. Batch ETL, model training, CI runners, dev/test.
- Workload can be paused / checkpointed. Interruption-ஐ தாங்கும்.
- Scale up/down dynamic ஆக தேவை. Queue depth-க்கு ஏற்ப.

Hybrid தான் உண்மையான architecture. Baseline-ஐ Reserved-ல் lock செய்து, burst-ஐ Spot-ல் எடுப்பது common pattern.

## Trade-offs

**Cost vs Availability**
Reserved = குறைந்த cost, 100% availability guarantee. Spot = மிக குறைந்த cost, availability guarantee இல்லை.

**Commitment vs Flexibility**
Reserved-ல் 1-3 வருட lock-in உள்ளது. Workload குறைந்தாலும் நீங்கள் பணம் கொடுக்க வேண்டும். Spot-ல் எந்த commitment இல்லை.

**Operational Complexity**
Reserved simple. Spot-க்கு interruption handling வேண்டும். Auto Scaling group, checkpointing, queue-based work design, graceful shutdown தேவை. Spot Fleet / capacity optimized allocation போன்ற abstractions கற்றுக்கொள்ள வேண்டும்.

**Failure Mode**
Reserved fail ஆனால் cost waste. Spot fail ஆனால் job loss, data inconsistency வரும். Spot திடீர் terminate ஆனால் in-memory state போய்விடும். இதை design செய்யாவிட்டால் production incident ஆகும்.

## Practical Example

ஒரு e-commerce platform. Peak hours-ல் 50 API servers, off-peak-ல் 20.

Baseline 20 servers எப்போதும் வேண்டும். அதற்கு 3-year Reserved Instances வாங்கினால் மாதம் ~40% save ஆகிறது.

Peak burst-க்கு தேவையான 30 servers-ஐ Spot-ல் வைத்திருங்கள். Auto Scaling Group spot fleet-ஐ scale செய்கிறது. API server stateless ஆக இருப்பதால் terminate ஆனாலும் load balancer அடுத்த instance-க்கு route செய்கிறது.

Night batch invoice generation job 100 nodes ஓடுகிறது. அது 4 மணி நேரம் மட்டும். Spot-ல் இயக்கினால் cost 80% குறைகிறது. Job-ஐ SQS queue-ல் work units ஆக பிரித்த
