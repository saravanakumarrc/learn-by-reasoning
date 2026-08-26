# Partitioning

> **Learning Path:** Distributed Systems
> **Section:** 3.2.10 — Messaging

## Problem

உங்க system-ல ஒரு single message queue இருக்கு. Producer-கள் order events-ஐ அங்க தள்ளுது. Consumer group அதை process பண்ணுது.

Traffic 10x ஆகுது. ஒரு consumer-ஆல முடியல. இன்னும் 10 consumer-களை add பண்ணினீங்க. ஆனாலும் எல்லா messages-ம் ஒரே queue-ல தான் வருது. Queue-ல lock contention வருது, throughput மேலே போகல. Latency spike ஆகுது.

இன்னொரு பிரச்சனை: ஒரு partition-க்கு fail ஆனால் முழு queue-ம் stop ஆகுது. ஒரே topic-ல எல்லா consumers-க்கும் same event தேவைன்னா, ஒரு slow consumer மற்றவங்களை block பண்ணுது.

இதுதான் partitioning தேவைப்படற pain.

## Mental Model

Partitioning என்பது ஒரே logical topic-ஐ பல independent lane-களாக பிரிப்பது.

ஒரு highway-ல ஒரே lane இருந்தால் traffic jam. 4 lane ஆக்கினால் cars parallel-ஆ போகும். ஆனால் ஒரு car-க்குள்ளேயே order முக்கியம் என்றால், அந்த car எப்போதும் அதே lane-ல தான் போகணும்.

Message queue-ல partition = ஒரு ordered log. ஒரு partition-ல மட்டும் order guarantee இருக்கும். பல partitions-ல parallel processing செய்யலாம்.

## How It Works

ஒரு topic-க்கு N partitions உருவாக்குறோம். Producer message அனுப்பும்போது partition key கொடுக்கிறார். பொதுவாக `order_id`, `user_id` போன்ற business key.

`partition_id = hash(partition_key) % N`

அதே key எப்போதும் அதே partition-க்கு போகும். இதனால் அந்த key-க்கான events-க்கு ordering guarantee கிடைக்கும்.

Consumer group-ல உள்ள consumers partitions-ஐ distribute பண்ணிக்கிறார்கள். Consumer A partition 0,1 handle பண்ணும். Consumer B partition 2,3 handle பண்ணும். ஒரு consumer die ஆனால் அவன் partitions மற்றவர்களுக்கு rebalance ஆகும்.

Offset per partition manage பண்ணப்படும்.

## Architectural Reasoning

Partitioning தேவைப்படும் constraints:

* **Throughput scale**: Single partition-ன் max throughput limited. Partitions அதிகரித்தால் aggregate throughput scale ஆகும்.
* **Parallel processing**: Consumer group size partitions-க்கு ஏற்றார் போல grow பண்ணலாம்.
* **Isolation**: ஒரு partition slow ஆனாலும் மற்ற partition-கள் தாக்காது.
* **Replay & retention**: Partition level-ல retention policy apply பண்ணலாம்.

Alternatives என்ன?
* Single queue + faster consumer: Vertical scale. Cost அதிகம், ceiling உண்டு.
* Sharding by service: Manual routing. Operability கடினம்.

ஏன் partitioning choose பண்ணுறோம்? Because horizontal scale வேண்டும், ordering per key வேண்டும், failure domain குறைக்க வேண்டும்.

## Trade-offs

* **Ordering vs Parallelism**: Global ordering இல்லை. Ordering guarantee மட்டும் per partition. அதனால் partition key தேர்வு முக்கியம்.
* **Hot partition**: ஒரு key ரொம்ப popular ஆனால் அந்த partition bottleneck ஆகும். Partition key distribution சீராக இல்லை என்றால் throughput imbalance வரும்.
* **Rebalancing cost**: Consumer group scale பண்ணும்போது rebalance நடக்கும். In-flight messages pause ஆகும். Partition count அதிகரித்தால் rebalance overhead அதிகரிக்கும்.
* **Partition count is hard to change**: Kafka-ல partitions increase பண்ணலாம், decrease கஷ்டம். முதலிலேயே over-provision பண்ணணும்.
* **Operational complexity**: Offset management, consumer lag per partition monitor பண்ணணும்.

## Practical Example

E-commerce order events.

Topic: `orders.events`, 12 partitions.

Producer event produce பண்ணும்போது key = `order_id`.

Service A - fraud detection, Service B - inventory, Service C - notification.

அனைவரும் same topic-ஐ consume பண்ணுவார்கள், ஆனால் அவர்கள் consumer group வேறு வேறு.

`order_id = 12345` என்ற event எப்போதும் partition 7-ல தான் வரும். Fraud service அந்த partition-ன் offset-ஐ track பண்ணும். Consumer crash ஆனால் அதே partition-ல இருந்து தொடரும்.

ஒரு flash sale-ல order volume 5x ஆகுது. நீங்கள் consumer instances 3-ல இருந்து 15-க்கு scale பண்ணுறீங்க. 12 partitions இருப்பதால் 12 consumers தான் fully utilize ஆகும். அதற்கு மேல் add பண்ணினாலும் idle ஆகும்.

## Reasoning Challenge

உங்களிடம் payment events வருகிறது. Requirement: ஒரு user-க்கான payments strict order-ல process ஆகணும். ஆனால் cross-user parallelism வேண்டும். Peak load 200k msg/sec.

Partition key என்ன வைப்பீர்கள்? Partition count எப்படி decide பண்ணுவீர்கள்? Hot user வந்தால் என்ன ஆகும்? அதை எப்படி handle பண்ணுவீர்கள்?

## Key Takeaways

* Partitioning = throughput-க்கு horizontal scale, ordering-க்கு per key isolation.
* Partition key தேர்வு தான் ordering guarantee-
