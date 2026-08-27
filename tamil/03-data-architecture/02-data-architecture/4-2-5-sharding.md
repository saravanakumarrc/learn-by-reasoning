# Sharding

> **Learning Path:** Data Architecture
> **Section:** 4.2.5 — Data architecture

### 1. Problem

உங்கள் application ஒரு single database-ல run ஆகுது. Traffic நல்லா grow ஆகுது. Peak-ல 20k writes/sec, 100k reads/sec வருது.

Single node-க்கு CPU, I/O, memory எல்லாம் limit இருக்கு. Disk fill ஆகுது. Backup எடுக்க நேரம் அதிகம் ஆகுது. ஒரு node down ஆனா எல்லாம் down.

Vertical scaling பண்ணலாம். பெரிய machine வாங்கலாம். ஆனால் அதுக்கு limit உண்டு. Cost அதிகம். மேலும் availability risk ஒரே இடத்துல இருக்கு.

இப்போ constraint என்ன? **Throughput, storage, availability எல்லாம் ஒரே node-ல தேக்கப்பட்டு இருக்கு.** இதை எப்படி பரப்புவது?

இங்கே தான் sharding வருது.

### 2. Mental Model

Sharding என்பது data-வை **நிறைய சிறிய pieces ஆக பிரித்து, ஒவ்வொரு piece-ஐயும் வெவ்வேறு node-ல வைப்பது**.

ஒரு பெரிய லைப்ரரியை ஒரே ஹால்ல வைக்காம, பெயர் அகராதி வாரியாக 10 பிரிவுகள் ஆக்குவது போல. A-M ஒரு node, N-Z இன்னொரு node. ஒரு புத்தகம் தேடும்போது எந்த பிரிவுன்னு தெரிந்தால் போதும்.

Key idea: **shard key** என்று ஒரு field-ஐ தேர்வு செய்து, அதன் மூலம் data எந்த shard-க்கு போகும்னு முடிவு பண்ணுவது.

### 3. How It Works

எளிமையாக இரண்டு வழி.

**Hash sharding:** `shard_id = hash(user_id) % num_shards`. 
user_id ஒன்னு வந்தால் எப்போதும் ஒரே shard-க்கு போகும். Data uniform ஆக பரவும். ஆனால் range query கஷ்டம்.

**Range sharding:** `user_id 1-1M -> shard1, 1M-2M -> shard2`.
Range query எளிது. ஆனால் hot spot வரும். ஒரு range-ல எல்லோரும் இருந்தால் அந்த shard overload ஆகும்.

Router / shard proxy இருக்கும். Client அதுக்கு request அனுப்பும், router shard key-ஐ பார்த்து சரியான shard-க்கு forward பண்ணும். Application-க்கு இது transparent ஆக இருக்கலாம், அல்லது app-லேயே routing logic இருக்கலாம்.

Sharding + replication ஒன்னா வரும். ஒரு shard-க்கு replica இருக்கும், availability-க்காக.

### 4. Architectural Reasoning

Sharding useful ஆகும் போது:

* Single database write/read limit தாண்டி விட்டது
* Storage size node capacity-க்கு அப்பால் போகுது
* Write load independent ஆக grow ஆகுது, read load grow ஆகுது
* Team-க்கு independent scaling வேண்டும்

Alternative என்ன? 
* Vertical scaling - பெரிய machine
* Read replica - read scale ஆகும், write scale ஆகாது
* Caching - hot data மட்டும் தீர்க்கும்

Sharding-ஐ தேர்வு செய்யும் போது நீங்கள் சொல்கிறீர்கள்: **data access pattern shard key-ல localize ஆகுது. Cross-shard transactions அவசியம் குறைவு.**

### 5. Trade-offs

**Scalability vs Complexity:** Throughput, storage இரண்டும் linear ஆக scale ஆகும். ஆனால் system complexity கூடும்.

**Rebalancing pain:** Shard count அதிகரிக்கும் போது data மறுபகிர்வு செய்ய வேண்டும். Hash sharding-ல consistent hashing use பண்ணி downtime குறைக்கலாம்.

**Hotspot:** சில shard keys அதிக popular ஆக இருக்கும். `user_id=1` எல்லோருக்கும் தேவைன்னா அந்த shard மட்டும் overload ஆகும்.

**Cross-shard operations:** Join, aggregate, global sort எல்லாம் கஷ்டம். "எல்லா users-க்கும் total orders" என்பது எல்லா shard-லயும் query பண்ணி combine செய்ய வேண்டும். Latency அதிகம்.

**Failure mode:** ஒரு shard down ஆனால் அந்த shard-க்கான data மட்டும் unavailable. Operational tooling வேண்டும்: shard map management, monitoring per shard.

### 6. Practical Example

E-commerce orders table. 500M rows, 10k writes/sec.

Shard key = `user_id`. Hash sharding with 64 shards.

User 12345-ன் order எழுதும் போது router hash பண்ணி shard 27-க்கு போகும். அதே user-ன் read எல்லாம் அதே shard-ல தான். Locality நல்லா இருக்கு.

இப்போ user profile update + order create ஒன்னா atomic ஆக வேண்டும். Profile table-ம் user_id-ல shard ஆகி இருந்தால் அதே shard-ல இருக்கும், same-node transaction possible. இல்லைன்னா cross-shard transaction தேவை, அது painful.

Cost: operational team-க்கு shard rebalancing runbook வேண்டும். New shard add பண்ணும் போது data migrate ஆகும்.

### 7. Reasoning Challenge

உங்களுக்கு payments system இருக்கு. `payment_id` random, `customer_id` stable. Daily report-க்கு last 7 days-ல எல்லா customers-க்கும் total amount வேண்டும்.

Shard key-ஆக `customer_id` வச்சா write locality நல்லா இருக்கும். ஆனால் daily report எப்படி செய்வீர்கள்? ஒவ்வொரு shard-லயும் scan பண்ணி aggregate பண்ண
