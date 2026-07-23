# CLAUDE.md

This repository packages reusable Agent Skills for Open Plantbook. Treat it as a skill bundle, not an application.

For Claude web, use `CLAUDE_WEB.md` as the Project Instructions / Project Knowledge bridge. Do not copy the Open Plantbook workflow into this file; `skills/openplantbook/SKILL.md` remains canonical.

Before changing a skill:

1. Read `AGENTS.md`.
2. Read the affected `SKILL.md`.
3. Keep `SKILL.md` lean and move detailed API notes into `references/`.
4. Do not add credentials, local `.env` files, logs, or private generated data.

Useful checks:

```bash
python3 -m py_compile plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py
python3 plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py --help
```

If `npx skills-ref` is already available, use it for structure validation. Do not install packages without explicit user approval.
