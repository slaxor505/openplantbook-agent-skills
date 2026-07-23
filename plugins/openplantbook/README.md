# Open Plantbook Plugin

This plugin contains reusable Agent Skills for Open Plantbook API workflows.

Author: Slava Pisarevskiy.

## Skills

| Skill | Description |
|-------|-------------|
| [openplantbook](./skills/openplantbook/SKILL.md) | Schema-first Open Plantbook API workflows for plant search, detail retrieval, care fields, and authenticated user-plant writes. |

## Layout

```text
skills/
└── openplantbook/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   └── publish-notes.md
    ├── scripts/
    │   └── openplantbook_cli.py
    └── skill-card.md
```

Plugin metadata:

```text
.claude-plugin/plugin.json
.codex-plugin/plugin.json
```

## Notes For Agents

- Read `skills/openplantbook/SKILL.md` before using or editing the skill.
- Keep API details schema-first; do not replace the live OpenAPI schema check with scraped HTML or stale snippets.
- Keep credentials out of repository files, logs, and user-visible output.
- Keep `skills/openplantbook/skill-card.md` aligned with the actual OpenClaw/ClawHub-facing behavior.
- Keep Codex/Claude web adapters in the root repo thin; they should point to the canonical skill, not duplicate it.
- Update this README and the root README when adding skills.
