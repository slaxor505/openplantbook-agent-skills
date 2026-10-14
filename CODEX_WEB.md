# Codex Web Adapter

Use this file as the Codex web entry point when the repository is connected at `https://chatgpt.com/codex`.

## Recommended Setup

1. Connect the GitHub repository to Codex web.
2. Start tasks from the repository root.
3. Let Codex read `AGENTS.md` for repo conventions.
4. Use the repo-scoped skill at `.agents/skills/openplantbook`, which points to the canonical `skills/openplantbook` folder.
5. If using Codex plugin installation, use the repo marketplace at `.agents/plugins/marketplace.json`. The repository root is the plugin.

## Invocation

Ask Codex directly:

```text
Use the openplantbook skill to search Open Plantbook for Monstera deliciosa and return care fields from the API.
```

If skill discovery is unavailable in the current web environment, tell Codex:

```text
Read skills/openplantbook/SKILL.md and follow it as the Open Plantbook workflow for this task.
```

## Boundaries

- Do not duplicate Open Plantbook workflow logic in Codex-only instructions.
- Treat `skills/openplantbook/SKILL.md` as canonical.
- Use `.codex-plugin/plugin.json` only as packaging/discovery metadata.
- Keep credentials outside the repository.

## Useful Files

- `AGENTS.md`: repo-wide maintenance and validation instructions.
- `.agents/skills/openplantbook`: Codex repo-scope skill symlink.
- `.agents/plugins/marketplace.json`: repo-local plugin marketplace entry.
- `.codex-plugin/plugin.json`: root Codex plugin manifest.
- `skills/openplantbook/SKILL.md`: canonical skill instructions.

