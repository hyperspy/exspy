<!-- Generated: 2026-10-11 | Parent: ../AGENTS.md -->

# exspy/_misc

## Purpose

Private physics data and download utilities: GOS/FFAST tables for
EELS/EDS quantification. Score 12 (distinct domain): lazy-loaded physics
constants, module boundary, high reference count from models/components.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| GOS download | `__init__.py` | `_download_GOS_files(download_all=True)`: Zenodo via `pooch`, md5-pinned, 3 retries |
| GOS source classes | `eels/base_gos.py`, `gosh_gos.py`, `gosh_gos_source.py`, `hartree_slater_gos.py`, `hydrogenic_gos.py` | generalized oscillator strengths |
| GOS helpers | `eels/tools.py` | |
| FFAST table | `eds/ffast_mac.py` | 748KB periodic-table constants; data, not code |

## CONVENTIONS

- `exspy.misc` (public) is the DEPRECATED re-export of this package;
  new imports use `exspy._misc`.
- Tables load lazily (`__getattr__`/`lazy_loader`) — importing
  `exspy._misc` never reads `ffast_mac.py`.

## ANTI-PATTERNS

- NEVER read `eds/ffast_mac.py` whole: 748KB periodic-table constants;
  it breaks naive tooling.
- NEVER hand-edit the generated data tables.
- Do not add a runtime download on import — download is explicit.
