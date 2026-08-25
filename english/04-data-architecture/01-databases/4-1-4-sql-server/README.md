# SQL Server

> **Learning Path:** Data Architecture
> **Section:** 3.1.4 — Databases

## The problem

You need durable, consistent relational storage that multiple applications trust for business-critical data, with strong transactional guarantees, fine-grained security, and predictable operational tooling.

The naive approach — files, NoSQL stores, or homegrown storage — fails when you need:
* ACID transactions across multiple tables
* Declarative querying with joins, aggregations, and constraints enforced by the engine
* Role-based security and auditability integrated with enterprise identity
* A single source of truth that reporting, OLTP, and ETL can all rely on without custom synchronization

That need created relational databases. SQL Server is Microsoft's implementation optimized for Windows/.NET enterprises.

## Mental model

Think of SQL Server as an integrated data platform, not just a query engine.

```
Client App --> SQL Server Engine --> Buffer Pool --> Storage Engine
                                   --> Transaction Log --> Durable Disk
                                   --> Security / AD Integration
```

The engine owns data pages in memory, writes changes to a write-ahead log first, then flushes to data files. Everything is governed by T-SQL and the storage engine's locking and recovery mechanisms.

## How it works, essentially

**Write path:** Transaction → log record written and hardened → changes applied to in-memory pages → eventually flushed to .mdf/.ndf. Recovery is log-driven.

**Read path:** Query optimizer builds plan → uses statistics and indexes → engine acquires locks/reads from buffer pool.

**High availability core:** Always On Availability Groups replicate a primary replica to secondaries with synchronous or asynchronous commit. Read-scale offloads, failover is automatic.

**Enterprise glue:** Windows Authentication / Active Directory integration, T-SQL procedural language, Service Broker, Integration Services, and since 2022 native vector search and in-database ML for AI workloads.

You don't need every feature. You need the mental model: log-first durability, buffer pool, and lock-based concurrency.

## Architectural reasoning

When SQL Server helps:

* **Existing Microsoft stack.** .NET applications, Azure AD, Power BI, and SharePoint already live there. Integration cost drops.
* **Strong relational guarantees required.** Financial ledgers, inventory, HR, ERP where correctness > raw scale.
* **Operational requirements.** Built-in backups, point-in-time restore, auditing, TDE, Always Encrypted for compliance.
* **Hybrid/on-prem constraints.** Air-gapped systems, regulated data that can't leave premises.

Alternatives:
* **PostgreSQL/MySQL** for open-source, lower licensing cost, cross-platform.
* **Cloud-native serverless** like Azure SQL, Aurora for elasticity.
* **Distributed SQL / NewSQL** when you need horizontal write scale beyond one node.

Choose SQL Server when the decision is driven by ecosystem fit and enterprise operations, not raw price per query.

## Trade-offs and failure modes

* **Licensing cost and lock-in.** Per-core licensing is expensive. T-SQL and proprietary features increase migration cost.
* **Vertical scale bias.** It scales up very well, scales out less naturally than distributed stores. Large OLTP workloads hit a single primary.
* **TempDB contention.** Sorting, spills, and version store contention on TempDB is a classic bottleneck under high concurrency.
* **Blocking and deadlocks.** Lock escalation and long transactions stall OLTP. Needs proper indexing and transaction design.
* **Log growth and I/O.** Unbounded log growth during bulk operations, or slow storage, kills availability.

Architects remember: SQL Server rewards careful schema design, indexing, and transaction boundaries. It punishes chatty apps and long-running transactions.

## Example

A regional bank runs core accounts on SQL Server on-prem with Always On Availability Groups. Primary handles transactions, secondary is readable for reporting. Windows Authentication ties directly to AD groups for least privilege. TDE protects data at rest for PCI.

When they add fraud detection, they use SQL Server 2022 vector search to store embeddings alongside transaction data, allowing a single query to join relational facts with similarity search without moving data to a separate vector DB. The decision is architectural: keep the source of truth in one engine to avoid sync complexity.

## Reasoning challenge

You are designing a new SaaS product on Azure. Workload is 70% relational OLTP, 30% analytical queries, with expected 10x growth in 18 months. Team is .NET-first, but cost sensitive.

Do you start with Azure SQL Database serverless, provisioned SQL Server on VMs, or PostgreSQL on Azure? What signals would make you switch later?

## Key takeaway

* SQL Server exists to provide ACID relational durability with enterprise integration on Windows/.NET.
* Its core value is operational maturity, security, and ecosystem fit, not cheapest query.
* Design for log durability, indexing, and short transactions; avoid TempDB and blocking pitfalls.
* Choose it for compliance-heavy, Microsoft-centric workloads; avoid it when you need cheap horizontal write scale or full portability.
