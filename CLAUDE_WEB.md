# Claude Web Adapter

Use this file as Claude web Project Instructions or as the first project knowledge file for this repository.

Claude web may not install Agent Skills or plugins the same way local coding agents do. The best portable approach is to give Claude web the same canonical skill files as project knowledge and instruct it to follow them.

## Recommended Setup

1. Create a Claude Project for Open Plantbook Agent Skills.
2. Add this repository, or upload these files as project knowledge:
   - `CLAUDE_WEB.md`
   - `README.md`
   - `skills/openplantbook/SKILL.md`
   - `skills/openplantbook/references/publish-notes.md`
   - `skills/openplantbook/scripts/openplantbook_cli.py`
   - `AGENTS.md`
3. Put the "Project Instruction" below in the Claude Project instructions field.

## Project Instruction

```text
When a user asks about Open Plantbook, plant lookup, plant-care thresholds, Open Plantbook API workflows, user-plant create/update/delete, or sensor upload integration, use the openplantbook skill from skills/openplantbook/SKILL.md.

Treat skills/openplantbook/SKILL.md as canonical. Load referenced files only when needed. Do not duplicate or rewrite the skill logic in Claude-specific instructions.

Use API-backed Open Plantbook workflows only. Do not scrape Browse DB HTML or use search snippets as fallback plant data. Fetch or inspect the live OpenAPI schema before schema-sensitive operations. Never print, store, or infer credentials from logs, history, backups, transcripts, or browser storage. For external writes and deletes, require explicit user intent and confirm ambiguous targets.
```

## Invocation

Ask Claude:

```text
Use the Open Plantbook project skill to search for Abelia and summarize care fields from the API.
```

Or:

```text
Read skills/openplantbook/SKILL.md and follow it for this Open Plantbook task.
```

## Boundaries

- This is an adapter for Claude web project knowledge, not a separate implementation.
- Keep all Open Plantbook domain logic in `skills/openplantbook/SKILL.md`.
- Keep secrets outside Claude project files unless the user deliberately provides credentials for a single task.
- If Claude web cannot execute the Python helper, it should draft the exact command or API request and explain what the user or a code-running agent should run.

