# Contributing

This repository is a local Python CLI application backed by Markdown operating knowledge, JSON program data, and generated session/report artifacts. Keep contributions small, explicit, and aligned with the behavior that actually exists.

## Branch Naming

Use lowercase, hyphen-separated branch names:

- `feature/<short-description>` for new behavior.
- `fix/<short-description>` for bug fixes.
- `docs/<short-description>` for documentation-only changes.
- `test/<short-description>` for tests or validation assets.
- `chore/<short-description>` for maintenance.

Examples:

```bash
git checkout -b docs/developer-experience-foundation
git checkout -b fix/gemini-error-handling
```

## Commit Message Convention

Use concise conventional-style commit messages:

- `docs: add developer setup guide`
- `feat: add workspace issue filtering`
- `fix: handle missing program record`
- `test: add active program scenario`
- `chore: update repository hygiene`

Each commit should represent one logical change. Avoid mixing application code, JSON program data, generated reports, and documentation unless the relationship is intentional and explained.

## Review Checklist

Before requesting review:

- Confirm the change matches the stated scope.
- Inspect `git diff` and `git diff --stat`.
- Confirm no secrets, credentials, API keys, or local shell configuration were added.
- Confirm generated files are intentional.
- Confirm JSON program data changes are intentional.
- Confirm any user-facing behavior is documented.
- Confirm the change does not silently alter existing program data.
- Confirm error handling is clear for CLI users.

## Testing Checklist

Use the smallest validation that proves the change:

- Run the CLI from the repository root when changing runtime behavior:

```bash
python app/main.py
```

- Use `app/test_gemini.py` only when validating Gemini connectivity:

```bash
python app/test_gemini.py
```

- Check generated files after flows that write output:

```bash
git status --short
git diff --stat
```

- For documentation-only changes, proofread commands, paths, and described behavior against the repository.

There is no currently wired automated Python test suite in the repository.

## Documentation Checklist

Update documentation when changing:

- CLI behavior or menu options.
- Program data shape under `data/programs/`.
- Generated report or session output.
- Gemini configuration requirements.
- Repository structure.
- Development setup or workflow.
- Architecture boundaries or future-vs-current behavior.

Documentation should describe implemented behavior clearly. Future ideas should be labeled as future work.

## When to Use ChatGPT

Use ChatGPT for:

- Brainstorming TPM workflows, program artifacts, and stakeholder communication.
- Drafting or refining Markdown content.
- Exploring product ideas before implementation.
- Summarizing program management concepts.
- Reviewing narrative clarity when repository access is not required.

Do not rely on ChatGPT alone for repository-specific facts unless it has been given the relevant files or output.

## When to Use Codex

Use Codex for:

- Repository-aware documentation updates.
- Code changes and refactoring.
- Reading local files and explaining current behavior.
- Creating focused tests or validation assets.
- Running local commands and reporting results.
- Checking diffs before review.

Give Codex explicit constraints when they matter, such as "do not modify JSON data", "documentation only", "do not create commits", or "do not install packages".

## Architecture Decisions

Architecture decisions should be based on the current repository state and documented tradeoffs.

Use this process:

1. Identify the current behavior and constraints.
2. Describe the problem being solved.
3. Compare practical options.
4. Record the chosen direction in `docs/ARCHITECTURE.md` or a dedicated docs file.
5. Label future considerations separately from implemented behavior.
6. Keep the implementation and documentation in sync.

Decisions that affect persistence, AI behavior, generated artifacts, or developer workflow should be reviewed before implementation.
