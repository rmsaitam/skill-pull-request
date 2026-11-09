# Issue and Spec Discovery

The Related issue section is only as good as the source. Find the requirement
before writing the body, and never invent an issue number or an acceptance
criterion.

## Search order

1. **User input:** an issue number, URL, ticket, or specification supplied by the user.
2. **Commits and branch:** `git log <base>..HEAD --oneline` and the branch name.
3. **Existing PR:** `gh pr view --json number,title,body,url` when a PR already exists.
4. **Repository documents:** search in `docs/`, `specs/`, `tasks/`, `.scratch/`, `README.md`, `PRD.md`, `SPEC.md`, and ADRs.
5. **Ask the user:** when the first four steps do not find the source.

## Closing versus referencing

Use a closing keyword only when the PR really resolves the issue:

```text
Closes #123
Fixes #123
Resolves #123
```

Use a reference keyword when the issue must stay open:

```text
Refs #123
Related to #123
Part of #123
```

Rules:

- Never use `Closes` to make a reference look stronger.
- List one issue per line when the PR closes several issues.
- Do not close an umbrella issue unless every sub-task is complete.
- When there is no issue, write `None` and explain that no issue was required.

## What to extract

From the source, extract:

- the problem and the expected outcome;
- the acceptance criteria, with stable IDs when available;
- the in-scope and out-of-scope items;
- constraints, edge cases, and error behavior;
- requirements that the diff must preserve but does not touch;
- migrations, configuration, and permission changes.

## Traceability

In the body, connect the change to the requirement:

- cite the issue or specification in the Related issue section;
- mention the acceptance criteria that the change implements;
- mention any acceptance criterion that is intentionally not implemented;
- flag scope that goes beyond the issue.

## When no issue exists

- If the repository requires an issue, ask before creating the PR.
- If the repository does not require one, write `None` and explain why in the Summary.
- Do not invent an issue number to satisfy a template.
