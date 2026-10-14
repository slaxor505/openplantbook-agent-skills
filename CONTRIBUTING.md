# Contributing to Open Plantbook Agent Skills

Contributions should improve reusable AI-agent workflows for Open Plantbook without adding runtime dependencies or private user context.

## Creating Or Updating A Skill

Skills live under:

```text
skills/<skill-name>/
```

Every skill needs:

- `SKILL.md`: required metadata and instructions.
- `references/`: optional detailed docs loaded only when needed.
- `scripts/`: optional deterministic helpers.
- `assets/`: optional output templates or media.
- `agents/`: optional UI metadata for agents that support it.
- `skill-card.md`: optional OpenClaw/ClawHub listing card.

`SKILL.md` frontmatter follows the [Agent Skills spec](https://agentskills.io/specification):

```yaml
---
name: openplantbook
description: What the skill does, and when to use it. Max 1024 characters.
license: MIT
compatibility: Requires Python 3 and outbound HTTPS access to open.plantbook.io.
metadata:
  author: Slava Pisarevskiy
  version: "1.0.0"
---
```

Rules:

- `name` matches the folder name. Lowercase letters, digits, and hyphens. No `claude` or `anthropic` in it.
- `description` says what the skill does and when to use it. The agent only sees this text before it loads the skill.
- `metadata` values are strings. The one exception is the `openclaw` block that ClawHub reads.
- Use paths relative to the skill folder in the body. Do not use tool-specific placeholders.
- Keep `SKILL.md` under 500 lines. Move long API details to `references/`.

## Versions

The version must be the same in `skills/openplantbook/SKILL.md` (`metadata.version`), `.claude-plugin/plugin.json`, and `.codex-plugin/plugin.json`. Bump it for every release. Marketplaces do not update users who are on the same version.

## Validation

Run this before handing off a change:

```bash
python3 tools/check.py
```

It needs PyYAML (`pip install pyyaml`). It checks the frontmatter, manifests, package hygiene, secrets, and the helper script. It also runs `claude plugin validate` when the `claude` CLI is installed.

To build the upload ZIPs:

```bash
python3 tools/package.py
```

If `npx skills-ref` is already available, also run:

```bash
npx skills-ref validate ./skills/openplantbook
```

It may warn about the nested `metadata.openclaw` block. ClawHub needs that block.

Do not install validation tools unless the user explicitly approves installation.

For OpenClaw-specific checks, install into a disposable or intended agent workspace only when that persistent change is explicitly requested:

```bash
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
```

## Pull Request Checklist

- [ ] `SKILL.md` name matches its directory.
- [ ] `README.md` lists the skill.
- [ ] `OPENCLAW.md`, `CODEX_WEB.md`, `CLAUDE_WEB.md`, `PUBLISHING.md`, and `skill-card.md` still match the skill surface.
- [ ] Versions match in `SKILL.md` and both `plugin.json` files.
- [ ] Helper scripts are dependency-free or clearly document required tools.
- [ ] No credentials, local env files, logs, transcripts, or private data are committed.
- [ ] Before any ClawHub/OpenClaw Hub publish or republish, the security review gate in `references/publish-notes.md` was run and all findings were resolved or documented.
- [ ] `python3 tools/check.py` passes, or a skipped check has a clear reason.
