# PR Body Template

Use the repository template when it exists. Otherwise use the default contract
below. The body must let a reviewer understand what changed, why, how to test it,
and what could go wrong without reading the whole diff first.

## Template detection

Check these paths in order:

1. `.github/PULL_REQUEST_TEMPLATE.md`
2. `.github/pull_request_template.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `docs/PULL_REQUEST_TEMPLATE.md`
5. A template supplied by the user

Use the first file that exists. Preserve its headings and fill every section.
When a required section does not apply, write `N/A` and explain why instead of
leaving it empty.

## Default contract

```md
## Summary

- What this PR does.
- Why the change is necessary.
- Main impact for users, APIs, or operations.

## Changes

- Area/component: relevant change.
- Area/component: relevant change.

## Related issue

Closes #123

## How to test

1. Step to reproduce or validate.
2. Alternative scenario or edge case.
3. Expected result.

## Risks and notes

- Breaking change, migration, configuration, or known limitation.
- Area that needs special reviewer attention.

## Checklist

- [ ] Tests added or updated
- [ ] Lint and typecheck passed
- [ ] Documentation updated when applicable
- [ ] No secret or sensitive data included
```

## Content rules

### Summary

- State the problem, the change, and the outcome.
- Write for a reviewer who has not read the issue.
- Keep it to three to five bullets or a short paragraph.

### Changes

- Group changes by component or behavior, not by file.
- Call out public API changes, migrations, and configuration.
- Mention deleted behavior and replacements.

### Related issue

Use exactly one of these forms:

| Intent | Keyword | Example |
| --- | --- | --- |
| Close the issue on merge | `Closes`, `Fixes`, `Resolves` | `Closes #123` |
| Reference without closing | `Refs`, `Related to`, `Part of` | `Refs #123` |
| No issue | `None` | `None` |

Never use a closing keyword for an issue that must remain open. When the PR closes
more than one issue, list each one on its own line.

### How to test

- Use numbered steps.
- Include the expected result.
- Include at least one edge case or negative scenario when relevant.
- Mention the commands, fixtures, or accounts a reviewer needs.

### Risks and notes

- List breaking changes and migration steps.
- List configuration, environment variables, and permissions that must change.
- List known limitations and follow-up work.
- Point reviewers to the highest-risk files or decisions.

### Checklist

- Keep the repository checklist when one exists.
- Mark an item only when it is true.
- For a draft PR, unchecked items are acceptable but must be intentional.

## Quality bar

A good body answers:

- What problem does this solve?
- What changed, and what did not change?
- How can a reviewer verify it?
- What could break, and how is it mitigated?
- Which issue or specification does it implement?

A weak body contains only a commit list, a generic sentence, or no test plan.
