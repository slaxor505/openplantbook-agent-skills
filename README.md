<p align="center">
  <strong>Open Plantbook Agent Skills</strong>
</p>

# Open Plantbook Agent Skills

Reusable Agent Skills for working with the [Open Plantbook](https://open.plantbook.io/) API from AI coding assistants and agent runtimes.

Author: Slava Pisarevskiy.

The repository root is one plugin with one skill. The same files serve every marketplace:

- `skills/openplantbook/`: the skill. Tools that read `SKILL.md` folders (skills.sh, `gh skill`, OpenClaw, Gemini CLI, Copilot, Cursor) find it here.
- `.claude-plugin/`: Claude Code plugin and marketplace manifests. Also accepted by Anthropic's directory.
- `.codex-plugin/` and `.agents/plugins/`: OpenAI (ChatGPT and Codex) plugin manifest and repo marketplace.
- `.agents/skills/openplantbook`: Codex repo-scoped skill pointer for Codex surfaces that scan `.agents/skills`.

The workflow logic lives only in `skills/openplantbook`. Plugin and web files are adapters that point back to it. See [PUBLISHING.md](PUBLISHING.md) for how to publish to each marketplace.

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
├── .github/
│   └── workflows/
│       ├── check.yml
│       └── release.yml
├── adapters/
│   ├── anthropic-claude-web.md
│   └── openai-codex-web.md
├── skills/
│   └── openplantbook/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   └── publish-notes.md
│       ├── scripts/
│       │   └── openplantbook_cli.py
│       └── skill-card.md
├── tools/
│   ├── check.py
│   └── package.py
├── AGENTS.md
├── CLAUDE.md
├── CLAUDE_WEB.md
├── CODEX_WEB.md
├── CONTRIBUTING.md
├── LICENSE
├── OPENCLAW.md
├── PUBLISHING.md
└── README.md
```

Key files:

- [skills/openplantbook/SKILL.md](skills/openplantbook/SKILL.md): the skill entry point.
- [skills/openplantbook/scripts/openplantbook_cli.py](skills/openplantbook/scripts/openplantbook_cli.py): dependency-free helper for search, detail, and create workflows.
- [PUBLISHING.md](PUBLISHING.md): how to publish to each marketplace, with open items.
- [tools/check.py](tools/check.py): validates the skill, manifests, and package hygiene.
- [tools/package.py](tools/package.py): builds the upload ZIPs in `dist/`.
- [CODEX_WEB.md](CODEX_WEB.md): OpenAI Codex web bridge.
- [CLAUDE_WEB.md](CLAUDE_WEB.md): Anthropic Claude web Project Instructions / Project Knowledge bridge.
- [OPENCLAW.md](OPENCLAW.md): OpenClaw install, credential, and ClawHub notes.
- [AGENTS.md](AGENTS.md): repo maintenance guidance for agents.
- [CONTRIBUTING.md](CONTRIBUTING.md): contribution and validation workflow.

## Supported Agent Surfaces

| Surface | Files | Notes |
|---------|-------|-------|
| Agent Skills tools (skills.sh, `gh skill`, Gemini CLI, Copilot, Cursor, and others) | `skills/openplantbook` | Portable skill folder |
| Anthropic directory, Claude Code, claude.ai plugins | `.claude-plugin/` | Plugin and marketplace manifests. The repo root is the plugin folder |
| claude.ai skill upload | `dist/openplantbook-skill-<version>.zip` | Built by `tools/package.py` |
| OpenAI ChatGPT and Codex plugins | `.codex-plugin/`, `.agents/plugins/marketplace.json` | Listing text and repo marketplace. Upload ZIP built by `tools/package.py` |
| OpenAI Codex web | `AGENTS.md`, `.agents/skills/openplantbook`, `CODEX_WEB.md` | Use repo instructions plus the repo-scoped skill pointer; fall back to explicitly reading `skills/openplantbook/SKILL.md` |
| Anthropic Claude web | `CLAUDE_WEB.md`, `README.md`, `skills/openplantbook/SKILL.md` | Use Claude Project Instructions / Project Knowledge rather than duplicating the skill |
| OpenClaw / ClawHub | `skills/openplantbook`, `OPENCLAW.md`, `skill-card.md` | Direct local install and ClawHub publication notes |

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

Pick the tool you use. [PUBLISHING.md](PUBLISHING.md) lists every marketplace and how to submit.

### Claude Code

```text
/plugin install openplantbook --marketplace slaxor505/openplantbook-agent-skills
```

On Claude Code older than 2.1.275, add the marketplace first:

```text
/plugin marketplace add slaxor505/openplantbook-agent-skills
/plugin install openplantbook@openplantbook-agent-skills
```

### ChatGPT and Codex

```bash
codex plugin marketplace add slaxor505/openplantbook-agent-skills
```

Then open `/plugins` in Codex and install Open Plantbook.

### Agent Skills CLI (skills.sh)

```bash
npx skills add slaxor505/openplantbook-agent-skills
```

Install into specific tools:

```bash
npx skills add slaxor505/openplantbook-agent-skills -a claude-code -a codex -a github-copilot -a cursor -a gemini-cli
```

### GitHub CLI

```bash
gh skill install slaxor505/openplantbook-agent-skills openplantbook
```

### claude.ai

Build the skill ZIP with `python3 tools/package.py`, then upload `dist/openplantbook-skill-<version>.zip` in **Settings** → **Features** → **Skills**. The skill needs network access to `open.plantbook.io`.

### OpenClaw

From the repository root:

```bash
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
```

From GitHub:

```bash
openclaw skills install git:https://github.com/slaxor505/openplantbook-agent-skills.git --agent main --as openplantbook
```

If OpenClaw cannot infer the nested skill path from a Git install, clone the repository and install `./skills/openplantbook` directly.

### Manual Copy

For runtimes that consume plain skill folders:

```bash
cp -r skills/openplantbook /path/to/agent/skills/
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

## What The Skill Runs And Sends

The skill is instructions plus one helper script. This is everything the helper does:

- **Runs:** `python3 skills/openplantbook/scripts/openplantbook_cli.py`. It uses the Python standard library only. It installs no packages, downloads no code, starts no other programs, and writes no files.
- **Network:** HTTPS requests to `https://open.plantbook.io` only. The host is fixed in the script and cannot be changed by an environment variable. Paths used: `/api/v1/plant/search`, `/api/v1/plant/detail/{pid}/`, `/api/schema/`, `/api/v1/token/`, and `/api/v1/plant/create`.
- **Sends:** the search text, plant IDs, and plant fields the user asks for. Credentials go only to that host, as an `Authorization` header, or as a client ID and secret sent to the token endpoint.
- **Reads:** the `OPENPLANTBOOK_*` environment variables, the private env file named by `OPENPLANTBOOK_ENV_FILE` (only the four credential names are read from it), and the dossier JSON file the user names for `create`.
- **Never:** prints credentials, reads shell history or logs, or scrapes Open Plantbook web pages.

Update and delete calls are described in `SKILL.md` as direct HTTP calls the agent makes with the user's approval. The helper script does not do them.

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

- Keep `SKILL.md` concise and trigger-focused. The `description` is the only text agents see before they pick a skill, so it must say what the skill does and when to use it.
- Use paths relative to the skill folder in `SKILL.md`. Do not use tool-specific placeholders.
- Put detailed or publication-specific notes in `references/`.
- Put deterministic repeated logic in `scripts/`.
- Keep generated files, caches, logs, credentials, and local dossiers out of git.
- There is one copy of the skill, in `skills/openplantbook/`. Do not add a second copy.
- Bump the version in `SKILL.md`, `.claude-plugin/plugin.json`, and `.codex-plugin/plugin.json` together before a release.
- Run `python3 tools/check.py` before every push. CI runs it on every pull request.

## Validation

Run from the repository root:

```bash
python3 tools/check.py
```

It needs PyYAML (`pip install pyyaml`). It checks:

- `SKILL.md` frontmatter against the [Agent Skills spec](https://agentskills.io/specification) and the claude.ai name rules.
- Plugin and marketplace manifests: valid JSON, matching names and versions, required listing fields.
- Package hygiene: README length and LICENSE, no symlinks except the Codex pointer, no cache or credential files, no files over 256 KiB, no binaries.
- A scan for hard-coded secrets and local file paths.
- The helper script: syntax and `--help`.
- `claude plugin validate`, when the `claude` CLI is installed.

Build the upload ZIPs:

```bash
python3 tools/package.py   # writes dist/
```

If the Agent Skills reference validator is already installed:

```bash
npx skills-ref validate ./skills/openplantbook
```

It may warn about the nested `metadata.openclaw` block. That block is required by ClawHub and OpenClaw (see [PUBLISHING.md](PUBLISHING.md#known-trade-offs)).

If OpenClaw is available and you intentionally want to install locally:

```bash
openclaw skills install ./skills/openplantbook --agent main --as openplantbook
openclaw skills info openplantbook --agent main
openclaw skills check --agent main
```

## Publishing Notes

Read [PUBLISHING.md](PUBLISHING.md) first. It covers the Anthropic directory, OpenAI, claude.ai, skills.sh, GitHub `gh skill`, ClawHub, and others, plus the open items only the maintainer can do.

Before any ClawHub/OpenClaw Hub publish or republish, run the security review gate in [skills/openplantbook/references/publish-notes.md](skills/openplantbook/references/publish-notes.md). Also see [skills/openplantbook/skill-card.md](skills/openplantbook/skill-card.md) and [OPENCLAW.md](OPENCLAW.md).

Manifest files:

- [.claude-plugin/plugin.json](.claude-plugin/plugin.json) and [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.codex-plugin/plugin.json](.codex-plugin/plugin.json) and [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json)

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
