# Phase 6: Security Architecture

**Stage:** Technical Lead

## இந்த phase ஏன் இங்க இருக்கு

Infrastructure-க்கு உடனே அப்புறம் வைச்சிருக்கோம், ஏன்னா most security controls (IAM, network segmentation, secrets) நேரடியா அந்த infrastructure primitives-மேல தான் attach ஆகுது. AI security-ஐ இந்த phase கடைசில ஒரு necessary early preview-ஆ வைச்சிருக்கோம்.

## இந்த phase முடிச்ச பிறகு answer பண்ண முடிற question

> Authentication மட்டும் போதாதா, ஏன் authorization-உம் தேவை?

## இந்த phase-ல இருக்கிற sections
- **[Application security](01-application-security/README.md)** — Single-service level-ல identity, access.
- **[Enterprise security](02-enterprise-security/README.md)** — Organization scale-ல identity, access.
- **[AI security](03-ai-security/README.md)** — Prompt injection, tool abuse, excessive agency, tenant isolation. Flag: இதுவும் ஒரு forward reference — RAG (Phase 12), tools (Phase 14), agents (Phase 15) build பண்ணின பிறகுதான் இந்த threats உண்மையில click ஆகும். அந்த stage-ல ஒரு deeper second pass பண்றது நல்லது.

---
[← Curriculum overview-க்கு திரும்ப போங்க](../README.md)
