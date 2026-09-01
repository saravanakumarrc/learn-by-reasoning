# Agent permissions

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.17 — Learn

## 1. Problem

நீங்கள் ஒரு Multi-Agent system build பண்ணுகிறீர்கள். ஒரு agent க்கு user query வந்தது. அது tool use பண்ணணும், database read பண்ணணும், மற்ற agent கிட்ட message அனுப்பணும், maybe payment API call பண்ணணும்.

**Problem என்ன?** Agent ஒரு autonomous code ஆக இருக்கும். அது hallucinate பண்ணும், tool misuse பண்ணும், over-privileged ஆக இருந்தால் தவறுதலாக critical action எடுக்கும்.

உதாரணமாக, ஒரு Customer Support Agent க்கு ticket status பார்க்க அனுமதி இருக்கு. ஆனால் அது refund initiate பண்ணும் tool-ஐயும் access பண்ணினால் என்ன ஆகும்? Wrong tool call, privilege escalation, data leak.

> What goes wrong if we don't have this? Agents can do anything they want, anytime, anywhere. That's production incident waiting to happen.

## 2. Mental Model

Agent permissions = **Who can do What, on Which resource, under Which conditions**.

இது operating system-ல user permissions மாதிரிதான். `read`, `write`, `execute` இருக்கு. ஆனால் agents-க்கு கொஞ்சம் அதிகம் தேவை: context-bound, time-bound, intent-bound.

Mental model: **A policy layer between agent decision and action execution**.

Agent decides "I need to call refund API". Permission layer asks: This agent has `refund:write`? On which customer? Is this user authorized? Is it within $500 limit? Is it during business hours? If yes, allow. If no, deny + audit.

## 3. How It Works

Core pieces:

* **Identity**: Agent has an identity, not just `agent-1`. Team, role, tenant, deployment environment.
* **Policy**: Declarative rules. `allow/deny` based on agent role, resource, action, condition.
* **Enforcement Point**: Tool caller / MCP server / API gateway. Permission check happens just before action execution, not inside LLM.
* **Audit Trail**: Every decision logged. Who requested, what was requested, allow/deny, why.

Flow:

`User Query → Agent Reasoning → Tool Intent → Permission Check → Allow/Deny → Execute or Reject`

LLM-ஐ trust பண்ணக்கூடாது. LLM output ஐ validate பண்ணணும்.

## 4. Architectural Reasoning

**When useful?** 
* Multiple agents share same tools
* Agents operate on sensitive data: PII, payments, internal systems
* Multi-tenant system where agents serve different customers
* Human-in-the-loop required for high-risk actions

**Constraint it addresses**: Safety, blast radius control, compliance.

**Alternatives:**
* No permissions: Fast but unsafe. Prototype-க்கு மட்டும்.
* Hard-code in agent prompt: "Never call refund". Prompt is not enforcement. LLM can jailbreak.
* Centralized policy service with enforcement at tool layer: Correct approach.

Architect choose பண்ணும் போது: Centralize policy evaluation. Don't scatter checks across agents.

## 5. Trade-offs

* **Security vs Flexibility**: Strict permissions reduce risk but make agent less autonomous. Too strict → agent always fails.
* **Central control vs Latency**: Permission check adds network hop. For high-frequency tools, cache decisions.
* **Granularity vs Complexity**: Fine-grained per-resource permissions are safer but policy explosion ஆகும். Start coarse, refine.
* **Auditability vs Cost**: Full audit log is must for compliance, but storage and query cost வரும்.

Important failure mode: **Permission bypass via tool chaining**. Agent A has read access, Agent B has write access. A calls B via message to indirectly do write. Need cross-agent permission propagation and delegation limits.

## 6. Practical Example

Enterprise RAG + Agent system.

Agents: `ResearchAgent`, `SummarizerAgent`, `ActionAgent`

Tools: `vector_db_search`, `internal_wiki_read`, `jira_create`, `payment_refund`

Permissions:
* `ResearchAgent`: `vector_db_search:read`, `internal_wiki_read:read`
* `SummarizerAgent`: `vector_db_search:read`
* `ActionAgent`: `jira_create:write` only for projects `SUPPORT`, `payment_refund:write` only if amount < $200 and needs human approval > $200

Policy enforced at MCP server. Agent calls tool → MCP checks policy engine → allow/deny.

Result: ResearchAgent can never accidentally create a Jira ticket. ActionAgent cannot refund $10k without approval.

## 7. Reasoning Challenge

உங்கள் system-ல் 3 agents இருக்கு: `BillingAgent`, `SupportAgent`, `OnboardingAgent`. அவை எல்லாம் `user_data` database-ஐ access பண்ண வேண்டும். `BillingAgent` க்கு email மட்டும் தேவை, `SupportAgent` க்கு full profile தேவை, `OnboardingAgent` க்கு write access தேவை ஆனால் production data இல்லாமல் sandbox மட்டும்.

ஒரே database table, ஒரே API. Permission model எப்படி design பண்ணுவீர்கள்? Field-level vs row-level vs environment-level? Trade-off என்ன?

## 8. Key Takeaways

* Agent permissions are about **controlling blast radius**, not about limiting intelligence.
* Enforce permissions **outside LLM**, at tool execution layer.
* Model permissions as **role + resource + action + condition**, not just allow/deny.
* Every permission decision must be **auditable**.
* Good permission design makes failures safe and debuggable, not just secure.
