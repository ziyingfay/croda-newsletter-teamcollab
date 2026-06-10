---
name: croda-project-management
description: Use this skill when starting, organizing, coding, testing, packaging, reviewing pull requests, or resuming the Croda / Heda Beauty newsletter project; when deciding where Croda frontend, backend, spider, parameter, reference, skill, or public output files belong; when producing RSS JSON, tagging JSON, report_content JSON, HTML reports, or monthly work packages; when enforcing React frontend, Python-only backend scripts, repository structure checks, or team contribution flow; and whenever correcting heda/Heda project paths to the canonical croda directory structure.
---

# Croda Project Management

This is the clean project-management skill for the Croda Beauty newsletter project. It preserves the project rules and reusable workflow, without carrying skill-development logs, requirement-change records, or temporary work notes.

## Start Checklist

Before substantial work:

1. Read `AGENTS.md`.
2. Read `project-management/skills/active/croda-project-management/references/directory-and-output-rules.md`.
3. Read `project-management/skills/active/croda-project-management/references/croda-context.md` only when business context, newsletter sections, customer roles, MVP boundaries, or tagging logic matter.
4. Check the relevant GitHub issue, pull request, or external project-management source if the work depends on current team decisions.

Use this skill as the source of truth for Croda project organization.

## Canonical Directory Map

Use this project tree for Croda product code and runtime artifacts. Treat `heda` as a spelling error and correct it to `croda`.

```text
croda/
├── product/                         # Product code, configuration, and runtime outputs
│   ├── croda-frontend/              # React frontend and report/admin UI
│   ├── croda-backend/               # Python backend API, services, and orchestration
│   ├── skills/                      # Customer-deliverable Xiaolongxia/OpenClaw skills
│   ├── spider/
│   │   ├── Wechat/                  # WeChat source ingestion
│   │   └── Website/                 # Website, media, and database ingestion
│   ├── parameter-file/              # Watchlists, source profiles, prompts, config
│   └── output/                      # Runtime output root; public exchange is product/output/result/
└── project-management/              # Project coordination skills and reference material
    ├── reference/
    └── skills/
```

Keep project-management files in the process area:

- `project-management/skills/` for internal project-management, repository-organization, collaboration, or governance skills.
- `project-management/reference/` for user-provided background and source material.

Keep customer-deliverable workflow skills in the product area:

- `product/skills/` for skills that the customer installs or that Xiaolongxia/OpenClaw reads as part of the production workflow, such as tagging and report-writing skills.
- Do not put customer-deliverable workflow skills under `project-management/skills/`.

Do not introduce new root names such as `heda-frontend`, `heda-backend`, `app/`, or `outputs/` for Croda runtime output.

## Documentation And Tracking

This clean template does not include local work logs, requirement-change logs, current-state files, or skill-development notes.

Use GitHub Issues, pull requests, or the team's external project-management system for:

- current status
- feature design discussion
- requirement changes
- bug and risk tracking
- test evidence and review notes

If a durable rule changes, update `AGENTS.md`, this `SKILL.md`, and the relevant file under `project-management/skills/active/croda-project-management/references/` in the same PR.

## Technology Rules

### Frontend

The frontend is fixed to React.

Rules:

- Put all frontend code under `product/croda-frontend/`.
- Use React as the UI framework.
- TypeScript, Vite, React Router, component libraries, and Node-based frontend build tooling are allowed inside `product/croda-frontend/`.
- Do not use Vue, Svelte, Angular, or other non-React frontend frameworks unless the user explicitly changes this decision.

### Backend

All backend scripts and automation scripts must be written in Python.

Allowed:

- Python scripts for spiders, cleaning, validation, tagging runners, report runners, render orchestration, and backend jobs.
- Node.js and JavaScript tooling only for frontend build work inside `product/croda-frontend/`.

Not allowed:

- Node.js backend scripts.
- Mixed Node.js + Python backend orchestration.
- JavaScript or TypeScript scripts under `product/croda-backend/` or `product/spider/`, unless the user explicitly approves an exception.

## Team Collaboration Rule

All team members should follow the same contribution flow, even if their local coding agent does not load this skill correctly.

Before opening a pull request:

1. Keep product changes under `product/`.
2. Keep references and internal project-management skill changes under `project-management/`; keep customer-deliverable workflow skills under `product/skills/`.
3. Run:

```bash
python .github/scripts/validate_structure.py
```

4. Fix any validation failure before pushing.

GitHub should run `.github/workflows/validate-structure.yml` on push and pull requests. Do not merge a PR if structure validation fails.

The validator protects against:

- recreated forbidden root directories such as `app/`, `outputs/`, root-level `spider/`, root-level `output/`, root-level `dev/`, root-level `skills/`, or `heda/`
- missing canonical Croda directories
- JavaScript / TypeScript backend scripts outside `product/croda-frontend/`
- non-React frontend framework dependencies when `product/croda-frontend/package.json` exists
- work logs saved directly as `project-management/dev/notes/work-log-YYYYMMDD.md` instead of the per-member work-log structure, when in-repo work logs are enabled

## Croda Output Rules

Put all Croda runtime deliverables under `product/output/`. Use `product/output/result/` as the shared public handoff area between programs.

```text
product/output/result/
```

Use these standard artifacts in the MVP flow:

| Stage | Required artifact |
|-------|-------------------|
| RSS / WeChat / website collection | Raw inputs and fetch logs under spider-owned output |
| Cleaning | Timestamp archive JSON under `product/output/result/spider/YYYYMM/` and fixed handoff JSON at `product/output/待打标.json` |
| Xiaolongxia 1 tagging | Tagging JSON under `product/output/result/tagging/YYYYMM/` |
| Xiaolongxia 2 report writing | `report_content` JSON under `product/output/result/report/YYYYMM/` |
| Rendering | HTML report under `product/output/result/report/YYYYMM/` |
| Run audit | `run_log` JSON under the component's public result subfolder |

### Public Directory Rule

Components may only exchange data through `product/output/result/`.

- Spider writes public results to `product/output/result/spider/YYYYMM/`.
- Tagging reads the fixed crawler handoff file from `product/output/待打标.json`.
- Tagging writes public results to `product/output/result/tagging/YYYYMM/`.
- Report generation reads from `product/output/result/spider/YYYYMM/` and `product/output/result/tagging/YYYYMM/`.
- Report generation writes to `product/output/result/report/YYYYMM/`.
- Do not read another component's private workspace directly.
- Do not make downstream programs depend on files inside `product/spider/`, `product/croda-backend/`, or any component-private folder.

### RSS Clean JSON Dual Naming

After RSS / WeChat / website cleaning creates the first clean JSON, always create two identical files:

```text
product/output/result/spider/YYYYMM/YYYYMMDD-HHMMSS-rss-clean.json
product/output/待打标.json
```

Rules:

- The timestamp-named file is the traceable archive artifact.
- `product/output/待打标.json` is an exact duplicate for the tagging step.
- Immediately after creation, the two files must contain identical JSON content.
- If the clean JSON is corrected before tagging, edit or regenerate the timestamp-named archive file first, then recreate `product/output/待打标.json` from it.
- Delete `product/output/待打标.json` after tagging completes successfully.
- Do not use vague names such as `latest.json`, `final.json`, `new.json`, or `copy.json` for this handoff.

Example:

```text
product/output/result/spider/202606/20260610-153000-rss-clean.json
product/output/待打标.json
```

## Placement Rules

Use these defaults:

| File type | Put it here |
|-----------|-------------|
| React frontend code, admin UI, report UI | `product/croda-frontend/` |
| Backend API, data service, orchestration service | `product/croda-backend/` |
| Customer-deliverable Xiaolongxia/OpenClaw skills, such as tagging or report-writing skills | `product/skills/` |
| WeChat / official account spider | `product/spider/Wechat/` |
| Website / media / database spider | `product/spider/Website/` |
| Watchlist, source list, tag dictionary config, prompt config | `product/parameter-file/` |
| Public runtime JSON, HTML, logs, screenshots for monthly runs | `product/output/result/<component>/YYYYMM/` |
| Test output artifacts that should be visible in the repo | `product/output/test-results/` |
| Requirements and source background | `project-management/reference/requirements/` or `project-management/reference/source-materials/` |
| Internal project-management, repository-organization, collaboration, or governance skills | `project-management/skills/` |

## Optional In-Repo Process Docs

This clean template does not include process docs or work logs by default. If the team decides to track them inside the repository, keep one shared source of truth:

- `project-management/dev/docs/设计文档.md`
- `project-management/dev/docs/需求变更日志.md`
- `project-management/dev/docs/测试记录.md`
- `project-management/dev/docs/问题跟踪.md`
- `project-management/dev/current-state.md`

Keep personal or agent session logs separately:

```text
project-management/dev/notes/work-log/<member-id>/YYYYMMDD.md
```

Rules:

- `<member-id>` comes from `project-management/dev/team/members.json`.
- Use the team member's GitHub username as the default member id. If it is not available in the coding-agent session, ask the teammate once during onboarding and register the stable id in `members.json`.
- Use lowercase letters, numbers, and hyphens only.
- Keep one daily log per member. If the same member works multiple times in one day, update that member's `YYYYMMDD.md`.
- Git and GitHub do not provide semantic deduplication for work logs. If two people edit the same file, Git may create a merge conflict; it will not know that two same-day logs should both be preserved. The registered member directory is the primary collision-prevention mechanism.
- GitHub skills/connectors may help inspect PRs or resolve conflicts, but the Croda skill must not depend on a connector being available for repository hygiene.

## MVP Workflow

Follow the Croda MVP order:

```text
RSS / WeChat / Website collection
-> clean RSS JSON
-> write timestamp archive JSON in product/output/result/spider/YYYYMM/ and duplicate as product/output/待打标.json
-> Xiaolongxia 1 tagging JSON
-> Xiaolongxia 2 report_content JSON
-> HTML render
-> final monthly report
```

Boundaries:

- MVP uses monthly folders and JSON artifacts.
- Do not make SQLite, a full data platform, or a complex admin backend a prerequisite for MVP work.
- Agent tagging should not write HTML.
- The renderer should not invent business insight; it renders `report_content.json`.
- Keep article evidence, original URLs, and run logs traceable.
- For fetch failures, implement retry behavior in the feature design. Default to 5 retries unless the issue or PR specifies another configurable value.

## Business Context

For the durable project context, read:

```text
project-management/skills/active/croda-project-management/references/croda-context.md
```

Put any user-provided source material, PRDs, or customer notes under `project-management/reference/`.

## End Checklist

Before finishing:

1. Run relevant tests or manual checks.
2. Run `python .github/scripts/validate_structure.py` when directory or technology rules may be affected.
3. Summarize created or updated artifacts, verification, and remaining risks in the final handoff, issue, or PR.
