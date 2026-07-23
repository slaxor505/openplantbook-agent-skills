# OpenClaw Scaffolding

This repository is shaped so OpenClaw can consume the plain skill directory:

```text
skills/openplantbook/
```

The plugin copy at `plugins/openplantbook/skills/openplantbook/` is kept for multi-agent plugin packaging and should stay in sync with the top-level skill mirror.

## Local Install

Install into an OpenClaw agent workspace from the repository root:

```bash
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
```

Install from a future GitHub repository:

```bash
openclaw skills install git:https://github.com/slaxor505/openplantbook-agent-skills.git --agent main --as openplantbook
```

If OpenClaw cannot infer the nested skill path from a Git install, clone the repository and install the skill directory path directly.

## Check After Install

```bash
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
python3 plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py --help
python3 skills/openplantbook/scripts/openplantbook_cli.py --help
```

## Credential Setup

Do not commit credentials. The canonical skill uses portable environment variables:

- `OPENPLANTBOOK_API_KEY`
- `OPENPLANTBOOK_OAUTH_CREDENTIALS`
- `OPENPLANTBOOK_CLIENT_ID` plus `OPENPLANTBOOK_CLIENT_SECRET`

For OpenClaw local installs, the recommended private env file is:

```text
~/.config/openclaw/secrets/skills/openplantbook.env
```

Point the portable helper at it with:

```text
OPENPLANTBOOK_ENV_FILE=~/.config/openclaw/secrets/skills/openplantbook.env
```

The private env file should use plain `KEY=value` lines. OAuth bundle example:

```text
OPENPLANTBOOK_OAUTH_CREDENTIALS={"client_id":"...","client_secret":"..."}
```

If you store credentials in OpenClaw config or another local secret store, map them into the portable variables above before running the helper. Do not reference OpenClaw config paths from the canonical `SKILL.md`.

## ClawHub Publication

The skill includes a ClawHub-style `skill-card.md` next to `SKILL.md`.

Before publishing, review:

```text
plugins/openplantbook/skills/openplantbook/references/publish-notes.md
plugins/openplantbook/skills/openplantbook/skill-card.md
skills/openplantbook/skill-card.md
```

The `references/publish-notes.md` security review gate must pass before any publish or republish. OpenClaw-specific credential paths may be documented in this file, but they must not appear in the packaged canonical skill.

After publication, OpenClaw may add installed-origin metadata under `.clawhub/` and release metadata such as `_meta.json`. Do not add fake origin metadata before the package is actually published or installed from ClawHub.
