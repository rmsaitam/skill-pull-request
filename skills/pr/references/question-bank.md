# Question Bank

Use this bank only when the user's message and the repository do not already
answer the question. Ask at most five questions per round. Prefer structured
multiple-choice questions when the host supports them. Otherwise ask numbered
questions and wait for answers.

Do not read the whole bank to the user. Select the questions that reduce the most
uncertainty. If the user already supplied a base, an issue, and a clear scope,
proceed without an interview.

## Round 1: Repository and base

### State

- Is the working tree clean, or should uncommitted changes be committed first?
- Is the current branch the intended head branch?
- Is the remote the intended repository?

### Base

- Which branch should receive the pull request: `main`, `master`, `develop`, or another branch?
- Should the comparison use the merge base (`base...HEAD`) or the tip of the base (`base..HEAD`)?
- Is the repository shallow, and is the merge base available locally?

### Scope

- Are there generated files, vendored code, or migrations that should be excluded?
- Should the PR include every commit on the branch or only a subset?

## Round 2: Issue and specification

### Source

- Which issue, ticket, or specification defines the expected behavior?
- Is the issue in the repository, in an issue tracker, or only in the conversation?
- Should the PR close the issue on merge, or only reference it?

### Traceability

- Which requirements or acceptance criteria should the body cite?
- Are there linked issues or prior discussions that define the scope?
- Is additional scope allowed, or must the PR stay strictly within the issue?

### Missing issue

- If the repository requires an issue and none exists, should one be created first?
- If no issue is required, should the Related issue section say `None`?

## Round 3: Validation and draft

### Checks

- Which checks are authoritative: lint, typecheck, tests, build, or another command?
- Are the checks expected to pass locally, or only in CI?
- Should the PR be a draft while CI is pending?

### Risk

- Does the diff touch authentication, authorization, permissions, billing, or destructive data operations?
- Does the diff contain migrations, environment variables, or configuration changes?
- Are there known limitations that reviewers must know about?

## Round 4: Collaboration

### Reviewers and labels

- Should reviewers, labels, assignees, or milestones be added?
- Who should review the security-sensitive parts?
- Does the repository require a specific review team?

### Language

- Should the title and body be written in English or in another language?
- Does the repository use Conventional Commits?

## Round 5: Monorepo and enterprise

### Monorepo

- Which package, workspace, or application is affected?
- Should the body list every affected workspace?
- Should the PR use a package-specific template or reviewer group?

### Host

- Is this GitHub.com, GitHub Enterprise Server, or another host?
- Which CLI is available: `gh`, `tea`, or another tool?
- Are there host-specific branch protection or authentication requirements?
