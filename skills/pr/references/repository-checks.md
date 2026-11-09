# Repository Checks

Run the checks the repository already defines. Do not invent a command or claim
that a check passed when it did not run.

## Detection

Read the repository manifests and configuration before choosing commands:

| Ecosystem | Files to inspect | Typical commands |
| --- | --- | --- |
| Node.js | `package.json`, lockfiles, `.npmrc` | `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` |
| pnpm | `pnpm-lock.yaml`, `package.json` | `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` |
| Yarn | `yarn.lock`, `package.json` | `yarn lint`, `yarn typecheck`, `yarn test`, `yarn build` |
| Bun | `bun.lockb`, `package.json` | `bun run lint`, `bun test`, `bun run build` |
| Python / uv | `pyproject.toml`, `uv.lock` | `uv run pytest`, `uv run ruff check`, `uv run mypy` |
| Python / poetry | `pyproject.toml`, `poetry.lock` | `poetry run pytest`, `poetry run ruff check` |
| Python / pip | `requirements*.txt`, `tox.ini`, `noxfile.py` | `pytest`, `ruff check`, `mypy` |
| Make | `Makefile` | `make test`, `make lint`, `make check` |
| Just | `justfile` | `just test`, `just lint`, `just check` |
| Rust | `Cargo.toml` | `cargo test`, `cargo clippy`, `cargo build` |
| Go | `go.mod` | `go test ./...`, `go vet ./...`, `go build ./...` |
| Java / Maven | `pom.xml` | `mvn test`, `mvn verify` |
| Java / Gradle | `build.gradle*` | `./gradlew test`, `./gradlew check` |

## Priority

Run checks in this order:

1. The checks documented in `CONTRIBUTING.md` or the README.
2. The checks configured in CI.
3. The scripts declared in the package manifest.
4. The ecosystem defaults.

## Failure policy

- Stop when a check fails and the failure is caused by the change.
- Report the command, the failing output, and the likely cause.
- Propose the smallest fix and wait for instructions.
- Do not open a PR with a known, unexplained failure.
- Do not disable, skip, or weaken a check to make the PR pass.
- If a failure is pre-existing and unrelated, state that with evidence and ask whether the user accepts it.

## Partial runs

When not every check can run locally, record:

- which checks ran;
- which checks were skipped;
- the reason for each skip;
- which checks should be verified in CI.

Prefer a draft PR when required checks are pending or unavailable locally.

## CI

After creating the PR, check the status when `gh` is available:

```bash
gh pr checks
```

Report the result. Do not merge when checks are failing or pending.
