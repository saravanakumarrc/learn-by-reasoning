# Dead-letter queues

> **Learning Path:** Distributed Systems
> **Section:** 3.2.8 — Messaging

## 1. Problem

ஒரு distributed system-ல message queue use பண்ணும்போது producer message அனுப்பிட்டு மறந்துடும். Consumer தான் அதை process பண்ணும்.

இப்போது inventory service ஒரு `OrderCreated` event-ஐ consume பண்ணும்போது code-ல bug இருக்கு. அல்லது downstream database down ஆகி temporary error வருது. Consumer exception throw பண்ணி message-ஐ acknowledge பண்ணாம விடுது.

Broker அந்த message-ஐ மறுபடியும் queue-க்கு திருப்பி விடும். Retry ஆகும். மறுபடியும் fail ஆகும். Retry ஆகும்.

இது என்ன ஆகும்?
* Good messages கூட stuck ஆகி queue pile up ஆகும்.
* Consumer continuously same poison message-ஐ முயற்சி பண்ணிக்கிட்டே இருக்கும். Throughput குறையும்.
* Retry backoff இல்லாமல் system-ஐ overload பண்ணும்.

இதற்கு ஒரு limit வேண்டும். முடியாத message-ஐ தனியா isolate பண்ணி, முக்கிய flow-ஐ protect பண்ணணும்.

அதுதான் dead-letter queue.

## 2. Mental Model

Dead-letter queue என்பது quarantine ward மாதிரி.

Normal queue = healthy patients ward. Consumer சரியா process பண்ணும்.

ஒரு message தொடர்ந்து fail ஆகி, "இதை இப்போ process பண்ண முடியாது" என்று தெரிந்தால், அதை main queue-ல இருந்து எடுத்து DLQ என்ற தனி queue-க்கு மாற்றி விடு.

Main flow தொடரும். DLQ-ல இருக்கும் message-ஐ பிறகு ஆராய்ச்சி பண்ணி, fix பண்ணி, reprocess பண்ணலாம்.

Key idea: **fail fast for the system, fail slow for the investigation.**

## 3. How It Works

Broker அல்லது consumer client இரண்டில் ஏதாவது இந்த logic-ஐ வைத்திருக்கும்.

பொதுவாக:
* Message consume ஆகும்.
* Consumer exception வரும்.
* Broker message-க்கு retry count-ஐ increment பண்ணும்.
* `maxDeliveryAttempts` / `maxRetries` எட்டினால் அல்லது specific error class-க்கு நேரடியாக DLQ-க்கு அனுப்பினால் message move ஆகும்.
* DLQ-க்கு original message + headers + failure reason கூடவே சேரும்.

Kafka-ல topic._dead-letter-queue, RabbitMQ-ல dead-letter exchange, SQS-ல redrive policy. Implementation வேறுபடும். Concept ஒன்றே.

Retry policy-ஐ DLQ-வுடன் இணைக்கும் போது backoff + DLQ கombination-ல system stable ஆகும்.

## 4. Architectural Reasoning

DLQ useful ஆகும் போது:
* Consumer deterministic failure உண்டு. e.g., schema mismatch, invalid payload, business rule violation.
* Temporary failure-ஐ retry-ல handle பண்ணி, permanent failure-ஐ isolate பண்ணணும்.
* Audit மற்றும் compliance-க்கு failed message-ஐ தக்க வைக்கணும்.
* Team-க்கு alert வரணும், முக்கிய flow block ஆகக்கூடாது.

Alternatives:
* Retry மட்டும், no DLQ: poison message infinite loop.
* Immediate drop: data loss, debug முடியாது.
* Manual DLQ: consumer மெதுவாக manual park பண்ணும். Error prone.

Architect ஏன் choose பண்ணுவார்? Availability vs correctness trade-off. Main queue-ன் health-ஐ காப்பாற்றுவதே முக்கியம். Failed message-ஐ பின்னர் தீர்க்கலாம்.

## 5. Trade-offs

**Visibility vs operational burden.** DLQ messages pile up ஆனால் அதை யார் பார்க்கும்? Monitor செய்யாமல் DLQ ஒரு black hole ஆகும்.

**Retry config தவறாக set பண்ணினால் temporary error கூட permanent ஆகும்.** maxRetries குறைவாக இருந்தால் recoverable failure DLQ-க்கு போய் விடும். அதிகமாக இருந்தால் delay.

**Poison message mask செய்யும்.** DLQ உள்ளது என்பதால் developer "எப்படியும் DLQ போகும்" என்று சோம்பேறித்தனம் வரும். Root cause fix ஆகாமல் போகும்.

**Reprocessing complexity.** DLQ-ல இருந்து message-ஐ மீண்டும் main queue-க்கு அனுப்பும் போது idempotency முக்கியம். இல்லாவிட்டால் duplicate side effects.

## 6. Practical Example

Enterprise order system.

`orders.created` topic-க்கு producer publish பண்ணும். `payment-service` consume பண்ணும்.

ஒரு நாள் third-party payment gateway API change ஆகி response schema மாறுகிறது. Consumer JSON parse fail ஆகிறது. `JsonMappingException` வருகிறது.

Retry 3 times, fail. Message DLQ-க்கு மாற்றப்படுகிறது. Alert trigger ஆகிறது.

Main queue-ல புதிய orders process ஆகிக்கொண்டே இருக்கிறது. Customer-க்கு delay இல்லை.

Team DLQ-ல message-ஐ பார்த்து payload பார்த்து schema fix பண்ணி, consumer deploy பண்ணி, DLQ messages-ஐ batch-ஆக reprocess பண்ணுகிறார்கள். Idempotency key-ல payment duplicate ஆகாமல் பார்த்துக்கொள்கிறார்கள்.

இல்லாமல் இருந்தால், queue block ஆகி, lag அதிகரித்து, order confirmations தாமதமாகும்.

## 7. Reasoning Challenge

உங்கள் service-க்கு 5 consumers. Same event தேவை. Consumer A ஒரு specific field validation fail ஆகும் போது தொடர்ந்து exception தருகிறது. இது data issue. Consumer B, C, D, E-க்கு அந்த event-க்கு எ
