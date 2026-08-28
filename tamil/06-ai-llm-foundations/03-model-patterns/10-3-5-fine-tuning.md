# Fine-tuning

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.5 — Model patterns

## 1. Problem

உங்களிடம் ஒரு general purpose LLM இருக்கு. அது broad knowledge பேசும். ஆனால் உங்கள் company-க்கு தேவை: banking domain-ல் குறிப்பிட்ட terminology-ல் பதில் சொல்லணும், internal policy-க்கு align ஆகணும், tone formal ஆக இருக்கணும்.

Prompt engineering மூலம் சில தூரம் போகலாம். ஆனால் பிரச்சனை என்ன?

* Every prompt-ல் context பெரிதாகும், latency அதிகம்
* Same instructions ஒவ்வொரு முறையும் repeat செய்ய வேண்டும்
* Model தவறாக பழைய habit-க்கு போய்விடும்
* Sensitive data-வை prompt-ல் கொடுக்க விரும்ப மாட்டீர்கள்

இங்கே தான் **Fine-tuning** தேவைப்படுகிறது. Model-ஐ உங்கள் data-க்கு ஏற்ப "train" செய்து, behavior-ஐ permanent ஆக மாற்றுவது.

> What problem became painful? Prompting is not enough for consistent style, domain knowledge, and privacy.

## 2. Mental Model

Fine-tuning என்பது model-ஐ pre-training போல் பெரிய dataset-ல் மீண்டும் train செய்வது இல்லை. அது அடிப்படை weights-ஐ பாதுகாத்து, உங்கள் specific task-க்கு adapt செய்வது.

எளிய analogy: ஒரு experienced engineer-க்கு new company-க்கு onboarding. அவர் coding தெரியும். Company coding standards, internal libraries, domain terms மட்டும் கற்றுக்கொள்ள வேண்டும். முழு கம்ப்யூட்டர் சயின்ஸ் மீண்டும் கற்றுக்கொள்ள வேண்டாம்.

Fine-tuning = domain adaptation with small, high-quality dataset.

## 3. How It Works

Base model already has general language understanding. Fine-tuning-ல் நீங்கள் provide செய்வது:

* **Instruction-response pairs** : `prompt -> expected output`
* **Completion examples** : specific style, tone, format
* **Domain text** : technical docs, internal FAQs, customer tickets

Training objective simple ஆக இருக்கும்: model input-ஐ பார்த்து expected output-ஐ predict செய்ய கற்றுக்கொள்ளும். Learning rate மிகவும் குறைவாக இருக்கும், அதனால் base knowledge forget ஆகாது.

Variants உள்ளன:
* **Full fine-tuning** : all weights update. Expensive, powerful.
* **Parameter-Efficient Fine-Tuning** : LoRA, QLoRA. Small adapter weights மட்டும் train செய்யும். Cost குறைவு, base model safe.

Fine-tuned model-ஐ deploy செய்த பிறகு prompt-ல் system instruction தேவை குறைகிறது. Model தானாக உங்கள் style-ல் பதில் செய்யும்.

## 4. Architectural Reasoning

Fine-tuning எப்போது useful?

* **Consistent style & tone** தேவைப்படும் customer-facing chatbot
* **Domain-specific language** : legal, medical, finance terminology
* **Task-specific format** : always output JSON with specific schema
* **Reduced prompt cost** : large context window தேவையில்லை

Alternatives என்ன?

* **Prompt engineering + RAG** : Knowledge external ஆக வைக்கலாம். Real-time update சுலபம். ஆனால் model behavior மாறாது.
* **In-context learning** : few-shot examples. Quick, zero training. ஆனால் consistency குறைவு.
* **Retrieval-Augmented Generation** : dynamic knowledge. Fine-tuning static knowledge.

ஆர்கிடெக்ட் எப்போது fine-tune செய்ய முடிவு செய்வார்?
Knowledge frequently change ஆகாது, மற்றும் style consistency critical ஆக இருந்தால். உதாரணமாக internal support agent, குறிப்பிட்ட tone-ல் பேச வேண்டும்.

## 5. Trade-offs

**1. Cost vs Control**
Fine-tuning-க்கு GPU time, data curation, evaluation தேவை. ஆனால் inference-ல் prompt tokens குறைகிறது, latency குறைகிறது.

**2. Static vs Dynamic**
Fine-tuned model-ஐ update செய்ய மீண்டும் train செய்ய வேண்டும். RAG-ல் data மாற்றினால் உடனே reflect ஆகும். Hybrid approach பொதுவானது: fine-tune for style, RAG for facts.

**3. Catastrophic forgetting & Overfitting**
Dataset சிறியதாக இருந்தால் model overfit ஆகும். Unseen prompts-ல் weird behavior. Base knowledge degrade ஆகலாம். Good validation set, diverse examples தேவை.

**4. Privacy & Security**
Fine-tuning data model weights-ல் embed ஆகிறது. Sensitive data leak ஆகும் risk உண்டு. Data sanitization, PII removal முக்கியம்.

Failure mode: உங்கள் dataset biased ஆக இருந்தால், model அந்த bias-ஐ amplify செய்யும்.

## 6. Practical Example

Enterprise banking chatbot.

Problem: Customers-க்கு loan eligibility, KYC process பற்றி கேட்கிறார்கள். Responses always formal Tamil/English mix, must not give legal advice, must use internal terms like "CIF ID", "KYC re-KYC".

Option A: Prompt + RAG. Works, but every response-ல் 4k token system prompt + policy. Latency high, cost high, occasional tone drift.

Decision: Small LoRA adapter fine-tune on 5k curated Q&A from internal support tickets + policy docs. Keep RAG for current interest rates.

Architecture:
`User Query -> RAG retriever -> Fine-tuned LLM with RAG context -> Output validator -> Response`

Result: Model automatically uses formal tone, correct terminology, never invents policy. Inference cost 30% குறைந்தது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு multilingual customer support bot உள்ளது. தமிழ், ஆங்கிலம் இரண்டிலும் ஆதரிக்க வேண்டும். Product catalog weekly update ஆகிறது. Brand voice strict ஆக இருக்க வேண்டும்.

Fine-tuning மட்டும் செய்யலாமா? RAG மட்டும் செய்யலாமா? அல்லது இரண்டும் சேர்ந்து? ஏன்?

## 8. Key Takeaways

* Fine-tuning என்பது behavior-ஐ permanent ஆக மாற்றுவது, knowledge-ஐ inject செய்வது அல்ல.
* Use it for style, tone, task format consistency. Use RAG for dynamic facts.
* Small high-quality dataset > large noisy dataset. Overfitting தவிர்க்க validation முக்கியம்.
* Every fine-tune is a trade-off: you gain consistency, you lose flexibility and incur training cost.
