# Authentication

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 10.2.7 — MCP

**Authentication for MCP**

### 1. The problem

MCP lets an AI client call tools exposed by a server. That is powerful, and dangerous.

Without authentication, any agent that can reach the server can invoke any tool: read files, query your CRM, create tickets, run shell commands. The problem is not just "who is the user" but "which agent, with which permissions, is allowed to call which tool on which data".

In tool calling & AI interfaces you have three trust boundaries:
* Human -> AI application
* AI application -> MCP client
* MCP client -> MCP server -> downstream systems

The last boundary is the one architects get wrong. The agent is autonomous, stateful, and often holds a token on behalf of a human. You need to prove identity, scope, and intent before a tool runs.

### 2. Mental model

Think of MCP as a universal remote for tools. Authentication is the lock on the remote and the permission list per button.

Local stdio MCP servers inherit OS user identity. Remote MCP servers over SSE/HTTP need explicit proof. The model is not session cookies for a browser, it is delegated access for an autonomous agent.

### 3. How it works

For remote MCP servers the spec converges on OAuth 2.1 for authentication and authorization.

```
flowchart LR
    Human --> App[AI App]
    App --> Client[MCP Client]
    Client --> Auth[Auth Server]
    Auth --> Client
    Client -->|Bearer token + scope| Server[MCP Server]
    Server --> Tools[Tools / Resources]
```

Flow:
1. MCP client discovers the server and finds an `oauth` capability.
2. Client redirects to authorization server. For confidential clients use client credentials; for user-delegated use Authorization Code + PKCE.
3. Server issues an access token with scopes, e.g. `crm:read`, `crm:write`, `files:read`.
4. Every MCP request is sent with the token. The MCP server validates signature, expiry, audience, and checks scope against the requested tool.
5. Token can be short-lived and refreshed. The server can also require mTLS for machine-to-machine links.

For local stdio, authentication is usually OS-level or implicit trust. That is an architectural choice, not a missing feature.

### 4. Architectural reasoning

When it helps:
* Remote servers exposed to the internet or across teams
* Servers that access PII, financial, or production systems
* Multi-tenant MCP where one server serves many agents

Alternatives:
* API keys: simple, static, no delegation. Good for internal, single-tenant, short-lived deployments. Bad for audit and revocation.
* mTLS: strong machine identity, no user context. Good for service-to-service.
* OAuth 2.1: standard delegation, scopes, audit trail, revocation. Cost is complexity.

Decision rule: use OAuth when identity and scope matter; use API keys or mTLS when you control the network and trust boundary is the host.

### 5. Trade-offs and failure modes

* **Scope creep.** Agents request broad scopes to avoid re-auth. Architect for least-privilege per tool, not per server. A read-only CRM tool should never get write scope.
* **Token lifetime vs latency.** Short tokens are safer but cause refresh churn. Cache and refresh proactively in the MCP client.
* **Agent as principal.** The token is for the human, but the actor is the agent. Log both `sub` and `agent_id` so you can audit what the agent did, not just who owns it.
* **Transport auth != authorization.** TLS protects in transit. It does not stop a compromised client from calling destructive tools.
* **Local trust assumption.** stdio servers assume the parent process is trusted. If the AI app is multi-tenant, that assumption breaks.

### 6. Example

Enterprise HR MCP server exposing `get_employee`, `create_ticket`.

* Public internet: MCP server behind API gateway. Client authenticates via OAuth to corporate IdP. Token scopes: `hr:read`, `support:write`. Server rejects `delete_employee` if scope missing.
* Internal dev laptop: stdio server for local file search. No OAuth, relies on OS user. Acceptable because trust boundary is the machine.

Same protocol, different auth models driven by deployment context.

### 7. Reasoning challenge

You are building an MCP server for a financial data warehouse. Agents from two products will use it: a customer-facing chatbot and an internal analyst copilot.

Do you use one OAuth client with broad scopes for both, or two clients with different scopes and separate token issuance? What breaks if you get it wrong?

### 8. Key takeaway

* Authentication in MCP is about binding identity and scope to autonomous tool calls, not just protecting the transport.
* Prefer OAuth 2.1 with fine-grained scopes for remote servers; use OS trust or mTLS for local stdio where appropriate.
* Design for least-privilege per tool and audit both human and agent identity.
* The right model depends on where the server runs and who can reach it, not on the protocol itself.
