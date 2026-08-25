# MCP architecture

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 10.2.1 — MCP

**10.2.1 — MCP**

### The problem

An AI agent is useless without context and actions. It needs to read a database, call an internal API, query a ticket system, or run a code tool.

Before MCP, every integration was bespoke:
* Each LLM vendor had its own tool calling format
* Each tool provider had its own SDK and auth
* The host app had to know how to discover, connect, and stream results for every server

Result: N x M integration matrix, fragile glue code, and no portability. You could not move a tool from Claude Desktop to your own agent without rewriting the connector.

The constraint is not just technical. It's architectural: you need a stable contract between an AI host and external capabilities, with discovery, schema, and lifecycle management.

### Mental model

MCP is a USB-C for AI tools.

A standard host-side client speaks one protocol to many servers. Each server exposes a typed capability surface — tools, resources, prompts — and the client negotiates transport and auth. The LLM never talks directly to the server; the host mediates.

### How it works

MCP is client-server over JSON-RPC.

```
flowchart LR
    User --> Host[AI Host e.g., Claude Desktop, IDE]
    Host --> MCPClient[MCP Client]
    MCPClient <--> |stdio / SSE / HTTP| MCPServer[MCP Server]
    MCPServer --> Tool[DB / API / Filesystem / Internal Service]
```

Three roles:
* **Host** runs the LLM and user session. It contains the MCP Client.
* **MCP Client** maintains the protocol session: initialize, list capabilities, call tools, stream resources.
* **MCP Server** is a lightweight process that implements a capability set. It exposes tools with JSON schemas, resources with URIs, and prompts.

Flow: Host starts client → client connects to server → server sends `tools/list` with schemas → LLM decides to call a tool → client validates arguments against schema → server executes → result returns to LLM in one turn.

Transport is intentionally simple: stdio for local processes, Server-Sent Events / HTTP for remote. No new network layer, just a contract.

### Architectural reasoning

**When it helps**
* You want tool reuse across multiple AI hosts without re-integrating.
* You need discoverable, typed interfaces for agents, not just ad-hoc function calling.
* You want to centralize security, logging, and rate limiting at the server boundary.

**Alternatives**
* Direct function calling / OpenAI Tools API: fast, but locked to one model vendor and one integration.
* Custom REST gateway per tool: works, but you own schema translation and versioning forever.
* LangChain / LlamaIndex agents: powerful orchestration, but they are frameworks, not a protocol.

MCP chooses standardization over optimization. It trades per-tool performance for portability and composability.

### Trade-offs and failure modes

* **Trust boundary is explicit.** The server runs with real credentials. A malicious or compromised server can exfiltrate data via tool results or prompt injection. You must sandbox servers and audit tool outputs before feeding them to the LLM.
* **No built-in auth standard.** Today auth is delegated to transport. That means you must design your own mTLS, OAuth, or token issuance per server. Architect for it.
* **Schema drift.** Tools change. If a server changes a parameter type without versioning, the LLM will hallucinate calls. Treat tool schemas like APIs: version them and validate strictly on the client.
* **Operational coupling.** A slow or crashing server blocks the agent turn. You need timeouts, retries, and circuit breakers at the client, and health checks for servers.
* **Least privilege.** Exposing an entire database as a MCP resource is tempting and dangerous. Prefer fine-grained tools, not raw data dumps.

### Example

Enterprise support copilot.

Host: internal chat app with MCP client.
Servers:
* `tickets-mcp-server` — tools: `search_tickets`, `create_ticket`. Reads from Jira via service account.
* `crm-mcp-server` — resources: `customer://{id}` with read-only access, tool: `get_recent_orders`.
* `policy-mcp-server` — prompts: `refund_policy_summary`.

The LLM discovers all three at startup. When a user asks "Why is order 123 delayed?", the agent calls `get_recent_orders`, then `search_tickets`, and returns a grounded answer. Swapping Claude for another host requires zero code changes; only the client config changes.

### Reasoning challenge

You need to expose an internal financial ledger to an AI agent for read-only queries. Do you build a single MCP server that proxies raw SQL, or multiple narrow servers per use case with explicit tools like `get_customer_balance` and `list_recent_transactions`?

Think about blast radius, auditability, prompt injection risk, and schema stability.

### Key takeaway

* MCP solves the N x M integration problem for AI tooling with a standard host-client-server contract.
* It moves integration complexity from the LLM to a typed server boundary you can secure, version, and observe.
* Choose it when portability and composability matter more than per-tool optimization.
* Design servers for least privilege, explicit schemas, and failure isolation; the LLM will trust whatever you return.
