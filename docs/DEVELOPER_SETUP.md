# Developer Setup

## Project Overview

TPM AI Agent is a local command-line assistant for Technical Program Managers. The current application loads Markdown operating knowledge, builds prompts for program analysis, optionally calls the Gemini API, stores program state as local JSON files, and generates Markdown executive reports.

The implemented runtime is intentionally simple:

- Python CLI entry point under `app/`.
- Static TPM knowledge under `instructions/`, `knowledge/`, `playbooks/`, `templates/`, `personas/`, `examples/`, and `tests/`.
- Program data under `data/programs/`.
- Generated prompts and responses under `sessions/`.
- Generated executive reports under `reports/executive/`.

## macOS Setup

Open Terminal and work from the repository root:

```bash
cd /Users/javi/Documents/TPM-AI-Agent
```

Check that macOS can find Python and Git:

```bash
python3 --version
git --version
```

## Homebrew Installation

Homebrew is the recommended package manager for installing local developer tools on macOS.

Check whether Homebrew is installed:

```bash
brew --version
```

If it is missing, install it from the official Homebrew instructions:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, follow any shell profile instructions printed by Homebrew, then verify:

```bash
brew doctor
```

## Python Virtual Environment

Create a local virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Confirm Python points to the virtual environment:

```bash
which python
python --version
```

Install the pinned and bounded dependencies:

```bash
python -m pip install -r requirements.txt
```

The application uses `pypdf` for selectable-text PDF extraction and validation,
FastAPI dependencies for the read-only API, and the isolated `reportlab==5.0.0`
backend dependency for ART-1.0. ReportLab is not imported by the Program domain,
Markdown reporting, persistence, or renderer-neutral contracts.

ART-1.0 owns two versioned Inter 4.1 static font assets under
`app/assets/fonts/inter/`. Do not install or substitute a system copy of Inter. The
runtime validates the bundled Regular and SemiBold files against their approved
SHA-256 values. The directory also contains the SIL Open Font License 1.1 and official
source metadata.

After installing dependencies, validate the environment:

```bash
python scripts/doctor.py
```

The doctor reports the exact ReportLab version and bundled-font checksum status. It
does not download fonts, generate PDFs, repair dependencies, or modify ReportLab
configuration.

## Git Installation

Install Git with Homebrew if it is not already available:

```bash
brew install git
```

Verify:

```bash
git --version
git status
```

## GitHub CLI Installation

Install GitHub CLI with Homebrew:

```bash
brew install gh
```

Authenticate when needed:

```bash
gh auth login
gh auth status
```

GitHub CLI is useful for repository hosting workflows, pull requests, and issue tracking. The local application does not require it to run.

## Codex Installation and PATH Troubleshooting

Install Codex according to the current official OpenAI Codex instructions for your environment.

After installation, verify the executable is available:

```bash
codex --version
which codex
```

If `codex` is not found:

- Restart the terminal after installation.
- Check whether the install location is in `PATH`.
- Print the current path:

```bash
echo "$PATH"
```

- For Homebrew-installed tools on Apple Silicon, confirm `/opt/homebrew/bin` is in `PATH`.
- For Homebrew-installed tools on Intel Macs, confirm `/usr/local/bin` is in `PATH`.
- Add the appropriate path in your shell profile, such as `~/.zshrc`, then restart the terminal.

## Gemini API Configuration

The application calls Gemini from `app/llm.py` only when the `GEMINI_API_KEY` environment variable is configured.

Set the key for the current terminal session:

```bash
export GEMINI_API_KEY="your-api-key"
```

Confirm it is set without printing the value:

```bash
test -n "$GEMINI_API_KEY" && echo "GEMINI_API_KEY is set"
```

To make it persistent for future zsh sessions:

```bash
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.zshrc
source ~/.zshrc
```

Do not commit API keys, shell profiles, `.env` files, or generated credentials to the repository.

## Running the Application

From the repository root, activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the CLI:

```bash
python app/main.py
```

The menu currently supports:

- Start a New Program.
- Manage an Active Program.
- Major Incident placeholder.
- Executive Review placeholder.
- Operational Readiness placeholder.

The New Program flow writes:

- `sessions/last_prompt.md`
- `sessions/last_response.md`

The Active Program workspace reads and writes:

- `data/programs/*.json`

Executive report generation writes:

- `reports/executive/*.md`

## Running Codex

Start Codex from the repository root:

```bash
codex
```

Use Codex for repository-aware development work such as documentation updates, code review, test planning, implementation tasks, and structured refactoring. Before asking Codex to edit files, state any constraints clearly, especially whether code, data, generated files, or commits are out of scope.

## Common Troubleshooting

### `ModuleNotFoundError` for Local Modules

Run the application from the repository root:

```bash
python app/main.py
```

The current modules use local imports such as `from router import route`, so the working directory matters.

### `ERROR: GEMINI_API_KEY is not configured.`

Set `GEMINI_API_KEY` in the active shell:

```bash
export GEMINI_API_KEY="your-api-key"
```

Then run the application again.

### `ERROR calling Gemini API`

Check:

- `GEMINI_API_KEY` is valid.
- Network access is available.
- The configured model in `app/llm.py` is available to the key.
- The Gemini API endpoint is reachable from the current network.

### `python: command not found`

Use `python3` or activate the virtual environment:

```bash
source .venv/bin/activate
python --version
```

### Generated Files Changed Unexpectedly

Running the application can modify:

- `data/programs/*.json`
- `sessions/last_prompt.md`
- `sessions/last_response.md`
- `reports/executive/*.md`

Review generated changes before committing.

## Recommended Development Workflow

1. Start from an updated main branch.
2. Create a short-lived feature branch.
3. Read the relevant docs and modules before editing.
4. Keep code, data, docs, and generated-output changes separated when practical.
5. Run the smallest useful validation for the change.
6. Review `git diff` before committing.
7. Open a pull request with a clear summary, validation notes, and known risks.

## Branch Strategy

Use short-lived branches with clear prefixes:

- `feature/<short-description>` for new behavior.
- `fix/<short-description>` for bug fixes.
- `docs/<short-description>` for documentation-only work.
- `test/<short-description>` for test-only work.
- `chore/<short-description>` for maintenance that does not change behavior.

Branch names should be lowercase and hyphen-separated.

Example:

```bash
git checkout -b docs/developer-experience-foundation
```

## Commit Strategy

Use small commits that explain one logical change. Prefer conventional-style messages:

- `docs: add developer setup guide`
- `feat: add active program issue tracking`
- `fix: handle missing program data`
- `test: add confidence scenario coverage`
- `chore: update repository hygiene`

Before committing:

- Confirm no secrets are present.
- Confirm generated files are intentional.
- Confirm JSON program data changes are intentional.
- Confirm docs match actual repository behavior.
- Run `git diff --stat` and inspect the full diff.
