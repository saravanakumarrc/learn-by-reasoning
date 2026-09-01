# Knowledge platform

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.8 — Enterprise patterns

## 1. Problem

உங்கள் enterprise-ல 500 engineers, product managers, support agents இருக்காங்க. அவங்களுக்கு தேவையான knowledge எல்லாம் வெவ்வேறு இடத்தில் இருக்கு.

Confluence-ல் design docs, GitHub-ல code comments, Slack-ல decisions, Jira-ல tickets, Notion-ல runbooks, Google Drive-ல presentations.

ஒரு engineer புது service deploy பண்ணணும். அவனுக்கு தெரியணும்: அந்த service-க்கு எந்த database use பண்ணினோம்? ஏன் அந்த choice எடுத்தோம்? Last incident என்ன? Rollback எப்படி பண்ணினோம்?

அவன் 7 tools-ல search பண்ணி, 3 மணி நேரம் waste பண்றான். அதே கேள்வி support agent-க்கும் வருது. புது joiner-க்கும் வருது.

**What goes wrong if we don't have this?** Knowledge silo, slow onboarding, repeated mistakes, tribal knowledge, AI agent-க்கு hallucination.

ஒரு enterprise knowledge platform தேவைப்படுவதற்கு இதுதான் painful problem.

## 2. Mental Model

Knowledge platform = **Single source of truth for context, not just documents**.

இது document repository இல்ல. இது ஒரு **retrievable, verifiable, actionable knowledge graph**.

நினைச்சுக்கோ: Company-யின் memory. Code, docs, decisions, incidents, metrics எல்லாம் structured ஆக link ஆகி இருக்கணும். Human கேட்டாலும், LLM agent கேட்டாலும் same answer வரணும்.

## 3. How It Works

Core pipeline 4 steps:

1. **Ingest**: Internal sources-ஐ connect பண்ணு. GitHub, Jira, Confluence, Slack, incident management, monitoring dashboards, runbooks.
   Source-ல change வந்ததும் crawl / webhook trigger.

2. **Normalize & Enrich**: Raw text-ஐ clean பண்ணி, metadata attach பண்ணு. Author, team, service name, timestamp, ticket ID. Entity extraction பண்ணி `service -> owner -> repo -> incident` மாதிரி links உருவாக்கு.

3. **Index for Retrieval**: Text embeddings + keyword index. Vector database-ல semantic search. Graph database-ல relationships. Hybrid retrieval.

4. **Access Layer**: Human UI for search, and API for agents. Provenance இருக்கணும்: "இந்த answer எந்த doc-ல இருந்து வந்தது, last updated எப்போ, who approved".

RAG pipeline-க்கு foundation இதுதான். Without good knowledge platform, RAG = hallucination.

## 4. Architectural Reasoning

**When useful?**
* Enterprise scale-ல cross-team knowledge தேவை
* AI agents-க்கு grounded answers தேவை
* Compliance & audit trail தேவை

**Constraint it addresses:** Fragmentation, staleness, trust.

**Alternatives:**
* Search over Confluence alone → Siloed, not real-time
* Central wiki → Write-heavy, quickly stale
* LLM fine-tuning on docs → Costly, slow update cycle

**Why choose platform approach?** Because knowledge is dynamic. Code changes daily, incidents happen weekly. Platform must be continuously synchronized, not batch dump.

## 5. Trade-offs

* **Freshness vs Cost**: Real-time sync வேணும், ஆனால் every Slack message-ஐ index பண்ணுவது expensive. முக்கிய sources filter பண்ணணும்.
* **Openness vs Security**: Engineers எல்லாருக்கும் access வேணும், ஆனால் PII, secrets, internal roadmap leak ஆகக்கூடாது. Fine-grained access control + redaction pipeline must.
* **Semantic search vs Exact retrieval**: Embedding கொடுக்கும் relatedness, ஆனால் ticket number, API spec மாதிரி exact match தேவை. Hybrid needed.
* **Centralization vs Ownership**: Central platform team build பண்ணும், ஆனால் knowledge quality team-கள் maintain பண்ணணும். Ownership model இல்லாமல் platform stale ஆகும்.

Failure mode: Platform தான் source of truth ஆகி, people original doc update பண்ணாமல் platform update மட்டும் பண்ணினால் divergence வரும். Always ingest from source of record.

## 6. Practical Example

Bank-ல fraud detection service இருக்கு. New engineer join பண்றான்.

Knowledge platform query: "fraud detection service database choice why"

Retrieval returns:
* Architecture ADR from Confluence, dated 2023-11, linked to Jira RFC-4521
* Incident INC-2024-08 where latency spiked, linked to runbook
* Current owner: payments-team@company.com
* Last code change: GitHub PR #1289

Agent-க்கு context ready. Human-க்கு citations ready.

Without platform, engineer 4 tools-ல hunt பண்ணி, maybe wrong old doc பார்த்து mistake பண்ணுவான்.

## 7. Reasoning Challenge

உங்களிடம் 20 teams உள்ளன. ஒவ்வொரு team-ம் Confluence space, GitHub repo, Slack channel வைத்திருக்கிறது.

Company-wide AI assistant build பண்ண வேண்டும். Support agent chatbot, internal Q&A bot.

இதில்:
* எல்லா data-யும் public search index-ல போட முடியாது
* Engineers source of truth-ஐ மாற்ற விரும்ப மாட்டார்கள்
* Freshness முக்கியம்

நீங்கள் knowledge platform-ஐ எப்படி design செய்வீர்கள்? Ingestion strategy, access control, freshness guarantee என்ன? Trade-off என்ன?

## 8. Key Takeaways

* Knowledge platform என்பது document store அல்ல, verifiable, linked, continuously synced corporate memory.
* Retrieval quality = ingestion quality + metadata + freshness. Embedding alone போதாது.
* AI agents-க்கு grounded answers கொடுக்க, provenance and access control கட்டாயம்.
* Every architectural solution creates maintenance ownership problem. Platform success depends on teams owning their source of truth.
