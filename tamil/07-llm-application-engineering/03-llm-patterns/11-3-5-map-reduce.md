# Map/reduce

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.5 — LLM patterns

## 1. Problem

உங்களிடம் ஒரு LLM application engineering path-ல் பெரிய dataset இருக்கு. உதாரணமாக 1M documents-ஐ embedding பண்ணணும், அல்லது 10M user queries-ல் sentiment extract பண்ணணும், அல்லது logs-ல் error patterns find பண்ணணும்.

ஒரே machine-ல் serial-ஆ process பண்ணா என்ன ஆகும்?
Latency பெரிசாகும். Throughput குறையும். ஒரு node fail ஆனால் முழு job restart.
Memory, CPU limits வரும்.

**What goes wrong if we don't have this?** Processing time hours/days ஆகும், cost அதிகரிக்கும், failure-ல் resilience இல்லை.

Map/reduce வந்ததே இந்த pain-க்காக தான்.

## 2. Mental Model

Map/reduce என்பது **divide and conquer**-ஐ distributed system-க்கு கொண்டு வந்த pattern.

நினைத்து பாருங்கள்: ஒரு பெரிய pile of work இருக்கு. அதை சிறு சிறு chunks ஆக பிரித்து parallel workers-க்கு கொடுக்கிறோம். Workers எல்லாரும் independently map செய்கிறார்கள். பிறகு intermediate results-ஐ சேர்த்து reduce பண்ணி ஒரு final answer-ஐ உருவாக்குகிறோம்.

Analogy: 1000 invoices-ல் total amount கண்டுபிடிக்கணும். 10 people-க்கு 100 invoices வீதம் கொடு. ஒவ்வொருவரும் தங்கள் batch-ன் sum-ஐ கணக்கிடு. பிறகு 10 sums-ஐ கூட்டு. Same logic, distributed.

## 3. How It Works

Map/reduce-ல் இரண்டு core functions மட்டும்:

**Map phase:** Input key-value pairs-ஐ எடுத்து intermediate key-value pairs-ஐ produce செய்யும். 
`map(key, value) -> list of ( intermediate_key, intermediate_value )`

உதாரணம்: document id, text -> word, 1

**Reduce phase:** Same intermediate key-க்கு வந்த அனைத்து values-ஐ கூட்டி combine செய்யும்.
`reduce(intermediate_key, list of values) -> result`

உதாரணம்: word, [1,1,1] -> word, 3

Shuffle என்பது map output-ஐ key-ன் படி group பண்ணி சம்பந்தப்பட்ட reducer-க்கு அனுப்பும் step.

இது declarative. நீங்கள் what to compute சொல்லுங்கள், எப்படி parallelize பண்ணுவது framework பார்த்துக்கும்.

## 4. Architectural Reasoning

எப்போது useful?

* Dataset size > single machine memory/CPU
* Work embarrassingly parallel ஆக இருக்கு
* Intermediate aggregation தேவை
* Fault tolerance தேவை

LLM Application Engineering-ல் map/reduce பயன்படும் இடங்கள்:

* **Embedding generation:** Millions of documents-ஐ chunks ஆக split செய்து multiple workers-ல் embed பண்ணி, vector database-ல் batch insert செய்யும். Map = chunk + embed, Reduce = deduplicate / merge metadata
* **RAG evaluation:** Thousands of queries-க்கு retrieval quality, relevance score calculate பண்ணி aggregate metrics-ஐ produce பண்ணும்
* **Log analysis / anomaly detection:** Huge log files-ல் error counts, latency percentiles கணக்கிட
* **Training data filtering:** Large corpus-ல் toxic content filter, language classify செய்து filter செய்ய

Alternatives: 
Simple parallel threads / multiprocessing - single machine limit.
Streaming frameworks like Spark Structured Streaming / Flink - low latency.
But batch, fault tolerant, large scale-க்கு MapReduce மாதிரி pattern மிகவும் clean.

## 5. Trade-offs

**Scalability vs Latency:** Map/reduce batch-oriented. Real-time இல்லை. Minutes/hours வரை ஆகும். Low latency தேவைப்பட்டால் fit ஆகாது.

**Fault tolerance vs Complexity:** Worker fail ஆனால் task retry ஆகும். Data locality பார்த்து schedule செய்ய வேண்டும். Operational complexity அதிகம்.

**Cost vs Throughput:** Idle resources வரை பயன்படுத்தி throughput அதிகரிக்கும். ஆனால் small jobs-க்கு overhead அதிகம். Startup cost, shuffle cost.

**Data movement:** Shuffle phase-ல் network traffic huge ஆகும். Key distribution skewed ஆனால் straggler reducer உருவாகும். Hot key problem.

## 6. Practical Example

நீங்கள் ஒரு LLM chatbot-க்கு knowledge base build பண்ணுகிறீர்கள். 2M support articles உள்ளன.

Architecture:

```
Documents -> Map workers -> chunking + embedding via LLM
              -> intermediate: doc_id, embedding vector
              -> Reduce / Shuffle -> merge, deduplicate, write to vector database
```

Map workers independent ஆக run ஆகும். ஒரு worker crash ஆனால் அந்த shard மட்டும் retry. Reduce-ல் you can also filter low quality embeddings.

இதனால் 2M documents-ஐ 8 nodes-ல் parallel process பண்ணி 4 hours-ல் முடிக்க முடியும். Single node-ல் 2 days ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 50M customer chat transcripts இருக்கு. ஒவ்வொரு transcript-லும் top 3 intents extract பண்ணி monthly intent distribution report தயாரிக்கணும்.

Producer speed வேறுபடும், some transcripts 10 pages, some 1 page. Replay தேவை இல்லை, ஆனால் job fail ஆனால் restart ஆக வேண்டும். Latency requirement: overnight batch ok.

இங்கே map/reduce pattern-ஐ எப்படி design செய்வீர்கள்? Map output key என்ன இருக்கும்? Skew எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

* Map/reduce என்பது large scale batch processing-க்கான divide-conquer pattern, distributed parallelism + fault tolerance கொடுக்கும்
* Map = transform, Reduce = aggregate. Shuffle என்பது key-ன் படி grouping
* LLM apps-ல் embedding generation, evaluation, data cleaning போன்ற batch workloads-க்கு இது natural fit
* Trade-off: high throughput & fault tolerance கிடைக்கும், ஆனால் latency அதிகம், shuffle cost உள்ளது
* Every architectural solution creates a new trade-off. Map/reduce கொடுக்கும் scale-க்கு ஈடாக operational complexity வரும்
