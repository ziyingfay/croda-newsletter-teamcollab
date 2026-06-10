# Croda Beauty Newsletter Project

This workspace now uses the Croda Project Management Agent structure.

Start new work by reading:

1. `AGENTS.md`
2. `project-management/skills/active/croda-project-management/SKILL.md`
3. `project-management/dev/docs/目录整理说明.md`

## Directory Map

```text
product/                         # Product code, configuration, and runtime outputs
├── croda-frontend/               # React frontend and report/admin UI
├── croda-backend/                # Python backend API, orchestration, services
├── skills/                       # Customer-deliverable Xiaolongxia/OpenClaw skills
├── spider/                       # WeChat and website ingestion
├── parameter-file/               # Source profiles, watchlists, prompts, tag dictionaries
└── output/                       # Runtime output root; public exchange is output/result/

project-management/              # Project management, references, and agent skills
├── skills/active/                # Internal project-management skills
├── reference/                    # Requirements, customer source materials, examples, archive
└── dev/                          # In-repo process docs, work logs, temporary build notes
```

Do not recreate root-level `app/`, `outputs/`, `dev/`, `reference/`, or `newsletter-tagging/` for Croda work. Use the mapped folders above.

Run the structure check after directory or technology changes:

```bash
python .github/scripts/validate_structure.py
```
