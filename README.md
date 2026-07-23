<p align="center">
  <strong>Open Plantbook Agent Skills</strong>
</p>

# Open Plantbook Agent Skills

Reusable Agent Skills for working with the [Open Plantbook](https://open.plantbook.io/) API from AI coding assistants and agent runtimes.

Author: Slava Pisarevskiy.

This repository packages the `openplantbook` skill in several compatible discovery shapes:

- `skills/openplantbook/`: direct skill folder for OpenClaw and tools that expect a top-level `skills/` directory.
- `plugins/openplantbook/skills/openplantbook/`: plugin-style layout for Agent Skills repositories, modeled after multi-skill repos such as Ping Identity's `ping-sdk-agent-skills`.
- `.agents/skills/openplantbook`: Codex repo-scoped skill pointer for Codex surfaces that scan `.agents/skills`.

The actual workflow logic still lives in one canonical skill folder: `skills/openplantbook`. Plugin and web files are adapters that point back to it.

## What This Is

Agent Skills are compact folders that teach an AI agent a repeatable workflow. A skill normally contains a `SKILL.md` file plus optional `references/`, `scripts/`, `assets/`, and agent-specific metadata.

This repository teaches agents how to use Open Plantbook safely and consistently:

- Search Open Plantbook for plants by scientific name, common name, or alias.
- Retrieve plant detail and care fields from the API.
- Create schema-aligned user plants from JSON dossiers.
- Guide update and delete workflows for user plants.
- Help build sensor upload integrations when explicitly requested.
- Use the live OpenAPI schema as the source of truth before schema-sensitive work.
- Keep credentials private and out of prompts, logs, commits, and user-visible output.

This repository does not include the Open Plantbook application or an SDK. The helper script uses direct HTTP and the live API schema.

## Open Plantbook Background

Open Plantbook is a community-sourced plant-care database with a web UI and API. Its documentation page links to interactive Swagger documentation at:

- `https://open.plantbook.io/api/docs/`

The canonical machine-readable schema endpoint is:

- `https://open.plantbook.io/api/schema/`

The live schema checked while preparing this README advertises:

- OpenAPI: `3.0.3`
- API version: `202606`
- Title: `Open Plantbook API`

Relevant API paths in that schema:

| Method | Path | Skill use |
|--------|------|-----------|
| `POST` | `/api/v1/token/` | OAuth2 client-credentials token acquisition |
| `GET` | `/api/v1/plant/search` | Search public/user plants |
| `GET` | `/api/v1/plant/detail/{pid}/` | Retrieve detail and care data |
| `POST` | `/api/v1/plant/create` | Create user plants |
| `PATCH` | `/api/v1/plant/update` | Update user plants or customize public plants into a user profile |
| `DELETE` | `/api/v1/plant/delete` | Delete user plants |
| `POST` | `/api/v1/sensor-data/instance` | Register sensor-upload plant instances |
| `POST` | `/api/v1/sensor-data/upload` | Upload JSON Time Series sensor data |

Open Plantbook supports OAuth2 and API-key token authentication. The skill treats OAuth as required for write operations unless the live schema changes.

## What The Agent Can Do

After installation, a compatible agent can use this skill for:

- Plant lookup: "Find Open Plantbook entries for Abelia."
- Detail retrieval: "Get care fields for `abelia chinensis` in English."
- Dossier publishing: "Create an Open Plantbook user plant from this schema-aligned JSON dossier."
- Update guidance: "Update the watering and light thresholds for this user plant."
- Delete guidance: "Delete user plant PID X after confirming the exact PID."
- Integration help: "Build a sensor uploader that registers plant instances and uploads JTS data."
- API debugging: "Inspect the live schema and explain why this payload is rejected."

The agent should not:

- Scrape the public Browse DB pages as a fallback for API data.
- Guess request fields when the schema is available.
- Recover credentials from shell history, logs, backups, transcripts, browser storage, or stale files.
- Print secrets or commit credential files.
- Perform writes or deletes without explicit user intent.

## Repository Layout

```text
.
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── .agents/
│   ├── plugins/
│   │   └── marketplace.json
│   └── skills/
│       └── openplantbook -> ../../skills/openplantbook
├── AGENTS.md
├── CLAUDE.md
├── CLAUDE_WEB.md
├── CODEX_WEB.md
├── CONTRIBUTING.md
├── LICENSE
├── OPENCLAW.md
├── README.md
├── adapters/
│   ├── anthropic-claude-web.md
│   └── openai-codex-web.md
├── plugins/
│   └── openplantbook/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── .codex-plugin/
│       │   └── plugin.json
│       ├── README.md
│       └── skills/
│           └── openplantbook/
│               ├── SKILL.md
│               ├── agents/
│               │   └── openai.yaml
│               ├── references/
│               │   └── publish-notes.md
│               ├── scripts/
│               │   └── openplantbook_cli.py
│               └── skill-card.md
└── skills/
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

Key files:

- [skills/openplantbook/SKILL.md](skills/openplantbook/SKILL.md): direct OpenClaw/local skill entry point.
- [plugins/openplantbook/skills/openplantbook/SKILL.md](plugins/openplantbook/skills/openplantbook/SKILL.md): plugin-packaged skill entry point.
- [scripts/openplantbook_cli.py](skills/openplantbook/scripts/openplantbook_cli.py): dependency-free helper for search, detail, and create workflows.
- [CODEX_WEB.md](CODEX_WEB.md): OpenAI Codex web bridge.
- [CLAUDE_WEB.md](CLAUDE_WEB.md): Anthropic Claude web Project Instructions / Project Knowledge bridge.
- [OPENCLAW.md](OPENCLAW.md): OpenClaw install, credential, and ClawHub notes.
- [AGENTS.md](AGENTS.md): repo maintenance guidance for agents.
- [CONTRIBUTING.md](CONTRIBUTING.md): contribution and validation workflow.

## Supported Agent Surfaces

This repository includes scaffolding for several agent ecosystems:

| Surface | Files | Notes |
|---------|-------|-------|
| Generic Agent Skills | `SKILL.md`, `references/`, `scripts/` | Portable skill contents |
| Skills CLI / plugin-style repos | `plugins/openplantbook/skills/openplantbook` | Layout follows common multi-skill repository structure |
| OpenAI Codex web | `AGENTS.md`, `.agents/skills/openplantbook`, `CODEX_WEB.md` | Use repo instructions plus the repo-scoped skill pointer; fall back to explicitly reading `skills/openplantbook/SKILL.md` |
| Codex plugins | `.codex-plugin/`, `plugins/openplantbook/.codex-plugin/`, `.agents/plugins/marketplace.json` | Plugin packaging and repo-local marketplace metadata |
| Anthropic Claude web | `CLAUDE_WEB.md`, `README.md`, `skills/openplantbook/SKILL.md` | Use Claude Project Instructions / Project Knowledge rather than duplicating the skill |
| Claude-compatible plugin metadata | `.claude-plugin/`, `plugins/openplantbook/.claude-plugin/` | Marketplace and plugin metadata |
| OpenClaw | `skills/openplantbook`, `OPENCLAW.md`, `skill-card.md` | Direct local install and ClawHub publication notes |

Other tools that understand Agent Skills can usually consume either the direct `skills/openplantbook` folder or the plugin path under `plugins/openplantbook/skills/openplantbook`.

## Web Agent Setup

### OpenAI Codex Web

Codex web should use the repository itself as context:

1. Connect this repository to Codex web.
2. Start tasks from the repository root so `AGENTS.md` is in scope.
3. Use the repo-scoped skill pointer at `.agents/skills/openplantbook` when skill discovery is available.
4. Use the repo-local Codex marketplace at `.agents/plugins/marketplace.json` when testing plugin installation.
5. If the web environment does not load skills automatically, prompt Codex to read `skills/openplantbook/SKILL.md` and follow it.

Bridge doc: [CODEX_WEB.md](CODEX_WEB.md).

### Anthropic Claude Web

Claude web should use project instructions and project knowledge:

1. Create a Claude Project.
2. Add `CLAUDE_WEB.md` as Project Instructions or as the first project knowledge file.
3. Add `README.md`, `AGENTS.md`, and the `skills/openplantbook` files as project knowledge.
4. Ask Claude to use the Open Plantbook project skill or explicitly read `skills/openplantbook/SKILL.md`.

Bridge doc: [CLAUDE_WEB.md](CLAUDE_WEB.md).

For both web agents, do not create a separate Open Plantbook workflow. Keep the skill logic in `skills/openplantbook/SKILL.md` and keep web files as adapters.

## Installation

### Agent Skills CLI

From a future GitHub repository:

```bash
npx skills add slaxor505/openplantbook-agent-skills
```

Install only the Open Plantbook plugin:

```bash
npx skills add slaxor505/openplantbook-agent-skills/plugins/openplantbook
```

Install only the skill:

```bash
npx skills add slaxor505/openplantbook-agent-skills/plugins/openplantbook/skills/openplantbook
```

### OpenClaw

From the repository root:

```bash
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
```

From a future GitHub repository:

```bash
openclaw skills install git:https://github.com/slaxor505/openplantbook-agent-skills.git --agent main --as openplantbook
```

If OpenClaw cannot infer the nested skill path from a Git install, clone the repository and install `./skills/openplantbook` directly.

### Manual Copy

For runtimes that consume plain skill folders:

```bash
cp -r skills/openplantbook /path/to/agent/skills/
```

Or use the plugin copy:

```bash
cp -r plugins/openplantbook/skills/openplantbook /path/to/agent/skills/
```

## Credential Configuration

Do not commit credentials into this repository.

The canonical skill uses a portable credential contract. The helper supports these live credential sources:

| Source | Use |
|--------|-----|
| `OPENPLANTBOOK_API_KEY` | Token auth for read/search/detail workflows |
| `OPENPLANTBOOK_CLIENT_ID` and `OPENPLANTBOOK_CLIENT_SECRET` | OAuth client credentials |
| `OPENPLANTBOOK_OAUTH_CREDENTIALS` | JSON OAuth bundle or `client_id:client_secret` shorthand |
| `OPENPLANTBOOK_ENV_FILE=/path/to/openplantbook.env` | Custom private env file |

Recommended private env file:

```text
OPENPLANTBOOK_OAUTH_CREDENTIALS={"client_id":"...","client_secret":"..."}
```

For UI or hub configuration, label the secret field as `Open Plantbook credential`, not `API key`, because write workflows may need OAuth credentials rather than a token key.

Agent-specific guides map platform secret stores to these variables. Keep local paths and platform config formats in adapter docs such as [OPENCLAW.md](OPENCLAW.md), [CODEX_WEB.md](CODEX_WEB.md), or [CLAUDE_WEB.md](CLAUDE_WEB.md), not in the canonical skill.

## Usage Examples

Ask the agent to use the skill:

```text
Use the openplantbook skill to search Open Plantbook for Monstera deliciosa and return care fields from the API.
```

Use the helper directly:

```bash
python3 skills/openplantbook/scripts/openplantbook_cli.py search "monstera"
python3 skills/openplantbook/scripts/openplantbook_cli.py detail "monstera deliciosa" --lang en --include care
python3 skills/openplantbook/scripts/openplantbook_cli.py create --from-dossier plant_dossiers/chlorophytum_orchidastrum.json
```

Use the plugin-path helper:

```bash
python3 plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py search "abelia"
```

## Safety Model

The skill is intentionally conservative:

- Schema-first: fetch `https://open.plantbook.io/api/schema/` before operations where endpoint shape, payload fields, limits, or response shape matter.
- API-only: use API-backed paths, not public Browse DB HTML or search snippets.
- Secret-safe: do not print, echo, store, or commit credentials.
- Write-aware: create, update, and delete are external changes and require explicit user intent.
- Delete-aware: confirm destructive deletes unless the user already provided an exact PID and explicit delete instruction.
- Error-transparent: summarize validation/auth/API failures without leaking secrets.
- Dependency-light: the helper uses Python standard library direct HTTP and does not require an SDK.

## Development Best Practices

This repository follows the patterns used by mature Agent Skills repositories:

- Keep `SKILL.md` concise and trigger-focused.
- Put detailed or publication-specific notes in `references/`.
- Put deterministic repeated logic in `scripts/`.
- Keep generated files, caches, logs, credentials, and local dossiers out of git.
- Maintain both README inventory tables and plugin README files when adding skills.
- Keep direct and plugin skill copies synchronized.
- Validate frontmatter and helper scripts before handoff.
- Do not install new validation tools unless the user explicitly approves installation.

When changing the skill, edit one copy first, then mirror it:

```bash
rsync -a --delete skills/openplantbook/ plugins/openplantbook/skills/openplantbook/
```

Or mirror the other direction if the plugin copy is the source of truth:

```bash
rsync -a --delete plugins/openplantbook/skills/openplantbook/ skills/openplantbook/
```

Never mirror secrets, generated caches, private test data, or local environment files.

## Validation

Run from the repository root:

```bash
python3 skills/openplantbook/scripts/openplantbook_cli.py --help
python3 plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py --help
diff -qr skills/openplantbook plugins/openplantbook/skills/openplantbook
find . -name '__pycache__' -o -name '*.pyc'
```

Validate Python syntax without leaving bytecode behind:

```bash
python3 - <<'PY'
from pathlib import Path
import ast
for path in [
    Path("skills/openplantbook/scripts/openplantbook_cli.py"),
    Path("plugins/openplantbook/skills/openplantbook/scripts/openplantbook_cli.py"),
]:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print("python syntax ok")
PY
```

Validate YAML frontmatter and plugin JSON:

```bash
python3 - <<'PY'
from pathlib import Path
import json
import yaml

skill_paths = [
    *Path("skills").glob("*/SKILL.md"),
    *Path("plugins").glob("*/skills/*/SKILL.md"),
]
for path in skill_paths:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"missing frontmatter: {path}")
    data = yaml.safe_load(text.split("---", 2)[1])
    if data.get("name") != path.parent.name:
        raise SystemExit(f"name mismatch: {path}")

json_paths = [
    *Path(".").glob(".*-plugin/*.json"),
    *Path("plugins").glob("*/.*-plugin/*.json"),
]
for path in json_paths:
    json.loads(path.read_text(encoding="utf-8"))

print("frontmatter and plugin json ok")
PY
```

If the Agent Skills reference validator is already installed:

```bash
npx skills-ref validate ./plugins/openplantbook/skills/openplantbook
```

If OpenClaw is available and you intentionally want to install locally:

```bash
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
```

## Publishing Notes

Before any ClawHub/OpenClaw Hub publish or republish, run the security review gate in the publish notes. This is required for the package to be ready for OpenClaw Hub security review.

For ClawHub/OpenClaw publication, review:

- [skills/openplantbook/skill-card.md](skills/openplantbook/skill-card.md)
- [skills/openplantbook/references/publish-notes.md](skills/openplantbook/references/publish-notes.md)
- [OPENCLAW.md](OPENCLAW.md)

For plugin-style publication, review:

- [.codex-plugin/plugin.json](.codex-plugin/plugin.json)
- [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json)
- [plugins/openplantbook/.codex-plugin/plugin.json](plugins/openplantbook/.codex-plugin/plugin.json)
- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [plugins/openplantbook/.claude-plugin/plugin.json](plugins/openplantbook/.claude-plugin/plugin.json)

Do not add fake installed-origin metadata. Files such as `.clawhub/origin.json` should be created by actual install or publish flows.

## Related Resources

- [Open Plantbook](https://open.plantbook.io/)
- [Open Plantbook documentation](https://open.plantbook.io/docs/)
- [Open Plantbook Swagger UI](https://open.plantbook.io/api/docs/)
- [Open Plantbook OpenAPI schema](https://open.plantbook.io/api/schema/)
- [Agent Skills](https://agentskills.io/)
- [Skills CLI](https://skills.sh/)
- [OpenClaw skill notes](OPENCLAW.md)

## License

MIT. See [LICENSE](LICENSE).
