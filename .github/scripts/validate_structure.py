#!/usr/bin/env python3
"""Validate Croda repository structure and collaboration guardrails."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_DIRS = [
    "product",
    "product/croda-frontend",
    "product/croda-backend",
    "product/skills",
    "product/skills/newsletter-tagging",
    "product/spider/Wechat",
    "product/spider/Website",
    "product/parameter-file",
    "product/output/result/spider",
    "product/output/result/tagging",
    "product/output/result/report",
    "project-management",
    "project-management/reference",
    "project-management/skills/active/croda-project-management",
]

FORBIDDEN_ROOT_DIRS = [
    "app",
    "outputs",
    "croda-frontend",
    "croda-backend",
    "spider",
    "parameter-file",
    "output",
    "dev",
    "reference",
    "skills",
    "heda",
    "heda-frontend",
    "heda-backend",
]

BACKEND_CODE_AREAS = [
    "product/croda-backend",
    "product/spider",
    "product/skills",
    "project-management/dev/scripts",
]

FRONTEND_DIR = ROOT / "product/croda-frontend"
WORK_LOG_ROOT = ROOT / "project-management/dev/notes/work-log"
TEAM_MEMBERS_FILE = ROOT / "project-management/dev/team/members.json"
MEMBER_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
WORK_LOG_FILENAME_RE = re.compile(r"^\d{8}\.md$")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    errors: list[str] = []

    for dirname in REQUIRED_DIRS:
        if not (ROOT / dirname).is_dir():
            errors.append(f"Missing required directory: {dirname}")

    for dirname in FORBIDDEN_ROOT_DIRS:
        if (ROOT / dirname).exists():
            errors.append(f"Forbidden root path exists: {dirname}")

    if (ROOT / "project-management/skills/active/newsletter-tagging").exists():
        errors.append(
            "Customer-deliverable workflow skills must live under product/skills/, "
            "not project-management/skills/: project-management/skills/active/newsletter-tagging"
        )

    for area in BACKEND_CODE_AREAS:
        area_path = ROOT / area
        if not area_path.exists():
            continue
        for path in area_path.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                errors.append(f"Backend code must be Python, not JS/TS: {rel(path)}")

    frontend_package = FRONTEND_DIR / "package.json"
    if frontend_package.exists():
        try:
            package = json.loads(frontend_package.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid frontend package.json: {exc}")
        else:
            deps = {}
            for key in ("dependencies", "devDependencies"):
                deps.update(package.get(key, {}) or {})
            if "react" not in deps or "react-dom" not in deps:
                errors.append("product/croda-frontend/package.json must include react and react-dom")
            forbidden_frontend_frameworks = {"vue", "svelte", "@angular/core"}
            used_forbidden = sorted(forbidden_frontend_frameworks.intersection(deps))
            if used_forbidden:
                errors.append(
                    "Frontend framework is fixed to React; remove forbidden framework dependencies: "
                    + ", ".join(used_forbidden)
                )

    notes_dir = ROOT / "project-management/dev/notes"
    if notes_dir.exists():
        for path in notes_dir.glob("work-log-*.md"):
            errors.append(
                "Work logs must be stored per member under "
                f"project-management/dev/notes/work-log/<member-id>/, not {rel(path)}"
            )

    registered_members: set[str] = set()
    if WORK_LOG_ROOT.exists() and not TEAM_MEMBERS_FILE.exists():
        errors.append(
            "project-management/dev/team/members.json is required when in-repo work logs are enabled"
        )

    if TEAM_MEMBERS_FILE.exists():
        try:
            team_config = json.loads(TEAM_MEMBERS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid team members registry: {exc}")
        else:
            members = team_config.get("members")
            if not isinstance(members, list) or not members:
                errors.append("project-management/dev/team/members.json must contain a non-empty members list")
            else:
                for index, member in enumerate(members):
                    if not isinstance(member, dict):
                        errors.append(f"Team member entry #{index + 1} must be an object")
                        continue
                    member_id = member.get("id")
                    if not isinstance(member_id, str) or not MEMBER_ID_RE.match(member_id):
                        errors.append(
                            "Team member id must use lowercase letters, numbers, and hyphens: "
                            f"entry #{index + 1}"
                        )
                        continue
                    if member_id in registered_members:
                        errors.append(f"Duplicate team member id in registry: {member_id}")
                    registered_members.add(member_id)

    if WORK_LOG_ROOT.exists():
        for member_dir in WORK_LOG_ROOT.iterdir():
            if not member_dir.is_dir():
                errors.append(f"Unexpected file in work-log root: {rel(member_dir)}")
                continue
            if not MEMBER_ID_RE.match(member_dir.name):
                errors.append(
                    "Work log member directory must use lowercase letters, numbers, and hyphens: "
                    f"{rel(member_dir)}"
                )
            if registered_members and member_dir.name not in registered_members:
                errors.append(
                    "Work log member directory is not registered in project-management/dev/team/members.json: "
                    f"{rel(member_dir)}"
                )
            for path in member_dir.rglob("*"):
                if path.is_dir():
                    continue
                if path.suffix != ".md":
                    errors.append(f"Work log files must be Markdown: {rel(path)}")
                    continue
                if path.parent != member_dir:
                    errors.append(
                        "Work log member directories should not contain nested folders: "
                        f"{rel(path)}"
                    )
                    continue
                if not WORK_LOG_FILENAME_RE.match(path.name):
                    errors.append(
                        "Work log filename must be YYYYMMDD.md inside a registered member directory: "
                        f"{rel(path)}"
                    )

    if errors:
        print("Croda structure validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Croda structure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
