# Agentic RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.3 — RAG architecture

## 1. Problem

உங்க RAG system இப்போ இப்படி இருக்கு: User query வருது → embedding → vector database-ல search → top-k chunks எடுத்து LLM-க்கு கொடுக்கிறோம் → answer.

இது simple questions-க்கு work ஆகும். ஆனா real world-ல என்ன நடக்கும்?

User கேட்கிறார்: "கடந்த காலாண்டில் எங்கள் top 5 customers-க்கு revenue எவ்வளவு, அவர்களுக்கு தள்ளுபடி தர முடியுமா?"

இதுக்கு ஒரே retrieval போதாது. 

* எந்த customers top 5? அதுக்கு database query வேண்டும்.
* revenue calculate பண்ண வேண்டும்.
* discount policy எந்த doc-ல இருக்கு?
* அதை cross-check பண்ணி reason பண்ணி final answer கொடுக்க வேண்டும்.

Single round retrieval + generation-ல பதில் துல்லியமாக வராது. Hallucination வரும். Wrong context தரும்.

**Problem என்ன?** Query simple இல்ல. Multi-step reasoning, multiple data sources, tool use, self-correction வேண்டும். Static RAG-க்கு இது painful.

## 2. Mental Model

Agentic RAG = RAG + Agent loop.

Classic RAG ஒரு தடவை search பண்ணி answer கொடுக்கும்.

Agentic RAG ஒரு **reasoning agent**-ஐ உள்ளே வைக்கும். அந்த agent தான்:

1. Plan பண்ணும்: என்ன தேவை?
2. Retrieve பண்ணும்: vector DB, SQL DB, API call
3. Reason பண்ணும்: கிடைச்ச info போதுமா?
4. Iterate பண்ணும்: இல்லைன்னா மறுபடி retrieve / query
5. Final answer synthesize பண்ணும்

Mental model: LLM ஒரு ப்ரொக்ராமர் மாதிரி, tools = retrieval, calculator, database, web search. Agent loop = while not satisfied do step.

## 3. How It Works

ஒரு typical flow:

**Query → Planner Agent → Decompose**

User: "Q3-ல churn ஆன customers யார், அவர்களுக்கு காரணம் என்ன?"

Agent plan:
* Step1: churn customers list எடு. Source: customer DB.
* Step2: அவர்களின் support tickets / feedback எடு. Source: vector DB.
* Step3: pattern summarize பண்ணு.

**Loop:**
1. Agent decides which tool use பண்ணணும். `tool = database_query` or `tool = vector_search`
2. Tool execute ஆகும், result திரும்ப வரும்
3. Agent result-ஐ analyze பண்ணி, போதுமானதா? இல்லைன்னா next query formulate பண்ணும்
4. Max iterations வரை continue
5. இறுதியில் grounded answer + citations

Key components:
* **LLM as reasoner / planner**
* **Toolset**: vector DB retriever, SQL executor, API caller, calculator
* **Memory / context window**: previous steps-ஐ remember பண்ணும்
* **Re-ranking / reflection**: answer quality check

## 4. Architectural Reasoning

இது எப்போ useful?

* Multi-hop questions
* Need structured data + unstructured data mix
* Need multiple retrievals with different filters
* Need tool use: calculation, DB aggregation, web search

Constraint இது address பண்ணுது: **One-shot retrieval limit**

Alternatives:
* **Classic RAG**: Fast, cheap, predictable. Simple factual lookup-க்கு போதும்
* **Agentic RAG**: Slow, expensive, but handles complex reasoning
* **Graph RAG / Hybrid RAG**: Better for relationships, but static

Architect choose agentic when:
* Accuracy > latency
* Question complexity high
* Data scattered across sources
* Need audit trail and citations

Trade-off is clear: You gain flexibility and accuracy, you lose latency and cost.

## 5. Trade-offs

**Latency vs Accuracy**
Agent loop ஒவ்வொரு iteration-க்கும் LLM call + tool call. 3-5 steps ஆகலாம். Classic RAG 1 step. Production-ல p95 latency முக்கியம்.

**Cost vs Quality**
LLM tokens + tool calls அதிகம். Rate limiting, cost per query jump ஆகும்.

**Control vs Hallucination**
Agent தான் plan பண்ணும். Bad plan = bad retrieval. Tool selection wrong ஆனால் garbage in garbage out. Need guardrails.

**Operability**
Debugging கடினம். Why agent அந்த tool-ஐ தேர்ந்தெடுத்தது? Reproducibility குறையும். Logging, tracing, step-by-step audit வேண்டும்.

Failure mode: Infinite loop / tool misuse. Agent திரும்ப திரும்ப same query பண்ணும். Max iterations, reflection prompt, tool output validation வேண்டும்.

## 6. Practical Example

Enterprise support chatbot.

User: "நான் order #12345-க்கு refund request பண்ணினேன். Status என்ன? Policy-க்கு ஏற்ப approve ஆகுமா?"

Agentic RAG flow:
1. Agent parses order id. `tool = order_service_api` call பண்ணி order status, amount, date எடுக்கும்
2. User history எடுக்க `tool = CRM DB query`
3. Refund policy doc retrieve பண்ண `tool = vector_search` with filter: refund policy
4. Agent reason பண்ணும்: order date 45 days ago → policy says 30 days window. So reject likely.
5. Final answer: "Order shipped, refund requested 10 days ago, pending. Policy per 30 days window, your order outside window, so likely reject. Escalate?"

Classic RAG இதை துல்லியமாக பண்ண முடியாது.

## 7. Reasoning Challenge

உங்களுக்கு இருக்கு: internal knowledge base + customer SQL DB + billing API.

User query: "மார்ச் மாதத்தில் revenue அதிகரித்த top 3 products-ஐ காட்டு, அவற்றிற்கான marketing spend எவ்வளவு?"

இங்கே agent என்ன steps எடுக்கும்? எந்த tools தேவை? எங்கே hallucination வரலாம்? இந்த design-ஐ நீங்கள் எப்போது பயன்படுத்துவீர்கள், எப்போது classic RAG-ஐயே stick பண்ணுவீர்கள்?

## 8. Key Takeaways

* Agentic RAG = RAG + planning + iterative tool use. One-shot retrieval-க்கு மேல் தேவையானதற்கு
* Problem solve பண்ணுது: multi-hop, multi-source, reasoning-required queries
* Cost & latency trade-off உண்டு. Complexity-க்கு ஏற்றவாறு use பண்ண வேண்டும்
* Agent control, guardrails, tracing இல்லாமல் production-ready ஆகாது
