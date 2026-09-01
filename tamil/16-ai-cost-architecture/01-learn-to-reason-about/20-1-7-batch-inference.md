# Batch inference

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.7 — Learn to reason about

## 20.1.7 — Batch inference: Learn to reason about

### 1. Problem

ஒரு LLM service-ஐ real-time ஆக run பண்ணும்போது ஒவ்வொரு request-க்கும் ஒரு inference ஆகுது. User chat பண்ணினா லேட்டன்சி matter ஆகும். ஆனால் பல use cases-ல user உடனே பதில் எதிர்பார்க்க மாட்டான்.

உதாரணமா:
* ஒரு நாள் முழுக்க வந்த 1 million customer support tickets-க்கு sentiment tag போடணும்
* Daily sales orders-க்கு summary generate பண்ணணும்
* User uploads ஆன 10,000 images-க்கு caption generate பண்ணணும்

இதுல ஒவ்வொரு request-ஐயும் ஒன்னொன்னா real-time inference பண்ணினா என்ன ஆகும்?
* GPU idle இருக்கும், peak-ல overload ஆகும்
* 1 request = 1 token generation start ஆகும், overhead அதிகம்
* Cost அதிகம் ஆகும், throughput குறைவு

**Pain point:** ஏராளமான similar requests வரும்போது, ஒவ்வொன்றையும் individually process பண்ணுவது inefficient மற்றும் கார்ப்பரேட் budget-ஐ வீணாக்கும்.

### 2. Mental Model

Batch inference என்பது ஒரு குவியல் requests-ஐ ஒரே inference run-ல் சேர்த்து process பண்ணுவது.

Real-time = ஒரு customer கேள்வி கேட்டான், உடனே பதில் வேண்டும்.
Batch = இந்த வாரம் வந்த எல்லா emails-க்கும் ஒரே நேரத்தில் summary போடலாம்.

உனக்கு ஒரு kitchen உண்டு. ஒரே நேரத்தில் ஒரு customer-க்கு மட்டும் சமைக்கலாம். அல்லது 100 plates-ஐ ஒரே oven-ல் batch-ஆக bake பண்ணலாம். Oven use பண்ற cost per plate குறையும்.

### 3. How It Works

பொதுவாக batch inference இப்படி நடக்கும்:

1. **Collector:** Requests அல்லது data items ஒரு queue / storage-ல் collect ஆகும். S3, Kafka, database table.
2. **Batching window:** Fixed time window-ல் அல்லது min batch size reach ஆனதும் ஒரு job trigger ஆகும்.
3. **Packing:** Multiple prompts/inputs ஒரு single tensor batch ஆக pack ஆகும். GPU-க்கு ஒரே முறை feed ஆகும்.
4. **Inference run:** Model ஒரே முறை run ஆகி, ஒரே batch-ல் output-கள் generate ஆகும்.
5. **Store results:** Outputs ஒரு DB / object storage-ல் சேமிக்கப்படும். Downstream jobs அல்லது user-க்கு notify ஆகும்.

Key difference: Real-time inference-ல் prompt arrival time = start time. Batch-ல் prompt arrival time ≠ start time. Latency அனுமதிக்கப்படும்.

### 4. Architectural Reasoning

Batch inference useful ஆகும் போது:

* **Latency SLA இல்லை:** Result needed within minutes/hours/days, not milliseconds.
* **Throughput முக்கியம்:** Cost per 1M requests குறைக்க வேண்டும்.
* **Workload predictable / bursty:** Night batch, daily ETL போல.
* **Same model, many inputs:** Throughput via packing.

Alternatives:
* **Real-time inference with autoscaling:** Low latency தேவை. Cost அதிகம்.
* **Streaming / continuous inference:** Near-real-time வேண்டும், latency குறைவு.
* **On-demand batch:** User trigger பண்ணும் போது batch ஆக run.

Architect ஏன் batch தேர்வு செய்வார்? GPU utilization maximize பண்ண, cost per token குறைக்க. Cloud providers-ல் batch endpoint-கள் 50-70% cheaper ஆக இருக்கும்.

### 5. Trade-offs

**Latency vs Cost:** Batch-ல் latency அதிகம். User wait பண்ண தயாரா இருக்கணும். Real-time-க்கு இது பொருந்தாது.

**Freshness vs Efficiency:** Data stale ஆகும் risk. நீ 24h batch பண்ணினா, decision 24h late ஆகும்.

**Complexity:** Orchestration தேவை. Job scheduling, retry, partial failure, result tracking, monitoring. Real-time API-க்கு ஒப்பிடும்போது ops overhead அதிகம்.

**Failure mode:** ஒரு batch job fail ஆனால், அதில் உள்ள அனைத்து requests-ம் fail ஆகும். Idempotency மற்றும் retry logic முக்கியம்.

**Model quality:** Long batch-ல் context length, prompt variation பெரியதாக இருக்கும். Padding overhead வரலாம். Dynamic batching vs static batching trade-off.

### 6. Practical Example

Enterprise RAG pipeline.

உனக்கு 500,000 product descriptions உள்ளன. அவற்றிற்கு embeddings generate பண்ண வேண்டும்.

Option A: Real-time API. ஒவ்வொரு description வரும் போதும் embedding request. Cost high, GPU underutilized.

Option B: Batch inference.

* Descriptions S3 bucket-ல் accumulate ஆகும்.
* Night 2 AM-ல் batch job trigger ஆகும். Lambda/Step Functions -> SageMaker Batch Transform / Bedrock Batch Inference.
* 1,000 descriptions ஒரு batch-ல் pack பண்ணி, GPU-வில் parallel ஆக embed பண்ணு.
* Results vector database-ல் upsert பண்ணு.

Result: Cost per embedding 60% குறைவு. Latency 8 hours ஆகும், ஆனால் product search-க்கு அது பரவாயில்லை.

### 7. Reasoning Challenge

உன்னிடம் ஒரு fraud detection system உள்ளது. Real-time transaction scoring 50ms SLA உள்ளது. அதே மாடலை வைத்து, ஒவ்வொரு நாள் முடிவிலும் முழு நாள் transactions-க்கு deeper explainability report generate பண்ண வேண்டும். இங்கே batch inference-ஐ எப்படி வடிவமைப்பீர்கள்? Real-time path-ஐ பாதிக்காமல் batch path-ஐ எப்படி isolate செய்வீர்கள்? Cost, failure, data freshness எப்படி manage பண்ணுவீர்கள்?

### 8. Key Takeaways

* Batch inference = latency அனுமதிக்கும் workloads-க்கு cost per token குறைக்கும் technique.
* Problem painful ஆனது: too many independent requests, GPU underutilization, real-time cost.
* Decision driven by SLA: If latency not critical, batch.
* Every architectural solution creates trade-off: lower cost for higher latency and operational complexity.
* Batch jobs need robust orchestration, retry, monitoring, and idempotency.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியும்.
