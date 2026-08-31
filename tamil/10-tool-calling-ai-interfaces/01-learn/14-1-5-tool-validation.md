# Tool validation

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.5 — Learn

## 1. Problem

உங்க AI agent ஒரு tool call பண்ணுது. உதாரணமாக `create_invoice(customer_id, amount)` அல்லது `transfer_money(to_account, amount)`.

Agent தப்பா parameter போட்டால் என்ன ஆகும்?

* `customer_id` empty string, `amount` negative number
* `to_account` format தப்பு, அல்லது ஒரு internal test account
* tool-ன் expected input schema-க்கு மாறாக field missing

Production-ல இது data corruption, financial loss, security breach வரை போகும்.

Tool validation இல்லாமல், agent "confidently incorrect" ஆக இருக்கும். LLM output unpredictable. அதனால் **எல்லா tool call-க்கும் gate வேண்டும்**.

## 2. Mental Model

Tool validation என்பது agent இன் முடிவுக்கும் உண்மையான tool execution-க்கும் இடையில் இருக்கும் **contract checker**.

ஒரு API gateway போல நினைத்துக்கொள்ளுங்கள்: request வருகிறது → schema check → business rule check → allow/deny.

Validation இரண்டு layer-ல வரும்:
1. **Syntactic validation** - type, format, required fields சரியா?
2. **Semantic / business validation** - value அர்த்தமுள்ளதா? safe-ஆ?

## 3. How It Works

Agent tool call செய்யும்போது:

`LLM output -> Tool Call Parser -> Validator -> Tool Executor`

Validator என்ன செய்கிறது?

* Schema validation: JSON schema / Pydantic model-ஐயும் போட்டு check செய்யும். `amount` number-ஆ? `email` regex match ஆகுதா?
* Range / enum check: amount > 0, status in ['pending','paid']
* Context validation: current user-க்கு இந்த customer_id access உண்டா? rate limit தாண்டவில்லையா?
* Safety policy: destructive tool-க்கு confirmation தேவையா? PII leak ஆகுதா?

Fail ஆனால்: error-ஐ structured ஆக திருப்பி agent-க்கு கொடு. Agent அதைப் படித்து self-correct செய்யும்.

## 4. Architectural Reasoning

Tool validation எப்போது முக்கியம்?

* Agent external system-ஐ touch செய்கிறது: database, payment, email, internal API
* Tool side effects உள்ளது: irreversible operations
* Multiple agents / users same tool-ஐ use செய்கிறார்கள்

Alternatives?

* **Trust LLM output**: வேண்டாம். Hallucination உறுதி.
* **Validate only at tool side**: தாமதமாக பிடிபடும். Agent retry loop, confusing errors.
* **Validate centrally before execution**: best. Single source of truth, observability எளிது.

Architect முடிவு: validation logic-ஐ tool definition-உடன் co-locate செய்யாமல், **Tool Validation Layer** என்று தனி layer ஆக்குங்கள். இது schema, policy, context check எல்லாவற்றையும் ஒரே இடத்தில் manage செய்யும்.

## 5. Trade-offs

* **Strict vs permissive validation**: Strict ஆனால் false negatives அதிகம், agent stuck ஆகும். Permissive ஆனால் bad calls தப்பிவிடும். Start strict, gradually relax with allowlists.
* **Latency**: Validation adds round-trip. Heavy business checks costly. Critical path-ல cache / pre-validate செய்யுங்கள்.
* **Complexity**: Validation rules grow. Schema versioning, policy drift ஆகும். Validation code-ஐ test செய்ய வேண்டும்.
* **Failure mode**: Validator itself bug ஆனால் all tools block ஆகும். Validator-ஐ high availability-ல வைக்க வேண்டும், circuit breaker வேண்டும்.

## 6. Practical Example

Enterprise support agent. Tool: `refund_order(order_id, amount, reason)`.

Validation layer செய்வது:

1. Schema: order_id string, amount number >0, reason enum
2. Business: amount <= order total - already refunded
3. Authorization: agent user has refund permission for this merchant
4. Policy: amount > 10000 என்றால் human approval தேவை

Agent `refund_order(order_id="ORD-123", amount=-50)` போட்டால் validator உடனே reject: `amount must be > 0`. Agent-க்கு error திரும்பி வரும். Agent correct value-ஐ கேட்டு retry செய்யும்.

இல்லாமல் இருந்தால் tool உள்ளே error விழும், அல்லது தவறான refund create ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 20 agents ஒரே `update_customer_profile` tool-ஐ use செய்கிறார்கள். Tool PII field-களை update செய்யும். GDPR compliance வேண்டும். Agent சில நேரம் extra fields hallucinate செய்கிறது.

Validation layer-ல நீங்கள் என்ன check செய்வீர்கள்? Syntax மட்டும் போதுமா? Context validation எங்கே சேர்ப்பீர்கள்?

## 8. Key Takeaways

* Tool validation என்பது agent reliability-க்கான **safety net**, not optional.
* Syntactic validation + business validation + authorization எல்லாம் ஒன்றாக வேண்டும்.
* Validation failure-ஐ agent-க்கு clear, actionable error ஆக திருப்பி அனுப்புவது self-correction-ஐ enable செய்கிறது.
* Every architectural solution creates trade-off: strictness vs flexibility, latency vs safety.
