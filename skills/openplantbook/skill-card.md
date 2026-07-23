## Description: <br>
Schema-first Open Plantbook API workflows for plant search, care data, and authenticated user-plant writes. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[slaxor505](https://clawhub.ai/user/slaxor505) <br>

## Author: <br>
Slava Pisarevskiy <br>

### License/Terms of Use: <br>
MIT <br>

## Use Case: <br>
Developers and agent users use this skill to search Open Plantbook, retrieve plant details and care fields, and create schema-aligned user plants from dossier JSON. The skill uses the live OpenAPI schema and a dependency-free direct-HTTP helper instead of an SDK or scraped HTML. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Authenticated write operations can create, update, or delete user plants in Open Plantbook. <br>
Mitigation: Require explicit user intent for writes and deletes, confirm ambiguous targets, and report API results without secrets. <br>
Risk: API credentials may be exposed if pasted into prompts, logs, repository files, or shell history. <br>
Mitigation: Use environment variables, a platform secret manager, or an explicit private env file documented by the relevant adapter; never print or commit credentials. <br>
Risk: Live API schema or Cloudflare behavior may change. <br>
Mitigation: Fetch `https://open.plantbook.io/api/schema/` before schema-sensitive work and use the documented user agent for direct HTTP requests. <br>

## Reference(s): <br>
- [Open Plantbook API docs](https://open.plantbook.io/docs/) <br>
- [Open Plantbook schema endpoint](https://open.plantbook.io/api/schema/) <br>
- [ClawHub skill page](https://clawhub.ai/slaxor505/openplantbook) <br>

## Skill Output: <br>
**Output Type(s):** [Markdown, JSON, shell commands, API payload summaries] <br>
**Output Format:** [Plain-language summaries, JSON API responses, validated schema-aligned payload keys, or helper CLI output.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires Python 3 and Open Plantbook credentials for API calls. Read/search/detail can use token auth or OAuth. Write workflows require OAuth unless the live schema changes.] <br>

## Skill Version(s): <br>
1.0.0 (repository scaffold) <br>

## Ethical Considerations: <br>
Users should review generated API payloads before write operations, avoid publishing private plant/user data, and apply their organization's safety, security, and compliance requirements before deployment. <br>
