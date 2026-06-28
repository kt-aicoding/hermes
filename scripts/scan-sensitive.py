#!/usr/bin/env python3
"""Scan repository files for sensitive data patterns.

The scanner reports only finding type, file, and line number. It never prints
matched values. It is intentionally conservative and supports a small allowlist
for documented placeholders.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


PATTERNS = [
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("openai_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    (
        "assignment_secret",
        re.compile(r"(?i)\b(?:API_KEY|ACCESS_TOKEN|SECRET|PASSWORD|TOKEN)\s*=\s*[^\s#]+"),
    ),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("telegram_bot_token", re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{30,}\b")),
    (
        "jwt_like",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    ),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("absolute_user_path", re.compile(r"/Users/[A-Za-z0-9._-]+")),
    ("long_numeric_id", re.compile(r"(?<!\d)\d{9,15}(?!\d)")),
    ("email_address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
]

ALLOW_LINE_SUBSTRINGS = [
    "ARK_API_KEY=...",
    "API key",
    "GitHub token",
    "Telegram / Discord / Slack token",
    "--migrate-secrets",
    "assignment-style `TOKEN=`, `SECRET=`, `PASSWORD=`, `API_KEY=`",
]

def git_lines(args: list[str]) -> list[str]:
    return subprocess.check_output(args, text=True).splitlines()


def git_bytes(args: list[str]) -> bytes:
    return subprocess.check_output(args, stderr=subprocess.DEVNULL)


def working_files() -> list[str]:
    return sorted(git_lines(["git", "ls-files", "--cached", "--others", "--exclude-standard"]))


def history_blobs() -> list[tuple[str, str, str]]:
    blobs: list[tuple[str, str, str]] = []
    commits = git_lines(["git", "rev-list", "--all"])
    seen: set[tuple[str, str]] = set()
    for commit in commits:
        for rel in git_lines(["git", "ls-tree", "-r", "--name-only", commit]):
            key = (commit, rel)
            if key in seen:
                continue
            seen.add(key)
            try:
                data = git_bytes(["git", "show", f"{commit}:{rel}"])
            except subprocess.CalledProcessError:
                continue
            blobs.append((commit, rel, data.decode(errors="ignore")))
    return blobs


def scan_text(scope: str, rel: str, text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if any(marker in line for marker in ALLOW_LINE_SUBSTRINGS):
            continue
        for finding_type, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(
                    {
                        "scope": scope,
                        "type": finding_type,
                        "file": rel,
                        "line": lineno,
                    }
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true", help="also scan blobs from all Git commits")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    root = Path(".").resolve()
    files = working_files()
    findings: list[dict[str, object]] = []

    for rel in files:
        path = root / rel
        if path.is_file():
            findings.extend(scan_text("working_tree", rel, path.read_text(errors="ignore")))

    commits_scanned = 0
    history_blob_count = 0
    if args.history:
        commits_scanned = len(git_lines(["git", "rev-list", "--all"]))
        for commit, rel, blob in history_blobs():
            history_blob_count += 1
            findings.extend(scan_text(f"git_history:{commit[:12]}", rel, blob))

    result = {
        "scanned_files": len(files),
        "commits_scanned": commits_scanned,
        "history_blobs_scanned": history_blob_count,
        "findings_count": len(findings),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"scanned_files: {result['scanned_files']}")
        if args.history:
            print(f"commits_scanned: {result['commits_scanned']}")
            print(f"history_blobs_scanned: {result['history_blobs_scanned']}")
        print(f"findings_count: {result['findings_count']}")
        for finding in findings:
            print(
                f"{finding['scope']}\t{finding['type']}\t"
                f"{finding['file']}:{finding['line']}"
            )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
