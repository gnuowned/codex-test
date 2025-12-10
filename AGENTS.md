# Repository Guidelines

## Project Structure & Module Organization
- Start new code in `src/`; keep entrypoints minimal and push logic into modules.
- Place automated tests in `tests/` mirroring `src/` paths (e.g., `src/auth/service.ts` ↔ `tests/auth/service.test.ts`).
- Store documentation or design notes in `docs/`; keep sample data in `fixtures/` when required.
- Keep configuration in the repo root (`package.json`, `Makefile`, `pyproject.toml`) so commands remain discoverable.

## Build, Test, and Development Commands
- Add project scripts to a single entrypoint (prefer `make` targets or npm/yarn scripts) and document them in this file.
- Suggested defaults: `npm run dev` for local watch mode, `npm test` for unit tests, `npm run lint` for static checks, and `npm run build` for production bundles.
- Use `.env.example` to capture required environment variables; avoid hardcoding secrets.

## Coding Style & Naming Conventions
- Default to the language formatter for the stack you introduce (e.g., `prettier` for JS/TS, `ruff` for Python). Check in config files.
- Use 2-space indentation for JS/TS and JSON; 4 spaces for Python; keep line length at 100–120 chars unless tooling enforces otherwise.
- Name modules and files with kebab-case or snake_case; classes in PascalCase; functions/variables in camelCase (JS/TS) or snake_case (Python).

## Testing Guidelines
- Co-locate fixtures with tests; prefer isolated unit tests over slow integration tests until the stack stabilizes.
- Use descriptive test names ("does X when Y") and mark slow or flaky tests with explicit tags.
- Aim for coverage on critical flows; document any intentional gaps in `TESTING_NOTES.md`.

## Commit & Pull Request Guidelines
- Follow Conventional Commits where practical (`feat:`, `fix:`, `chore:`, `docs:`). Keep subjects under ~72 chars.
- In PR descriptions, list intent, key changes, and testing performed; link issues or tickets when available.
- Include screenshots or logs for user-facing changes or failing cases that were fixed.

## Security & Configuration Tips
- Never commit secrets; use `.env` + `.gitignore` and provide sanitized samples.
- Add minimal RBAC/API keys for local use; rotate credentials promptly if exposed.
- Favor least-privilege defaults in new services and document required permissions in `docs/security.md`.
