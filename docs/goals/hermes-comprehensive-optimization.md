# Hermes Comprehensive Exploration And Optimization Goal

## Outcome

Make this repository a public, reusable, verifiable Hermes/OpenClaw migration practice repository, with clear onboarding, accurate docs, safe scripts, no unresolved sensitive-data findings, and `origin/main` synchronized with the local `main` branch.

## Context

Workdir: repository root (`$REPO_ROOT`)

Remote: `https://github.com/kt-aicoding/hermes`

Before continuing after any resume or context compaction, reread current state instead of relying on memory:

1. `README.md`
2. `docs/`
3. `scripts/`
4. `git status --short --branch`
5. `git log --oneline --decorate -5`
6. `gh repo view kt-aicoding/hermes --json nameWithOwner,url,visibility,defaultBranchRef`

## Scope

In scope:

- README information architecture, diagrams, quick start, migration path, safety boundaries, and public onboarding clarity.
- Documentation under `docs/`, including installation, OpenClaw migration, launchd/cron operation, cron optimization, and verification checklists.
- Scripts under `scripts/`, including static safety, syntax, default behavior, and consistency with documentation.
- GitHub remote synchronization and repository metadata checks.
- Sensitive-data and local-identifier scanning for current repository files and current history.
- Goal-related commits and pushes to `origin/main`.

Out of scope unless explicitly authorized by the user:

- Modifying real `$HOME/.hermes` or `$HOME/.openclaw` runtime data.
- Reading, printing, or committing raw secrets, tokens, cookies, `.env` contents, or private logs.
- Enabling global auto-approval or automatic external messaging.
- Creating real GitHub issues or pull requests.
- Rewriting Git history or force-pushing.
- Modifying Hermes Agent source code.

## Constraints

- Protect dirty worktrees. Stage and commit only goal-related files.
- Do not revert user changes unless explicitly asked.
- Public documentation should use `$HOME`, environment variable names, placeholders, or relative paths instead of local absolute user paths.
- Do not include personal chat IDs, phone numbers, raw tokens, private logs, or copied credential values.
- Prefer Mermaid for diagrams and avoid unnecessary binary assets.
- Scripts must be safe by default: read-only checks stay read-only, and writing behavior requires explicit `--apply` or equivalent.

## Milestones

1. Inventory the repository and identify README/docs/scripts gaps from current state.
2. Improve public onboarding so a reader can understand the purpose quickly and reproduce the migration safely.
3. Align docs and scripts so paths, commands, defaults, and safety boundaries do not contradict each other.
4. Validate script syntax, documentation structure, Mermaid blocks, and sensitive-data hygiene.
5. Commit and push related changes, then complete a current-state audit.

## Per-item loop

For README, each docs file, and each script:

1. Inventory: identify the file purpose, readers, and related commands or scripts.
2. Targeted read: inspect the current file, related docs, and related scripts.
3. Improve: make the smallest complete change that improves accuracy, reusability, safety, or onboarding.
4. Validate: run relevant static checks, syntax checks, sensitive scans, and current-state git checks.
5. Review diff: confirm the diff is goal-related and does not leak sensitive data.
6. Commit/push: stage only related files and push to `origin/main`.
7. Record blockers if validation or remote state cannot be completed.

## Verification

Use current-state evidence. At minimum, run or justify an equivalent:

```bash
git status --short --branch
git log --oneline --decorate -5
find . -maxdepth 3 -type f -print | sort
python3 -m py_compile scripts/*.py
python3 scripts/scan-sensitive.py --history
git diff --stat
gh repo view kt-aicoding/hermes --json nameWithOwner,url,visibility,defaultBranchRef
```

Sensitive-data scanning must cover tracked files and current history for:

- GitHub token patterns
- OpenAI/Anthropic/API key patterns
- assignment-style `TOKEN=`, `SECRET=`, `PASSWORD=`, `API_KEY=`
- private key blocks
- Telegram bot token patterns
- JWT-like strings
- AWS access key patterns
- `/Users/<name>` absolute paths
- known local usernames
- long numeric IDs
- email addresses

Do not print matched sensitive values. Report only finding type, file path, and line number. Resolve or document any false positives.

## Done when

The goal is complete only when all are true:

- README has clear purpose, TL;DR, diagrams, quick start, migration flow, script descriptions, docs navigation, and safety boundaries.
- `docs/` content is consistent with README and scripts.
- `scripts/` pass syntax checks and preserve safe default behavior.
- Mermaid diagrams and Markdown fences are structurally valid enough for GitHub rendering.
- Sensitive scan has zero unresolved findings.
- All goal-related changes are committed and pushed.
- `git status --short --branch` shows local `main` synchronized with `origin/main`.
- `gh repo view kt-aicoding/hermes` confirms the expected public repo and default branch.
- A completion audit has inspected current state and every explicit requirement above.

## If blocked

- If GitHub auth blocks push or repo inspection, record the attempted command, timestamp, error category, and required owner action; continue safe local work.
- If Hermes runtime is unavailable, complete static validation and document the missing prerequisite instead of fabricating runtime results.
- If unpushed sensitive data is found, redact or remove it, then rerun scans before committing.
- If already-pushed real sensitive data is found, stop and ask the user before history rewriting or force-pushing.
- If a requested action requires reading secrets, enabling auto-approval, sending external messages, or changing repository visibility/settings, pause and ask the user.

## Completion audit

Before marking complete:

- [ ] Reread README, docs, scripts, and git status from current state.
- [ ] Enumerate all in-scope files.
- [ ] Confirm each in-scope file is completed, not applicable, or externally blocked.
- [ ] Confirm each completed item has validation evidence.
- [ ] Confirm pushed commits match `origin/main`.
- [ ] Confirm sensitive scans pass with no unresolved findings.
- [ ] Confirm no unrelated dirty files remain.
- [ ] Confirm final report contains no raw secret values.

## Final report

The final report must include:

- Summary of improvements
- Files changed
- Commit hash and remote branch
- Validation commands and results
- Sensitive scan result
- Remote repository URL
- Remaining limitations or external blockers, if any
