# Monorepo and Enterprise

The default workflow targets GitHub.com with the `gh` CLI. Adapt it when the
repository is a monorepo or the host is different.

## Monorepos

Identify the affected packages or workspaces before writing the body:

```bash
git diff --name-only <base>...HEAD
```

Then map the paths to workspaces using the repository configuration:

- `package.json` workspaces;
- `pnpm-workspace.yaml`;
- `nx.json` or `turbo.json`;
- `lerna.json`;
- `go.work`;
- `Cargo.toml` workspace members;
- `pyproject.toml` workspace or package layout.

Report the affected packages in the Changes section:

```md
## Changes

- `packages/api`: add token validation.
- `packages/web`: show the validation error.
- `packages/shared`: add the shared token schema.
```

Run the checks for each affected package, not only the repository root. Mention
any package whose checks did not run.

## Package-specific templates

Some monorepos keep templates under `packages/*/.github/` or
`.github/PULL_REQUEST_TEMPLATE/`. Use the template that matches the affected
package and state which one was used.

## Reviewers

Monorepos often require code owners. Do not add reviewers without approval. When
the user approves, use:

```bash
gh pr create --reviewer <login> --reviewer <org/team>
```

or update an existing PR:

```bash
gh pr edit <number> --add-reviewer <login>
```

## GitHub Enterprise Server

`gh` works with GitHub Enterprise Server after authentication:

```bash
gh auth login --hostname <host>
gh pr create --repo <host>/<owner>/<repo> ...
```

Confirm the host before creating the PR. Do not assume `github.com`.

## Gitea and other hosts

`gh` is GitHub-specific. For Gitea, use `tea`:

```bash
tea pr create --base <base> --head <branch> --title "<title>"
```

For other hosts, use the host's CLI or API and keep the same body contract. State
the host and the CLI in the handoff.

## Branch protection

Enterprise repositories often require:

- signed commits;
- a linear history;
- required status checks;
- required reviewers;
- a specific merge queue.

Read the repository rules before creating the PR. Do not bypass them. If the
branch cannot be pushed, report the blocking rule and ask the user how to
proceed.
