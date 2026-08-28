# Context compression

> **Learning Path:** RAG Architecture
> **Section:** 12.1.16 — Learn

## 1. Problem

உங்க RAG system-ல user question கேட்டதும், retriever 10-15 chunks எடுத்து LLM-க்கு கொடுக்கிறீங்க. அது சரி.

ஆனால் real world-ல documents நீளமா இருக்கும். Legal contract, support ticket thread, research paper. ஒரு query-க்கு 20 chunks = 20k tokens. LLM context window 128k என்றாலும், அது எல்லாம் relevant இல்ல.

Problem என்ன?
1. **Irrelevant noise** உள்ளே வருது. LLM confuse ஆகுது, hallucination அதிகம்.
2. **Cost & latency** பெருகுது. Token அதிகம் = money அதிகம், latency அதிகம்.
3. **Context window waste** ஆகுது. உண்மையில் தேவையான 2-3 sentences மறைந்து போகுது.

இங்கே தான் context compression தேவைப்படுது. Retrieve பண்ணியதை மட்டும் தூக்கி கொடுக்காம, **query-க்கு உண்மையில் தேவையான தகவலை மட்டும் சுருக்கி, தெளிவாக்கி** கொடுக்கணும்.

## 2. Mental Model

Context compression என்பது filter இல்லை. Filter என்பது whole chunk-ஐ வைத்துக்கொள்வது அல்லது தூக்கி எறிவது.

Compression என்பது: **"இந்த chunk-ல இருக்கும் தகவலை query-க்கு ஏற்ப rephrase / summarize / extract பண்ணி, noise-ஐ அகற்றி, signal-ஐ மட்டும் tight ஆக கொடு"**.

அனலாகி: ஒரு 50 பக்க report-ஐ முழுவதும் LLM-க்கு கொடுக்காம, நீங்களே முக்கியமான 3 புள்ளிகளை extract பண்ணி சொல்வது.

## 3. How It Works

Typical RAG pipeline-ல compression இரண்டு இடத்தில் வரும்:

**Retrieve → Compress → Generate**

1. **Query-aware summarization:** Retrieved chunks-ஐ எடுத்து, "user query-க்கு பதில் கொடுக்க தேவையான பகுதி மட்டும்" என்ற instruction-உடன் LLM-ஆல் summarize பண்ணுது.
2. **Extractive compression:** Chunk-ல இருந்து query-relevant sentences மட்டும் pick பண்ணுது. Sentence embeddings + similarity score வைத்து top sentences எடுக்கலாம்.
3. **Map-Reduce style:** பெரிய doc-ஐ small pieces ஆக split பண்ணி ஒவ்வொன்றையும் summarize பண்ணி, அப்புறம் அந்த summaries-ஐ மீண்டும் summarize பண்ணுது.

Implementation ரொம்ப simple. ஒரு small rewriter model அல்லது same LLM with low temperature:
> "Summarize the following text focusing only on information relevant to: [query]"

## 4. Architectural Reasoning

Context compression எப்போது useful?

* Retrieval மிக அதிகம், precision குறைவு. 20 chunks திரும்புது, ஆனால் 80% noise.
* Documents long-form. Contracts, tickets, logs.
* LLM context window limited அல்லது cost sensitive. Production RAG-ல token cost முக்கியம்.
* Need higher faithfulness. Less noise = less hallucination.

Alternatives என்ன?
* **Better retrieval:** Hybrid search, reranking. இது relevant chunks-ஐ அதிகம் கொண்டு வரும். ஆனால் chunk இன்னும் நீளமாகவே இருக்கும்.
* **Chunk size tuning:** Small chunk size எடுத்தால் noise குறையும், ஆனால் context loss ஆகும்.
* **Compression:** Retrieve ஆனதை பிறகு refine பண்ணுது. Retrieval quality-ஐ மேம்படுத்தாமல், அதன் output-ஐ clean பண்ணுது.

Architect choose பண்ணும்போது reasoning: Retrieval-ஐ மேலும் improve பண்ணுவது diminishing returns கொடுக்குது. அப்புறம் compression தான் cheap win.

## 5. Trade-offs

* **Faithfulness vs compression ratio:** அதிகம் சுருக்கினால் details தொலையும். LLM summary பண்ணும்போது subtle nuance மாறலாம். Critical domain-ல இது risk.
* **Latency & cost:** Compression-க்கு extra LLM call தேவை. Retrieve + Compress + Generate = 2-3 LLM calls. Latency அதிகம். ஆனால் final generate call-ல token குறையும், அது cost-ஐ குறைக்கலாம்.
* **Error propagation:** Compression step-ல hallucination ஏற்பட்டால், அது final answer-ல பரவும். Garbage in garbage out.
* **Operational complexity:** Pipeline இன்னொரு stage add ஆகுது. Monitoring, failure handling தேவை.

## 6. Practical Example

Enterprise support RAG. Customer ticket thread 200 messages. User asks: "எனது refund status என்ன?"

Retriever 8 chunks தருது. 3 chunks ஆரம்ப greeting, 2 chunks unrelated billing dispute, 3 chunks refund discussion.

Compression step:
> "Extract only refund-related facts: request date, amount, approval status, expected date."

Output becomes 4 lines:
* Refund requested on 2025-11-02 for $120
* Approved by agent on 2025-11-10
* Processing time 5-7 business days
* No status update after approval

LLM இப்போது இதை பார்த்து சரியான answer கொடுக்கும். Noise இல்லை.

## 7. Reasoning Challenge

உங்களுக்கு legal RAG system இருக்கு. ஒரு contract 40 pages. User query: "Termination clause penalty என்ன?"

Retriever 12 chunks தருது, 8k tokens. Context window tight. Compression பண்ணலாம். ஆனால் legal domain-ல accuracy முக்கியம்.

இங்கே extractive compression மட்டும் பயன்படுத்துவீர்களா, அல்லது abstractive summarization பயன்படுத்துவீர்களா? ஏன்? அந்த தேர்வு என்ன trade-off கொண்டு வரும்?

## 8. Key Takeaways

* Context compression = retrieve ஆனதை query-aware ஆக சுருக்கி, noise அகற்றுவது. Filtering அல்ல.
* அது precision-ஐ மேம்படுத்தி cost & latency-ஐ குறைக்க உதவும், ஆனால் extra LLM call & faithfulness risk add பண்ணும்.
* Retrieval-ஐ முழுவதுமாக மாற்றாது. Retrieve + Compress ஒன்றாக வேலை செய்யும்.
* சுருக்கும் அளவு, domain risk-ஐ பொறுத்து தேர்வு செய்ய வேண்டும்.
