# Pull Request

[![skills.sh](https://skills.sh/b/rmsaitam/skill-pull-request)](https://skills.sh/rmsaitam/skill-pull-request)

A pull request skill for coding agents. It creates, updates, or reviews a GitHub
Pull Request from the current branch with a structured and validated body.

The skill analyzes the full diff against a base branch, finds the related issue,
validates the repository state, runs the project checks, checks for secrets and
risky changes, and submits the PR with the `gh` CLI. It never merges,
force-pushes, changes the diff, or bypasses a failed check.

## What it does

- Verifies the branch, working tree, remote, and commit range.
- Detects the base branch or asks for it when ambiguous.
- Reads every commit and changed file, not only the last commit.
- Finds the issue or specification and chooses closing or reference keywords.
- Scans the diff for secrets, sensitive files, and authentication changes.
- Runs the repository lint, typecheck, test, and build commands when available.
- Drafts a title and a structured body, then validates the body with
  `skills/pr/scripts/validate_pr.py`.
- Creates the PR with `gh pr create` or updates it with `gh pr edit`, always using
  `--body-file`.
- Returns the PR URL, branches, commit and file counts, check results, and next actions.

## Supported agents

| Agent | Manifest |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json` |
| Codex | `.codex-plugin/plugin.json` |
| Cursor | `.cursor-plugin/plugin.json` |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` |
| Antigravity | `plugin.json` |
| skills.sh / generic Agent Skills | `skills/pr/SKILL.md` |

All agents use the same skill and PR body contract.

## Install

### skills.sh

The recommended installation path is the open Agent Skills CLI. It discovers
`skills/pr/SKILL.md` in this repository and installs it for the agents you select.
Node.js 22.20 or newer is required.

```bash
npx skills add rmsaitam/skill-pull-request
npx skills add rmsaitam/skill-pull-request -g -y
```

Use `-g` for a global install and `-y` to skip prompts. To list the skills
available in this repository without installing:

```bash
npx skills add rmsaitam/skill-pull-request --list
```

To install only this skill for a specific agent:

```bash
npx skills add rmsaitam/skill-pull-request --skill pr -a claude-code
```

### Claude Code

Add the marketplace and install the plugin:

```bash
/plugin marketplace add rmsaitam/skill-pull-request
/plugin install pull-request
```

### Codex

Point the Codex marketplace at this repository and install `pull-request`.

### Cursor, Copilot CLI, and Antigravity

Use the plugin marketplace manifests in `.cursor-plugin/`, `.github/plugin/`, or
`plugin.json`, or install through `skills.sh`.

### Manual copy

Copy the skill directory directly:

```bash
mkdir -p ~/.agents/skills
cp -R skills/pr ~/.agents/skills/pr
```

Confirm the package before installing:

```bash
python3 scripts/validate_plugin.py .
```

## Requirements

- Git with access to the repository remote.
- The GitHub CLI `gh`, authenticated with `gh auth status`.
- Python 3.10 or newer for the validators.
- The project's own lint, typecheck, test, and build commands when they exist.

## Usage

Run the skill from the branch that should become the PR:

```text
Use the pr skill to open a pull request against main.
```

Or invoke the command directly:

```text
/pr
/pr --draft
/pr --base develop
/pr --update
/pr --save-body
```

### Arguments

- `--draft`: create the pull request as a draft.
- `--base <branch>`: set the target branch. Default: detect the repository's main branch.
- `--update`: update the title and body of an existing PR instead of creating another.
- `--save-body [path]`: keep the validated body as `PULL-REQUEST.md` or the given path.

### Modes

- **Create**: analyze the branch, validate, push, and run `gh pr create`.
- **Update**: analyze the branch, validate, and run `gh pr edit`.
- **Review only**: inspect the PR and report gaps without editing it. For a full
  diff review, use the `code-review` skill.

## The PR body

The default body contract is:

```md
## Summary

- What this PR does.
- Why the change is necessary.
- Main impact for users, APIs, or operations.

## Changes

- Area/component: relevant change.

## Related issue

Closes #123

## How to test

1. Step to reproduce or validate.
2. Expected result.

## Risks and notes

- Breaking change, migration, configuration, or known limitation.

## Checklist

- [ ] Tests added or updated
- [ ] Lint and typecheck passed
- [ ] Documentation updated when applicable
- [ ] No secret or sensitive data included
```

When `.github/PULL_REQUEST_TEMPLATE.md` exists, its headings replace the default
contract. Use `Closes`, `Fixes`, or `Resolves` only when the PR really closes the
issue. Use `Refs` or `Related to` for issues that must remain open.

## Safety

- Never merge, enable auto-merge, force-push, or rewrite history.
- Never bypass a failed check, required review, or branch protection.
- Stop when a secret, credential, or sensitive file is present in the diff.
- Require human confirmation for changes to authentication, authorization,
  permissions, billing, or destructive data operations.
- Prefer a draft pull request while required checks are pending.

## Validate a body

From this repository:

```bash
python3 skills/pr/scripts/validate_pr.py BODY --title "feat(auth): add token validation"
```

When the skill is installed, resolve `scripts/validate_pr.py` from the installed
`pr` skill directory.

Useful flags:

```bash
python3 skills/pr/scripts/validate_pr.py BODY --title "fix(api): reject expired sessions" --require-issue
python3 skills/pr/scripts/validate_pr.py BODY --template .github/PULL_REQUEST_TEMPLATE.md
python3 skills/pr/scripts/validate_pr.py BODY --allow-unchecked --strict
python3 skills/pr/scripts/validate_pr.py BODY --title "feat(pr): add skill" --require-conventional --json
```

The validator checks required sections, section order, summary depth, test steps,
issue keywords, checklist items, title length and convention, placeholders, and
possible secrets.

## Create and update

The skill runs, in order:

```bash
git push -u origin HEAD
gh pr create --base <base> --head <branch> --title "<title>" --body-file <body-file> --draft
```

Push any new commits first, then update an existing PR:

```bash
git push -u origin HEAD
gh pr edit <number-or-url> --title "<title>" --body-file <body-file>
```

`gh` is GitHub-specific. For GitHub Enterprise Server, authenticate with
`gh auth login --hostname <host>`. For Gitea, use `tea` and keep the same body
contract.

## Repository layout

```text
skills/pr/SKILL.md               Skill instructions
skills/pr/references/            Templates, conventions, safety, and check guidance
skills/pr/scripts/               PR body validator
scripts/validate_plugin.py       Plugin structure validator
commands/                        Slash commands
agents/openai.yaml               Codex agent metadata
assets/                          Icon and logo
tests/                           Validator tests and fixtures
```

## Development

Requires Python 3.10 or newer. The validators use only the standard library.

```bash
make test        # run the test suite
make coverage    # run tests with an 80% coverage gate
make validate    # validate the plugin structure
make check       # coverage plus plugin validation
```

## License

MIT. See `LICENSE`.
