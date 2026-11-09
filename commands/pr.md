---
description: Create, update, or draft a GitHub pull request from the current branch.
argument-hint: "[--draft] [--base <branch>] [--update] [--save-body [path]]"
---

# Pull Request

Invoke the `pr` skill to create or update a pull request for the current branch.
The skill reads the full diff against the base branch, finds the related issue,
validates the repository state, runs the project checks, drafts a structured body,
validates the body, and submits it with the GitHub CLI.

## Instructions

- Do not modify the diff. Do not merge, force-push, rebase, or amend commits.
- Do not bypass a failed check, a required review, or branch protection.
- Stop when the current branch is the base branch or when there is nothing to open.
- Write the body to a temporary file and pass it with `--body-file`. Never use `--body`.
- Validate the body before submitting. Resolve the script path from the `pr`
  skill directory:

  ```bash
  python3 <path-to-skill>/scripts/validate_pr.py <body-file> --title "<title>"
  ```

- Use `Closes #123` only when the PR really closes the issue. Use `Refs #123` or
  `Related to #123` otherwise.
- Detect an existing PR and update it instead of creating a duplicate.
- Create with `gh pr create --base <base> --head <branch> --title "<title>" --body-file <file>`.
- Update with `gh pr edit <number-or-url> --title "<title>" --body-file <file>`.
- Use `--draft` when the user requests a draft or when required checks are pending.
- Do not add reviewers, labels, or assignees without approval.
- Report the PR URL, branches, commit and file counts, check results, and next actions.

## Body contract

Use `.github/PULL_REQUEST_TEMPLATE.md` when it exists. Otherwise use the default
contract: Summary, Changes, Related issue, How to test, Risks and notes, and
Checklist. See `skills/pr/references/pr-body-template.md`.
