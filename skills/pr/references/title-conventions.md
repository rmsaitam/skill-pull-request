# Title Conventions

The title is the first thing a reviewer reads. It must describe the whole change,
not the last commit.

## Rules

- Use the repository language and convention.
- Prefer the imperative mood: `Add token validation`, not `Added token validation`.
- Keep it at or below 70 characters.
- Do not end with a period.
- Do not use a generic title such as `Update files`, `Fix bug`, or `Changes`.
- Do not use an issue number as the whole title.
- Derive the title from the complete diff and commit range.
- Describe the user-visible outcome or the engineering change, not the file list.

## Conventional Commits

When the repository uses Conventional Commits, keep the prefix:

```text
feat(auth): add token validation
fix(api): reject expired sessions
refactor(db): extract connection pool
docs(pr): document the validation contract
test(pr): cover secret detection
chore(ci): cache dependencies
```

Guidelines:

- Use the type that matches the dominant change.
- Use a scope only when the repository uses scopes.
- Keep the subject short and imperative.
- Put breaking-change details in the body, not only in the title.

## Examples

| Weak | Better |
| --- | --- |
| `Update auth` | `feat(auth): add token validation` |
| `Fix tests` | `test(api): cover expired session handling` |
| `PR for issue 482` | `feat(auth): add token validation` |
| `Changes after review` | `fix(parser): handle empty input` |
| `WIP` | `feat(search): add prefix matching` |

## Length

- Target: 50 characters or fewer.
- Hard limit: 70 characters.
- Above 70: shorten the subject and move details to the body.
- Above 80: the validator fails.

## Language

- Follow the repository's recent merged PR titles.
- Do not mix languages in the same title.
- Keep identifiers, API names, and error codes in their original form.
