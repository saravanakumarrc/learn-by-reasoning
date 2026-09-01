# Evaluation platform

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.10 — Enterprise patterns

## 1. Problem

உங்க team RAG system-ஐ build பண்ணிட்டு இருக்கு. LLM agent-கள் deploy ஆகுது. 

பிரச்சனை என்ன? Model-ஐ மாற்றினால் quality மாறும். Prompt-ஐ tweak பண்ணினால் output மாறும். Retrieval top-k மாற்றினால் hallucination மாறும்.

Production-ல போடுவதற்கு முன் இதை எப்படி தெரிஞ்சுக்குவீங்க? Manual testing பண்ண முடியாது. 50 prompts-க்கு 5 engineers review பண்ணினாலும் coverage கிடைக்காது. Regression வரும். Stakeholder-க்கு confidence இருக்காது.

What goes wrong if we don't have evaluation? Ship பண்ணிட்டு தான் தெரியும். அப்போது cost அதிகம்.

## 2. Mental Model

Evaluation platform = **test suite for AI behavior**.

Software-ல unit test, integration test இருக்கிற மாதிரி, LLM system-க்கு நமக்கு golden data, metrics, automated judges வேணும்.

Core idea: **Non-functional requirements-ஐ measurable ஆக்குறது**. Correctness, relevance, safety, latency, cost.

Evaluation platform என்பது data, harness, metrics, dashboard, regression tracking-ஐ ஒன்றாக கட்டுப்படுத்தும் system.

## 3. How It Works

Minimal loop:

**Dataset → Run → Judge → Metric → Track**

1. **Dataset**: Test cases. Real user queries, synthetic prompts, edge cases. Inputs + expected behavior.
2. **Run**: Harness invokes your system: API, RAG pipeline, agent. Capture inputs, retrieved docs, intermediate steps, final output, latency, tokens.
3. **Judge**: Score output. Rule-based, LLM-as-judge, or human review.
4. **Metric**: Accuracy, faithfulness, relevance, F1, ROUGE, custom business metric.
5. **Track**: Results versioned per model/prompt/config. Regression visible.

Offline eval for PRs, online eval for production traffic sampling.

## 4. Architectural Reasoning

எப்போது useful?

* Multiple models, prompts, retrieval configs compare பண்ணும் போது
* RAG pipeline-ல retriever vs reranker vs prompt change impact தெரிய வேண்டும்
* Agent tool use correctness தேவை
* Safety / policy violation தடுக்க வேண்டும்

Constraint it addresses: **non-deterministic system-ல repeatable quality signal**.

Alternatives:

* Manual spot check → cheap start, doesn't scale, no regression
* Ad-hoc notebook eval → fast, not reproducible, no CI
* Production monitoring only → too late, no A/B safety

Architect choose evaluation platform when quality is a first-class requirement and system evolves fast.

## 5. Trade-offs

**LLM-as-judge vs human judge**
LLM judge cheap, fast, consistent. But bias, self-preference. Human judge ground truth, expensive, slow. Real systems mix: LLM filter + human review for high-risk.

**Offline vs online**
Offline gives controlled comparison. Online gives real user distribution. Both needed. Offline for pre-release, online for drift.

**Coverage vs cost**
More test cases = better signal. More cases = more compute cost, latency. Need curated core set + sampled production.

**Generic metrics vs business metric**
BLEU/ROUGE easy but often misleading. Faithfulness, citation accuracy more useful but harder to compute. Trade-off between easy signal and real value.

Failure modes: Dataset leakage, judge overfitting, metric gaming. If you optimize for metric, system may cheat metric but not user value.

## 6. Practical Example

Enterprise support RAG.

System: User query → retrieval from knowledge base → LLM answer with citations.

Evaluation platform setup:

* Dataset: 500 real support tickets + 100 synthetic edge cases like ambiguous queries, outdated docs.
* Metrics: Retrieval Recall@5, Answer relevance, Faithfulness to source, Citation presence, Hallucination rate, Latency P95.
* Run: Each PR triggers offline eval against baseline. Model A vs Model B, top-k 5 vs 10.
* Regression gate: Faithfulness drop >2% → block merge.
* Online: 5% production traffic sampled, logged, weekly human review for safety.

Result: Prompt change improved relevance but dropped faithfulness. Caught before release.

## 7. Reasoning Challenge

உங்களிடம் 3 different LLM models உள்ளது. Prompt version 2 உள்ளது. Retrieval top-k 5 vs 10 test பண்ணுகிறீர்கள். Budget மட்டுப்படுத்தப்பட்டுள்ளது.

Eval platform-ல நீங்கள் எந்த metrics-ஐ primary ஆக்குவீர்கள்? Offline eval-ல எத்தனை test cases போதும்? Production-ல எந்த signal-ஐ alert-க்கு use பண்ணுவீர்கள்?

Why?

## 8. Key Takeaways

* Evaluation platform என்பது AI system-க்கான CI/CD quality gate.
* Metrics without ground truth and versioning என்பது noise.
* Offline eval for comparison, online eval for reality.
* Optimize for business-relevant metrics, not generic scores.
* Every eval design is a trade-off between cost, speed, and trust.
