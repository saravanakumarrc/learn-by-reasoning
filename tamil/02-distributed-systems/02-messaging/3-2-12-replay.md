# Replay

> **Learning Path:** Distributed Systems
> **Section:** 3.2.12 — Messaging

## Problem

ஒரு e-commerce system-ல OrderPlaced event வெளியிடுகிறது. Inventory service, Payment service, Notification service மூன்றும் அதை consume பண்ணுது.

Payment service-ல bug வந்து, OrderPlaced event-களை process பண்ணாமல் error ஆக்கிடுது. Team bug fix பண்ணி deploy பண்ணியதும், அந்த இடைவெளியில் வந்த events எல்லாம் போய்விட்டதா? 

இல்லை, இன்னும் மோசம். புதுசா Fraud Detection service ஒன்றை கிளம்பினீர்கள். கடந்த 30 நாள் order pattern தேவைப்படுகிறது. அந்த events எங்கே?

இதுதான் replay தேவைப்படும் இடம். Message ஒரு முறை மட்டும் பார்க்க முடியும் என்றால், failure, late joiner, bug fix, reprocessing எல்லாம் கஷ்டம்.

## Mental Model

Message-ஐ ஒரு அழிக்க முடியாத ஒலிப்பதிவு போல நினைத்துக்கொள்ளுங்கள்.

Producer event-ஐ log-ல append பண்ணுகிறது. Consumer அந்த log-ஐ படிக்கிறது, தன்னுடைய position-ஐ offset ஆக மார்க் பண்ணுகிறது.

தேவைப்பட்டால் எந்த consumer-மும் திரும்பி போய் ஆரம்பத்திலிருந்தோ, குறிப்பிட்ட offset-லிருந்தோ மீண்டும் படிக்க முடியும். இது tape recorder-ஐ rewind பண்ணுவது போல.

## How It Works

முக்கியமான விஷயங்கள் மூன்று:

**Durable log**: Broker message-களை disk-ல append-only log ஆக வைத்திருக்கிறது. Memory queue அல்ல.

**Offset tracking**: ஒவ்வொரு consumer group-க்கும் எந்த offset வரை consume செய்தோம் என்று குறித்து வைக்கிறது. Broker இதை store செய்கிறது.

**Independent consumption**: Consumer A நின்றாலும் Consumer B தனி offset-ல் தொடர முடியும். Producer-க்கு block ஆகாது.

ஒரு consumer crash ஆனால், அது திரும்பி வந்து last committed offset-க்கு அடுத்ததிலிருந்து தொடரும். Bug fix செய்து பழைய offset-க்கு திரும்பி வைத்தால் replay ஆகும்.

## Architectural Reasoning

Replay பயனுள்ளது:

* **Late joiner**: புதிய service-க்கு historical events தேவை. DB snapshot + event replay பண்ணி current state-ஐ build பண்ணலாம்.
* **Bug fix & reprocessing**: Consumer logic தவறாக இருந்தது. Log-ஐ மீண்டும் run பண்ணி சரியான state-ஐ recreate பண்ணலாம்.
* **Disaster recovery**: Consumer data corrupt ஆனால், log-லிருந்து rebuild பண்ணலாம்.

எப்போது use பண்ணக்கூடாது? Low latency, low volume, one-time notification போன்றவற்றில் replay வேண்டாம். அங்கே at-most-once queue போதும்.

Kafka, Pulsar போன்ற log-based systems replay-க்கு பொருத்தமானவை. RabbitMQ classic queue-ல் replay இயல்பாக இல்லை.

## Trade-offs

* **Storage cost vs replay window**: Log-ஐ எவ்வளவு நாள் வைத்திருக்கிறோம்? Retention 7 நாள் என்றால் 7 நாளுக்கு முந்தைய replay சாத்தியமில்லை. அதிக retention = அதிக disk & cost.
* **Ordering & duplicates**: Replay பண்ணும்போது at-least-once delivery வரும். Consumer idempotent ஆக இருக்க வேண்டும். இல்லையெனில் double payment போன்ற பிரச்சனை.
* **Operational complexity**: Consumer offset-ஐ நிர்வகிப்பது, consumer group rebalance பண்ணுவது, replay window-ஐ configure பண்ணுவது எல்லாம் extra ops burden.
* **Performance**: பல consumers ஒரே partition-ல் replay பண்ணினால் read amplification வரும். Throughput drop ஆகும்.

## Practical Example

பேங்க் transaction system. Payment Service OrderPlaced event-ஐ கேட்கிறது. 2 நாள் முன்பு tax calculation logic-ல் bug இருந்தது, சில transactions தவறான tax-ல் process ஆனது.

Fix செய்த பிறகு, Kafka topic payment.events-ல் கடந்த 30 நாள் retention இருக்கிறது. Consumer group payment-service-v2-ஐ புதிய code-ல் start பண்ணி offset-ஐ bug ஆரம்பித்த நாளுக்கு rewind பண்ணி replay செய்கிறீர்கள். Replayed events idempotent processor-ல் போய் சரியான tax-ஐ recalculate பண்ணி correction ledger-ஐ update செய்கிறது.

இதற்கு message-கள் immutable log-ல் இருந்ததால் மட்டுமே சாத்தியம்.

## Reasoning Challenge

உங்களிடம் 20 consumers இருக்கு. எல்லாருக்கும் same event தேவை. Consumer processing speed வேறுபடுகிறது. Producer-ஐ block பண்ணக்கூடாது. Replay-ம் வே
