# Private networking

> **Learning Path:** Security Architecture
> **Section:** 6.2.3 — Enterprise security

# Private Networking — Enterprise Security

## 1. Problem

ஒரு enterprise-ல் core services எல்லாம் cloud-ல ஓடுது. Payment service, ledger service, customer PII store போன்றவை.

அவை public subnet-ல public IP வாங்கி நிற்கும் போது என்ன ஆகும்?

Internet-ல இருந்து direct scan பண்ண முடியும். Security group தவறாக திறந்தால், zero-day வந்தால், misconfiguration நடந்தால், எல்லாம் வெளியே தெரியும். Compliance audit-ல fail ஆகும்.

அதே service-கள் ஒன்றுக்கொன்று பேசும் traffic கூட public internet வழியாக போனால், data leak ஆகும், latency unpredictable ஆகும், cost அதிகமாகும்.

**பிரச்சனை:** நமக்கு வேண்டியது internal communication மட்டும் private-ஆ இருக்க வேண்டும், external access மட்டும் கட்டுப்படுத்தப்பட வேண்டும்.

## 2. Mental Model

Private networking என்பது office-ல உள்ள internal LAN-ஐ cloud-ல extend பண்ணுவது.

உள்ளே இருக்கும் service-களுக்கு RFC1918 private IP வழங்கப்படும். அந்த IP internet-ல இருந்து route ஆகாது. Traffic provider-ன் backbone-ல மட்டும் இருக்கும்.

அதாவது, public phone number கொடுக்காமல் internal extension மூலம் மட்டும் பேசும் அமைப்பு.

## 3. How It Works

Enterprise-ல இது பெரும்பாலும் இப்படி அமைகிறது:

* **VPC + Private Subnet:** Public subnet-ல IGW இருக்கும். Private subnet-ல IGW இல்லை. Route table-ல default route internet-க்கு இல்லை.
* **Egress control:** Private subnet-ல இருந்து internet வேண்டுமெனில் NAT Gateway / NAT Instance வழியாக மட்டும். Ingress இல்லை.
* **Private connectivity:** On-prem data center-க்கு VPN / Direct Connect. Service to service-க்கு VPC Peering, Transit Gateway, PrivateLink.
* **Zero public exposure:** Service-களுக்கு public IP இல்லை. Access via private DNS, internal load balancer மட்டும்.

டேட்டா packet எப்போதும் provider network-லயே இருக்கும், public internet-ல தொடாது.

## 4. Architectural Reasoning

Private networking useful ஆகும் போது:

* **Sensitive workload:** PCI, HIPAA, financial core data. Data internet-ல expose ஆகக்கூடாது.
* **Service-to-service trust:** Microservices ஒன்றுக்கொன்று தொடர்பு கொள்ளும் போது, public internet வழியாக போக வேண்டாம்.
* **Compliance boundary:** Audit-ல "data does not leave private network" என்று காட்ட வேண்டும்.

Alternatives என்ன?

* Public subnet + strict security group: Simple, ஆனால் attack surface அதிகம்.
* Public internet + VPN: Access கிடைக்கும், ஆனால் performance மற்றும் reliability குறைவு.
* Service Mesh with mTLS over public: Encryption இருக்கும், ஆனால் network layer-ல exposure இருக்கும்.

Architect ஏன் private-ஐ தேர்வு செய்கிறார்? Attack surface-ஐ drastically குறைக்க, data exfiltration risk-ஐ குறைக்க, மற்றும் operational control முழுமையாக வைத்துக்கொள்ள.

## 5. Trade-offs

* **Security vs Accessibility:** Private-ஆ இருந்தால், எல்லா access-க்கும் bastion host / jump box / VPN வேண்டும். Developer debug செய்ய கடினம்.
* **Cost:** NAT Gateway hourly + data processing charge. PrivateLink, Direct Connect initial investment அதிகம்.
* **Operational complexity:** Route table, NACL, security group, peering limits எல்லாம் manage பண்ண வேண்டும். Misconfiguration-ல service unreachable ஆகும்.
* **Failure mode:** NAT Gateway single point of failure ஆகும். AZ fail ஆனால் egress தடை. Private DNS resolution fail ஆனால் internal name resolve ஆகாது.

Every architectural solution creates another trade-off.

## 6. Practical Example

Bank-ல core ledger service private subnet-ல ஓடுகிறது. Public IP இல்லை.

API Gateway public-ல இருக்கும். அது PrivateLink மூலம் internal service-ஐ reach பண்ணும். Internet traffic ledger-ஐ touch செய்யாது.

Fraud detection SaaS vendor-க்கு outbound call தேவை. அதற்கு NAT Gateway வழியாக மட்டும் egress. Logging VPC Flow Logs-ல.

இதனால் ledger எப்போதும் internet-ல இருந்து invisible. Compliance team happy. ஆனால் on-call engineer-க்கு troubleshooting-க்கு bastion host வழியாக SSH வேண்டும்.

## 7. Reasoning Challenge

உங்களிடம் 3 environments இருக்க
