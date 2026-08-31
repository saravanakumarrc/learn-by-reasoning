# Tool schemas

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.2 — Learn

## 1. Problem

உங்க agent-க்கு external tool-களை call பண்ண permission இருக்கு. `get_weather`, `create_ticket`, `search_inventory` மாதிரி.

LLM எப்படி தெரிஞ்சுக்கும் எந்த tool-ஐ எப்போ use பண்ணனும், என்ன parameters கொடுக்கனும், என்ன format-ல return வரும்?

ஒரு tool-ஐ ஆளாளுக்கு வித்தியாசமா கூப்பிட்டா? Parameter name typo ஆனால்? Type mismatch ஆனால்? Required field miss ஆனால்?

Production-ல agent call பண்ணும் போது runtime error, silent failure, hallucinated parameter எல்லாம் வரும். Debugging கஷ்டம்.

Tool schemas தேவைப்படுவது இந்த chaos-ஐ control பண்ண.

## 2. Mental Model

Tool schema = ஒரு tool-ன் contract.

Human engineer-க்கு API spec எப்படி இருக்கோ, அதே மாதிரி LLM-க்கும் ஒரு machine-readable spec வேணும்.

Schema சொல்லும்:
- tool என்ன பண்ணும்
- என்ன input parameters வேணும், type என்ன, required ஆ?
- output என்ன shape-ல வரும்

இது LLM-க்கு reasoning anchor ஆகும். இது validation layer ஆகும்.

## 3. How It Works

Tool schema பொதுவா JSON Schema அல்லது OpenAPI style-ல define பண்ணுவாங்க.

ஒரு எளிய example:

```json
{
  "name": "create_support_ticket",
  "description": "Creates a support ticket for a customer issue",
  "parameters": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"},
      "issue_type": {"type": "string", "enum": ["billing","technical","refund"]},
      "priority": {"type": "string", "enum": ["low","medium","high"]},
      "description": {"type": "string"}
    },
    "required": ["customer_id","issue_type","description"]
  }
}
```

LLM system prompt-ல அல்லது tool registry-ல இந்த schema கொடுக்கப்படும். Model generate பண்ணும் போது இந்த schema-வை follow பண்ணி function call JSON produce பண்ணும்.

Runtime-ல schema validator tool arguments-ஐ check பண்ணும். Invalid ஆனால் reject பண்ணி model-க்கு error திருப்பி அனுப்புவோம்.

## 4. Architectural Reasoning

Tool schema useful ஆகும் போது:

- Agent multiple tools use பண்ணும் போது. Model confusion குறையும்.
- Tool input validation தேவைப்படும் போது. LLM hallucinate பண்ணும், schema அதை catch பண்ணும்.
- Team-ல different developers tools build பண்ணும் போது. Schema contract ஆக இருக்கும்.
- Observability வேணும். Tool call logs-ல parameter shape தெரியும்.

Alternatives:
- Free text description மட்டும் கொடுப்பது. Flexible ஆனால் unreliable.
- Hardcoded prompts. Small scale-ல work ஆகும், scale ஆனால் break ஆகும்.
- Strict code generation. Overkill.

Architect choose பண்ணும் போது trade-off பார்க்கணும்: schema strictness vs flexibility.

## 5. Trade-offs

**Precision vs Creativity.** Schema strict ஆக இருந்தால் model hallucinations குறையும். ஆனால் edge cases handle பண்ண முடியாது. Too loose schema என்றால் validation value இல்லை.

**Schema maintenance cost.** Tool evolve ஆனால் schema update பண்ணனும். Versioning முக்கியம். இல்லைன்னா agent outdated spec use பண்ணி fail ஆகும்.

**Description quality matters.** Schema fields மட்டும் போதாது. Good description தான் model-க்கு *when* to use tool என்பதை சொல்லும். `description` field-ல reasoning cue இருக்கணும்.

**Failure mode.** Schema mismatch ஆனால் tool call fail ஆகும். அதனால் retry logic, graceful fallback வேணும். Model-க்கு error feedback கொடுத்து self-correct பண்ண வைக்கணும்.

## 6. Practical Example

Enterprise support agent.

Tools:
1. `search_kb` - knowledge base search
2. `get_customer_orders` - customer orders fetch
3. `create_support_ticket` - ticket create

Schema define பண்ணாம இருந்தா model `customer_id` க்கு `customer name` கொடுக்கும். `issue_type` ல typo பண்ணும்.

Schema define பண்ணின பிறகு:
- Model parameter names சரியா generate பண்ணும்.
- `enum` வச்சதால invalid issue_type தவிர்க்கப்படும்.
- Required fields missing ஆனால் validator catch பண்ணி model-க்கு "customer_id missing" error திருப்பி அனுப்பும்.

System design-ல schema registry வைத்து tools dynamically load பண்ணலாம். Agent startup-ல schema fetch பண்ணி context-ல inject பண்ணலாம். இது maintainability increase பண்ணும்.

## 7. Reasoning Challenge

உங்களிடம் `refund_order` tool இருக்கு. Parameters: `order_id` string, `amount` number, `reason` enum [`duplicate`,`wrong_item`,`damaged`].

Agent user request-ல "order 12345 க்கு refund பண்ணுங்க, எனக்கு full amount வேணும்" என்று கேட்டது.

Model generate பண்ணிய function call-ல `amount` missing, `reason` missing.

இங்கே schema validation என்ன பண்ணும்? Agent என்ன next step எடுக்கணும்? Schema-ஐ மாற்றாமல் இந்த problem-ஐ எப்படி handle பண்ணுவீங்க?

## 8. Key Takeaways

- Tool schema என்பது LLM-க்கு API contract. Problem-ஐ definition தான்.
- Schema clarity தான் correct tool use-ன் முதல் condition. Description > field names.
- Validation layer வச்சு hallucinated calls-ஐ early reject பண்ணு, model-க்கு error feedback கொடு.
- Schema strictness ஒரு architectural decision. Precision வேணுமா flexibility வேணுமா என்பதை system constraints பார்த்து முடிவு பண்ணு.
