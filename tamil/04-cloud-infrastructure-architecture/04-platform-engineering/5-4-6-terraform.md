# Terraform

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.4.6 — Platform engineering

## 1. Problem

உங்கள் team Cloud-ல VPC, subnets, security groups, EKS cluster, RDS, S3 bucket எல்லாம் console-ல கையால் க்ளிக் பண்ணி create பண்ணுது. ஒரு engineer-க்கு setup செய்ய 3 மணி நேரம் ஆகுது. Wiki-ல steps இருக்கு, ஆனால் யாரும் அதை update பண்ண மாட்டேங்குறாங்க.

அடுத்த sprint-ல dev environment-க்கு மட்டும் ஒரு extra security group rule add ஆகுது. Production-ல அது இல்ல. ஒரு engineer தற்செயலாக production RDS-ஐ terminate பண்ணிட்டான். Rollback-க்கு என்ன செய்வது என்று தெரியல.

இது pain எங்கே? **Manual change = undocumented change**. Reproducibility இல்ல, review இல்ல, audit trail இல்ல. Infrastructure-ஐ code மாதிரி treat பண்ண முடியல.

இந்த பிரச்சனை பெரிதாகும்போது தான் Terraform வருது.

## 2. Mental Model

Terraform என்பது **declarative infrastructure state-ஐ code-ல வைத்து, real world state-ஐ அதற்கு converge பண்ணும் engine**.

நீங்கள் சொல்லுவது: "எனக்கு இந்த VPC இப்படி இருக்க வேண்டும்". Terraform பார்க்கும்: "இப்போது எப்படி இருக்கு? வித்தியாசம் என்ன? எந்த order-ல apply பண்ணணும்?".

இது recipe போல. Manual cooking-ல chef memory-யை நம்புறான். Recipe-ல ingredients list இருந்தால் யார் வேண்டுமானாலும் அதே dish-ஐ reproduce பண்ண முடியும்.

## 3. How It Works

மூன்று core ideas:

**1. HCL configuration:** Resource-களை declare பண்ணுவீங்க.
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
```
Provider plugin cloud API-களை கவனிக்கும்.

**2. State file:** Terraform cloud resources-ன் actual state-ஐ `.tfstate`-ல track பண்ணும். இதுதான் source of truth. State இல்லாமல் drift தெரியாது.

**3. Plan / Apply loop:**
* `terraform plan` - desired state vs real state compare பண்ணி diff காட்டும்.
* `terraform apply` - dependency graph பார்த்து correct order-ல create/update/delete பண்ணும்.

Module என்பது reusable building block. Team-க்குள் standard EKS module, VPC module என share பண்ணலாம்.

## 4. Architectural Reasoning

Terraform எப்போது useful?

* Multi-environment parity வேண்டும்: dev, staging, prod ஒரே definition-ல இருக்கணும்.
* Platform team self-service வழங்க வேண்டும்: dev teams-க்கு "eks module-ஐ call பண்ணுங்க" என்று கொடுக்கணும்.
* Audit, review, CI/CD integration வேண்டும்.

Alternatives என்ன?
* CloudFormation / CDK - AWS native, ஆனால் multi-cloud கஷ்டம்.
* Pulumi - real programming language, ஆனால் state model வேறு.
* Ansible / Chef - imperative, configuration management.

Architect ஏன் Terraform தேர்வு செய்வார்? Declarative + provider ecosystem + mature state management + module reusability. Team already Git workflow use பண்ணுறது என்றால் Terraform fit ஆகும்.

## 5. Trade-offs

**State management is a liability.** State file centralized, sensitive, corrupt ஆனால் disaster. Remote backend with locking தேவை. S3 + DynamoDB lock பொதுவான pattern.

**Drift.** யாராவது console-ல manual change பண்ணினால் Terraform அதை தெரிந்து கொள்ளாது. `terraform plan` drift-ஐ catch பண்ணும், ஆனால் process-ஐ enforce செய்ய வேண்டும்.

**Complexity moves.** Manual click complexity configuration complexity ஆக மாறும். Module boundaries, variables, outputs, data sources design தேவை. Bad module = worse than manual.

**Vendor abstraction cost.** Provider updates late வரும், cloud feature Terraform support-க்கு காத்திருக்க வேண்டி வரும்.

Every architectural solution creates another problem. Terraform gives repeatability, ஆனால் state ownership, access control, module versioning போன்ற operational problems கொடுக்கும்.

## 6. Practical Example

Platform engineering team-க்கு 10 product teams EKS cluster வேண்டும். அவரவர் console-ல create பண்ணினால் security group rules, node sizing, logging எல்லாம் inconsistent ஆகும்.

Platform team ஒரு Terraform module உருவாக்கும்:
`modules/eks-platform` - VPC, EKS, node groups, IRSA, logging, monitoring default-ல.

Product team `main.tf`-ல:
```hcl
module "platform_eks" {
  source = "git::..."
  team_name = "payments"
  node_instance_type = "m6
