# Contributing

This project follows a minimal, release-oriented workflow focused on correctness, auditability, and clarity for institutional users.

## Development setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

2. Install the project in editable mode with development dependencies:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install --editable ".[dev]"
   ```

3. Verify the setup:
   ```bash
   pytest
   python -m ruff check .
   agent-governance --demo
   ```

## Code style and checks

- Use Ruff for linting:
  ```bash
  python -m ruff check .
  ```
- Ensure all tests pass:
  ```bash
  pytest
  ```
- Ensure no known vulnerabilities in dependencies:
  ```bash
  pip-audit
  ```

## Releasing

Before tagging a new version:

1. Update `pyproject.toml`:
   - Increment `version` following semantic versioning (e.g. `0.1.0` → `0.2.0`).
2. Update `CHANGELOG.md`:
   - Add a new section for the version with date and changes.
3. Run full checks:
   ```bash
   pytest
   python -m ruff check .
   pip-audit
   agent-governance --demo
   ```
4. Commit changes with a clear message, e.g.:
   ```text
   chore: prepare v0.1.0 release
   ```
5. Create a Git tag:
   ```bash
   git tag -a v0.1.0 -m "v0.1.0"
   git push origin v0.1.0
   ```
6. (Optional) Build a wheel for distribution:
   ```bash
   python -m build --wheel
   ```

## Security and compliance

- Do not commit secrets, credentials, or private keys.
- Keep audit log schemas and tamper-evidence logic stable; document any breaking changes prominently in the changelog.
- When adding new integrations or tool boundaries, update the security scanner rules and include tests.