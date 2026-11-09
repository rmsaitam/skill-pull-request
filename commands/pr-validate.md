---
description: Validate a pull request title and body before creating or updating the PR.
argument-hint: "[path/to/body.md] [--title <title>] [--template <path>]"
---

# Validate Pull Request

Validate a pull request body produced by the `pr` skill before it is submitted.

## Instructions

- Default to a body file supplied by the user. Do not read a stale `PULL-REQUEST.md`
  unless the user points to it.
- Run the bundled validator. Resolve the script path from the `pr` skill
  directory:

  ```bash
  python3 <path-to-skill>/scripts/validate_pr.py <body-file> --title "<title>"
  ```

- Use `--template <path>` to validate against the repository PR template.
- Use `--require-issue` when the repository requires a linked issue.
- Use `--require-checklist` to reject unchecked checklist items.
- Use `--allow-unchecked` for a draft pull request.
- Use `--require-conventional` when the repository uses Conventional Commits.
- Use `--json` for machine-readable output and `--strict` to treat warnings as failures.
- Do not modify the body unless the user explicitly asks for fixes. If fixes are
  requested, preserve the content and re-run the validator.
