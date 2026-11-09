# Validation Checklist

Use this checklist when Python is unavailable or when you need to verify a PR body
manually. The script `skills/pr/scripts/validate_pr.py` is the source of truth;
this checklist mirrors its gates.

## 1. Repository state

- [ ] The working tree is clean, or the user confirmed the included changes.
- [ ] The current branch is not the base branch.
- [ ] There is at least one commit between the base and `HEAD`.
- [ ] The remote is the intended repository.
- [ ] No secret, credential, or sensitive file is present in the diff.

## 2. Base and issue

- [ ] The base branch was supplied or detected and validated.
- [ ] The merge base exists locally.
- [ ] The issue or specification was found, or its absence was recorded.
- [ ] Closing keywords are used only when the PR really closes the issue.
- [ ] Reference keywords are used for issues that must remain open.

## 3. Title

- [ ] The title describes the whole change.
- [ ] The title is imperative and has no trailing period.
- [ ] The title is at or below 70 characters.
- [ ] The Conventional Commits prefix is preserved when the repository uses it.
- [ ] The title is not generic and is not only an issue number.

## 4. Body structure

- [ ] The repository template was used when it exists.
- [ ] `Summary` is present and explains what, why, and the impact.
- [ ] `Changes` is present and groups changes by area.
- [ ] `Related issue` is present and uses a valid keyword or `None`.
- [ ] `How to test` is present and has numbered steps.
- [ ] `Risks and notes` is present and lists breaking changes and limitations.
- [ ] `Checklist` is present and has at least three items.
- [ ] No section is empty or filled with a placeholder.

## 5. Content quality

- [ ] The body does not contain `TODO`, `TBD`, `FIXME`, or a placeholder.
- [ ] The body does not contain a secret or personal data.
- [ ] The test plan has an expected result.
- [ ] The risk section names the highest-risk area for reviewers.
- [ ] The body does not claim that a check ran when it did not.

## 6. Validation and submission

- [ ] `validate_pr.py` passes with the selected options.
- [ ] `gh auth status` succeeds.
- [ ] The body was written to a file and passed with `--body-file`.
- [ ] The PR was created with the intended base and head branches.
- [ ] An existing PR was updated instead of duplicated.
- [ ] No merge, force-push, or check bypass occurred.
- [ ] The handoff reports the URL, branches, counts, checks, and next actions.
