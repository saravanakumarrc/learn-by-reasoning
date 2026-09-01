# Subgraphs

> **Learning Path:** AI Orchestration
> **Section:** 17.1.12 — LangGraph concepts

## 1. Problem

ஒரு AI Orchestration system வளரும்போது ஒரு graph-ல nodes அதிகமாகிவிடும். ஒரே graph-ல user intent classify பண்ணுவது, tool call பண்ணுவது, RAG retrieve பண்ணுவது, response generate பண்ணுவது, safety check பண்ணுவது எல்லாம் இருக்கும்.

இதில் என்ன பிரச்சனை வரும்?

* Graph படிக்கவே கஷ்டம். முழு flow ஒரே பார்வையில் புரியாது.
* ஒரு சிறிய logic மாற்றினாலும் முழு graph-ஐ test பண்ண வேண்டியிருக்கும்.
* Same sub-workflow, different entry points-ல தேவைப்படும். உதாரணமாக `billing_lookup` flow எப்போதும் `extract entity → validate → fetch from DB → format` என்றே இருக்கும்.
* Team parallel-ஆ work பண்ண முடியாது. எல்லோரும் ஒரே graph file-ஐ touch பண்ண வேண்டும்.

What goes wrong if we don't have this? Graph becomes spaghetti, change risky, reuse zero.

## 2. Mental Model

Subgraph என்பது ஒரு **mini-graph** இது ஒரு black box node மாதிரி behave செய்கிறது.

உள்ளே பல steps இருக்கலாம். வெளியில் இருந்து பார்த்தால் அது ஒரே node தான். Input வாங்கும், output தரும். Internal complexity hide ஆகும்.

அனலாகி: Microservice-ல ஒரு service-க்குள்ளே internal functions இருக்கும். API consumer-க்கு அது ஒரு endpoint தான். அதே concept தான் graph-ல.

## 3. How It Works

LangGraph-ல subgraph என்பது ஒரு Graph object-ஐ மற்றொரு Graph-ன் node-ஆக பயன்படுத்துவது.

உள்ளே:
* தனி state schema இருக்கலாம், அல்லது parent state-ஐ inherit பண்ணலாம்
* தனி entry node, exit node இருக்கும்
* Internal routing, conditional edges இருக்கும்

வெளியில்:
* ஒரு node name-ஆக தோன்றும்
* Parent graph-க்கு `input` மற்றும் `output` மட்டும் தெரியும்

Compiler internal-ஆ subgraph-ஐ expand பண்ணி compile செய்கிறது. Execution time-ல அது seamless.

## 4. Architectural Reasoning

எப்போது useful?

* **Modularity:** `onboarding`, `payment_flow`, `support_escalation` போன்ற தனித்த workflow-களை isolate பண்ண
* **Reuse:** Same subgraph-ஐ multiple parent graphs-ல பயன்படுத்தலாம். உதாரணமாக `entity_extraction` subgraph-ஐ chat agent-லயும், email agent-லயும்
* **Team ownership:** Different teams different subgraphs own பண்ணலாம்
* **Testing:** Subgraph-ஐ தனியாக unit test பண்ணலாம், mock input/ output கொடுத்து

என்ன constraint-ஐ address பண்ணுகிறது? Complexity growth, coupling, operational risk.

Alternatives:
* Flat graph with many nodes
* Separate independent graphs + manual orchestration

Subgraph choose பண்ணுவது என்பது composition over flatness. Decision cost: abstraction layer.

## 5. Trade-offs

**Encapsulation vs Visibility**
Internal steps hide ஆகும். Debugging செய்யும்போது parent graph-ல error வந்தால், subgraph உள்ளே trace பண்ண வேண்டும். Observability add பண்ண வேண்டும்.

**State coupling**
Parent state மற்றும் child state sync பண்ண வேண்டும். Too much sharing = tight coupling. Too little sharing = data pass overhead. நீங்கள் state schema design பண்ணும்போது boundary தெளிவாக வைக்க வேண்டும்.

**Latency**
Subgraph என்பது additional hop அல்ல. ஆனால் உள்ளே multiple LLM calls இருந்தால் latency accumulate ஆகும். Timeout, retry policy parent-ல apply ஆகுமா? தனியா வைக்க வேண்டுமா?

**Operational complexity**
Graph compile time அதிகரிக்கும். Reuse நன்மை தரும், ஆனால் change propagation புரிந்து கொள்ள வேண்டும். ஒரு subgraph version update பண்ணினால் எந்த parent graphs பாதிக்கும்?

Failure mode: Subgraph stuck ஆனால் parent graph-க்கு மட்டும் timeout தெரியும். Internal retry logic இல்லாமல் parent block ஆகும்.

## 6. Practical Example

Enterprise Support Agent.

Parent graph:
`classify_intent → route → respond`

Route node உள்ளே 3 subgraphs இருக்கு:
* `billing_subgraph`: extract invoice id → validate → fetch DB → format answer
* `technical_subgraph`: extract product + error → search knowledge base → RAG retrieve → generate fix
* `escalation_subgraph`: sentiment check → collect context → create ticket

ஒரு user message வரும்போது classify_intent "billing" என்றால், parent graph `billing_subgraph` node-ஐ call பண்ணும். அது உள்ளே 4 steps run பண்ணி output தரும். Parent-க்கு அது ஒரு single step மாதிரி.

அதே `entity_extraction` subgraph-ஐ billing, technical இரண்டிலும் reuse பண்ணலாம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு `customer_onboarding` flow உள்ளது. அதில் KYC check, credit check, welcome email send என 12 nodes உள்ளன. அதே 12 steps ஒரு `partner_onboarding` flow-லயும் 80% தேவைப்படுகிறது. வேறுபாடு என்னவென்றால் partner flow-ல credit check இல்லை, ஆனால் contract e-sign step உள்ளது.

இதை ஒரே flat graph-ஆ வைக்கலாமா? இல்லை subgraph-ஐ create பண்ணி reuse பண்ணலாமா? எந்த boundary-ல subgraph cut பண்ணுவீர்கள்? State-ஐ எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

* Subgraph என்பது graph-க்குள் graph. Reuse, readability, ownership-க்காக.
* உள்ளே complexity hide பண்ணலாம், ஆனால் observability கண்டிப்பாக வேண்டும்.
* State boundary தெளிவாக இருக்க வேண்டும். Parent-child coupling குறைவாக வை.
* ஒரு flow திரும்ப திரும்ப வருகிறதா? அதை subgraph ஆக்கு. One mental model: composition.

இதை தெரிந்தால் போதும்: **Graph big ஆகும்போது, முதலில் subgraph-ஆ split பண்ணு, பிறகு optimize பண்ணு.**
