# Time-series databases

> **Learning Path:** Data Architecture
> **Section:** 4.1.14 — Databases

## 1. Problem

உங்க platform-ல 50 microservices இருக்கு. ஒவ்வொன்னும் latency, error rate, request count-ஐ 10 seconds க்கு ஒரு முறை அனுப்புது. ஒரு நாளைக்கு சுமார் 4 மில்லியன் data points. 

இதை Postgres-ல timestamp கொண்டு சேமித்தீர்கள் என்றால் என்ன நடக்கும்?

Write-கள் அதிகரிக்கும் போது index bloat ஆகும். `WHERE timestamp BETWEEN ... AND ...` query 30 நாள் range-க்கு 10 விநாடிகள் எடுக்கும். `GROUP BY` பண்ணி hourly average எடுக்க வேண்டும் என்றால் full scan தேவை. 

இன்னும் மோசம்: 90 நாளுக்கு மேல் data வேண்டாம் என்று முடிவு செய்தால், `DELETE` பண்ணுவது table-ஐ lock பண்ணும். Storage cost தினமும் பெருகும்.

இது ஒரு வருடத்திற்கு பிறகு operational nightmare ஆகிறது. Relational DB append-only time data-க்கு ஒன்றும் உகந்ததல்ல.

## 2. Mental Model

Time-series database என்பது **time ஐ first-class citizen ஆக நடத்தும் DB**.

நினைவில் வைத்துக்கொள்ள வேண்டியது:

* Data append-only, அதாவது பழைய data மாறாது.
* 90% writes, 10% reads. Reads பெரும்பாலும் time range + aggregation.
* Key என்பது `(metric_name, tags, timestamp)` போன்றது.

அதனால் storage மற்றும் query இரண்டும் time-க்கு எதிராக optimize செய்யப்படுகின்றன.

## 3. How It Works

Time-series DB-கள் relational model-ஐ கைவிட்டு இதை செய்கின்றன:

* **Time partitioning / Sharding by time.** Data தானாக month / day / hour க்கு பிரிக்கப்படும். Query வரும்போது தேவையான partition மட்டும் திறக்கப்படும்.
* **Write-optimized storage.** Rows-ஐ sort பண்ணி sequential write செய்யப்படும். LSM-tree அடிப்படையிலான engines இதை விரும்புகின்றன.
* **Compression.** தொடர்ச்சியான timestamp-ல் delta encoding, value-கள் மீண்டும் மீண்டும் வரும் போது dictionary compression பயன்படுத்தப்படும். InfluxDB போன்றவை 10x-90x compression பார்க்கின்றன.
* **Downsampling.** Raw data 10 sec granularity-ல் 30 நாள் வரை வைத்து, அதற்கு மேல் hourly அல்லது daily aggregate-ஆக மாற்றப்படும். இது retention policy-ன் ஒரு பகுதி.
* **Retention policy.** Time-க்கு ஏற்ப தானாக data expire ஆகும். TTL மூலம் partition delete போல நடக்கும், row-by-row delete இல்லை.

இதனால் `SELECT avg(latency) FROM metrics WHERE service='payment' AND time > now()-1h` என்பது milliseconds-ல் வருகிறது.

## 4. Architectural Reasoning

Time-series DB தேவைப்படும் போது:

* High ingestion rate, append-only writes. உதாரணம்: IoT sensors, metrics, logs, financial ticks.
* Query pattern predictable: time range filter + aggregation + tag filter.
* Data lifecycle குறுகியது. Hot data recent, cold data downsample/ archive.

Alternatives என்ன?

* **Relational DB:** Small scale, ad-hoc analytics தேவைப்பட்டால். Write throughput மற்றும் storage cost விரைவில் பிரச்சனை.
* **Wide-column / NoSQL like Cassandra:** Time partitioning செய்தால் work செய்யும். ஆனால் built-in downsampling, retention, continuous queries இல்லை.
* **Object storage + query engine:** S3 + Athena / DuckDB. Long term cold storage-க்கு நல்லது. Real-time dashboard-க்கு latency அதிகம்.
* **Data warehouse:** Historical analysis-க்கு சரி. Real-time ingestion க்கு அல்ல.

ஆர்கிடெக்ட் ஒரு தேர்வு செய்யும்போது கேட்க வேண்டியது: "நாம் எவ்வளவு வேகமாக write செய்ய வேண்டும், எவ்வளவு காலம் raw data தேவை, query எப்படி இருக்கும்?"

## 5. Trade-offs

* **Write speed vs Query flexibility.** Time-series DB time range queries-ல் சிறந்தது. Ad-hoc JOIN, complex transactions தேவைப்பட்டால் மோசம்.
* **Retention மற்றும் cost.** Downsampling இல்லாமல் storage cost கட்டுப்படுத்த முடியாது. ஆனால் downsampling செய்தால் raw fidelity இழக்கிறோம்.
* **Operational complexity.** Dedicated cluster, compaction, retention policy tune செய்ய
