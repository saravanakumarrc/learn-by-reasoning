# Networking

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.1.3 — Cloud fundamentals

## Problem

Cloud-ல ஒரு service deploy பண்ணினீங்க. Local-ல perfect-ஆ work ஆகுது. Cloud-ல எதிர்பாராத timeout, intermittent failure, slow response வருது.

ஒரு distributed system-ல service A service B-ஐ call பண்ணும்போது network failure வரலாம். Packet loss ஆகலாம். Latency spike ஆகலாம். Connection reset ஆகலாம்.

இது code bug இல்லை. Network-ஐ reliable pipe மாதிரி நினைத்தது தான் பிரச்சனை. Cloud-ல நீங்கள் wires-ஐ own பண்ணல. Shared network-ல run பண்றீங்க.

## Mental Model

Network = best effort delivery system.

நீங்கள் TCP use பண்றீங்கன்னா, connection ஆகும். Handshake, retransmit, ordering எல்லாம் வரும். ஆனாலும் network congested ஆனால் latency increase ஆகும். Packet drop ஆனால் retry ஆகும். Timeout வரும்.

Cloud-ல இதுக்கு மேல ஒரு layer இருக்கு. VPC, subnet, route table, security group, load balancer. இது எல்லாம் நீங்கள் control பண்ணக்கூடிய logical network boundaries.

Key idea: **நெட்வொர்க் ஒரு constraint**. Latency, bandwidth, cost, security எல்லாம் இங்கே தீர்மானிக்கப்படும்.

## How It Works

Request flow basic-ஆ இப்படி:

```
Client -> DNS -> Load Balancer -> Service in private subnet -> Database
```

DNS name resolve ஆகி IP கிடைக்கும். TCP 3-way handshake ஆகும். TLS handshake ஆகலாம். Request போகும். Response வரும்.

Cloud networking-ல முக்கியமான layer:

* **VPC**: உங்கள் private network boundary. IP range உங்கள் கட்டுப்பாட்டில்.
* **Subnet**: AZ-க்குள் isolate பண்ணும். Public subnet-ல Internet Gateway இருக்கும். Private subnet-ல NAT Gateway மூலம் outbound மட்டும்.
* **Route Table**: traffic எங்கே போகணும் என்பதை சொல்லும்.
* **Security Group**: stateful firewall. Instance level.
* **NACL**: stateless subnet level.

East-West traffic என்பது service to service உள்ளே. North-South என்பது internet-ல இருந்து உள்ளே.

## Architectural Reasoning

Cloud-ல network design பண்ணும்போது இதை கேட்கணும்:

**Traffic எங்கிருந்து வருது, எங்கே போகுது?**

Public API வேணுமா? App load balancer public subnet-ல வைக்கலாம். Backend services private subnet-ல வைக்கலாம். DB கூட private.

**Cross AZ / Region தேவையா?**

Same AZ-ல latency குறைவு, cost குறைவு. Multi-AZ deploy பண்ணி high availability வேணும்னா cross AZ traffic வரும். அது cost ஆகும்.

**Private connectivity தேவையா?**

On-prem system connect வேணும்னா VPC peering, Transit Gateway, AWS PrivateLink / Azure Private Link use பண்ணணும். Public internet வழியா போகக்கூடாது.

**Service discovery எப்படி?**

DNS + internal load balancer. Service mesh-ல mTLS, traffic routing.

Network-ஐ explicit-ஆ design பண்ணுவது reliability மற்றும் security-க்கு முக்கியம்.

## Trade-offs

* **Latency vs Availability**: Same AZ cheap & fast, multi-AZ resilient but higher latency & cost. Cross region even more.
* **Public exposure vs Security**: Public IP கொடுத்தால் simple ஆனால் attack surface அதிகம். Private + load balancer + security group என்பது complex ஆனால் safe.
* **Operational simplicity vs Cost**: NAT Gateway simple ஆனால் hourly cost + data processing. VPC endpoints அதிக setup ஆனால் cheaper & private.
* **Throughput vs Connection limits**: TCP connection reuse, keep-alive பண்ணலைன்னா connection churn வரும். Load balancer connection limits வரும்.

Failure modes: DNS fail, routing misconfig, security group block, AZ outage, network partition. இது எல்லாம் application error-ஆ தெரியும்.

## Practical Example

E-commerce checkout service. API Gateway -> ALB -> 3 microservices in EKS
