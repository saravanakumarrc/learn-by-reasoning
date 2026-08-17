# AI Solution Architect Learning Content Generator

This project converts the uploaded AI Solution Architect learning path into a structured JSON catalog and uses a local Ollama model to generate one Markdown document per topic.

## Files

- `learning_path.json` — complete curriculum, phases, sections, topics and generation status.
- `master_base_prompt.md` — your master learning prompt. Put `{{TOPIC}}` where the topic should be inserted.
- `generate_content.py` — generates topic content through Ollama.
- `requirements.txt` — Python dependency.

## Setup

```bash
pip install -r requirements.txt
```

Make sure Ollama is running:

```bash
ollama serve
```

Then check your installed models:

```bash
ollama list
```

## Generate

Generate all pending topics:

```bash
python generate_content.py --model muse-glimmer
```

Generate only one topic:

```bash
python generate_content.py --model muse-glimmer --section 8.1.1
```

Preview prompts without calling the model:

```bash
python generate_content.py --status pending --limit 1 --dry-run
```

The script updates `learning_path.json` after each topic so generation can be resumed safely.
