<!-- Generated: 2026-10-11 | Parent: ../AGENTS.md -->

# exspy/tests

## Purpose

pytest suite mirroring the package layout. Score 17 (>15): 38 py files,
7 subdirs (components/material/misc/models/signals + drawing), 6.5k LOC.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| One dir per package area | `components/`, `material/`, `misc/`, `models/`, `signals/`, `drawing/` | mirrors source tree |
| Top-level cross-cutting tests | `test_deprecated_import.py`, `test_eager_import.py`, `test_non_uniform_not_implemented.py` | |
| Shared fixtures | `conftest.py`, `data/` | |
| Heaviest test | `models/test_eelsmodel.py` (811 LOC) | runs against real GOS tables |

## CONVENTIONS

- New test file names mirror the source module: `_eels.py` -> `test_eels.py`.
- Tolerance asserts compare against stored expected values, never against
  a re-derived computation.
- Running the full suite needs GOS data (CI downloads it via the shared
  workflows); locally scope with `-k` when offline.

## ANTI-PATTERNS

- NEVER test lazy and eager in one file without marking — one file per
  surface keeps the failure split clean.
- Do not add network calls; use `data/` fixtures.