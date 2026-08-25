# Private networking

> **Learning Path:** Security Architecture
> **Section:** 5.2.3 — Enterprise security

**Private networking**

### 1. The problem

You have moved workloads to cloud and broken them into dozens of services. They now talk to each other over the public internet, or over a network you share with everyone else.

That creates three architectural problems:
* **Unnecessary exposure.** Any service with a public IP is an attack surface, even if it only serves internal consumers.
* **Lateral movement.** Once an attacker gets into one internet-reachable service, they can scan and move to others.
* **Data exfiltration and compliance.** Regulated data crossing the public internet triggers audit, legal, and contractual risk.

The problem is not authentication. It is *where the traffic travels and who can reach the network in the first place*.

### 2. Mental model

Think of an office building.

Public internet = the street. Anyone can walk by, see the address, try the door.
Private network = internal corridors with no street access. You need a badge to get into the building, and once inside you move room-to-room without re-entering the street.

Private networking means: resources have no public address, traffic stays on the provider’s backbone, and access is possible only from explicitly allowed private entry points.

### 3. How it works

The essential mechanism is isolation plus controlled ingress/egress.

* **Isolated network namespace:** A VPC / VNet gives you a private IP range. Private subnets have no Internet Gateway.
* **Routing control:** Default routes go to NAT Gateway for outbound only, never to IGW for inbound. No public IPs assigned.
* **Private connectivity:** PrivateLink / Private Service Connect / VPC Endpoint lets a service be reachable via a private IP from within the same cloud boundary, without a public endpoint.
* **Zero public path:** Traffic between services in the same private network never leaves the provider’s fabric.

```
mermaid
flowchart LR
    Client[Public Client] --> IGW[Internet Gateway]
    IGW --> LB[Public LB]
    LB --> PublicSubnet[Public Subnet]
    PrivateSubnet[Private Subnet] -.no IGW.- x
    NAT[NAT Gateway] --> IGW
    PrivateSubnet --> NAT
    PrivateSubnet --> VPC Endpoint
    VPC Endpoint --> S3[Private SaaS / Storage]
```

Public traffic must be explicitly admitted. Private traffic is the default.

### 4. Architectural reasoning

Private networking helps when the *value* of a service is internal and the *cost* of exposure is high.

* **When it helps:** internal APIs, databases, model training jobs, feature stores, queues, and anything handling PII/PHI/financial data. Services that only other services call.
* **What it solves:** removes the internet as an attack vector, reduces blast radius, satisfies data residency and “no public internet” compliance controls.
* **Alternatives:** public endpoint + strong auth + WAF, VPN / Direct Connect for admin access, bastion host.
* **Why choose private:** authentication can be bypassed. Network isolation is defense in depth. It also reduces accidental exposure from misconfiguration.

Rule of thumb: If a service has no legitimate public user, it should have no public network path.

### 5. Trade-offs and failure modes

* **Complexity and operability.** Debugging is harder. You need VPC flow logs, private DNS, and a clear map of endpoints. Engineers expect `curl` from laptop to work.
* **Egress cost and latency.** NAT Gateways and PrivateLink have hourly and data-processing fees. Private connectivity can be cheaper than giant egress but more expensive than direct internet in some cases.
* **Access for humans.** Developers need a private jump path: VPN, bastion, or AWS Session Manager. If that path is poorly designed, teams work around it with public IPs.
* **Failure modes to watch:** leaked public IP on a private instance, default route pointing to IGW, DNS resolution falling back to public, and cross-account peering without strict route filters. One misconfigured security group can punch a hole to the internet.

Private networking does not replace authentication and encryption. It just moves the trust boundary inward.

### 6. Example

Enterprise AI platform with customer data.

* Model training jobs run in a private subnet. They read from an S3 bucket via VPC Endpoint, no internet gateway.
* Inference API is public with auth for customers.
* Internal evaluation service, feature store, and vector DB are private only. They are reached via PrivateLink from the inference service inside the same VPC.
* Admin access is via a private VPN and AWS Systems Manager Session Manager. No bastion host is publicly reachable.

Result: training data never traverses public internet, internal services have zero public attack surface, and compliance audit can demonstrate “data never leaves the private network boundary”.

### 7. Reasoning challenge

You are designing a multi-tenant SaaS with an internal billing reconciliation worker that calls Stripe, reads from a Postgres DB with PII, and is triggered by an SQS queue.

Do you place the worker in a private subnet with NAT Gateway egress only, or give it a public IP with security group restricting inbound? What breaks if you later need to onboard a partner to invoke the worker via API?

Explain your decision in terms of attack surface, egress control, and future integration cost.

### 8. Key takeaway

* Private networking is about *where traffic is allowed to go*, not just who is allowed to use it.
* Default to private for services with no public users; make public access an explicit, justified exception.
* Isolation reduces blast radius and satisfies compliance, at the cost of operational complexity and connectivity constraints.
* PrivateLink / VPC endpoints are the architectural tool that lets private services scale without opening the internet.
