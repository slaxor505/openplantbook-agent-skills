# Contributing to Open Plantbook Agent Skills

Contributions should improve reusable AI-agent workflows for Open Plantbook without adding runtime dependencies or private user context.

## Creating Or Updating A Skill

Skills live under:

```text
plugins/openplantbook/skills/<skill-name>/
```

Every skill needs:

- `SKILL.md`: required metadata and instructions.
- `references/`: optional detailed docs loaded only when needed.
- `scripts/`: optional deterministic helpers.
- `assets/`: optional output templates or media.
- `agents/`: optional UI metadata for agents that support it.
- `skill-card.md`: optional OpenClaw/ClawHub listing card.

`SKILL.md` frontmatter should include:

```yaml
---
name: openplantbook
description: "Open Plantbook API workflows with schema-first plant search, detail, and user-plant writes."
license: MIT
metadata:
  author: Slava Pisarevskiy
  version: "1.0.0"
---
```

Keep descriptions trigger-focused and keep long API details in `references/`.

## Validation

Run these before handing off a change:

```bash
python3 -m py_compile plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py
python3 plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py --help
python3 -m py_compile skills/openplantbook/scripts/openplantbook_cli.py
python3 skills/openplantbook/scripts/openplantbook_cli.py --help
python3 - <<'PY'
from pathlib import Path
import yaml
for p in [*Path("plugins").glob("*/skills/*/SKILL.md"), *Path("skills").glob("*/SKILL.md")]:
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"missing frontmatter: {p}")
    yaml.safe_load(text.split("---", 2)[1])
print("frontmatter ok")
PY
```

If `npx skills-ref` is already available, also run:

```bash
npx skills-ref validate ./plugins/openplantbook/skills/openplantbook
```

Do not install validation tools unless the user explicitly approves installation.

For OpenClaw-specific checks, install into a disposable or intended agent workspace only when that persistent change is explicitly requested:

```bash
openclaw skills install ./plugins/openplantbook/skills/openplantbook --agent main --as openplantbook
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
```

## Pull Request Checklist

- [ ] `SKILL.md` name matches its directory.
- [ ] Root and plugin README files list the skill.
- [ ] `OPENCLAW.md`, `CODEX_WEB.md`, `CLAUDE_WEB.md`, and `skill-card.md` still match the skill surface.
- [ ] Helper scripts are dependency-free or clearly document required tools.
- [ ] No credentials, local env files, logs, transcripts, or private data are committed.
- [ ] Before any ClawHub/OpenClaw Hub publish or republish, the security review gate in `references/publish-notes.md` was run and all findings were resolved or documented.
- [ ] Validation commands were run or skipped with a clear reason.
