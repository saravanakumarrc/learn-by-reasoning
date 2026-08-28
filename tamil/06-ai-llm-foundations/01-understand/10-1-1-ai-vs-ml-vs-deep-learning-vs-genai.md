# AI vs ML vs Deep Learning vs GenAI

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.1 — Understand

## 1. Problem

உங்களிடம் ஒரு பெரிய e-commerce site இருக்கு. Spam email filter பண்ணணும், product recommendation பண்ணணும், customer query-க்கு பதில் generate பண்ணணும்.

முதல்ல நீங்கள் rule-based system எழுதுவீங்க. `if email contains "free money" then spam`. 

அது வேலை செய்யும்... ஒரு காலத்துக்கு. New spam patterns வந்துடும். Rules எழுதுவது, maintain பண்ணுவது பெரிய overhead ஆகும். Data pattern மாறும்போது system மெதுவாக fail ஆகும்.

இங்கே வரும் core pain: **நாம் மனிதர்களுக்கு எளிதாக தெரியும் patterns-ஐ code-ல hardcode பண்ண முடியாது.** Scale ஆகும்போது இது painful ஆகும்.

## 2. Mental Model

இதை ஒரு hierarchy-ஆக பாருங்கள், definition அல்ல.

**AI** = broad goal. Machine human-like tasks பண்ணுவது. Reasoning, perception, decision making. 

**ML** = AI-க்கு ஒரு approach. Explicit rules கொடுக்காமல், data-ல இருந்து pattern கற்றுக்கொள்ளும். Model train பண்ணி, inference பண்ணுவது.

**Deep Learning** = ML-ன் ஒரு subset. Neural network with multiple layers. Feature engineering-ஐ model-க்குள்ளே automate பண்ணும்.

**GenAI** = capability, not just technique. Train செய்யப்பட்ட model-ஐ input-க்கு புதிய content generate செய்ய பயன்படுத்துவது. Text, image, code, speech. இதற்கு பெரும்பாலும் large Deep Learning models தேவை.

சுருக்கமாக: AI > ML > Deep Learning. GenAI என்பது ML/Deep Learning-ஐ use செய்து generation பண்ணும் use case.

## 3. How It Works

Rule-based: human writes logic.

ML: நீங்கள் examples கொடுங்கள். Model parameters-ஐ data-க்கு fit ஆக adjust பண்ணும். Supervised, unsupervised, reinforcement learning என variants இருக்கும்.

Deep Learning: Input-ஐ raw data-வாக கொடுக்கலாம். Images, text tokens. Network-ன் layers தானாக intermediate features கண்டுபிடிக்கும். More data, more compute தேவை.

GenAI: பெரிய pre-trained model-ஐ fine-tune or prompt செய்து, புதிய output generate பண்ணுவது. LLM, diffusion model இதன் உதாரணம்.

## 4. Architectural Reasoning

எப்போது என்ன தேவை?

**AI** என்பது goal. எந்த system-லும் நீங்கள் AI technique use பண்ணலாம்.

**ML** தேவைப்படும் போது: உங்களுக்கு historical data இருக்கு, pattern repeat ஆகுது, but rule எழுத கஷ்டம். உதாரணம்: fraud detection, churn prediction, recommendation.

Constraint: labeled data இருக்க வேண்டும், அல்லது unsupervised pattern கண்டுபிடிக்கும் தேவை.

**Deep Learning** தேவைப்படும் போது: data volume மிக அதிகம், feature engineering manual-ஆக செய்ய முடியாது. Image classification, speech recognition, NLP.

Trade: compute கூடும், model interpretability குறையும்.

**GenAI** தேவைப்படும் போது: user wants creative, personalized output. Summarization, code generation, chatbot, content creation.

இது உங்களுக்கு reasoning, context understanding வேண்டும். Pre-trained foundation model தேவை.

## 5. Trade-offs

**Data vs Rules:** ML/Deep Learning data தேவை. Data இல்லாமல் rules மட்டுமே போதும். Data quality கெட்டால் model fail.

**Interpretability vs Accuracy:** Classical ML models ஓரளவு explainable. Deep Learning black box. GenAI இன்னும் அதிகம்.

**Latency & Cost:** Simple ML model inference cheap. Large LLM inference expensive, latency அதிகம். Production-ல caching, distillation, smaller model பயன்படுத்த வேண்டும்.

**Hallucination & Safety:** GenAI generate செய்யும். Factually wrong output தரும். RAG, guardrails, human-in-the-loop தேவை.

## 6. Practical Example

E-commerce platform.

**Recommendation engine:** user history, purchase pattern இருந்து next product predict பண்ணணும். இது classic ML/Deep Learning problem. Training data அதிகம் இருக்கு. Real-time latency தேவை. Lightweight model, embeddings + nearest neighbor.

**Product description generation:** New SKU வந்தது, marketing team-க்கு 10 variants description வேண்டும். Human writing slow. GenAI model-ஐ use செய்து, product specs input கொடுத்து generate பண்ணலாம். Quality check தேவை.

ஒரே system-ல இரண்டும் இருக்கும். ஒன்று prediction, ஒன்று generation.

## 7. Reasoning Challenge

உங்களிடம் limited labeled data ~5k samples, need credit card fraud classification, latency <50ms, explainability audit-க்கு தேவை. Deep Learning model vs Gradient Boosted Trees எது தேர்வு செய்வீங்க? ஏன்? GenAI எங்கே fit ஆகும்?

## 8. Key Takeaways

* AI என்பது goal, ML என்பது data-driven approach, Deep Learning என்பது ML-ன் powerful subset, GenAI என்பது generation capability.
* Rule-based brittle. Data patterns repeat ஆனால் ML useful.
* Deep Learning feature engineering-ஐ automate பண்ணும், ஆனால் data, compute, opacity அதிகம்.
*
