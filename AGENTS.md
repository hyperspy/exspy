<!-- Generated: 2026-10-10 | Updated: 2026-10-10 -->

# eXSpy

## Purpose

eXSpy is a HyperSpy extension providing the electron energy-loss spectroscopy
(EELS) and energy-dispersive X-ray (EDS/EDX) signal and model components, on
top of the HyperSpy multi-dimensional data analysis framework. It ships the
`exspy.signals.EELSSpectrum`/`EDSpectrum` classes and the corresponding model
components for fitting.

## Key Files

| File | What it is |
| --- | --- |
| `pyproject.toml` | Build/config; `[tool.towncrier]` fragments in `upcoming_changes/` with `package_dir = "exspy"`. |
| `exspy/` | The Python package source. |
| `.pre-commit-config.yaml` | ruff + shared HyperSpy AI-policy hooks (`check-ai-co-author`, `check-agents-policy`). |
| `.github/workflows/compliance.yml` | Shared compliance caller (jobs `ai-trailers`, `changelog`, `agents-policy`). |
| `upcoming_changes/` | towncrier changelog fragments. |
| `.opencode/config.json` | OpenCode agent rules (Atlas), including the HyperSpy AI policy. |

## For AI Agents

### Working in this repository

- Run `pre-commit install` (pre-commit + commit-msg stages) before your first
  commit.
- Python tests: `pytest exspy tests` (GOS test data downloads via the shared
  workflows on CI).
- Docs build with warnings-as-errors: sphinx-build -W (see the shared
  workflow doc build).
- Every user-facing change needs a fragment in `upcoming_changes/` named
  `<issue>.<type>.rst`.

### Policy

- This repository follows the HyperSpy AI policy — see the pinned block below.
- Non-trivial AI-assisted changes need an accepted proposal in
  hyperspy/hyperspy-proposals BEFORE the implementation PR.

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
<!-- hyperspy-ai-policy:begin -->
## HyperSpy AI policy (ecosystem contract)

Canonical source: https://github.com/hyperspy/.github/blob/main/AI-POLICY.md - do not reword
this block; the `check-agents-policy` pre-commit hook keeps it synchronized.

- Non-trivial AI-assisted changes need an accepted proposal in
  https://github.com/hyperspy/hyperspy-proposals BEFORE the implementation PR is reviewed.
  Trivial changes: PR review suffices.
- Every AI-assisted commit carries the trailer `Assisted-by: <tool>:<model>`
  (example: `Assisted-by: OpenCode:deepseek-4.0-pro`). Attribute the tool you interact with,
  not a wrapper.
- NEVER add `Co-authored-by:` trailers for AI tools; they are reserved for human co-authors.
  The `check-ai-co-author` commit-msg hook and the `compliance / ai-trailers` CI check reject
  them.
- Disable your tool's automatic co-author injection before committing: Claude Code
  `"includeCoAuthoredBy": false`; GitHub Copilot `github.copilot.chat.commitMessageGeneration`
  off; Cursor commit attribution off; OpenCode / oh-my-openagent: check skill and plugin configs.
- Run `pre-commit install` (installs the commit-msg stage) before your first commit; CI
  re-checks every PR commit regardless.
- Declare AI assistance in the pull-request template and link the accepted proposal when one
  is required.
<!-- hyperspy-ai-policy:end -->
