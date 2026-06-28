#!/usr/bin/env python3
"""Restore Hermes cron prompts from OpenClaw cron payloads.

Default mode is dry-run. Use --apply to write changes.
This script assumes Hermes Agent is installed locally because it imports
Hermes' cron.jobs module to preserve schema normalization.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


AI_KEYWORDS = [
    "AI Ideas",
    "Issue",
    "PR",
    "创意",
    "Papers",
    "Product Hunt",
    "Reddit",
    "Hugging Face",
    "ArXiv",
    "Twitter",
    "TechCrunch",
    "Dev.to",
    "GitHub",
    "Hacker News",
    "应用场景",
    "2077日报",
]

ROOT_KEYWORDS = ["系统健康", "定时任务健康", "订阅账单", "三爪"]


def display_path(path: Path, home: Path) -> str:
    """Return a stable path for reports without exposing local usernames."""
    try:
        return "$HOME/" + str(path.expanduser().relative_to(home)).rstrip("/")
    except ValueError:
        return str(path)


def redact_delivery(delivery: object) -> object:
    """Keep routing shape while redacting concrete recipient identifiers."""
    if not isinstance(delivery, dict):
        return delivery
    redacted = dict(delivery)
    for key in ("to", "chat_id", "channel_id", "thread_id", "user_id", "phone", "email"):
        if redacted.get(key):
            redacted[key] = "[REDACTED]"
    return redacted


def choose_workdir(name: str, prompt: str, root_workdir: str, ai_workdir: str) -> str:
    text = f"{name}\n{prompt}"
    if any(keyword in text for keyword in ROOT_KEYWORDS):
        return root_workdir
    if any(keyword in text for keyword in AI_KEYWORDS) or "ava-agent/awesome-ai-ideas" in text:
        return ai_workdir
    return root_workdir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--hermes-home", default=str(Path.home() / ".hermes"))
    parser.add_argument("--openclaw-home", default=str(Path.home() / ".openclaw"))
    parser.add_argument(
        "--hermes-agent",
        default=None,
        help="Hermes Agent checkout path. Defaults to <hermes-home>/hermes-agent.",
    )
    parser.add_argument("--root-workdir", default=None)
    parser.add_argument("--ai-workdir", default=None)
    args = parser.parse_args()

    hermes_home = Path(args.hermes_home).expanduser()
    openclaw_home = Path(args.openclaw_home).expanduser()
    user_home = Path.home().expanduser()
    hermes_agent = Path(args.hermes_agent).expanduser() if args.hermes_agent else hermes_home / "hermes-agent"
    source_path = openclaw_home / "cron" / "jobs.json.migrated"
    jobs_path = hermes_home / "cron" / "jobs.json"
    root_workdir = args.root_workdir or str(hermes_home / "openclaw-workspaces" / "workspace")
    ai_workdir = args.ai_workdir or str(hermes_home / "openclaw-workspaces" / "workspace" / "awesome-ai-ideas")

    if not source_path.exists():
        raise SystemExit(f"missing OpenClaw cron source: {source_path}")
    if not jobs_path.exists():
        raise SystemExit(f"missing Hermes cron jobs file: {jobs_path}")
    if not hermes_agent.exists():
        raise SystemExit(f"missing Hermes Agent path: {hermes_agent}")

    venv_python = hermes_agent / "venv" / "bin" / "python"
    if sys.version_info < (3, 10) and venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])

    sys.path.insert(0, str(hermes_agent))
    from cron.jobs import load_jobs, update_job  # type: ignore

    source = json.loads(source_path.read_text())
    source_by_id = {job["id"]: job for job in source.get("jobs", [])}
    now = datetime.now(timezone.utc).isoformat()
    backup_dir = None
    if args.apply:
        backup_dir = hermes_home / "backups" / f"cron-opt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(jobs_path, backup_dir / "jobs.before.json")

    changes = []
    skipped = []

    for job in load_jobs():
        src = source_by_id.get(job["id"])
        if not src:
            skipped.append({"id": job["id"], "name": job.get("name"), "reason": "no OpenClaw source job"})
            continue

        payload = src.get("payload") or {}
        message = (payload.get("message") or "").strip()
        if not message:
            skipped.append({"id": job["id"], "name": job.get("name"), "reason": "empty payload.message"})
            continue

        message = message.replace("~/.openclaw/workspace", str(hermes_home / "openclaw-workspaces" / "workspace"))
        workdir = choose_workdir(job.get("name") or "", message, root_workdir, ai_workdir)

        changes.append(
            {
                "id": job["id"],
                "name": job.get("name"),
                "prompt_changed": job.get("prompt") != message,
                "old_prompt_length": len(job.get("prompt") or ""),
                "new_prompt_length": len(message),
                "old_workdir": display_path(Path(job["workdir"]), user_home) if job.get("workdir") else None,
                "new_workdir": display_path(Path(workdir), user_home),
                "enabled": job.get("enabled"),
                "state": job.get("state"),
                "next_run_at": job.get("next_run_at"),
                "openclaw_timeout_seconds": payload.get("timeoutSeconds"),
                "openclaw_model": payload.get("model"),
                "openclaw_delivery": redact_delivery(src.get("delivery")),
            }
        )

        if args.apply:
            migration = dict(job.get("migration") or {})
            migration.update(
                {
                    "source": "openclaw",
                    "prompt_restored_from": str(source_path),
                    "prompt_restored_at": now,
                    "openclaw_timeout_seconds": payload.get("timeoutSeconds"),
                    "openclaw_model": payload.get("model"),
                    "openclaw_delivery": redact_delivery(src.get("delivery")),
                    "optimized_by": "optimize-cron-from-openclaw.py",
                }
            )
            update_job(job["id"], {"prompt": message, "workdir": workdir, "migration": migration})

    report = {
        "apply": args.apply,
        "source": display_path(source_path, user_home),
        "jobs_path": display_path(jobs_path, user_home),
        "root_workdir": display_path(Path(root_workdir), user_home),
        "ai_workdir": display_path(Path(ai_workdir), user_home),
        "changed_or_checked": len(changes),
        "skipped": skipped,
        "changes": changes,
    }

    if backup_dir is not None:
        report["backup_dir"] = display_path(backup_dir, user_home)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
