# Persistent volumes

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.14 — Kubernetes

## 1. Problem

உங்க application ஒரு Pod-ல ஓடுது. அந்த Pod-க்குள்ள container `/data` folder-ல file எழுதுது. சரி.

இப்போ Node crash ஆச்சு, அல்லது Pod evict ஆச்சு, அல்லது Deployment-ல rolling update பண்ணினீங்க. புது Pod வேற Node-ல ஏறுது.

என்ன ஆச்சு? எல்லா data-வும் போச்சு.

Pod என்பது ephemeral. Container filesystem restart ஆனால் போயிடும். `emptyDir` கூட Pod வாழ்க்கையோடு முடிஞ்சுடும்.

இதை ஏன் ஏற்படுத்துகிறீர்கள்? Database, file upload service, job output, cache warm data மாதிரி stateful workloads-க்கு இது fatal.

> Problem என்ன? Pod மாறும், data நிலைக்க வேண்டும்.

## 2. Mental Model

Pod = cattle. Storage = pet.

Kubernetes-ல persistent storage-க்கு நீங்கள் Pod-லிருந்து storage-ஐ detach பண்ணி, lifecycle-ஐ independent ஆக்கணும்.

Persistent Volume என்பது cluster-ல உள்ள storage resource. PersistentVolumeClaim என்பது application-ன் storage request.

Pod மாறினாலும், அதே PVC-யை mount பண்ணும் புது Pod-க்கு data தொடரும்.

## 3. How It Works

நீங்கள் செய்வது மூன்று layer:

**StorageClass → Provisioner → PV → PVC → Pod**

StorageClass வரையறுக்கும்: dynamic provisioning எப்படி நடக்கும், storage type என்ன - SSD, NFS, EBS, GCE PD.

PVC ஒரு claim. `storage: 20Gi, accessModes: ReadWriteOnce` என request பண்ணுவீங்க.

Control plane matching பண்ணி PV-வை bind பண்ணும். Pod-ல volumeMount பண்ணினால், அந்த PV உங்க container path-ல mount ஆகும்.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-ssd
```

Pod-ல:
```yaml
volumes:
- name: data
  persistentVolumeClaim:
    claimName: app-data
volumeMounts:
- name: data
  mountPath: /data
```

Node-ல Pod schedule ஆன பிறகு, PV அந்த Node-க்கு attach ஆகும்.

## 4. Architectural Reasoning

Persistent Volume தேவைப்படுவது எப்போது?

* Pod restart ஆனாலும் data தேவை
* Pod node மாறினாலும் data தேவை
* Multiple replicas ஒரே data-வை share செய்ய வேண்டும்

Alternatives:
* `emptyDir`: Pod வாழ்நாளுக்கு மட்டும். Ephemeral workloads-க்கு சரி.
* `hostPath`: Node local. Node மாறினால் data போகும். Anti-pattern.
* Persistent Volume: Cluster managed, durable.

Decision point: StatefulSet + PVC பயன்படுத்துவது ஒரு Pod-க்கு ஒரு stable identity + stable storage வேண்டும் என்பதற்கு. MySQL, Redis, Kafka brokers மாதிரி.

Deployment + PVC என்பது single writer சூழல். ReadWriteOnce-ல multiple replicas mount பண்ண முடியாது.

## 5. Trade-offs

**Performance vs Durability:** Network storage EBS/GCE PD latency அதிகம். Local SSD வேகம் அதிகம் ஆனால் node failure-ல data போகும். Local PV pod reschedule ஆகாது.

**Access mode:** ReadWriteOnce = ஒரே நேரத்தில் ஒரு node மட்டும் write. ReadWriteMany தேவைப்பட்டால் NFS/CSI driver தேவை. Complexity அதிகம்.

**Availability vs Operability:** PVC delete ஆனால் data போய் விடும். PVC-யை orphan பண்ணாமல் cleanup policy தேவை. Snapshot/backup strategy தனியாக வேண்டும். Persistent Volume என்பது backup இல்லை.

**Cost:** Provisioned storage செலவு தொடரும். Unused PVC-கள் மறைந்த செலவாகும்.

Failure mode: PV stuck in `Terminating` state, volume attachable பிரச்சனை cross zone-ல. StatefulSet upgrade-ல ordering முக்கியம்.

## 6. Practical Example

Enterprise file upload service.

Users file upload பண்ணி `/uploads` folder-ல save ஆகும். Deployment-ல 3 replicas.

Problem: Replica 1-ல upload ஆன file replica 2-ல கிடைக்காது. Pod restart ஆனால் file போகும்.

Solution: Single writer Deployment with ReadWriteOnce PVC. Ingress sticky session போட்டு uploads எல்லாம் ஒரே Pod-க்கு போகும்.

மாற்று: Object storage S3 compatible செய்து application-ல directly S3-க்கு write பண்ணுவது. அப்போ PVC தேவையே இல்லை. Architecturally cleaner for shared files.

இங்கே decision: Small scale internal tool என்றால் PVC போதும். Scale, multi region, shared access வேண்டும் என்றால் object storage தான்.

## 7. Reasoning Challenge
