# Answer relevance

> **Learning Path:** AI Evaluation
> **Section:** 18.2.7 — RAG metrics

## 1. Problem

RAG system build பண்ணியாச்சு. Retriever-ம், LLM-ம் சரியா வேலை செய்யுது. ஆனால் user கேட்கும் கேள்விக்கு answer relevant-ஆ இருக்கா? இல்லை என்றால்?

ஒரு உதாரணம்: User கேட்கிறார் "எங்க company-க்கு refund policy என்ன?". Retriever 3 documents கொண்டு வந்தது. ஒன்று refund policy, ஒன்று shipping policy, ஒன்று old refund policy 2022-ல் மாறியது.

LLM இதை படித்து ஒரு answer generate பண்ணுகிறது. Answer-ல் facts correct-ஆ இருக்கலாம், grammar நன்றாக இருக்கலாம். ஆனால் user கேட்ட specific question-க்கு பதில் இல்லை. Shipping details தேவையில்லாமல் வந்துவிட்டது. Old policy-யும் கலந்துவிட்டது.

இங்கே problem என்ன? Retrieval good, generation good, ஆனால் **answer relevance** கெட்டுபோனது. 

Why does this exist? Because RAG-ல் நாம் evaluate பண்ணும்போது retrieval accuracy மட்டும் பார்த்தால் போதாது. Final answer user-க்கு useful-ஆ இருக்கிறதா என்பது தான் business impact.

## 2. Mental Model

Answer relevance என்பது: **User query + context + generated answer** இந்த மூன்றுக்கும் இடையே உள்ள alignment.

ஒரு service-க்கு API call பண்ணும்போது contract முக்கியம். இங்கே contract என்பது user intent.

Retriever context-ஐ கொடுத்தது. LLM answer-ஐ generate பண்ணியது. Relevance என்பது answer, query-யின் intent-ஐ satisfy பண்ணுகிறதா, context-ல் இருந்து மட்டும் எடுத்து சொல்கிறதா என்பது.

Think of it as: Query is the requirement. Answer is the delivery. Relevance is whether delivery matches requirement.

## 3. How It Works

RAG metrics-ல் relevance-ஐ measure பண்ண பல வழிகள் உள்ளன.

**Human evaluation**: Ground truth answer-ஐ பார்த்து human rater 1-5 scale-ல் rate பண்ணுவார். Reliable ஆனால் slow & costly.

**LLM-as-a-judge**: Reference answer or query-க்கு எதிராக LLM-ஐ use பண்ணி relevance score கொடுக்கச் சொல்வது. Prompt-ல் "Is the answer relevant to the query? Respond Yes/No with reason". Cost குறைவு, fast.

**Retrieval-based signals**: Context-ல் உள்ள sentences-ஐ answer-ல் cover பண்ணியதா? Query keywords answer-ல் appear ஆனதா? இது proxy மட்டுமே.

**Embedding similarity**: Query embedding vs answer embedding cosine similarity. Fast automated, ஆனால் nuance miss ஆகும்.

Practical RAG evaluation-ல் நாம் hybrid பயன்படுத்துகிறோம். Offline benchmark-ல் LLM-as-judge, production-ல் sampled human review.

## 4. Architectural Reasoning

எப்போது relevance முக்கியம்?

* Agent workflow-ல் multiple steps இருக்கும்போது, wrong relevance cascade ஆகும்.
* Customer support RAG-ல் hallucinated relevant answer விட irrelevant correct answer மோசமானது.
* Finance/legal domain-ல் extra information கூட risky.

Constraint இது: LLM generally fluent-ஆ பேசும். Fluent ≠ relevant. Model context-ல் இருக்கும் irrelevant info-யையும் பயன்படுத்தி plausible answer generate பண்ணும்.

Alternative? Retrieval quality improve பண்ணுவது. ஆனால் perfect retrieval கிடையாது. Context window-ல் noise வரும். அதனால் generation stage-ல் relevance enforce பண்ண வேண்டும்.

அதனால் architect-ஆ நாம்:
* Re-ranker use பண்ணி top-k context quality improve
* Prompting-ல் instruction கொடுத்து "answer only what is asked"
* Post-generation check: answer-ல் query entities cover ஆனதா என check

## 5. Trade-offs

**Relevance vs Completeness**: Answer very narrow-ஆ இருந்தால் relevant ஆனால் incomplete. Too broad-ஆ இருந்தால் complete ஆனால் irrelevant info dilute ஆகும்.

**Relevance vs Faithfulness**: Answer context-க்கு faithful ஆக இருக்கலாம், ஆனால் query-க்கு irrelevant. அல்லது query-க்கு relevant ஆனால் context-ல் இல்லாத hallucination. இரண்டும் வேறு metrics.

**Automation vs Accuracy**: LLM-as-judge cheap, ஆனால் bias உண்டு. Human evaluation accurate ஆனால் scale ஆகாது.

Failure mode: Over-retrieval. 10 chunks கொடுத்தால் LLM attention dilute ஆகி core question-ஐ miss பண்ணும். Relevance drop ஆகும்.

## 6. Practical Example

Enterprise knowledge base RAG.

Query: "Q4 2025-ல் sales target எவ்வளவு?"
Retrieved: Q4 2025 target doc, Q3 target doc, annual planning doc.

Good system: Answer = "Q4 2025 sales target 12M USD" + source citation.

Bad relevance: Answer = "Q4 2025-ல் sales target 12M USD. Q3 target 9M USD. Annual planning process..." 

Second answer factually correct, ஆனால் relevance low. User asked one number. Extra info noise.

Metric: LLM-as-judge prompt: "Does answer directly respond to query without extra unrelated info? Score 0-1". Production-ல் நாம் threshold 0.8 set பண்ணி low relevance answers-ஐ flag பண்ணி human review-க்கு அனுப்புவோம்.

## 7. Reasoning Challenge

உங்களிடம் RAG system இருக்கு. User query: "எங்க employee handbook-ல் parental leave policy என்ன?"

Retriever top-3 docs கொடுத்தது: Parental leave policy 2024, Maternity leave 2023, HR contact.

LLM generate பண்ணிய answer: Parental leave policy details + "மேலும் விவரங்களுக்கு HR team-ஐ தொடர்பு கொள்ளவும்" + maternity leave 2023-ல் இருந்த duration.

இங்கே relevance எப்படி measure பண்ணுவீர்கள்? Relevant ஆ? If not, retrieval-ல் பிரச்சனையா, generation-ல் பிரச்சனையா? என்ன fix செய்வீர்கள்?

## 8. Key Takeaways

* Answer relevance என்பது query intent vs final answer alignment. Retrieval quality மட்டும் போதாது.
* Fluent answer ≠ relevant answer. LLM context noise-ஐ use பண்ணி plausible filler add பண்ணும்.
* Evaluate relevance with LLM-as-judge for speed + human sample for ground truth.
* Architectural lever: re-ranking, tighter k, instruction prompting, and post-generation relevance check.
* Relevance trade-off செய்கிறது completeness, faithfulness, and operational cost-உடன்.
