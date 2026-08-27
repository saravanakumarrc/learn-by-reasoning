# ArgoCD

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.4.4 — Platform engineering

## 1. Problem

உங்களுக்கு Kubernetes-ல 30-40 microservices இருக்கு. ஒவ்வொரு service-க்கும் Helm chart இருக்கு. Deployment எப்படி நடக்குது?

Dev பண்ணுவார், `kubectl apply -f` அல்லது CI-ல `helm upgrade` பண்ணுவார். ஒரு நாள் production-ல ஒரு service down ஆகுது. யார் மாற்றம் பண்ணினார்கள்? எந்த commit? எப்போது? தெரியல.

சிலர் production-ல நேரடியாக `kubectl edit` பண்ணி quick fix பண்ணிட்டாங்க. அந்த மாற்றம் Git-ல இல்ல. அடுத்த deployment-ல அது மறைஞ்சிடும். இது drift.

Manual deployment-ல என்ன வலி வரும்?
* Who changed what, when? audit இல்ல
* Desired state vs live state mismatch
* Rollback கடினம்
* Environment promotion-ல human error
* Team A-ன் மாற்றம் Team B-ன் service-ஐ break பண்ணும்

Platform team-க்கு தேவை: Git repo ஒன்று தான் source of truth. மாற்றம் Git-ல மட்டும் வரணும். Cluster அதை தானாக follow பண்ணணும்.

## 2. Mental Model

ArgoCD என்பது GitOps-க்கான pull-based reconciler.

நினைச்சுக்கோங்க: Git repo = desired state. Kubernetes cluster = live state. ArgoCD continuously இரண்டையும் compare பண்ணி, வித்தியாசம் இருந்தால் sync பண்ணும்.

Push model-ல CI pipeline cluster-க்கு push பண்ணும். Pull model-ல ArgoCD தான் Git-ஐ poll பண்ணி, தேவைப்பட்டால் cluster-ஐ மாற்றும்.

அதனால் ArgoCD-க்கு Kubernetes-ல run ஆகும் application-ன் முழு declarative description Git-ல இருக்கணும்.

## 3. How It Works

ஒரு ArgoCD Application resource உருவாக்குறீங்க. அதில் repo URL, path, target Kubernetes cluster, namespace சொல்லுறீங்க.

ArgoCD-க்குள் இரண்டு பகுதி:
* **Repo Server**: Git repo-வை clone பண்ணி, manifest-களை parse பண்ணும். Helm chart-ஐ render பண்ணும்.
* **Application Controller**: Git-ல இருக்கும் desired manifest-ஐ live cluster object-களோட compare பண்ணும். Diff இருந்தால் sync செய்யும்.

Workflow:
Git commit -> ArgoCD detects change -> compare desired vs live -> UI-ல OutOfSync காட்டும் -> auto-sync அல்லது manual approve -> apply -> status update.

ApplicationSet மூலம் ஒரே template-ல 20 service-களுக்கு application auto-generate பண்ணலாம். Image updater போன்ற tools Git-ல image tag-ஐ மாற்றி ArgoCD-ஐ trigger பண்ணும்.

## 4. Architectural Reasoning

ArgoCD useful ஆகும் போது:
* Multiple teams, multiple environments dev/staging/prod
* Declarative Git workflow already இருக்கு
* Audit trail, rollback வேண்டும்
* Self-service platform வேண்டும்

Constraint-ஐ address பண்ணும்:
* **Drift detection**: Live cluster-ல manual மாற்றம் வந்தாலும் ArgoCD கண்டுபிடித்து revert அல்லது alert பண்ணும்
* **Standardisation**: ஒவ்வொரு app-க்கும் Application CR தான் contract
* **Separation of concerns**: Dev team Git-ல PR போடும். Platform team sync policy வைத்திருக்கும்

Alternative என்ன?
* Flux: GitOps, similar pull-based. Community preference மாறும்.
* CI push: Jenkins/GitLab CI `kubectl apply`. Simple ஆனால் drift, audit குறைவு.
* kubectl/Helm manual: Small setup-க்கு okay, scale ஆகாது.

ArgoCD-ஐ choose பண்ணுவது ஏன்? UI-driven, mature RBAC, multi-cluster support, ApplicationSet, progressive delivery integration எளிது.

## 5. Trade-offs

* **Pull vs Push latency**: ArgoCD poll interval சார்ந்தது. உடனடி deployment வேண்டுமெனில் webhook வேண்டும். CI push immediate ஆகும்.
* **Git as source of truth**: Secrets-ஐ Git-ல வைக்க முடியாது. External secret operator, SealedSecrets, Vault integration தேவை. அது complexity add பண்ணும்.
* **Permissions blast radius**: ArgoCD controller-க்கு cluster-ல broad RBAC தேவை. Compromise ஆனால் பெரிய impact.
* **Operability**: ArgoCD itself stateful ஆகும். HA setup, repo server cache, webhook receiver maintain பண்ண வேண்டும். Small team-க்கு overhead.
* **Sync strategy**: Automated sync பண்ணினால் risky. Manual sync + approval வேண்டும். Approval process slow ஆகும்.

Failure mode: Repo unreachable ஆனால் ArgoCD sync முடியாது. Git history rewrite ஆனால் sync break ஆகும். Large manifest diff-ல partial apply fail ஆகி inconsistent state வரும்.

## 6. Practical Example

Fintech company, platform team 3 clusters: dev, staging, prod. 25 microservices, ஒவ்வொன்றுக்கும் mono-repo இல்ல, service repo.

ArgoCD-ல ApplicationSet use பண்ணி `apps/*` folder-ல உள்ள ஒவ்வொரு service-க்கும் application auto-create பண்ணுகிறார்கள். Repo URL, path from git.

Dev: auto-sync enabled. Staging: sync + manual approval. Prod: sync window 10am-6pm, approval by two platform engineers.

Developer PR merge பண்ணியதும் ArgoCD dev cluster-ஐ auto sync பண்ணும். CI-ல image build ஆனதும் Git image tag-
