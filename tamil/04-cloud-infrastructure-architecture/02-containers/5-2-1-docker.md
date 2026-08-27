# Docker

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.2.1 — Containers

## 1. Problem

உங்கள் team ஒரு Java service build பண்ணுது. Local laptop-ல `mvn package` ஓடுது, `java -jar` ஓடுது. Staging-க்கு deploy பண்ணும்போது Java version வேற, lib missing, environment variable வேற. "It works on my machine" problem.

Production-ல ஒரு server-ல deploy பண்ணணும். அடுத்த release-க்கு அதே server-ஐ manual-ஆ setup பண்ணணும். Scaling-க்கு புது VM raise பண்ணணும். OS patch, dependency upgrade எல்லாம் downtime உண்டாக்கும்.

இங்கே painful ஆகிறது: **environment consistency, dependency management, release speed, and machine provisioning cost.**

## 2. Mental Model

Docker-ன் core idea simple: app + அதற்கு தேவையான dependencies + runtime + config ஒன்றாக ஒரு standardised package-ஆ போடு. அதை எந்த host-லயும் அப்படியே run பண்ணு.

VM-க்கு முழு OS copy தேவை. Container-க்கு host kernel share பண்ணிக்கொண்டு, process-ஐ isolate பண்ணுவது போதும். Namespace + cgroup வழியாக isolation கிடைக்கும்.

அதனால் ஒரு container என்பது lightweight, fast-starting, portable process wrapper.

## 3. How It Works

Docker image என்பது read-only layers-ன் stack. Base image -> OS packages -> app dependencies -> app code. ஒவ்வொரு layer immutable.

Dockerfile இதை define பண்ணும்:

```
FROM node:20
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
```

`docker build` இதை image ஆக்கும். `docker run` அந்த image-ஐ ஒரு container ஆக start பண்ணும்.

Host-ல Docker engine இருக்கும். அது container-க்கு network namespace, filesystem namespace கொடுக்கும். Multiple containers ஒரே kernel-ல run ஆகும், ஆனால் ஒன்றுக்கொன்று தெரியாது.

```
Host OS + Kernel
  └─ Docker Engine
      ├─ container A: app + node + libs
      ├─ container B: app + node + libs
      └─ container C: postgres
```

VM போல virtual hardware இல்லை. அதனால் start time seconds, resource overhead குறைவு.

## 4. Architectural Reasoning

Docker தீர்க்கும் constraint என்ன?

* **Consistency across environments**: dev, test, prod ஒன்றாக இருக்கும். "works on my machine" முடியும்.
* **Fast provisioning and scaling**: Container start ஆவது milliseconds-seconds. VM நிமிடங்கள்.
* **Dependency isolation**: ஒரு service-க்கு Node 18 வேண்டும், இன்னொன்றுக்கு Java 17 வேண்டும். Same host-ல conflict இல்லாமல் ஓடும்.
* **Immutable artifact**: Image build ஒரு முறை, எங்கே வேண்டுமானாலும் deploy.

Alternatives என்ன? Bare metal, VM, system packages, manual scripts. VM full isolation தரும் ஆனால் heavy. Bare metal cheap ஆனால் operational complexity high. Serverless abstract everything, ஆனால் control குறைவு.

Architect choose Docker when you need portability + density + repeatable builds, and you are okay sharing kernel.

## 5. Trade-offs

**Isolation vs efficiency**: VM full OS isolation தரும். Container kernel-level isolation. Multi-tenant sensitive workloads-க்கு risk.

**Image size and drift**: Base image + layers பெரிதாகும். Unused layers, secret leakage, outdated base images பிரச்சனை. Image governance தேவை.

**State**: Container ephemeral. Database, file uploads போன்ற state-ஐ container-ல வைக்கக்கூடாது. Volume or external service தேவை. Stateful apps-க்கு extra care.

**Security surface**: Privileged container, host mount, misconfigured Dockerfile எல்லாம் escape vector. Runtime security scanning, least privilege run தேவை.

**Operational complexity**: Single monolith deploy எளிது. Container-ல multiple containers orchestrate பண்ண வேண்டும். அதற்கு Kubernetes போன்ற platform வந்தது.

Every solution creates new problem: fast scale கிடைத்தது, ஆனால் networking, service discovery, logging, secret management புது challenge வந்தது.

## 6. Practical Example

Enterprise-ல payment service microservice ஆக split ஆகிறது. `payment-api`, `fraud-check`, `notification` என 3 services.

முன்பு: ஒவ்வொரு service-க்கும் தனி VM, manual apt install, config file copy. Deploy 45 mins.

Docker-க்கு பிறகு:

* ஒவ்வொரு service-க்கும் Dockerfile, image build CI-ல.
* `docker-compose` local-ல முழு stack ஓடும்.
* Production-ல images pull பண்ணி same config-ல run.
* Rollback என்றால் previous image tag-க்கு switch.

அதே image dev laptop, staging, prod எல்லாம் போகும். Debugging-க்கு `docker logs`, `docker exec` போதும்.

## 7. Reasoning Challenge

உங்களிடம் legacy monolith app இருக்கு. அது glibc 2.31, old Python 3.7, custom C library link பண்ணி இருக்கு. இதை production-ல run பண்ண ஒரு dedicated VM இருக்கு.

Requirement: Zero downtime deploy, quick rollback, dev environment replicate.

நீங்கள் Docker-ஐ use பண்ணுவீர்களா? Custom base image build பண்ண வேண்டுமா? அல்லது VM-ஐயே keep பண்ணுவ
