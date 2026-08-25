# Resources

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 10.2.4 — MCP

**The problem**

You are building agents that need real world data and actions. One agent needs CRM records, another needs Jira tickets, another needs internal wiki and a billing API.

Without a standard, each integration is bespoke: custom SDK, custom auth, custom schema mapping, custom error handling. The agent host has to know how every tool works. Adding a new tool means code changes in the host, not just configuration.

Worse, tool definitions drift. The model learns tool signatures from descriptions, and those descriptions are hand-written and inconsistent. Security and audit become scattered across N integrations.

The need is a standard interface between an AI host and external capabilities, so tools are discoverable, self-describing, and interchangeable.

### Mental model

MCP is a USB-C for AI tools.

The AI host is the laptop. MCP servers are peripherals. The protocol defines a common plug: how the host discovers what the server can do, how it calls tools, and how it reads resources. The host does not need to know the internals of each server.

### How it works

MCP is a client-server protocol, typically JSON-RPC over stdio or Server-Sent Events.

* **Host** = LLM app, agent runtime, IDE, or chat client. It contains an MCP client.
* **Server** = a process that wraps one capability domain. It exposes three things:
  * **Tools** - actions the model can call, e.g. `create_ticket`, `search_crm`. Self-described with name, description, JSON schema for input/output.
  * **Resources** - read-only data the model can access, e.g. `file://docs/pricing.md`, `db://tickets`.
  * **Prompts** - reusable prompt templates.

Discovery is automatic. On connect the server sends its capabilities and tool schemas. The host can then present them to the model without hard-coding.

```mermaid
flowchart LR
    Host[AI Host / Agent] -->|MCP Client| Server[MCP Server]
    Server --> Tools[Tools: create_ticket, search_crm]
    Server --> Resources[Resources: wiki, files]
    Server --> Prompts[Prompts]
    Server -->|Transport| stdio[/SSE]
```

The model sees a unified tool list and calls via the client. No custom glue per integration.

### Architectural reasoning

When it helps:
* Agents need many heterogeneous tools and you want zero-code onboarding for new ones.
* You want to reuse the same tool set across multiple hosts, e.g. Claude Desktop, custom agent, IDE.
* You want to enforce a single security boundary per domain rather than per host.

What it solves:
* Decoupling of agent logic from tool implementation.
* Standardized schema and auth for tool calling.
* Local-first and remote-first servers can coexist.

Alternatives:
* Direct function calling with custom adapters. Cheaper for 1-2 tools, explodes with N.
* A central API gateway that normalizes tools. Works but creates a single bottleneck and coupling.
* Prompt-based tool description. Brittle and insecure.

Choose MCP when the number and churn of tools matters more than minimal latency and you control the tool surface.

### Trade-offs and failure modes

* **Trust boundary.** The server runs with access to sensitive data. A compromised MCP server is a direct model-accessible attack surface. Isolate servers, run with least privilege, audit tool calls.
* **Schema drift.** Tool input schemas are the contract. Change a field and every agent breaks silently. Version servers and test schemas.
* **Latency and partial failure.** Tools are remote RPCs. A slow CRM server blocks the agent turn. Design timeouts, retries, and graceful degradation. Prefer read resources for large data over tool output.
* **Over-exposure.** It's easy to expose too much. A server that exposes raw DB queries is a prompt injection risk. Expose curated tools, not raw capabilities.
* **Operational complexity.** You now have N server processes to deploy, monitor, and secure. Observability must cover tool call success, latency, and model misuse.

### Example

Enterprise support agent.

Host = internal agent runtime. MCP servers:
* `crm-server` exposes `search_customer`, `get_subscription`.
* `jira-server` exposes `create_ticket`, `list_tickets`.
* `wiki-server` exposes resources for runbooks.

Agent asks: "Customer X is complaining about billing." Model discovers tools via MCP, calls `search_customer`, reads `wiki://billing-troubleshooting`, creates ticket via Jira. Adding a new knowledge base means deploying a new MCP server, no host change.

### Reasoning challenge

Your team wants to expose the internal Postgres database directly via an MCP server with a generic `sql_query` tool so the model can "figure it out".

Do you allow it? What constraints would you put in place instead?

### Key takeaway

* MCP standardizes how AI hosts discover and call tools, not the tools themselves.
* It moves integration cost from the host to self-describing servers.
* Choose it for multi-tool, multi-host environments where tool churn is high.
* Watch trust boundaries, schema versioning, and operational overhead of many servers.
