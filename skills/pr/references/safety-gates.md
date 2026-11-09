# Safety Gates

A pull request publishes code and context to other people. Run the safety gate
before pushing or creating the PR.

## Secret and sensitive-file scan

Inspect the changed files and the diff for:

- `.env`, `.env.*`, `.envrc`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`, `id_ed25519`;
- credentials, tokens, passwords, and connection strings;
- secret stores, vault configuration, and cloud credentials;
- private keys and signing material;
- personal data, customer data, and production dumps.

Example commands:

```bash
git diff --name-only <base>...HEAD
git diff <base>...HEAD | grep -nE 'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_|-----BEGIN .*PRIVATE KEY-----'
```

Rules:

- Stop when a possible secret is present.
- Ask the user to remove it and rotate the credential.
- Do not print the secret value. Replace it with `[REDACTED]`.
- Do not continue with a "temporary" secret in the diff.

## Sensitive-code changes

Require explicit human confirmation when the diff touches:

- authentication and session handling;
- authorization, roles, and permission checks;
- billing, payments, and pricing;
- data deletion, retention, or migration;
- encryption, key management, and signing;
- CI/CD, infrastructure, and deployment configuration;
- dependency lockfiles and build scripts.

Record the confirmation and the reviewer in the handoff. Prefer a draft PR when
the change needs a security review.

## History and remote safety

- Never force-push.
- Never rewrite history, amend, rebase, or reset unless the user explicitly asks.
- Never delete a remote branch.
- Never bypass branch protection, required reviews, or required checks.
- Never enable auto-merge.
- Stop when `git push` is rejected. Report the reason instead of working around it.

## Access

Confirm authentication before creating the PR:

```bash
gh auth status
```

Do not ask the user to paste a token into the conversation. Use the CLI login
flow or the environment the user already configured.

## Redaction

When reporting a risk, include the file, the line, and the category, not the
value:

```text
Potential GitHub token in config/deploy.yml:14. Value redacted.
```

## Incident response

If a secret was already pushed:

1. Stop the PR workflow.
2. Tell the user to rotate the credential.
3. Remove the secret from the branch and, when necessary, from history.
4. Record the incident and the rotation in the handoff.
5. Do not create the PR until the credential is rotated and the diff is clean.
