# Infrastructure as Code

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.4.5 — Platform engineering

## 1. Problem

நீங்கள் ஒரு team-ல் இருக்கிறீர்கள். 3 environments இருக்கு: dev, staging, prod. ஒவ்வொரு முறையும் ஒரு new service deploy பண்ணும்போது EC2 create பண்ணணும், security group rule add பண்ணணும், RDS instance size மாற்றணும், VPC peering enable பண்ணணும்.

இதை ஒரு senior engineer கைமுறையாக AWS console-ல் க்ளிக் க்ளிக் பண்ணி செய்வார். 

இரண்டு மாதம் கழித்து:

* dev-ல் ஒரு rule இருக்கு, prod-ல் இல்லை
* ஒரு instance-ன் type யார் மாற்றினார்கள் என்று தெரியவில்லை
* rollback பண்ண வேண்டுமென்றால் என்ன மாற்றினோம் என்று ஞாபகம் இல்லை
* new team member join பண்ணினால், environment-ஐ replicate பண்ண முடியாது

**What goes wrong if we don't have this?** Manual infra = snowflake servers, drift, tribal knowledge, slow onboarding, human error, audit-க்கு proof இல்லை.

இந்த pain தான் Infrastructure as Code வந்ததற்கு காரணம்.

## 2. Mental Model

Infrastructure as Code என்பது infrastructure-ஐ application code போல் treat பண்ணுவது.

Code இருப்பது போல்:

* version control ல இருக்கும்
* peer review ஆகும்
* CI/CD மூலம் apply ஆகும்
* change history தெரியும்
* reproduce பண்ண முடியும்

Mental model: **Desired state-ஐ describe பண்ணு, tool அதை actual state-க்கு converge பண்ணும்.**

இது imperative ஆக "இதை create பண்ணு, அதை attach பண்ணு" என்று கட்டளை அளிப்பதல்ல. பெரும்பாலும் declarative ஆக "எனக்கு 3 AZ-களில் 2 node-கள் கொண்ட ECS cluster வேண்டும்" என்று சொல்வது.

## 3. How It Works

ஒரு IaC tool இரண்டு விஷயங்களை செய்கிறது:

1. **Definition**: Terraform HCL, CloudFormation JSON/YAML, Pulumi TypeScript/Python போன்ற மொழியில் infra-ஐ define பண்ணுவது
2. **State management**: என்ன உருவாக்கப்பட்டுள்ளது என்பதை state file-ல் track பண்ணுவது

Flow:
Git commit → PR review → CI pipeline → `terraform plan` → approval → `terraform apply` → cloud resources created/updated

Drift detection என்பது actual cloud state vs desired state-ஐ ஒப்பிடுவது. `terraform plan` அதை காட்டும்.

Immutable infra pattern-உம் இங்கிருந்து வருகிறது. Server-ஐ patch பண்ணாமல், definition மாற்றி redeploy பண்ணுவது.

## 4. Architectural Reasoning

எப்போது useful?

* Multiple environments replicate பண்ண வேண்டும்
* Team size > 1, collaboration தேவை
* Compliance / audit trail தேவை
* Disaster recovery, region failover தேவை
* Platform team self-service வழங்க வேண்டும்

Constraint it addresses: **operational consistency மற்றும் repeatability.**

Alternatives:

* Manual console + runbooks
* Configuration management tools மட்டும்: Ansible, Chef, Puppet — இவை existing servers-ஐ configure பண்ணும், servers-ஐ create பண்ணாது
* Full platform abstraction: Terraform Cloud, Pulumi ESC, internal self-service platform

Architect ஏன் தேர்வு செய்வார்? Because infra changes become code reviewable, testable, reversible.

Consequence: நீங்கள் இப்போது state management, secrets handling, blast radius, dependency ordering போன்ற புதிய problems-ஐ சந்திக்க வேண்டும்.

## 5. Trade-offs

**Consistency vs complexity.** IaC குறைவான drift கொடுக்கும், ஆனால் initial setup, state locking, module design செலவு உண்டு.

**Declarative safety vs fine control.** Declarative ஆக சொன்னால் tool எப்படி செய்யும் என்பது உங்கள் கட்டுப்பாட்டில் இல்லை. Edge case-ல் imperative escape hatch தேவைப்படும்.

**State file என்பது single point of failure.** Terraform remote state S3 + DynamoDB lock இல்லாமல் team-ல் concurrent apply = corruption. State security கவனிக்க வேண்டும்.

**Speed vs safety.** Small change கூட full plan run ஆகும். Large monorepo-ல் `apply` slow ஆகும். அதற்காக workspaces, modules, targeted apply போன்ற patterns வரும்.

Failure mode: யாரோ console-ல் manual change பண்ணினால், அடுத்த apply-ல் அது overwrite ஆகும் அல்லது drift ஆகிவிடும். இதற்கு policy-as-code, OPA, SCP, மற்றும் least-privilege access தேவை.

## 6. Practical Example

Enterprise microservices platform.

Platform team ஒரு `network` module உருவாக்குகிறது: VPC, private/public subnets, NAT, security groups. App team ஒரு `app` module உருவாக்குகிறது: ECS cluster, Fargate service, RDS.

Repo structure:
```
infra/
  modules/network/
  modules/app/
  environments/dev/
  environments/prod/
```

PR வருகிறது: prod-ல் RDS instance type db.r5.large → db
