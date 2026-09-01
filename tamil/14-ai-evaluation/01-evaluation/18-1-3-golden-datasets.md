# Golden datasets

> **Learning Path:** AI Evaluation
> **Section:** 18.1.3 — Evaluation

## 1. Problem

உங்க team ஒரு LLM-based agent பண்ணுது. Retrieval, tool calling, response generation எல்லாம் சரியா வேலை செய்யுது. 

Production-ல போட்டதும் எதிர்பாராத முடிவுகள் வருது. பழைய model-க்கு fine-tune பண்ணினோம், metrics improve ஆகுதுன்னு தோணுது. ஆனா உண்மையில் user experience மோசமாகுது.

**என்ன பிரச்சனை?** Model சரியா work பண்ணுதா இல்லையான்னு தெரியல. Evaluation எப்படி பண்ணுறீங்க? Random prompts வச்சு manual check பண்ணீங்கன்னா அது inconsistent. LLM-as-judge வச்சீங்கன்னா அது ஒரு model இன்னொரு model-ஐ judge பண்றது - bias வரும்.

உங்களுக்கு ஒரு **ground truth** வேணும். அது இல்லாம regression-ஐ பிடிக்க முடியாது, model update safe-ஆ release பண்ண முடியாது.

அதான் Golden dataset தேவை.

## 2. Mental Model

Golden dataset = **நீங்கள் நம்பும் சரியான answers உடன் கூடிய, curated input-output pairs**.

இது ஒரு reference standard மாதிரி. Model-இன் output-ஐ இதோட compare பண்ணி objective score கிடைக்கும்.

எளிய analogy: Driving test-ல examiner-க்கு ஒரு answer key இருக்கும். Student-இன் answer-ஐ அதோட compare பண்ணுவாங்க. Golden dataset அந்த answer key.

இது static இல்ல. Domain, task, quality bar மாறும்போது grow ஆகும்.

## 3. How It Works

Golden dataset என்பது மூன்று பாகங்கள்:

**1. Prompt / Input**: Realistic, representative queries. Production logs-ல இருந்து sample எடுக்கலாம். Edge cases-ம் கலக்கணும்.

**2. Expected Output / Ground Truth**: Human expert அல்லது highly trusted process-ஆல் verify செய்யப்பட்ட correct answer. RAG-க்கு expected citations, agents-க்கு expected tool calls, structured output-க்கு expected JSON schema.

**3. Metadata**: Why this is important, difficulty level, category, failure mode it tests.

Evaluation flow:
`Model output → Compare with Golden expected output → Score using exact match / semantic similarity / rubric`

இது offline evaluation-க்கு உதவும், மற்றும் CI pipeline-ல regression guard ஆக இயங்கும்.

## 4. Architectural Reasoning

Golden dataset எப்போது useful?

* Model iteration-ல regression catch பண்ண வேண்டும்
* Prompt change, retrieval change, tool change impact measure பண்ண வேண்டும்
* Release gate வைக்க வேண்டும்: score drop > X% என்றால் block release
* Different model versions, temperature, retrieval configs ஒப்பிட வேண்டும்

Alternative என்ன?
* LLM-as-judge: flexible, cheap, ஆனால் non-deterministic, bias உண்டு
* Human evaluation: accurate, ஆனால் slow & expensive
* Synthetic benchmarks: MMLU, GSM8K போன்றவை - generic, domain-specific nuance இல்லை

Architect decision: Golden dataset என்பது **costly to build, cheap to run**. முக்கியமான critical paths-க்கு மட்டும் maintain பண்ணுங்க. அதை தான் evaluation backbone ஆக்குங்க. LLM-as-judge-ஐ exploratory analysis-க்கு use பண்ணுங்க.

## 5. Trade-offs

**Coverage vs Maintenance cost**: 1000 golden examples maintain பண்ணுவது கஷ்டம். Data drift ஆனால் stale ஆகும். Small but high-value set maintain பண்ணுவது better.

**Exact match vs Semantic equivalence**: Payment amount "1000" vs "₹1000" - exact match fail ஆகும். Rubric based scoring, normalization தேவை.

**Static vs Living**: Golden set static ஆக இருந்தால் model அதற்கு overfit ஆகும். Production failures-ல இருந்து continuously add பண்ணி evolve பண்ணணும்.

**Human gold vs Synthetic gold**: Human gold expensive but trustworthy. Synthetic gold cheap ஆனால் model bias propagate ஆகும். Hybrid approach common: human review synthetic data.

Failure mode: Golden dataset-ல bias இருந்தால், அது model-ஐ அந்த bias-க்கு push பண்ணும். Diversity குறைவாக இருந்தால் false confidence கொடுக்கும்.

## 6. Practical Example

Banking chatbot. RAG + tool calling agent.

Golden dataset-ல 150 examples:

* `Input`: "என் last 3 transactions காட்டு"
  `Expected`: tool call `get_transactions(user_id, limit=3)` + summary
  `Metadata`: category=tool_use, difficulty=low

* `Input`: "loan EMI எவ்வளவு?"
  `Expected`: retrieve policy doc, cite section 4.2, no hallucination
  `Metadata`: category=citation, difficulty=medium

Every PR-ல CI run: model output vs golden set → precision, recall, tool call accuracy, citation accuracy. Score < 92% என்றால் block merge.

Production-ல weekly new failure cases collect பண்ணி golden set-க்கு add பண்ணுவாங்க. இப்படி living benchmark ஆகிறது.

## 7. Reasoning Challenge

உங்களிடம் RAG system உள்ளது. Golden dataset-ல 200 questions உள்ளது, 90% accuracy உள்ளது. New model version-ல 92% accuracy வந்தது, ஆனால் production support tickets 15% increase ஆனது.

என்ன problem இருக்கலாம்? Golden dataset-ஐ எப்படி improve பண்ணுவீர்கள்? Exact match scoring போதுமா?

## 8. Key Takeaways

* Golden dataset என்பது trusted ground truth, regression கண்டுபிடிக்கும் reference standard
* Build it from real production queries + edge cases, human verified
* Use it for automated offline evaluation and release gating, not for ad-hoc exploration
* Keep it small, high-quality, living, and diverse; trade-off is maintenance cost vs confidence
* Every architectural decision creates trade-off: coverage vs cost, static vs living, exact vs semantic
