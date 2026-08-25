# gRPC

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.3 — 2. API engineering

**The problem**

You have 50+ internal services talking to each other. REST/JSON works, but at scale it hurts:
- Every request pays for text parsing and large payloads
- HTTP/1.1 means one TCP connection per request or complex connection pooling
- No standard way to do bidirectional streaming
- Schema is implicit, so breaking changes are discovered at runtime
- You need the same contract enforced across Go, Java, Python, TypeScript

You want low latency, efficient wire format, and a single source of truth for the API contract that can generate clients and servers.

**Mental model**

gRPC is contract-first RPC over HTTP/2.

Think of it as: you write the API once in a language-neutral IDL, code generators produce strongly typed clients/servers for each language, and the runtime transports those calls over HTTP/2 with binary protobuf payloads.

It is not a REST replacement for the public web. It is an internal service-to-service protocol optimized for machine-to-machine.

```mermaid
flowchart LR
    Client[Service A] -->|proto contract| Codegen
    Codegen --> ClientStub
    Codegen --> ServerStub
    ServerStub -->|HTTP/2 + protobuf| Service B
    Service B -->|HTTP/2 + protobuf| Service A
```

**How it works**

Essential mechanism only:
- **IDL**: `.proto` defines services, methods, messages. This is the contract.
- **Codegen**: `protoc` generates client/server stubs for each language. Types are enforced at compile time.
- **Transport**: HTTP/2 gives multiplexed streams over one TCP connection, header compression, and flow control.
- **Serialization**: Protocol Buffers is binary, schema-evolution friendly, ~3-10x smaller than JSON.
- **RPC styles**: Unary request/response, server streaming, client streaming, bidirectional streaming.

That’s it. The runtime handles connection pooling, retries, deadlines, and status codes.

**Architectural reasoning**

When it helps:
- High-throughput, low-latency internal services where CPU and bytes matter
- Polyglot microservices needing a single contract
- Real-time features that need streaming, e.g. live telemetry, chat, or model inference streaming
- You want generated types and early breaking-change detection

Alternatives:
- **REST/JSON over HTTP/1.1/2**: Human readable, browser native, great for public APIs and debugging. Higher overhead, no streaming standard.
- **GraphQL**: Flexible client queries, good for public facades. Adds complexity for internal services.
- **Message queues**: Async decoupling, durability. Wrong tool for synchronous request/response.

Decision rule: Use gRPC for internal service mesh. Expose REST/JSON at the edge via a gateway that translates.

**Trade-offs and failure modes**

- **Observability**: Binary protobuf is not human readable. You need proto reflection, logging interceptors, and tools like grpcurl. Debugging is harder than curl.
- **Browser/Firewall**: gRPC requires HTTP/2. Browsers now support it, but many proxies and legacy networks only speak HTTP/1.1. Public APIs need translation.
- **Versioning**: Protobuf fields are optional by default, but removing/renaming fields still requires discipline. Breaking changes propagate via generated code.
- **Error model**: gRPC uses status codes + metadata, not HTTP status richness. Mapping to REST errors is manual.
- **Operational coupling**: Version skew between client and server can cause silent failures. You need contract testing and canary rollouts.
- **Cost**: Codegen and schema management add build complexity. Small teams may not benefit.

**Example**

Payments platform. `PaymentService.ProcessPayment` is called 10k RPS from Order, Fraud, and Ledger services in Java, Go, and Python.

Proto:
```proto
service PaymentService {
  rpc ProcessPayment(ProcessRequest) returns (ProcessResponse);
  rpc StreamStatus(stream StatusRequest) returns (stream StatusUpdate);
}
```
Order service uses the generated Go client. Ledger uses Java client. Both compile against the same `.proto`. HTTP/2 multiplexing means one connection per service pair handles thousands of concurrent RPCs. Streaming allows Ledger to push status updates back without polling.

Edge API Gateway translates public REST `POST /payments` to gRPC internally.

**Reasoning challenge**

You are designing a real-time AI assistant backend. Model inference service streams tokens back to the API service, which fans out to WebSocket clients. The API service also calls a user-profile service for each request.

Would you use gRPC for the API-to-model call, API-to-profile call, and API-to-client? What would you use for API-to-client and why? What operational concern becomes critical with streaming gRPC?

**Key takeaway**

- gRPC solves internal service-to-service efficiency and contract safety, not browser interoperability
- The real value is the proto contract + codegen, HTTP/2 + protobuf are enablers
- Choose it for high-throughput microservices, streaming, and polyglot teams; keep REST at the public edge
- Watch for debuggability, versioning discipline, and HTTP/2 network compatibility
