# Tool permissions

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.6 — Learn

## 1. Problem

ஒரு LLM agent-க்கு tools கொடுக்கும்போது நீங்கள் என்ன நினைக்கிறீர்கள்? "Agent எதை call பண்ணலாம்?" என்பது மட்டும் இல்லை. "யார் கேட்கிறார்? எந்த context-ல்? எந்த data-ஐ access பண்ணலாம்?" என்பதும் முக்கியம்.

உதாரணமாக, உங்கள் agent-க்கு `get_user_pii`, `create_invoice`, `delete_project` மூன்றும் tool ஆக இருக்கு. User chat-ல் சாதாரண customer என்றால் invoice create பண்ணலாம், ஆனால் delete project பண்ணக்கூடாது. Admin user என்றால் delete செய்யலாம்.

Tool-ஐ கொடுத்துவிட்டால் agent அதை எப்போதும் use பண்ண முடியும் என்றால், அது security incident ஆகும். Tool permissions இல்லாமல், agent ஒரு confused request-ல் sensitive action எடுத்துவிடும். அதுதான் problem.

## 2. Mental Model

Tool permissions என்பது **who can do what, with which data, when** என்பதற்கான gate.

இது மூன்று layer-ல் வேலை செய்கிறது:

* **Tool-level permission:** இந்த tool-ஐ யாரால் call பண்ண முடியும்? `create_invoice` internal only? `search_web` public?
* **Parameter-level permission:** Tool call-ல் வரும் arguments-ல் எந்த field-ஐ allow பண்ணுவது? `get_user_pii(user_id)`-ல் user_id = self user மட்டுமா? அல்லது any user?
* **Context-level permission:** இந்த session-ன் user role, tenant, time, risk level பார்த்து allow/deny.

நினைத்துக்கொள்ள: API gateway-ல் JWT check பண்ணுவது போல, agent tool invocation-க்கு முன் ஒரு policy check.

## 3. How It Works

Practical flow:

1. User message வருகிறது → LLM decides tool call.
2. Tool call intent + parameters உருவாகிறது.
3. **Permission evaluator** ஓடுகிறது. இது policy engine.
4. Allow என்றால் tool execute. Deny என்றால் safe fallback: refuse or ask clarification.

Policy எங்கே இருக்கும்?
* Static allowlist per role: `role:customer → tools: [search, create_ticket]`
* Dynamic policy: `delete_project` allowed only if `project.owner_id == caller.user_id` OR `caller.role == admin`
* Data-level filter: `get_user_pii` allowed only for own user_id, unless audit scope.

Implementation pattern:
* Tool registry-ல் metadata attach பண்ணு: `required_permission: "billing.write"`, `sensitive: true`
* Middleware layer: `check_permission(caller_context, tool_name, args)` → boolean
* Audit log: யார் எந்த tool-ஐ எப்போது try பண்ணினார், allow/deny.

## 4. Architectural Reasoning

Tool permissions தேவைப்படும் சூழல்:

* Multi-tenant SaaS agent: ஒரு tenant-ன் agent மற்ற tenant data-ஐ touch பண்ணக்கூடாது.
* Human-in-the-loop: High-risk tools like `transfer_money`, `delete_db` needs approval.
* Least privilege: Agent-க்கு தேவையான tools மட்டும் expose பண்ணு.

Alternatives:
* No permissions, trust LLM. → Simple, but unsafe.
* Permissions at tool definition time only. → Static, context aware இல்லை.
* Full human approval for all tools. → Safe, but latency & UX கெட்டுபோகும்.

Architect choose பண்ணும்போது கேட்க வேண்டியது: Risk level என்ன? Tool irreversible ஆ? Data sensitivity எப்படி? Team size & operational cost?

## 5. Trade-offs

* **Safety vs Agility**: Strict permissions agent-ஐ safe ஆக்கும், ஆனால் useful tool use குறையும். Over-restrict பண்ணினால் agent "I can't help" என்று சொல்லும்.
* **Central policy vs Distributed**: Central policy engine simple to audit, ஆனால் single point of failure & latency. Distributed checks fast, ஆனால் inconsistent ஆகும்.
* **Static vs Dynamic**: Static role-based easy. Dynamic context-based powerful, ஆனால் policy evaluation complex, test hard.
* **Audit cost**: Every deny/allow log பண்ணினால் observability கிடைக்கும், ஆனால் storage & cost increase.

Failure mode: Permission check bypass ஆனால் agent privilege escalation ஆகும். Tool argument injection மூலம் user_id மாற்றி PII leak ஆகும். அதனால் args validation + policy enforcement இரண்டும் தேவை.

## 6. Practical Example

Enterprise support agent.

Tools:
* `search_knowledge_base`
* `create_support_ticket`
* `refund_order`
* `get_user_pii`

Roles: customer, support_agent, finance_admin

Policy:
* customer → search, create_ticket only. `get_user_pii` allowed only for own user_id.
* support_agent → search, create_ticket, get_user_pii but only for assigned tickets.
* finance_admin → refund_order allowed.

Flow: Customer "My order refund பண்ணுங்க" என்று கேட்டால், agent `refund_order` tool-ஐ suggest பண்ணும். Permission evaluator caller role = customer → deny. Agent user-க்கு "I can raise a ticket for refund, finance team will review" என்று சொல்லும்.

இங்கே tool permission system இல்லாமல் agent தவறாக refund trigger பண்ணியிருக்கும்.

## 7. Reasoning Challenge

உங்களிடம் 2 tools இருக்கு: `list_projects` மற்றும் `delete_project`. 3 user types: viewer, editor, owner.

Editor project-ஐ edit பண்ணலாம், delete பண்ணக்கூடாது. Owner delete பண்ணலாம். Viewer மட்டும் list பண்ணலாம்.

ஒரு request வருகிறது: user=editor, action=delete_project, project_id=123. Permission check எப்படி design பண்ணுவீர்கள்? Tool-level deny போதுமா, இல்லை parameter-level check தேவையா? Why?

## 8. Key Takeaways

* Tool permissions = who can call which tool with what data, not just tool exposure.
* Enforce at invocation time with caller context, role, and data scope.
* Least privilege மற்றும் auditability ஆகியவை architecturally non-negotiable for production agents.
* Every permission decision creates a trade-off between safety, latency, and agent usefulness.
