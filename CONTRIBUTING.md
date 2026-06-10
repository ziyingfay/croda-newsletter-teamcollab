# Croda Team Contribution Rules

## Before Coding

1. Read `AGENTS.md`.
2. Read `project-management/skills/active/croda-project-management/SKILL.md`.
3. Keep product work under `product/`.
4. Keep skill and reference updates under `project-management/`.
5. Record decisions and discussion in GitHub Issues, pull requests, or the team's external project-management space by default.

## Directory Guardrails

Do not create these root directories:

- `app/`
- `outputs/`
- `croda-frontend/`
- `croda-backend/`
- `spider/`
- `parameter-file/`
- `output/`
- `dev/`
- `reference/`
- `skills/`
- `heda/`
- `heda-frontend/`
- `heda-backend/`

Use the canonical layout:

```text
product/
├── croda-frontend/
├── croda-backend/
├── spider/
├── parameter-file/
└── output/

project-management/
├── reference/
└── skills/
```

## Technology Rules

- Frontend is fixed to React.
- Backend scripts, spider scripts, validators, agent runners, and orchestration scripts must use Python.
- Node.js is allowed only for frontend build tooling inside `product/croda-frontend/`.

## Pull Request Flow

1. Work on a feature branch.
2. Run:

```bash
python .github/scripts/validate_structure.py
```

3. Open a pull request.
4. Do not merge if the structure validation check fails.
5. If a directory rule needs to change, update `AGENTS.md` and `project-management/skills/active/croda-project-management/SKILL.md` in the same PR.
6. If the team enables in-repo work logs, use `project-management/dev/notes/work-log/<member-id>/YYYYMMDD.md` and register member ids in `project-management/dev/team/members.json`.
