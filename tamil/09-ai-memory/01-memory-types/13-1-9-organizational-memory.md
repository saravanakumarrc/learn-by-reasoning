# Organizational memory

> **Learning Path:** AI Memory
> **Section:** 13.1.9 — Memory types

## 1. Problem

உங்கள் AI agent வாடிக்கையாளர் support-க்கு வேலை செய்கிறது. ஒரு user-க்கு கடந்த 3 மாதத்தில் ticket திறந்தார், payment fail ஆனது, அவருக்கு special discount கொடுக்கப்பட்டது.

இப்போது அதே user மீண்டும் chat-க்கு வந்து "என் last issue என்ன ஆச்சு?" என்று கேட்கிறார்.

Agent-க்கு என்ன தெரியும்? அந்த conversation மட்டும் தான் தெரியும்.

Ticket system, CRM, billing DB — இதெல்லாம் agent-க்கு தெரியாது. Agent-க்கு context window மட்டுமே memory.

இதுதான் பிரச்சனை. AI-க்கு தனிப்பட்ட user-க்கான memory இருக்கும், ஆனால் **organization-முழுக்க பகிரப்படும் knowledge, policy, decision history, lessons learned** — இவை எல்லாம் எங்கே இருக்கும்?

ஒரு engineer என்ன பார்க்கிறார்? Every team தனியாக wiki எழுதுகிறது, Slack-ல் பேசுகிறது, Notion-ல் dump செய்கிறது. New hire-க்கு அந்த knowledge கிடைக்காது. Agent-க்கு அது accessible ஆகாது.

**What goes wrong if we don't have this?** Agent ஒவ்வொரு முறையும் reinvent பண்ணும். Same decision திரும்ப திரும்ப கேட்கப்படும். Hallucination அதிகரிக்கும். Operational cost ஏறும்.

## 2. Mental Model

Organizational memory என்பது **company-க்கு சொந்தமான, durable, searchable knowledge base** ஆகும்.

இது individual user memory அல்ல. இது team memory.

நினைத்துப் பாருங்கள்: ஒரு library. ஆனால் அது static documents அல்ல. அது:
- past decisions ஏன் எடுக்கப்பட்டது
- incidents மற்றும் post-mortems
- product policies, pricing rules
- customer interactions patterns
- internal tools usage

இந்த memory ஒரு AI agent-க்கு read/write செய்ய திறந்திருக்க வேண்டும்.

Mental model simple: **Short-term memory = conversation context. Long-term personal memory = user profile. Organizational memory = shared institutional knowledge.**

## 3. How It Works

Architecturally இது ஒரு knowledge layer.

```
Agent → Retriever → Organizational Memory Store → Structured + Unstructured docs
                ↓
            Embedding + Vector DB for semantic search
                ↓
            Graph DB for relationships: decision → incident → policy
```

Workflow:
1. Agent ஒரு query வரும்போது, அது முதலில் internal context பார்க்கும்.
2. போதுமான தகவல் இல்லையெனில், query-ஐ vectorize செய்து organizational memory-ல் search செய்யும்.
3. Relevant chunks, policies, past tickets retrieve ஆகும்.
4. Agent அதை reasoning-க்கு use செய்யும்.
5. New insight வந்தால், அதை summarize செய்து memory-க்கு write back செய்யலாம் — human approval உடன்.

Key point: Write path controlled ஆக இருக்க வேண்டும். எல்லா agent output-ஐயும் auto-write செய்யக்கூடாது.

## 4. Architectural Reasoning

இது useful ஆகும்போது:
- Multiple agents same knowledge share செய்ய வேண்டும்
- Compliance / audit trail தேவை
- Onboarding speed தேவை
- Agent consistency வேண்டும்

Constraints அது address பண்ணும்:
- **Consistency:** ஒரே policy எல்லா agent-க்கும் same
- **Scalability:** Knowledge centralize ஆகி, reuse ஆகும்
- **Operability:** Engineers ஒரே source of truth பார்க்கலாம்

Alternatives:
- Static wiki + RAG: எளிய start, ஆனால் stale ஆகும்
- Database only: structured ஆனால் unstructured lessons capture ஆகாது
- No memory: agent stateless, cheap ஆனால் useless

Architect choose பண்ணுவார் ஏன்? Because without organizational memory, AI system என்பது isolated chatbot ஆகவே இருக்கும். Business value குறைவு.

## 5. Trade-offs

1. **Freshness vs Stability.** Organizational memory அடிக்கடி update ஆக வேண்டும். ஆனால் uncontrolled write = hallucination spread. Solution: write via human-in-the-loop or verified pipeline.

2. **Search quality vs Cost.** Vector search + hybrid search தரத்தை கொடுக்கும், ஆனால் embedding storage, retrieval latency, cost ஏறும். Small company-க்கு overkill ஆகலாம்.

3. **Access control vs Usability.** Some knowledge internal only, some customer-facing. Fine-grained permissions தேவை. Too strict = agent blind. Too open = leak.

4. **Structured vs Unstructured.** Pure vector DB எல்லா text-ஐயும் store செய்யும். ஆனால் policy versioning, decision metadata track செய்ய structured store தேவை. Hybrid design பொதுவாக வேண்டும்.

Failure mode: Stale memory. Agent outdated policy-ஐ retrieve செய்து customer-க்கு தவறான info கொடுக்கும். இதை தடுக்க TTL, versioning, source attribution must.

## 6. Practical Example

Enterprise support AI agent.

Sources: Jira tickets, Confluence post-mortems, Zendesk solutions, internal policy docs, product release notes.

Pipeline:
- Daily ETL: new tickets, resolved incidents -> summarize -> store in vector DB with metadata: team, product, date, severity.
- Graph edges: incident → root cause → fix → related policy.

Agent query: "Refund policy for failed payment in EU?"

Agent retriever: organizational memory-ல் search செய்து:
- Policy doc v2.3, updated 2024-11
- Recent post-mortem: Stripe failure on 2025-06-12, manual refund process
- Similar tickets resolved

Agent response consistent ஆகும், citation உடன்.

இதன் விளைவு: Agent hallucinates குறையும், support engineer-கள் repetitive questions-ஐ குறைக்கலாம்.

## 7. Reasoning Challenge

உங்கள் org-ல் 3 teams இருக்கு: Sales, Support, Engineering. ஒவ்வொருவரும் தங்கள் Notion, Slack, Confluence-ல் தகவல் வைத்திருக்கிறார்கள்.

நீங்கள் ஒரு AI agent build செய்கிறீர்கள், அது customer inquiry-க்கு பதில் தர வேண்டும். ஆனால் sensitive pricing info sales team மட்டுமே பார்க்க வேண்டும்.

இங்கே organizational memory-ஐ எப்படி design செய்வீர்கள்? Data ingestion, access control, write policy எப்படி இருக்கும்? ஏன்?

## 8. Key Takeaways

- Organizational memory = shared institutional knowledge, not personal user memory
- Agent quality depends on retrieval quality from durable, versioned memory
- Write path must be controlled; auto-write spreads hallucination
- Design for freshness, access control, and hybrid structured + vector storage
- Every architectural solution creates trade-off: consistency vs cost vs operability
