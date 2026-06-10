# Croda Directory And Output Rules

## Canonical Tree

```text
croda/
├── product/
│   ├── croda-frontend/
│   ├── croda-backend/
│   ├── skills/
│   ├── spider/
│   │   ├── Wechat/
│   │   └── Website/
│   ├── parameter-file/
│   └── output/
└── project-management/
    ├── reference/
    └── skills/
```

Use `croda`, not `heda`, in every path and generated instruction.

## Skill Placement

Customer-deliverable skills belong under `product/skills/`. These are skills that the customer installs or that Xiaolongxia/OpenClaw reads in the product workflow, such as article tagging or report-writing skills.

Internal project-management skills belong under `project-management/skills/`. These are only for repository organization, collaboration, governance, and agent operating rules.

Do not place customer-deliverable workflow skills under `project-management/skills/`.

## Optional Project Management Collaboration

This clean template does not include local process docs or work logs by default. If the team enables in-repo project-management records, keep shared process docs single-copy under `project-management/dev/docs/`.

Personal or agent work logs must use:

```text
project-management/dev/notes/work-log/<member-id>/YYYYMMDD.md
```

The member id comes from `project-management/dev/team/members.json`. Use the teammate's GitHub username by default; if unavailable, register a stable lowercase id during onboarding.

Git and GitHub do not semantically deduplicate duplicate logs. The registered member directory and `validate_structure.py` prevent same-day work-log collisions.

## Backend Scripts

Use React for all frontend UI work in `product/croda-frontend/`.

Use Python for all backend scripts, crawler scripts, data cleaning jobs, validators, agent runners, orchestration scripts, and render orchestration. Do not introduce Node.js backend scripts.

Node.js is allowed only for frontend build tooling inside `product/croda-frontend/`.

## Tracking And Durable Decisions

This clean template does not include local development logs, requirement-change records, test notes, or current-state files.

Use GitHub Issues, pull requests, or the team's external project-management system for active decisions and work history. If a durable rule changes, update `AGENTS.md`, `SKILL.md`, and this reference file.

## Monthly Output

Use `product/output/result/` as the shared public handoff directory. Components must not read each other's private workspaces directly.

```text
product/output/result/spider/YYYYMM/
product/output/result/tagging/YYYYMM/
product/output/result/report/YYYYMM/
```

The temporary fixed tagging handoff file lives at:

```text
product/output/待打标.json
```

The first cleaned RSS JSON must be written twice:

```text
product/output/result/spider/YYYYMM/YYYYMMDD-HHMMSS-rss-clean.json
product/output/待打标.json
```

The two files must be identical immediately after creation.
Delete `product/output/待打标.json` after tagging completes successfully.

## MVP Artifacts

```text
raw/fetch inputs
fetch_log.json
YYYYMMDD-HHMMSS-rss-clean.json
product/output/待打标.json
tagging.json
report_content.json
report.html
run_log.json
```
