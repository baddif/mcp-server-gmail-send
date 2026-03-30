# Release Notes - v1.1.1 (2026-03-31)

This patch release focuses on packaging, CLI/MCP entrypoint standardization, and contract compliance.

## Highlights

- Bumped version to v1.1.1
- Requirements updated to include runtime dependencies (typer) and to be pip-installable
- Output schema standardized to top-level {success, data, error} per SKILL_GENERATION_RULES.md
- Added `main.py` as Typer CLI and FastMCP-compatible entrypoint
- Added `Skill.md` documenting the input/output schema and examples
- Updated `mcp_config.json` to follow naming conventions (`gmail_send`) and point to `main.py`
- Updated unit tests to match the new contract and to mock SMTP calls

## Developer Notes

- To install runtime dependencies:

```bash
pip install -r requirements.txt
```

- CLI:

```bash
python3 main.py gmail-send <username> <app_password> <content> <to_email> --subject "Test"
```

- MCP mode requires a compatible FastMCP implementation; the repository includes a local `mcp_server.py` for testing.

## Changelog
See `version.py` for full changelog details.

---

# Release Notes - v1.1.2 (2026-03-31)

This release adds CI automation and small packaging improvements.

## Highlights

- Added `.github/workflows/ci.yml` to run tests on push and PR
- Minor metadata improvements and prep work for automated releases

## Developer Notes

- CI will run pytest if available; otherwise it falls back to the repository's unittest script.

