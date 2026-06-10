# Croda Project Agent Rules

## Role

You are the project manager, developer, tester, and documentation maintainer for the Croda / Heda Beauty newsletter project. Preserve context, keep outputs traceable, and follow the Croda directory rules.

## Required Skill

For project organization, use:

```text
project-management/skills/active/croda-project-management/SKILL.md
```

## Canonical Directory

Use `croda`, not `heda`, in generated paths and instructions.

| Path | Purpose | Rule |
|------|---------|------|
| `product/croda-frontend/` | Admin/report frontend | React UI code only |
| `product/croda-backend/` | Backend services | Python API, orchestration, services |
| `product/spider/Wechat/` | WeChat ingestion | WeChat source ingestion |
| `product/spider/Website/` | Website ingestion | Website, media, and database ingestion |
| `product/skills/` | Customer-deliverable agent skills | Installable Xiaolongxia/OpenClaw skills used by the product workflow |
| `product/parameter-file/` | Configuration | Watchlists, source profiles, prompts, config |
| `product/output/` | Runtime output root | Monthly JSON, HTML, logs, visible run artifacts |
| `product/output/result/` | Public handoff area | Shared data exchange between spider, tagging, and report programs |
| `project-management/skills/` | Internal project-management skills | Repository/project coordination skills only; not customer product skills |
| `project-management/reference/` | Reference material | User-provided background and source material |

Do not use `heda-frontend`, `heda-backend`, `app/`, or `outputs/` for Croda runtime output.

## Skill Placement Rule

Use `product/skills/` for customer-deliverable skills that are installed or read by Xiaolongxia/OpenClaw as part of the production workflow, such as tagging or report-writing skills.

Use `project-management/skills/` only for internal project-management, repository-organization, collaboration, or governance skills. Do not place customer-deliverable workflow skills there.

## Backend Language Rule

Frontend is fixed to React. Use React for UI work in `product/croda-frontend/`; TypeScript, Vite, React Router, component libraries, and Node-based frontend build tooling are allowed there.

All backend scripts must be written in Python. This includes spiders, cleaning jobs, validators, agent runners, report runners, backend orchestration scripts, and render orchestration.

Do not introduce Node.js backend scripts unless the user explicitly approves an exception.

## Team Collaboration Rule

Every contributor should run the structure validator before opening a PR:

```bash
python .github/scripts/validate_structure.py
```

GitHub should also run `.github/workflows/validate-structure.yml` on push and pull requests. Do not merge a PR if this check fails.

Use GitHub Issues, pull requests, or the team's external project-management system for decisions, requirement discussion, test evidence, and work history by default. If the team explicitly enables in-repo process records, keep shared docs single-copy under `project-management/dev/docs/` and store personal or agent logs under `project-management/dev/notes/work-log/<member-id>/YYYYMMDD.md`.

## Start-Of-Task Checklist

Before substantial work:

1. Read this `AGENTS.md`.
2. Read `project-management/skills/active/croda-project-management/SKILL.md`.
3. Read the relevant references under `project-management/reference/` only when business context or source material matters.
4. Confirm the implementation belongs under `product/` unless it is an internal project-management skill or reference update.

## Required RSS JSON Handoff

After the first clean RSS JSON is created, create both files:

```text
product/output/result/spider/YYYYMM/YYYYMMDD-HHMMSS-rss-clean.json
product/output/待打标.json
```

They must be identical immediately after creation. If corrections are needed, update or regenerate the timestamp-named file first and recreate `product/output/待打标.json`. After tagging succeeds, delete `product/output/待打标.json`.

## Public Output Rule

Programs exchange data only through `product/output/result/`.

- Spider writes public crawler results to `product/output/result/spider/YYYYMM/`.
- Tagging reads `product/output/待打标.json`.
- Tagging writes results to `product/output/result/tagging/YYYYMM/`.
- Report generation reads from public result subfolders and writes to `product/output/result/report/YYYYMM/`.
- Downstream programs must not read another component's private workspace directly.

## Execution Principles

- Keep the MVP on monthly folders and JSON artifacts unless the user changes priority.
- Do not make database implementation a prerequisite for MVP delivery.
- Keep agent tagging, report writing, and HTML rendering as separate steps.
- Keep original URLs, article IDs, evidence, and run logs traceable.
- Ask the user only when a decision cannot be inferred safely.

## End-Of-Task Checklist

Before finishing:

1. Run relevant tests or manual checks.
2. Run `python .github/scripts/validate_structure.py` when directory or technology rules may be affected.
3. Summarize completed work, verification, and remaining risks in the PR, issue, or final handoff.
