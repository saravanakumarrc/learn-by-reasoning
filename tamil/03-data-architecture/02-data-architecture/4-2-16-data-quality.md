# Data quality

> **Learning Path:** Data Architecture
> **Section:** 4.2.16 — Data architecture

## 1. Problem

நீங்கள் ஒரு data pipeline-ஐ build பண்ணீங்க. Source-ல இருந்து data வந்து, transform ஆகி, data warehouse-ல load ஆகுது. Dashboard-ல numbers காட்டுது.

பிரச்சனை: Business team கேட்குது, "இந்த revenue number சரியா?" Data team சொல்லுது, "Source-ல இருந்து வந்தது." Engineering சொல்லுது, "Pipeline run ஆகியிருக்கு." Analyst சொல்லுது, "எனக்கு null வருது."

எல்லாரும் சரி, ஆனா trust இல்ல. ஒரு order-க்கு `customer_id` missing, `amount` negative, `created_at` future date, duplicate rows. Model train பண்ணும் போது silent error வருது. Report அனுப்பிய பிறகு தான் தெரியுது data தப்பு.

Data quality இல்லாமல், data volume இருந்தும் value இல்ல.

## 2. Mental Model

Data quality என்பது clean data அல்ல. **Trust-க்கான ஒரு contract**.

ஒரு engineer-க்கு API contract இருக்கு: input என்ன, output என்ன. Data-க்கும் அதே contract வேண்டும்.

Mental model: Data என்பது product. அதற்கு spec இருக்கு. Spec-ல வரையறுக்கப்பட்ட dimensions:
* **Validity** - schema-க்கு ஒத்துவருதா? `email` format சரியா?
* **Accuracy** - real world-க்கு match ஆகுதா?
* **Completeness** - mandatory field missing இல்லையா?
* **Consistency** - அதே entity இரண்டு system-ல ஒரே மாதிரி இருக்கா?
* **Uniqueness** - duplicate இல்லையா?
* **Timeliness** - data எப்போது available ஆகணும், எப்போது வந்தது?

இது தனித்த concept அல்ல, system boundary-யில் enforce செய்யும் ஒன்று.

## 3. How It Works

Data quality-ஐ நீங்கள் ஒரே இடத்தில் enforce பண்ண முடியாது. Layered approach தேவை.

```
Source System -> Validation -> Ingestion -> Transform -> Quality Checks -> Consumption
```

* **Schema enforcement**: ingestion-ல JSON schema / Avro schema. வந்த record invalid என்றால் reject or quarantine.
* **Data contracts**: producer-consumer இடையே explicit contract. Field name, type, nullability, PII classification.
* **Checks in pipeline**: Great Expectations, dbt tests போன்றவை. Row count, null rate, freshness, referential integrity.
* **Observability**: data quality metrics-ஐ monitor பண்ணி alert போடு. `orders table freshness > 2 hours` என்றால் page.

Quality check fail ஆனால் என்ன செய்வது? Fail fast vs fail open என்பது decision.

## 4. Architectural Reasoning

**Problem painful ஆகும் போது?** Data downstream-ல பயன்படும் போது. ML model, financial report, customer-facing feature.

Options:
* **Trust source**: Source team fix பண்ணுவார்கள் என்று நம்பு. Cheapest initial, expensive later.
* **Validate at ingestion**: Strict schema, reject bad rows. Data loss risk.
* **Validate in warehouse**: dbt tests, anomaly detection. Late detection, costlier fix.
* **Validate at consumption**: Analyst filter பண்ணுவார். Chaos.

Architect decision பொதுவாக:
* Critical business data -> enforce at ingestion + contract + warehouse checks.
* Exploratory data -> lightweight checks, quarantine.

Data quality என்பது central team-க்கு மட்டும் அல்ல. Producer team ownership தான் scalable.

## 5. Trade-offs

**Strictness vs Flexibility**
Strict validation = fewer bad rows, ஆனால் source schema evolve ஆகும் போது pipeline break ஆகும். Loose validation = pipeline up, ஆனால் garbage accumulates.

**Latency vs Quality**
Real-time ingestion-ல deep validation செய்ய முடியாது. அப்போது async validation + dead letter queue பயன்படுத்து.

**Cost vs Coverage**
100% checks cost high. Most architects Pareto principle apply பண்ணுவார்கள்: 20% critical fields-க்கு 80% checks.

**Fail fast vs Silent degradation**
Reject bad row = producer alert ஆகும், fix வரும். Quarantine = downstream safe, ஆனால் debt accumulate ஆகும்.

Failure mode: ஒரு upstream field rename ஆனது, schema evolve ஆகாமல் pipeline run ஆகி null-கள் fill ஆகும். இது silent data corruption.

## 6. Practical Example

E-commerce order pipeline.

Source: order-service -> Kafka -> data warehouse.

Architectural choice:
* Producer order-service publishes `order_created` event with data contract: `order_id string not null, customer_id string not null, amount decimal >0, currency enum`.
* Kafka consumer validates schema using schema registry. Invalid event -> dead letter topic.
* dbt-ல tests: `order_id unique`, `amount > 0`, `customer_id` exists in dim_customer, `freshness < 1 hour`.
* Quality dashboard shows `null rate`, `row count delta`, `duplicate rate`. Slack alert if threshold breach.

Result: Analyst-க்கு data trust உள்ளது. Business கேட்டால் "இந்த number definition இதுதான்" என்று சொல்ல முடியும்.

## 7. Reasoning Challenge

உங்களிடம் 3rd party vendor-ல இருந்து daily customer file வருகிறது. File format அடிக்கடி மாறுகிறது, ஆனால் sales team அந்த data-ஐ next day report-க்கு கட்டாயம் தேவை. Schema strict validation பண்ணினால் pipeline break ஆகும், loose validation பண்ணினால் bad data warehouse-க்கு போகும்.

இங்கே நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Validation-ஐ எங்கே வைப்பீர்கள்? Bad rows-ஐ எப்படி handle பண்ணுவீர்கள்? ஏன்?

## 8. Key Takeaways

* Data quality என்பது feature அல்ல, system property. Trust-ஐ build பண்ண வேண்டும்.
* Enforce at boundary: schema + contract at ingestion, checks in pipeline, monitor at consumption.
* Strictness-க்கும் flexibility-க்கும் trade-off உண்டு. Critical data-க்கு strict, exploratory-க்கு loose.
* Quality without ownership fail ஆகும். Producer team தான் source quality-க்கு owner.
