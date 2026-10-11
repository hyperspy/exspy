# PROJECT KNOWLEDGE BASE

**Generated:** 2026-10-11T05:35:00Z
**Commit:** 5adf501
**Branch:** AI_policy

## OVERVIEW

eXSpy is a HyperSpy extension providing EELS and EDS/EDX signal classes and model
components on the HyperSpy framework. Pure Python, numpy/hyperspy stack.

## STRUCTURE

```
exspy/
├── exspy/            # the package: signals/, components/, models/, _misc/, utils, material
│   └── _misc/        # private GOS data + lazy-loaded EELS/EDS physics tables
├── exspy/tests/      # pytest suite mirroring package layout
├── doc/              # Sphinx docs (-W builds), user guide + API reference
├── examples/         # sphinx-gallery scripts (# %% cells)
└── upcoming_changes/ # towncrier fragments (<issue>.<type>.rst)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Signal classes (EELSSpectrum, EDSpectrum) | `exspy/signals/` | lazy-attached via `__init__.pyi` stubs |
| Model components (gaussian, power law, …) | `exspy/components/` | exported through `hyperspy_extension.yaml` |
| EELS/EDS model fitting | `exspy/models/` | `EELSModel(Model1D)`, `EDSModel` |
| GOS tables / physical data | `exspy/_misc/` | `eds/ffast_mac.py` is a 748KB data file — never read whole |
| Unit conventions | `exspy/utils/` | `quantity_to_string`/`quantities` wrappers |
| Element properties | `exspy/material/` | `elements.py`, physical data |
| Changelog fragments | `upcoming_changes/` | `185.maintenance.rst` pattern |
| CI + policy | `.github/` | compliance.yml calls the org reusable workflow |

## CODE MAP

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `EELSSpectrum` | class | `exspy/signals/eels.py` | high | core signal |
| `EDSpectrum` | class | `exspy/signals/eds.py` | high | core signal |
| `EELSModel` | class | `exspy/models/eelsmodel.py` | med | 1D fitter; longest file |
| `_download_GOS_files` | fn | `exspy/_misc/__init__.py` | med | Zenodo via pooch, md5-pinned |
| `ffast_mac` | data | `exspy/_misc/eds/ffast_mac.py` | low | 748KB constants |

## CONVENTIONS

- Towncrier fragments REQUIRED per user-facing change: `upcoming_changes/<issue>.<type>.rst` (`new`, `enhancements`, `bugfix`, `api`, `deprecation`, `doc`, `maintenance`); config derives `package_dir = "exspy"` from `[tool.towncrier]`.
- Docs build warnings-as-errors: `sphinx-build -W`.
- `exspy.misc` is the DEPRECATED re-export surface; new code imports `exspy._misc`.
- Signals use `lazy_loader.attach_stub` with `__init__.pyi` stubs — keep stubs in sync.
- `exspy/_misc/eels/` and `eds/` physics tables: FFAST/Segre data, loaded lazily, never edited by hand.

## ANTI-PATTERNS (THIS PROJECT)

- NEVER commit generated artifacts (`doc/_build`, `coverage.xml`, `.coverage`).
- NEVER import `exspy.misc` (deprecated) in new code.
- NEVER add `Co-authored-by:` trailers naming AI tools (policy: `Assisted-by: <tool>:<model>`).
- DO NOT hand-edit `exspy/_misc/*/ffast_mac.py`-style data tables.

## UNIQUE STYLES

- Commit trailer convention shared org-wide (AI-POLICY.md, pinned block below).
- Integration tests gated behind the `run-integration-tests` PR label.

## COMMANDS

```bash
python3 -m pytest exspy tests            # unit suite
pre-commit install                        # commit-msg stage included
pre-commit run --all-files               # ruff + json + policy hooks
```

## NOTES

- `ffast_mac.py` (748KB) breaks naive file reads — size-aware tooling only.
- Release flow: `releasing_guide.md` + `prepare_release.py`.
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

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
