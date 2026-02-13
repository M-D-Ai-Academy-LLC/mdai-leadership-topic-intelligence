# AGENTS.md

Operational guide for coding agents working in this repository.

## Project Snapshot

- Project: `mdai-leadership-topic-intelligence`
- Domain: search analytics for corporate leadership topics
- Stack: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, scikit-learn
- CLI entrypoint: `python run.py --task full -q "executive leadership"`
- API entrypoint: `src/api/app.py` (`FastAPI` app object: `app`)

## Setup

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. `mkdir -p data logs outputs reports visualizations`

## Build, Lint, Typecheck, Test

Use these defaults unless a task explicitly requires something else.

### Lint and Format

- Lint: `ruff check src/ tests/`
- Lint with auto-fix: `ruff check src/ tests/ --fix`
- Format: `ruff format src/ tests/`

### Type Checking

- `mypy src/ --ignore-missing-imports`

### Test Commands

- CI-equivalent unit tests: `PYTHONPATH=src pytest tests/unit/ -v --tb=short`
- Full suite: `PYTHONPATH=src pytest tests/ -v --tb=short`
- Unit marker: `PYTHONPATH=src pytest tests/ -m unit -v`
- Integration marker: `PYTHONPATH=src pytest tests/ -m integration -v`

### Single Test Execution (use these often)

- Single file: `PYTHONPATH=src pytest tests/unit/test_config.py -v`
- Single test: `PYTHONPATH=src pytest tests/unit/test_config.py::test_settings_defaults -v`
- Keyword filter: `PYTHONPATH=src pytest tests/unit/ -k settings_defaults -v`

### Optional Build Smoke Check

- `python -m pip install build`
- `python -m build`

## Runtime Flags for Deterministic Validation

- `NO_NETWORK_MODE=true`
- `ENABLE_SERPAPI=true`
- `ENABLE_TRENDS=true`
- `ENABLE_COMPETITORS=true`
- `DATABASE_URL=sqlite:///./data/test_topic_intel.db`

`tests/conftest.py` already applies these defaults for test runs.

## CI Baseline

Current CI (`.github/workflows/ci.yml`) runs:

1. `ruff check src/ tests/`
2. `mypy src/ --ignore-missing-imports`
3. `PYTHONPATH=src pytest tests/unit/ -v --tb=short`

Match this baseline locally before significant changes.

## Code Style and Engineering Rules

Derived from `pyproject.toml` and current source conventions.

### Python Formatting

- Python target: 3.11 (`requires-python >=3.11`)
- Max line length: 120
- Use `ruff format`
- Double quotes for strings
- Spaces for indentation

### Imports

- Prefer absolute local imports (example: `from core.config import settings`).
- Import order: standard library, third-party, local modules.
- Avoid wildcard imports.
- Keep import paths compatible with `PYTHONPATH=src`.

### Naming

- Files/modules: `snake_case.py`
- Variables/functions: `snake_case`
- Classes: `PascalCase`
- Constants/environment variables: `UPPER_SNAKE_CASE`
- Tests: file `test_*.py` or `*_test.py`, function `test_*`, class `Test*`

### Typing and Schemas

- Add explicit type hints for new or modified public logic.
- Prefer concrete containers where useful (`list[str]`, `dict[str, Any]`).
- Keep contracts strict at boundaries: `contracts/` for agent I/O, `models/` for domain entities.
- Keep `volume` optional where source systems may omit it.
- Respect mypy configuration in `pyproject.toml`.

### Pydantic Guidelines

- Use `BaseModel` with `Field(...)` constraints.
- Validate at API/agent/integration boundaries.
- Prefer explicit bounds/defaults for numeric fields.
- For mutable defaults in new code, use `Field(default_factory=list|dict)`.

### Error Handling and Logging

- Fail predictably at system boundaries.
- Catch exceptions only where fallback behavior is intentional.
- Log context with `loguru.logger`.
- Re-raise exceptions when pipeline progression should stop.
- Keep API/CLI error messages concise and actionable.

### Architecture and Boundaries

- `integrations/`: external services/APIs
- `agents/`: orchestration and business workflows
- `contracts/`: strict I/O schemas
- `models/`: shared data models
- `storage/`: persistence and cache
- Preserve feature-flag behavior and reproducibility (`run_id`, `config_hash`).

## API and CLI Notes

- Preserve async flow and report generation behavior in `run.py`.
- FastAPI app lives in `src/api/app.py`; routes in `src/api/routes.py`.
- Maintain response schema compatibility when changing API endpoints.

## Git Workflow

- Never commit directly to `main`/`master`.
- Agent branch target: `jose-ai`.
- Human branch target: `victor`.
- After pushing `jose-ai`, open a PR to `main`.

## Documentation and Attribution Policy

- Do not add AI/self-referential attributions in code, docs, or commits.
- Keep documentation professional and team-authored in tone.

## Cursor and Copilot Rules Status

At time of writing, no additional repository rules were found in:

- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

If any of these appear later, treat them as authoritative and update this file.

## Agent Working Defaults

- Prefer minimal, targeted diffs over broad refactors.
- Run lint and relevant tests after code changes.
- For contract/model changes, run `tests/unit/test_contracts.py` plus related tests.
- Keep external calls guarded by feature flags and `NO_NETWORK_MODE` assumptions.
