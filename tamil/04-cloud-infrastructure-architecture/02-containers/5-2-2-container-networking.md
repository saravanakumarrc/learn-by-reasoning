# Container networking

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.2.2 — Containers

## Problem

உங்ககிட்ட ஒரு host இருக்கு. அதுல 50 containers ஓடுது. ஒவ்வொன்னும் ஒரு microservice. Order service, Payment service, Inventory service.

VM காலத்துல ஒவ்வொரு service-க்கும் ஒரு VM, அதுக்கு ஒரு IP, routing எல்லாம் clear.

Container-ல kernel share பண்ணுறோம். ஒவ்வொரு container-க்கும் தனி network namespace கொடுத்துட்டோம். அப்போ container-க்குள்ள `eth0` இருக்கு, `localhost` இருக்கு, ஆனா அது வெளி உலகத்துக்கு தெரியாது.

இப்போ Order service Payment service-ஐ `http://payment:8080`ன்னு call பண்ணனும். அந்த IP எங்க இருக்கு? Container start ஆனதும் stop ஆனதும் IP மாறும். Host ல இருந்து எப்படி பேசும்? Multi-node cluster-ல இன்னொரு node-ல இருக்கும் container-க்கு எப்படி போகும்?

இது painful ஆனதால்தான் container networking தேவைப்பட்டது.

## Mental Model

Container-ஐ ஒரு process மாதிரி நினைக்காதீங்க. அது ஒரு isolated network stack உள்ள process.

Network namespace = தனி network interface, routing table, firewall rules.

Host-ல இருந்து container-க்கு போக `veth pair`ன்னு ஒரு virtual cable போடுறோம். ஒரு முனை container-ல, ஒரு முனை host bridge-ல.

அதனால container-க்கு தனி IP கிடைக்கும், ஆனா host kernel தான் traffic-ஐ forward பண்ணும்.

Kubernetes-ல இதை ஒரு step மேல எடுத்துட்டாங்க: Pod-க்கு ஒரு IP, அந்த IP cluster-முழுக்க reachable ஆகணும்.

## How It Works

Single node-ல Docker:

`container eth0 <--> veth pair <--> docker0 bridge <--> host network`

Container-க்குள்ள `eth0` க்கு 172.17.0.x கிடைக்கும். `docker0` bridge அதை host-க்கு connect பண்ணும். Port mapping ` -p 8080:80` என்றால் host firewall + NAT பண்ணி வெளி request-ஐ உள்ளே கொண்டு வரும்.

Multi-node cluster-ல:

ஒவ்வொரு node-க்கும் pod CIDR கிடைக்கும். Node A-ல 10.244.1.0/24, Node B-ல 10.244.2.0/24.

A-ல இருக்கும் Pod B-ல இருக்கும் Pod-ஐ அடைய:

1. **Underlay routing**: ஒவ்வொரு node-லும் pod CIDR-ஐ advertise பண்ணி, host network-ல direct route போடுறது. Calico இது பண்ணும்.
2. **Overlay network**: Host IP-கள் மட்டுமே routing தெரியும். Pod traffic-ஐ VXLAN / IPIP-ல encapsulate பண்ணி கொண்டு போவது. Flannel இது பண்ணும்.
3. **eBPF data plane**: Cilium மாதிரி kernel-லேயே programmable datapath போட்டு, IP + policy enforce பண்ணும்.

இதுக்கு மேல Kubernetes Service + DNS layer வரும். Service ஒரு stable virtual IP + kube-proxy / iptables / eBPF rules வைத்து backend pod-களுக்கு load balance பண்ணும்.

```
Pod A -> veth -> CNI -> Node network -> Overlay/Route -> Node B network -> CNI -> Pod B
```

## Architectural Reasoning

Container networking தேவைப்படும் constraints:

* **Isolation**: Containers ஒன்றுக்கொன்று தனித்து இருக்கணும், ஆனா communicate பண்ணணும்.
* **Ephemeral identity**: Pod start/stop ஆகும், IP மாறும். Service discovery தேவை.
* **Multi-node reachability**: ஒரு node-ல ஆரம்பித்த request இன்னொரு node-ல முடியணும்.
* **Policy**: எந்த service எந்த service-ஐ அணுகலாம் என்பதை control பண்ணணும்.

என்ன choose பண்ணுவீங்க?

* Small single node dev: Docker bridge போதும்.
* Production k8s on-prem: Calico for pure routing, low latency.
* Cloud VPC native: CNI that uses VPC IP directly, no overlay overhead.
* High policy / observability: Cilium eBPF.

## Trade-offs

**Host network vs Pod network**
Host network latency குறைவு, ஆனா isolation போய் port conflict வரும். Security team கண்டிப்பாக allow பண்ண மாட்டார்கள்.

**Overlay vs Underlay**
Overlay simple to setup, ஆனா encapsulation overhead + MTU issues. Underlay efficient, ஆனா network admin-க்கு pod CIDR routing setup பண்ணணும்.

**IP per Pod vs IP per Node**
IP per Pod = fine-grained, ஆனா IP exhaustion / routing table size. IP per Node + NAT = சிக்கனம், ஆனா debugging கடினம்.

**CNI complexity**
CNI plugin தான் network create பண
