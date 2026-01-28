You will be adding code quality tools to this Python project

Follow these steps to add comprehensive code quality tooling:

1. **Update pyproject.toml**
   - Add development dependencies: black, ruff, mypy, pytest, pytest-cov
   - Configure black with line-length = 100
   - Configure ruff with appropriate lint rules
   - Add per-file ignores where needed (e.g., E402 for initialization code)

2. **Create development scripts in scripts/ directory**
   - `format.sh` / `format.bat` - Auto-format code with Black and Ruff
   - `check.sh` / `check.bat` - Check code quality without modifying files
   - `quality.sh` / `quality.bat` - Run all quality tools

3. **Install dev dependencies**
   ```bash
   uv sync --group dev
   ```

4. **Format and fix existing code**
   ```bash
   uv run black backend/ --line-length 100
   uv run ruff check backend/ --fix
   ```

5. **Create scripts/README.md** with usage documentation

6. **Verify all checks pass**
   ```bash
   uv run black backend/ --check --line-length 100
   uv run ruff check backend/
   ```

7. **Commit changes** with descriptive message

Common fixes to apply:
- Replace bare `except:` with `except Exception:` or `contextlib.suppress()`
- Add `from None` to exception re-raises: `raise ... from None`
- Use ternary operators for simple if-else assignments
- Remove unused loop variables
- Use modern type hints: `str | None` instead of `Optional[str]`
