# Contributing

This repository is intended to become a collaborative AI automation system for solopreneurs.

## Start here

1. Read `README.md`.
2. Inspect `.ai/` for system instructions and architecture.
3. Check GitHub Issues before starting work.
4. Pick an issue or open one using the appropriate template.
5. Create a branch.
6. Make the smallest coherent change.
7. Test it.
8. Open a pull request.

## Branch naming

Use:

- `feature/<short-name>`
- `fix/<short-name>`
- `task/<short-name>`
- `integration/<short-name>`
- `docs/<short-name>`

## Commit style

Prefer:

- `feat: add ...`
- `fix: resolve ...`
- `task: implement ...`
- `docs: update ...`
- `refactor: simplify ...`

## Rules

- Never commit API keys, tokens, cookies, passwords, or private credentials.
- Keep provider-specific code isolated behind clear interfaces.
- Prefer small, testable modules.
- Document new environment variables in `.env.example`.
- If a change affects an agent workflow, update the relevant architecture/workflow documentation.
- One PR should solve one coherent problem.

## For contributors

If you are unsure where to start, search for issues labelled `good first issue`, `help wanted`, or `task`.
