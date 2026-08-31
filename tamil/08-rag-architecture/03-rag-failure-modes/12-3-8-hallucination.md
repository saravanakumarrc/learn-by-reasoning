# Hallucination

> **Learning Path:** RAG Architecture
> **Section:** 12.3.8 — RAG failure modes

## 1. Problem

உங்கள் RAG system-க்கு ஒரு user கேட்கிறார்: "எங்கள் company-ல் Q3 2025-க்கான revenue target என்ன?"

Retriever சரியாக relevant documents-ஐ கண்டுபிடித்து LLM-க்கு கொடுக்கிறது. LLM அந்த context-ஐ படித்துவிட்டு பதில் சொல்கிறது. ஆனால் பதில் தவறானது. அல்லது context-ல் இல்லாத ஒரு குறிப்பிட்ட எண்ணை கற்பனையாக உருவாக்கி தருகிறது.

அந்த பதில் confident-ஆகவும், plausible-ஆகவும் இருக்கிறது. User நம்பிவிடுகிறார். Business decision தவறாகிறது.

இது தான் hallucination. இது RAG-ல் ஏன் ஏற்படுகிறது? LLM ஒரு generative model. அதன் வேலை complete செய்வது. Context இல்லாத இடத்தை fill பண்ணுவது. RAG அதை குறைக்கிறது, ஆனால் அழிக்கவில்லை.

## 2. Mental Model

Hallucination என்பது **grounding failure**.

LLM-க்கு தரப்பட்ட evidence-க்கு அப்பால் அது தன் internal knowledge / statistical pattern-ஐ பயன்படுத்தி பதில் தயாரிக்கிறது.

RAG-ல் இரண்டு இடத்தில் grounding break ஆகலாம்:

1. **Retrieval gap**: உண்மையான தகவல் corpus-ல் இல்லை அல்லது retriever கண்டுபிடிக்கவில்லை. LLM-க்கு போதுமான context இல்லை.
2. **Generation drift**: Context இருக்கிறது, ஆனால் LLM அதை தவறாக interpret பண்ணி, அதை mix பண்ணி, அல்லது context-ல் இல்லாததை confidently சேர்க்கிறது.

சுருக்கமாக: Model-க்கு "எனக்கு தெரியவில்லை" என்று சொல்ல தெரியாது.

## 3. How It Works

Typical RAG pipeline: Query → Retriever → Context → LLM → Answer

Hallucination வரும் வழிகள்:

**A. Retrieval failure**
User query "Q3 2025 revenue target". Retriever Q2 data, generic revenue doc-ஐ மட்டும் கொண்டு வருகிறது. Specific target இல்லை. LLM இடைவெளியை fill பண்ணுகிறது.

**B. Context overload / noise**
10 documents கொடுக்கப்படுகிறது, 9-ல் irrelevant info இருக்கிறது. LLM confuse ஆகி, இரண்டு docs-ஐ merge பண்ணி புதிய தகவலை உருவாக்குகிறது.

**C. Prompting weakness**
System prompt-ல் "அறியாத தகவலுக்கு உறுதியாக பதில் சொல்லாதே" என்று இல்லை. Citation கட்டாயம் இல்லை.

**D. Over-reliance on parametric knowledge**
Model training-ல் பார்த்த similar company targets இருந்தால், அதை பயன்படுத்தி "நியாயமான" எண்ணை கற்பனை செய்கிறது.

## 4. Architectural Reasoning

Hallucination-ஐ முழுவதுமாக அகற்ற முடியாது. அதை **manage** செய்ய வேண்டும்.

எப்போது இது painful ஆகிறது?
- Financial, legal, medical, compliance data-ல்
- User trust critical ஆக இருக்கும் chatbot-ல்
- Answer-க்கு audit trail தேவைப்படும் enterprise RAG-ல்

Architectural options:

* **Better retrieval**: Hybrid search, reranking, query expansion. Retrieval gap-ஐ குறைக்க.
* **Context grounding constraints**: LLM-க்கு "answer only from context, else say I don't know" என்ற instruction. Output schema-ல் citation mandatory.
* **RAG with verification**: Generated answer-ஐ மீண்டும் retriever-ல் pass பண்ணி, claim-கள் context-ல் supported ஆ? என்று check பண்ணும் self-consistency / RAG verification layer.
* **Guardrails**: Post-generation classifier that detects unsupported claims, hallucination score.
* **Smaller context window, higher quality**: 3 strong chunks > 20 noisy chunks.

## 5. Trade-offs

**Retrieval quality vs latency and cost**: Better reranking, multi-step retrieval கொடுத்தால் hallucination குறையும், ஆனால் latency & cost அதிகரிக்கும்.

**Strict grounding vs answer coverage**: "I don't know" rate அதிகரிக்கும். User experience குறையும். ஆனால் trust அதிகரிக்கும்.

**Citation fidelity vs model flexibility**: Citation enforce செய்தால் model creative synthesis குறையும். சில use cases-ல் synthesis தேவை.

**Operational complexity**: Hallucination detection, logging, human-in-the-loop review pipeline சேர்ப்பது team size மற்றும் operability-க்கு cost.

Failure mode: Over-correction. System எல்லாவற்றுக்கும் "I don't know" என்று சொல்ல ஆரம்பித்தால், RAG-ன் value இல்லாமல் போகும்.

## 6. Practical Example

Enterprise support RAG. Knowledge base-ல் product manual, release notes உள்ளது.

User: "Error code 5032 எப்படி fix பண்ணுவது?"

Retriever ஒரு பழைய doc-ஐ கொண்டு வருகிறது. அதில் fix steps இல்லை. LLM: "Error code 5032 என்பது database connection timeout. Service restart பண்ணவும், connection pool அதிகரிக்கவும்."

இது plausible ஆனால் hallucinated. உண்மையான root cause ஒன்றும் வேறு.

Architectural fix:
1. Retriever confidence score < threshold என்றால் LLM-க்கு context கொடுக்காமல் "இந்த error-க்கு specific doc கிடைக்கவில்லை" என்று சொல்.
2. System prompt-ல் "answer must be supported by provided chunks, include citation [doc_id]" கட்டாயம்.
3. Generated steps-ஐ post-processor-ல் claim extraction + embedding similarity check செய்து, context-ல் support இல்லாத claim-களை redact செய்.

## 7. Reasoning Challenge

உங்கள் RAG system 1000 QPS handle பண்ணுகிறது. Financial report Q&A. Compliance team "ஒவ்வொரு answer-க்கும் source citation தேவை" என்கிறார்கள். Product team "latency 500ms-க்குள் இருக்க வேண்டும்" என்கிறார்கள்.

இந்த இரண்டு constraints-ஐ satisfy பண்ணும் வகையில் hallucination-ஐ manage செய்ய நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Citation generation-ஐ எப்படி enforce பண்ணுவீர்கள்? ஏன்?

## 8. Key Takeaways

* Hallucination என்பது retrieval gap + generation drift இரண்டின் கலவை. Grounding failure தான் core.
* Hallucination-ஐ அழிக்க முடியாது, manage செய்ய முடியும். Trade-off trust vs coverage.
* Strict prompting + citation enforcement + retrieval quality மூன்றும் சேர்ந்தால் தான் production RAG safe ஆகும்.
* Every architectural choice for reducing hallucination adds latency, cost, or reduces answer coverage.
