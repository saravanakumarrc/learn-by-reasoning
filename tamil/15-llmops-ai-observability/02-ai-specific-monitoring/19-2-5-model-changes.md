# Model changes

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.5 — AI-specific monitoring

### 1. Problem

உங்க production-ல ஒரு LLM-powered service ஓடிக்கொண்டிருக்கு. RAG pipeline, agent, அல்லது classification service எதுவாக இருந்தாலும் சரி.

ஒரு நாள் users சொல்றாங்க: "output quality முன்னைவிட மோசமா இருக்கு". அல்லது latency spike ஆகுது. அல்லது cost ஏறிடுச் சு.

நீங்கள் என்ன செய்வீர்கள்? Traditional monitoring-ல CPU, memory, request latency, error rate எல்லாம் fine ஆக காட்டும். ஆனால் model-ன் behavior மாறிடுச்சு.

இதுதான் **model changes** என்ற AI-specific monitoring பிரச்சனை. Code மாறாமலே output மாறும். Why? Model version மாறியிருக்கலாம், prompt மாறியிருக்கலாம், retrieval data மாறியிருக்கலாம், temperature/top-p மாறியிருக்கலாம், upstream API change ஆகியிருக்கலாம்.

What goes wrong if we don't have this? Silent degradation. Business metric மோசமாகும், user trust போகும், நீங்கள் root cause-ஐ கண்டுபிடிக்க நாட்கள் எடுக்கும்.

### 2. Mental Model

Model changes monitoring என்பது **model-ஐ ஒரு living component ஆக treat பண்ணுவது**. Code deploy பண்ணும்போது version pin பண்ணுவது போல, model behavior-ஐயும் pin பண்ணி observe பண்ணணும்.

நீங்கள் monitor பண்ணுவது 3 layers:
* **Input layer**: prompt, context, retrieved documents, user features
* **Model layer**: model version/id, parameters, provider, latency, token usage
* **Output layer**: generated text, scores, classifications, embeddings drift

Model change என்பது இந்த மூன்றில் எதாவது மாறுவதுதான்.

### 3. How It Works

ஒவ்வொரு request-க்கும் நீங்கள் metadata-ஐ log பண்ணுறீங்க.

```
request_id, timestamp, user_id, prompt_hash, system_prompt_version, model_name, model_version, temperature, retrieved_doc_ids, top_k, output_text, output_tokens, latency_ms, cost, evaluation_score
```

இதை ஒரு observability store-ல வைக்கிறீங்க. பிறகு:

* **Version tagging**: ஒவ்வொரு inference call-க்கும் model version, prompt version, retrieval index version ஆகியவற்றை tag பண்ணுங்கள்.
* **Golden dataset**: நிலையான 100-500 test prompts. ஒவ்வொரு deploy-க்கும் இவற்றின் output distribution-ஐ compare பண்ணுங்கள்.
* **Drift detection**: Input embedding distribution, output quality metrics, latency/cost distribution மாற்றத்தை statistical test-ல பிடிக்கிறோம்.

பெரும்பாலான teams இதை LLM observability tools-ல செய்வார்கள்: LangSmith, Arize, Langfuse, Phoenix. அவை trace, span, evaluation, drift dashboard கொடுக்கும்.

### 4. Architectural Reasoning

இது எப்போ useful?

* Model provider silent update பண்ணும்போது. OpenAI `gpt-4o-2024-08-06` -> `gpt-4o-2024-11-20` போல.
* உங்க own fine-tuned model-ஐ retrain பண்ணி roll out பண்ணும்போது.
* Prompt engineering மாற்றங்கள், system prompt A/B test.
* RAG-ல vector database அல்லது knowledge base update ஆகும்போது.
* Temperature, max tokens, retry policy மாறும்போது.

Constraint இது: LLM output non-deterministic. Same input-க்கு வெவ்வேறு output வரலாம். அதனால் exact match monitoring பயன்படாது. Distribution-level monitoring தேவை.

Alternative: வெறும் business metrics மட்டும் பார்ப்பது. Conversion, user rating. அது lagging indicator. Root cause தெரியாது.

### 5. Trade-offs

* **Observability vs Cost**: ஒவ்வொரு request-ன் full prompt/output-ஐ store பண்ணுவது expensive. PII, cost, storage. Sampling, summarization, retention policy வேண்டும்.
* **Sensitivity vs Noise**: Drift threshold குறைவாக வைத்தால் false alarm அதிகம். அதிகமாக வைத்தால் real degradation miss ஆகும்.
* **Granularity vs Operability**: Request level trace வைப்பது நல்லது, ஆனால் dashboard overload ஆகும். Model version, prompt version குறுக்கே aggregate பண்ணுவது முக்கியம்.
* **Privacy vs Debugging**: Real user prompts-ஐ log பண்ணுவது debug-க்கு உதவும் ஆனால் privacy risk. Anonymization, masking தேவை.

Failure mode: Model version change ஆனால் monitoring-ல tag இல்லாமல் போனால், நீங்கள் அதை model drift ஆகவே நினைப்பீர்கள்.

### 6. Practical Example

ஒரு enterprise support agent உள்ளது. RAG + LLM. Model = `gpt-4o`, prompt version `v3.2`, index version `kb-2025-09-01`.

நீங்கள் daily golden set-ல 200 customer queries-ஐ run பண்ணி:
* Answer relevance score
* Factuality score
* Latency p95
* Token cost per query

ஒரு நாள் relevance score 0.82 -> 0.71 குறைந்தது. Dashboard-ல model version tag பார்த்தால் provider `gpt-4o` internal version `2024-08-06` to `2024-11-20` மாறியிருக்கு. Prompt மாறல, index மாறல.

நீங்கள் canary rollout: 10% traffic-ஐ பழைய model version-க்கு திருப்பி score restore ஆகிறதா பார்க்கிறீர்கள். ஆகிறது. அப்போது decision clear: provider model change தான் root cause. நீங்கள் prompt adaptation அல்லது model pin செய்யலாம்.

### 7. Reasoning Challenge

உங்கள் RAG system-ல knowledge base refresh ஆகிறது every week. உங்கள் retrieval recall மெதுவாக குறைந்து வருகிறது. ஆனால் LLM latency, error rate normal.

இதை detect செய்ய நீங்கள் எந்த signals-ஐ track செய்வீர்கள்? Model version மட்டும் போதுமா? அல்லது retrieval layer-க்கு தனி versioning & drift monitoring வேண்டுமா? ஏன்?

### 8. Key Takeaways

* Model behavior மாறும், code மாறாமலே. அதை version & tag செய்யாமல் monitor செய்ய முடியாது.
* Monitor input, model, output ஆகிய மூன்று layers-ஐயும், distribution level-ல.
* Golden dataset + automated evaluation = early warning for silent degradation.
* ஒவ்வொரு architectural change-க்கும் trade-off உண்டு: observability cost vs debugging speed.
