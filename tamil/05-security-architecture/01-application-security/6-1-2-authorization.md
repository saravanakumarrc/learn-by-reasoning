# Authorization

> **Learning Path:** Security Architecture
> **Section:** 6.1.2 — Application security

## Problem

உங்க system-ல user login பண்ணிட்டார். Authentication முடிஞ்சுது. அவர் யாருன்னு தெரியும்.

இப்போ அவர் `/api/orders/delete` call பண்ணார். அவருக்கு அது அனுமதி இருக்கா?

Authentication இருந்தாலும் authorization இல்லாம, எல்லா authenticated user-க்கும் எல்லா endpoint-ம் திறந்து தான் இருக்கும். ஒரு intern production data-வை delete பண்ணிட்டான். Support engineer customer-ன் credit card-ஐ பார்த்துட்டான்.

இங்கே வலி என்ன? **Who can do what on which resource.** இது code-ல hardcode ஆகி விட்டால், புது role வந்தா, policy மாறினா, deploy பண்ணியே மாற்றணும். Audit கூட சரியாக இருக்காது.

## Mental Model

Authorization = gatekeeper.

Authentication சொல்லும்: "இது Arjun, employee id 8421".
Authorization சொல்லும்: "Arjun-க்கு orders:read இருக்கு, orders:write இல்லை. அவர் own department-ன் orders மட்டும் பார்க்கலாம்."

Mental model ரொம்ப simple:
**Subject - Action - Resource - Context = Allow / Deny**

Subject = user, service account.
Action = read, write, delete, approve.
Resource = order, invoice, customer.
Context = time, IP, tenant, data ownership.

Permission என்பது ஒரு claim. அதை நீங்கள் எங்க store பண்ணினாலும், evaluate பண்ணுவதே authorization.

## How It Works

Typical request flow:

Client -> API Gateway -> AuthN -> AuthZ check -> Service

1. Request வரும் போது token இருக்கும். JWT-ல subject, tenant id, roles மாதிரி claims இருக்கும்.
2. AuthZ middleware இதை பார்த்து policy engine-க்கு கேட்கும்: `can(user, action, resource, context)?`
3. Policy engine ஒரு decision தரும். Allow / Deny.
4. Decision-ஐ log பண்ணுங்கள். Audit trail கிடைக்கும்.

Policy எப்படி store பண்ணலாம்?
* **RBAC**: Role Based Access Control. User -> Role -> Permissions. `finance_manager` role-க்கு `invoice:approve` permission.
* **ABAC**: Attribute Based Access Control. Rule based. `user.department == resource.department AND action == read`.
* Hybrid தான் real world-ல work ஆகும். RBAC base, ABAC fine grain.

## Architectural Reasoning

Authorization-ஐ எங்க வைக்கிறீங்க?

**In-service checks**: ஒவ்வொரு service-லும் `if user.role == admin` என்று எழுதினால், policy duplicate ஆகும். மாற்றம் கஷ்டம்.

**Centralized policy service / sidecar**: ஒரு central PDP - Policy Decision Point. Service கேள்வி கேட்கும், decision வாங்கும். Policy ஒரே இடத்தில். Operability நல்லது.

எப்போது எது?
* Small system, stable roles -> RBAC in middleware போதும்.
* Multi-tenant SaaS, field level permissions, time based access -> ABAC / policy engine தேவை.
* High throughput internal services -> decision-ஐ cache பண்ணுங்கள். JWT-ல permissions embed பண்ணி short TTL வைத்து latency குறையுங்கள்.

## Trade-offs

**Centralization vs Latency**: Central PDP சரியானது, ஆனால் ஒவ்வொரு request-க்கும் network call = latency. Local cache or push model தேவை.

**Flexibility vs Complexity**: ABAC ரொம்ப flexible, ஆனால் policy எழுதுவது கஷ்டம், test பண்ண கஷ்டம். RBAC simple, ஆனால் fine grain வேண்டுமென்றால் role explosion ஆகும்.

**Policy distribution**: Policy-ஐ service-ல replicate பண்ணினால் fast, ஆனால் consistency problem. Update propagation தேவை.

**Failure mode**: Authorization service down ஆனால்? Fail-closed பண்ணுவீர்களா? அல்லது last known decision use பண்ணுவீர்களா? Security-ல default deny தான் safe.

## Practical Example

Enterprise billing system.

Roles: customer_user, support_agent, finance_manager, admin.

Requirement:
* customer_user தன் own tenant-ன் invoices மட்டும் read பண்ணலாம்.
* support_agent எல்லா tenants-ன் invoices read பண்ணலாம், ஆனால் amount > 1M என்றால் read மட்டும்.
* finance_manager approve பண்ணலாம், ஆனால் business hours மட்டும்.
* Admin எல்லாம் பண்ணலாம்.

Design:
API Gateway-ல authentication முடிந்ததும், request context-ல `user_id, tenant_id, role` வரும்.
Middleware request-ஐ `can(user, action, resource_type, resource_id)` என்று policy engine-க்கு அ
