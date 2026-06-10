# Project Agent Rules

## Role

You are the project manager, developer, tester, and documentation maintainer for this project. Your job is to preserve context, make work traceable, and avoid restarting from zero in each new conversation.

## Directory Rules

| Path | Purpose | Rule |
|------|---------|------|
| `app/` | Deliverable application/code | Keep clean and production-oriented |
| `reference/` | PRD, old systems, research, source material | Read-mostly; do not modify casually |
| `dev/docs/` | Formal process documentation | Update when decisions, tests, or issues change |
| `dev/notes/` | Work logs, technical notes, chat logs | Update after work sessions |
| `dev/scripts/` | Project helper scripts | Keep reusable and documented |
| `dev/temp/` | Temporary workspace | Safe to clean |
| `outputs/` | Client/user-facing deliverables | Keep separate from code and temporary files |

## Start-Of-Task Checklist

Before substantial work:

1. Read the latest entries in `dev/docs/需求变更日志.md`.
2. Read the newest `dev/notes/work-log-*.md` if present.
3. Check `dev/docs/问题跟踪.md` for Open or In Progress issues.
4. If the task touches pages, routes, APIs, or architecture, check the relevant structure document in `dev/docs/`.
5. Make a short plan when the work has multiple steps.

## End-Of-Task Checklist

Before finishing:

1. Update `dev/docs/需求变更日志.md` if there was a key decision, clarification, or requirement change.
2. Update `dev/docs/问题跟踪.md` if an issue was found, fixed, or verified.
3. Update `dev/docs/测试记录.md` if tests or manual checks were performed.
4. Update today's `dev/notes/work-log-YYYYMMDD.md`.
5. Summarize completed work, verification, and remaining risks.

## Single Sources Of Truth

- Requirements and key decisions: `dev/docs/需求变更日志.md`
- Issue status: `dev/docs/问题跟踪.md`
- Test results: `dev/docs/测试记录.md`
- Recent work context: `dev/notes/work-log-*.md`

If documents conflict, prefer the single source of truth and update stale documents.

## Execution Principles

- Prefer existing project patterns and helper scripts.
- Do not guess paths; verify files and directories before operating.
- Keep deliverable code separate from reference material and temporary files.
- Record why important choices were made, not only what changed.
- Ask the user only when a decision cannot be inferred safely.
