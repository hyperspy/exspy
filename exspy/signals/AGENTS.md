<!-- Generated: 2026-10-11 | Parent: ../AGENTS.md -->

# exspy/signals

## Purpose

The EELS and EDS signal classes. Score 21 (>15): 19 top-level files,
`__init__.pyi` module boundary, every consumer imports these.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Core signal classes | `eels.py`, `eds.py`, `eds_sem.py`, `eds_tem.py` | eager |
| Lazy variants | `_lazy_*.py` | one per eager class |
| Signal registration | `__init__.pyi` | `lazy_loader.attach_stub`; keep in sync with `__init__.py` |
| Dielectric function | `_dielectric_function.py` + `_lazy_*.py` | shared by EELS |

## CONVENTIONS

- Every eager class has a `_lazy_` mirror; change both or neither.
- Do not import `hyperspy.signals` here; this package *extends* it.
- Type stubs (`__init__.pyi`) are the export surface `__getattr__` resolves.

## ANTI-PATTERNS

- NEVER edit `__init__.pyi` without re-running the lazy-loader attach.
- No file here may import from `exspy.tests`.
