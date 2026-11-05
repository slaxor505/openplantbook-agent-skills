# Publishing guide

How to publish the `openplantbook` skill to each marketplace. Rules were checked against vendor docs in October 2026. They change often, so re-check a vendor page if a step fails. The commands below come from those docs. They were not run against the live services.

## Before every release

1. Bump the version. It must match in all three places (`tools/check.py` enforces this):
   - `skills/openplantbook/SKILL.md` → `metadata.version`
   - `.claude-plugin/plugin.json` → `version`
   - `.codex-plugin/plugin.json` → `version`
2. Run the checks and build the packages:

   ```bash
   python3 tools/check.py
   python3 tools/package.py
   ```

3. Run the ClawHub security gate in [references/publish-notes.md](skills/openplantbook/references/publish-notes.md) if you publish there.
4. Commit, push, then tag: `git tag v1.0.1 && git push origin v1.0.1`. The release workflow checks the tag against the version and attaches both ZIPs to a GitHub release.

`tools/package.py` writes to `dist/` (not committed):

| File | Use |
|------|-----|
| `openplantbook-skill-<version>.zip` | One skill folder. For claude.ai skill upload. |
| `openplantbook-plugin-<version>.zip` | Plugin with manifests, skill, README and LICENSE. For the OpenAI portal and claude.ai plugin upload. |
| `SHA256SUMS` | Checksums of both ZIPs. |

## Marketplaces

| Marketplace | What you submit | Review |
|-------------|-----------------|--------|
| [Anthropic directory](#anthropic-directory-claudeai-cowork-claude-code) | GitHub repo (this repo root) | Automated scan + human review |
| [Own Claude Code marketplace](#own-claude-code-marketplace) | Nothing. Already works. | None |
| [claude.ai personal upload](#claudeai-personal-upload) | Skill ZIP | None |
| [OpenAI (ChatGPT and Codex)](#openai-chatgpt-and-codex) | Plugin ZIP. **On hold**, see below. | Automated scan + human review |
| [skills.sh](#skillssh) | Nothing. Listed after installs. | Automated audits |
| [GitHub `gh skill`](#github-gh-skill) | Nothing. Tag a release. | None |
| [ClawHub / OpenClaw](#clawhub--openclaw) | Skill folder | Automated security checks |
| [Gemini CLI, Copilot, Cursor and others](#gemini-cli-copilot-cursor-and-others) | Nothing. Installed from GitHub. | None |

### Anthropic directory (claude.ai, Cowork, Claude Code)

1. You need a paid claude.ai plan (Pro, Max, Team or Enterprise). The GitHub repo must be public.
2. Open <https://claude.ai/directory/manage> → **Submit new** → **Plugin bundle**.
3. Enter `slaxor505/openplantbook-agent-skills`. The plugin folder is the repo root.
4. Press **Validate**, fix every **Blocks** finding, then submit.

Notes:

- Skills are not a submission type on their own. They go in a plugin bundle.
- The README must describe everything the plugin runs, sends or fetches. See "What the skill runs and sends" in the [README](README.md#what-the-skill-runs-and-sends).
- The helper reads `OPENPLANTBOOK_*` credentials from the environment and sends them to `open.plantbook.io`. The scan may hold this version for a human reviewer ("Uses a credential from the user's machine"). A hold is not a rejection.
- Later versions are picked up from the tracked branch. Bump `version` each time, or users keep the old copy.
- `claude plugin validate .` shows a note that `CLAUDE.md` at the plugin root is not loaded. This is harmless.

### Own Claude Code marketplace

No review. Works now:

```text
/plugin marketplace add slaxor505/openplantbook-agent-skills
/plugin install openplantbook@openplantbook-agent-skills
```

### claude.ai personal upload

1. Run `python3 tools/package.py`.
2. In claude.ai open **Settings** → **Features** (or **Capabilities**) → **Skills** → upload `dist/openplantbook-skill-<version>.zip`.

Limits:

- Needs code execution enabled. Plans: Pro, Max, Team, Enterprise.
- The skill needs network access to `open.plantbook.io`. The user's or admin's network setting decides this.
- The upload is per user. It does not sync to the Claude API or to other people.
- The Claude API runs skills in a sandbox with no network. The helper cannot reach Open Plantbook there, so do not upload it to the API.

### OpenAI (ChatGPT and Codex)

**Status: on hold (November 2026).** OpenAI's portal says: "We are not accepting more skills-only submissions at this time." The decision is to skip the OpenAI directory for now. Revisit when OpenAI reopens skills-only plugins, or if a remote MCP server for Open Plantbook is built. Codex users can still install straight from GitHub (see the last note in this section). The steps below are kept for when this reopens.

1. Verify your developer identity in OpenAI organization settings. You need Apps Management write access.
2. Run `python3 tools/package.py`.
3. Open <https://platform.openai.com/plugins> → **Create plugin** → **Skills only** → upload `dist/openplantbook-plugin-<version>.zip`.
4. Fix the findings under **Metadata & Skills**, complete the listing, and submit for review.

Notes:

- One public listing serves both ChatGPT and Codex.
- The listing text comes from `.codex-plugin/plugin.json` → `interface`.
- Icon, logo, privacy policy URL and terms URL are already set in `.codex-plugin/plugin.json`. The icon is 512x512 pixels and the logo is 1427x512.
- OpenAI does not run Claude-style install prompts for credentials. A skills-only plugin that needs a credential may be questioned in review. OpenAI's suggested fix is an MCP server with OAuth, which is a bigger change. Decide this if review asks.
- Direct install for testing: `codex plugin marketplace add slaxor505/openplantbook-agent-skills`.

First upload of 1.0.1 (November 2026) came back with four findings:

| Finding | Status |
|---------|--------|
| "Subtitle must be 30 characters or fewer." | Fixed. The subtitle is `interface.shortDescription` in `.codex-plugin/plugin.json`. It is now 26 characters. `tools/check.py` enforces the limit. |
| "We are not accepting more skills-only submissions at this time." | **On hold. Not fixable in the package.** OpenAI has closed the "Skills only" type for now. Decision: skip OpenAI for now. Other options for later: ask OpenAI when it reopens, or add a remote MCP server and submit with MCP. OpenAI says an MCP server cannot be added to a skills-only plugin later, so it must be in the first ZIP. |
| "We couldn't confirm the selected category." | Parked until OpenAI reopens. Pick a category that matches the plugin's purpose and make the first sentence of `interface.longDescription` state it. |
| "Review the plugin's privacy policy against the submission guidelines." | Parked until OpenAI reopens. Compare the policy at the URL in the manifest with OpenAI's plugin guidelines. |

### skills.sh

There is no submission form. The skill appears on the leaderboard after people install it:

```bash
npx skills add slaxor505/openplantbook-agent-skills
```

Optional badge for the README:

```markdown
[![skills.sh](https://skills.sh/b/slaxor505/openplantbook-agent-skills)](https://skills.sh/slaxor505/openplantbook-agent-skills)
```

### GitHub `gh skill`

```bash
gh skill install slaxor505/openplantbook-agent-skills openplantbook
gh skill install slaxor505/openplantbook-agent-skills openplantbook@v1.0.1   # pinned to a tag
```

Before the first release, run `gh skill publish` from a checkout. It validates against the Agent Skills spec and offers to turn on immutable releases and tag protection. It may flag the nested `metadata.openclaw` block (see [Known trade-offs](#known-trade-offs)).

### ClawHub / OpenClaw

Run the security gate in [publish-notes.md](skills/openplantbook/references/publish-notes.md), then:

```bash
clawhub login
clawhub skill publish ./skills/openplantbook --version 1.0.1
```

ClawHub publishes every skill under MIT-0. This repo stays MIT.

### Gemini CLI, Copilot, Cursor and others

No manifest is needed. These tools read `SKILL.md` folders.

```bash
npx skills add slaxor505/openplantbook-agent-skills -a gemini-cli -a github-copilot -a cursor
gemini skills install https://github.com/slaxor505/openplantbook-agent-skills.git --path skills
```

## Known trade-offs

- **`metadata.openclaw` is a nested object.** The Agent Skills spec says `metadata` values are strings. ClawHub and OpenClaw read this block for requirements and UI, so it stays. `tools/check.py` allows it on purpose. A strict validator may warn.
- **Credentials come from environment variables.** This is the portable contract in the skill. Anthropic's scan may hold a version for review. OpenAI prefers OAuth through MCP.
- **Network is required.** `compatibility` in `SKILL.md` says so. The skill is not useful in no-network sandboxes.
- **`.agents/skills/openplantbook` is a symlink.** Codex web uses it. Anthropic's checker warns about symlinks it loads, but it loads only `skills/`. The ZIPs never include it.
- **Codex repo marketplace path.** `.agents/plugins/marketplace.json` points at `./`. This follows OpenAI's docs but was not tested with the `codex` CLI.

## Open items

Only the maintainer can do these:

- [x] Make the GitHub repo public (needed for the Anthropic directory). Done.
- [x] Add icon and logo. Done: both manifests point to the images in the `assets` folder.
- [x] Add privacy policy and terms URLs. Done: both manifests have them.
- [ ] Check the terms URL. It points to the Open Plantbook home page (`https://open.plantbook.io/`). If you have a dedicated terms page, change it in both `plugin.json` files.
- [x] Square icon at 512x512 or larger. Done: the icon is 512x512.
- [ ] Verify the OpenAI developer identity. Parked: only needed if the OpenAI submission is resumed.
- [ ] Test the skill on each surface after install (a read-only search is enough).
