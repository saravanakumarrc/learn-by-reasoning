# Faithfulness

> **Learning Path:** AI Evaluation
> **Section:** 18.2.6 — RAG metrics

## 1. Problem

RAG system-ல LLM context-ல கொடுத்த documents மட்டும் பார்த்து answer generate பண்ணணும். ஆனா நடைமுறையில் என்ன ஆகுது?

User கேட்கிறார்: "Q3-ல் revenue எவ்வளவு?"
Retriever கொடுத்தது: Q3 revenue 120M, Q4 revenue 150M, Q3 expenses 80M.

LLM answer பண்ணுது: "Q3 revenue 120M, மொத்த வருட revenue 270M"

இங்கே 270M என்பது LLM தானாக கணக்கிட்டது. Source-ல இல்லை. இது hallucination இல்லை, ஆனால் faithfulness violation.

இன்னொரு case: Source சொல்லுது "product X discontinued in 2023". LLM answer பண்ணுது "product X discontinued in 2022". Factually wrong, ஆனால் source-க்கு புறம்பானது.

Faithfulness என்பது answer **source documents-க்கு உண்மையாக இருக்கிறதா** என்பது. Correctness வேறு. Faithfulness வேறு.

ஏன் இது painful? Production RAG-ல user trust போகும். Compliance, finance, legal use-case-ல source-க்கு மாறுபட்ட answer கொடுத்தால் liability வரும்.

## 2. Mental Model

Faithfulness = **Grounding**.

LLM-ன் generation ஒரு function ஆக பார்க்கலாம்: `answer = f(query, retrieved_context)`. அந்த answer-ல உள்ள ஒவ்வொரு claim-ம் retrieved context-ல support ஆகிறதா? Support ஆகிற claim-கள் மட்டுமே இருக்கணும்.

Analogy: நீங்கள் ஒரு witness-க்கு முன்னால் நிற்கிறீர்கள். நீங்கள் சொல்லக்கூடியது அவர் கொடுத்த statement-ல இருந்து மட்டும். உங்கள் சொந்த memory, inference, common sense கூடாது. அதுதான் faithfulness.

## 3. How It Works

Evaluation-ல faithfulness-ஐ measure பண்ண இரண்டு வழி:

**1. Reference-based, automatic:** 
Answer-ல உள்ள facts-ஐ extract பண்ணி, அவை retrieved passages-ல உள்ளதா என்பதை check பண்ணுவது. NLI model-ஐ use பண்ணி entailment score கொடுக்கலாம். 
Claim-level faithfulness = supported claims / total claims.

**2. Human / LLM-as-judge:**
LLM-க்கு query + context + answer கொடுத்து: "இந்த answer-ல உள்ள ஒவ்வொரு statement-ம் context-ல இருந்து derive ஆகிறதா?" என்று கேட்கலாம். Score 0-1.

Important nuance: Faithfulness does NOT require answer to be complete. Source-ல இருந்து எடுக்காமல் extra info add பண்ணாமல் இருந்தால் போதும். Under-generation allowed, over-generation not allowed.

## 4. Architectural Reasoning

எப்போ faithfulness முக்கியம்?

* Enterprise RAG: customer support, legal, finance, healthcare. Source document-ஐ cite பண்ண வேண்டும்.
* Agent workflows where tool output-ஐ summarize பண்ணுகிறோம்.
* High-risk outputs where hallucination cost high.

Constraint இது address பண்ணுது: **LLM-ன் parametric knowledge vs retrieved knowledge கலக்காமல் தடுப்பது.**

Alternatives:
* **Faithfulness via prompt engineering**: "Answer only using context, say I don't know if not found". Helps, but model still hallucinates under pressure.
* **Faithfulness via RAG architecture**: retrieval augmentation with grounding constraints, e.g., retrieval-conditioned generation, faithfulness reward in fine-tuning.
* **Faithfulness via post-hoc verification**: generate then verify claims against source with NLI, reject/rewrite if violation.

Architect choose பண்ணும்போது கேட்க வேண்டியது: Do we need strict grounding or can we allow model reasoning? Strict grounding = faithfulness first. Reasoning first = correctness and completeness first.

## 5. Trade-offs

* **Faithfulness vs Completeness**: Faithfulness strict-ஆ வைத்தால் answer too short / "I don't know" அதிகம் வரும். User satisfaction குறையும்.
* **Faithfulness vs Latency/Cost**: Claim verification, NLI checking, self-consistency loops cost extra LLM calls.
* **Faithfulness vs Flexibility**: Summarization, paraphrasing, combining multiple passages - where does paraphrase end and fabrication start? Model இரண்டையும் கலக்கும்.
* **Faithfulness metric itself is noisy**: LLM-as-judge faithfulness evaluate பண்ணும் போது judge-ன் own bias வரும். Different retrievals, different faithfulness.

Failure modes:
* Citation without support: model cite பண்ணும் passage-ல fact இல்லை.
* Implicit inference: source A + source B இருந்தால் conclusion C logical ஆகும், ஆனால் source-ல explicit இல்லை. Faithfulness check fail ஆகும்.
* Numeric calculation: source-ல numbers இருக்கு, model calculate பண்ணி கொடுக்கும். Faithfulness low, but correctness maybe high.

## 6. Practical Example

Enterprise support RAG.

Retrieved context:
> "Plan Gold includes 24x7 support. Plan Silver includes business hours support only. Support SLA for Gold is 2 hours."

Query: "Silver plan SLA என்ன?"

Bad answer: "Silver plan SLA is 4 hours, because Gold is 2 hours". Faithfulness = 0. Source-ல Silver SLA இல்லை.

Good faithful answer: "Retrieved context-ல Silver plan SLA குறிப்பிடப்படவில்லை. Gold plan SLA 2 hours."

இங்கே completeness இல்லை, ஆனால் faithfulness உள்ளது.

Production-ல நீங்கள் faithfulness score monitor பண்ணி, threshold கீழ் போனால் answer-ஐ reject பண்ணி fallback: "I don't have enough information" என்று கொடுக்கலாம்.

## 7. Reasoning Challenge

உங்களிடம் medical RAG system உள்ளது. Source documents: clinical guidelines. Retrieved context-ல drug dosage range கொடுக்கப்பட்டுள்ளது. LLM answer-ல patient weight-ன் அடிப்படையில் exact dosage calculate பண்ணி கொடுக்கிறது.

Faithfulness score குறைவாக வருகிறது. ஆனால் clinicians சொல்கிறார்கள் calculation useful.

நீங்கள் என்ன செய்வீர்கள்? Faithfulness strict-ஆ enforce பண்ணுவீர்களா, அல்லது calculation-ஐ allow பண்ணுவீர்களா? ஏன்? Trade-off என்ன?

## 8. Key Takeaways

* Faithfulness = answer grounded in retrieved context, not in model parametric knowledge.
* Faithfulness ≠ factual correctness. Faithful answer can still be incomplete or even wrong if source wrong.
* Strict faithfulness improves trust and compliance, but reduces completeness and requires verification overhead.
* Measure faithfulness at claim level, not just whole answer level.
* Every architectural choice to increase faithfulness adds latency, cost, or conservativeness.
