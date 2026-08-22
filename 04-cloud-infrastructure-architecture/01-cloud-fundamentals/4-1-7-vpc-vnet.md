# VPC/VNet

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.1.7 — Cloud fundamentals

**VPC / VNet**

### 1. The problem

You are moving workloads to a shared cloud. The physical network is multi-tenant. You need:

* Logical isolation from other customers
* Private IP space for your services to talk without traversing the public internet
* Control over routing, segmentation, and ingress/egress
* Predictable network identity for security policies

Without that, every service is exposed to the internet, you cannot enforce private communication, and you cannot model on-premises network boundaries in the cloud.

### 2. Mental model

A VPC / VNet is your private virtual datacenter network inside a public cloud.

You own a private RFC1918 CIDR block, e.g. `10.0.0.0/16`. Inside it you carve subnets, attach route tables, and define who can talk to whom. It is not a physical network, it is a logically isolated soft network with its own routing plane.

Think of it as a leased data center floor: you get the walls, you decide where the rooms are, and the cloud provider handles the building.

### 3. How it works

Essential mechanisms only:

* **CIDR and subnets.** The VPC defines an IP range. Subnets partition it by placement and access, e.g. public vs private.
* **Route tables.** Determine where traffic goes: to another subnet, to a NAT gateway, to an Internet Gateway, to a transit gateway.
* **Gateways.** Internet Gateway for inbound/outbound internet, NAT Gateway for private subnets to egress, PrivateLink/Private Service Connect for private SaaS access.
* **Network security.** Security groups are stateful allow-lists attached to instances. Network ACLs are stateless subnet firewalls. Both enforce the trust boundary.
* **Isolation.** By default, VPC traffic stays inside the VPC. Cross-account or cross-region requires explicit peering or transit.

`flowchart LR
Internet --> IGW[Internet Gateway]
IGW --> VPC[VPC / VNet 10.0.0.0/16]
VPC --> Pub[Public Subnet]
VPC --> Priv[Private Subnet]
Pub --> ALB[Load Balancer]
ALB --> App[App Tier]
Priv --> App
Priv --> DB[(Database)]
Pub --> NAT[NAT Gateway]
NAT --> Internet
`

### 4. Architectural reasoning

When it helps:
* You need a private backbone for services that should never be public.
* You need network segmentation for compliance or blast radius control.
* You need deterministic routing for hybrid cloud with on-prem via VPN/Direct Connect.

Alternatives:
* Flat public subnets with security groups only. Cheaper, but everything is internet-reachable by mistake.
* Host-level firewall only. Weaker isolation, harder to audit.
* Service mesh with mTLS only. Solves app-layer identity, not network reachability.

Choose VPC when network-level isolation and control are architectural requirements, not just convenience. It enables the decision to keep data planes private by default and expose only a controlled edge.

### 5. Trade-offs and failure modes

* **IP exhaustion.** CIDR is hard to change later. Architects over-allocate or use /16 per VPC and plan for secondary CIDRs early.
* **Routing sprawl.** Transit peering meshes create O(n²) complexity. Use a hub-spoke model with a transit gateway.
* **Security group sprawl.** Implicit deny is good until you have hundreds of permissive rules. Default deny, least privilege, and central review matter.
* **Latency and cost.** NAT gateways, cross-AZ traffic, and inter-region peering add cost and latency. Private services via PrivateLink cost more than public endpoints but avoid data exfiltration risk.
* **Failure mode:** Misconfigured route table sends private DB traffic to internet. Security group allows 0.0.0.0/0 on port 22. Both are silent until breach.

### 6. Example

Payments service on AWS.

* VPC `10.0.0.0/16` with private subnets in 3 AZs for app and Aurora.
* Public subnet with ALB fronting app tier.
* No public IPs on app or DB. App reaches internet via NAT for patches.
* Security groups: ALB allows 443 from internet; App allows 8080 only from ALB SG; DB allows 5432 only from App SG.
* PrivateLink to internal fraud detection service.

Result: data plane is never internet reachable, blast radius is limited per AZ, audit surface is small.

### 7. Reasoning challenge

You have a SaaS with 3 tenants that must be logically isolated but share the same VPC for cost reasons. One tenant requires PCI data to stay in EU, another needs low-latency access to a US SaaS API. How would you segment networking, and what VPC design choices would you make or avoid?

### 8. Key takeaway

* VPC/VNet exists to give you private, isolated network control in a multi-tenant cloud.
* Design for private-by-default: public subnets only for edge, private subnets for workloads.
* CIDR and routing are architectural decisions, not operational tweaks.
* Security is layered: network ACLs + security groups + private connectivity.
