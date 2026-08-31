# Hallucination

> **Learning Path:** RAG Architecture
> **Section:** 12.3.8 — RAG failure modes

## 1. Problem

உங்கள் RAG system ஒரு customer support agent-ஆக run ஆகுது. User கேட்கிறார்: "என் last order எப்போது deliver ஆகும்?"

Retriever உண்மையான order data-வை கொண்டு வந்து context-ல் கொடுக்கிறது. ஆனால் LLM பதில் சொல்லும்போது: "உங்கள் order #48291 நேற்று 14:30-க்கு delivered ஆகிவிட்டது. Signature: R. Kumar"

உண்மையில் அந்த order pending-ல் தான் இருக்கிறது.

இது ஒரு hallucination. Retrieval சரியாக இருந்தும், generation தவறாக உருவாக்கி விட்டது.

**What goes wrong if we don't handle this?** User trust போகும். Wrong action எடுக்கும். Financial/legal risk வரும். RAG என்றாலும், output unreliable ஆகிறது.

> Problem painful enough: LLM-க்கு knowledge இல்லாத இடத்தில் confident-ஆக பொய் சொல்லும்.

## 2. Mental Model

Hallucination என்பது LLM-ன் **confabulation**. அது context-ல் இல்லாத தகவலை, training data-வில் இருந்து கற்பனை செய்து பூர்த்தி செய்யும்.

RAG-ல் இரண்டு இடத்தில் நடக்கும்:

1. **Retrieval hallucination**: Retriever தொடர்பில்லாத, irrelevant documents-ஐ கொண்டு வருகிறது. அல்லது wrong chunk.
2. **Generation hallucination**: Retrieved context சரியாக இருந்தும், LLM அதை தவறாக interpret செய்து, கற்பனையான details சேர்க்கிறது.

Mental model: LLM என்பது pattern completer, truth verifier அல்ல. Context கொடுத்தாலும், அது context-ஐ ground truth-ஆக பயன்படுத்தும் guarantee இல்லை.

## 3. How It Works

RAG pipeline: Query → Retriever → Ranker → Context → LLM → Answer

Hallucination எப்படி creep ஆகிறது?

* **Context gap**: User question-க்கு தேவையான info retrieved context-ல் இல்லை. LLM பதில் தர வேண்டும் என்ற pressure-ல் fill-in-the-blanks செய்கிறது.
* **Conflicting context**: 3 docs கொண்டு வரப்படுகிறது, 2 பழைய pricing, 1 புதிய pricing. LLM mix செய்து தவறான price கொடுக்கிறது.
* **Over-trust in parametric memory**: "RAG" என்றாலும் LLM தன்னுடைய training knowledge-ஐ முன்னுரிமை கொடுக்கிறது, retrieved doc-ஐ ignore செய்கிறது.
* **Prompt leakage**: System prompt சரியாக grounding enforce செய்யவில்லை. LLM-க்கு "unknown என்று சொல்லு" என்ற boundary இல்லை.

## 4. Architectural Reasoning

Hallucination-ஐ zero ஆக்க முடியாது. நீங்கள் manage செய்ய வேண்டும்.

**When this becomes painful**: 
* Customer-facing answers, financial, medical, legal domain
* High-stakes RAG where citation தேவை
* Agent workflows where LLM output அடுத்த tool call-ஐ trigger செய்கிறது

**Options and reasoning**:

* **Better retrieval**: Hybrid search + reranker + context window pruning. Less noise, better relevance. Trade-off: latency and cost.
* **Grounding enforcement**: Prompt engineering: "Answer only from context. If not present, say I don't know." System prompt + few-shot examples. Trade-off: LLM sometimes too conservative, refuses valid answers.
* **Citation requirement**: LLM-ஐ force செய்ய source chunk id/span-ஐ cite செய்ய. Post-generation verifier checks citation actually supports claim. Trade-off: output format complexity.
* **Self-consistency + verification**: Same query-ஐ 3 times run, majority vote. Or generate answer, then generate verification question and check against context. Trade-off: 2-3x LLM cost.
* **Guardrails layer**: Output-ஐ classifier மூலம் hallucination probability score செய்து, threshold கீழ் reject செய். Trade-off: false positives.

Architect ஆக நீங்கள் decide செய்வது: **Acceptable hallucination rate** என்ன? Support chatbot-க்கு 2% ஏற்புடையது. Loan approval RAG-க்கு 0% தேவை.

## 5. Trade-offs

* **Faithfulness vs Completeness**: Strict grounding = safe ஆனால் "I don't know" அதிகம். Loose grounding = helpful ஆனால் hallucination அதிகம்.
* **Latency vs Safety**: Retrieval + rerank + citation check + verification = slow மற்றும் costly. Real-time chat-ல் இது பிரச்சனை.
* **Context size vs Precision**: பெரிய context கொடுத்தால் LLM lost-in-the-middle ஆகும். சிறிய context கொடுத்தால் missing info வரும்.
* **Parametric knowledge vs Retrieved knowledge**: LLM-க்கு common sense தேவை. ஆனால் அதை அதிகம் நம்பினால் hallucination வரும்.

Failure mode: Citation hallucination. LLM fake citation id கொடுக்கும். அதனால் citation check-க்கும் verifier தேவை.

## 6. Practical Example

Enterprise RAG for HR policy.

User asks: "Remote work allowance எவ்வளவு?"

Retriever returns 2 chunks:
1. 2023 policy: ₹10,000/month
2. 2024 policy update: ₹15,000/month for employees in Tier 1 cities.

LLM hallucinate செய்து: "Allowance ₹15,000 for all employees."

சரியான architecture:

* Retriever hybrid search + date filter
* Reranker context-ஐ relevance + recency-க்கு sort செய்
* Prompt: "Use only provided context. If policy varies by condition, mention condition. If info missing, say unknown."
* Generation-க்கு பிறகு, output parser extracts claim "₹15,000 for all". Verifier checks if context supports "all". Does not support. So answer flagged.

Result: "Tier 1 city employees-க்கு ₹15,000/month. உங்கள் city Tier 1 இல்லையெனில் தற்போது policy apply ஆகாது."

## 7. Reasoning Challenge

உங்களிடம் financial RAG agent இருக்கிறது. User கேட்கிறார்: "Q3 revenue எவ்வளவு?" Retriever 3 docs கொண்டு வருகிறது: Q3 draft, Q3 final, Q3 restated. LLM ஒரு single number கொடுக்கிறது.

உங்கள் constraints: Answer latency < 2 seconds, hallucination rate < 0.1%, cost sensitive.

இந்த scenario-ல் நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Retrieval, prompting, verification எதை prioritize செய்வீர்கள்? ஏன்?

## 8. Key Takeaways

* Hallucination என்பது LLM-ன் default behavior, RAG தானாக தீர்க்காது.
* Grounding என்பது retrieval quality + generation discipline + verification ஆகியவற்றின் கலவை.
* Architect ஆக நீங்கள் trade-off செய்ய வேண்டும்: faithfulness vs completeness vs latency vs cost.
* Production RAG-ல் "I don't know" என்பது ஒரு feature, failure அல்ல.
