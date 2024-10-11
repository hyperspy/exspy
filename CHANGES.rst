Changelog
*********

Changelog entries for the development version are available at
https://exspy.readthedocs.io/en/latest/changes.html


.. towncrier-draft-entries:: |release| [UNRELEASED]

.. towncrier release notes start

0.3 (2024-10-11)
================

New features
------------

- Support for `Dirac GOS <https://zenodo.org/records/12800856>`_ in the gosh format for EELS quantification, which includes the relativistic effects (e.g. spin-orbit coupling) based on Dirac equation. (`#72 <https://github.com/hyperspy/exspy/issues/72>`_)


Enhancements
------------

- Make ``numexpr`` an optional dependency to allow installation in pyodide. (`#80 <https://github.com/hyperspy/exspy/issues/80>`_)
- Mention source of :attr:`~exspy.material.elements` database in docstring (`#87 <https://github.com/hyperspy/exspy/issues/87>`_)


Bug Fixes
---------

- Add back functionalities, which were unintentionally removed from public API when splitting from hyperspy in :mod:`exspy.utils.eds`, :mod:`exspy.utils.eels` and :mod:`exspy.material`. (`#59 <https://github.com/hyperspy/exspy/issues/59>`_)
- :meth:`exspy.models.EDSModel.fit_background` fixes:

  - fix error when using linear fitting,
  - fix resetting signal range after fitting background,
  - suspend plot when fitting background. (`#76 <https://github.com/hyperspy/exspy/issues/76>`_)
- Plot background and integration windows fixes and improvements:

  - fix plotting windows with navigation dimension >=2,
  - raise improved error message when windows are out of the range of the signal, (`#86 <https://github.com/hyperspy/exspy/issues/86>`_)


Improved Documentation
----------------------

- Fix examples in user guide, which needed to be updated after the split from hyperspy. (`#59 <https://github.com/hyperspy/exspy/issues/59>`_)


0.2.1 (2024-07-12)
==================

Bug Fixes
---------

- Fix gradients of the :class:`~.components.EELSArctan` component. (`#55 <https://github.com/hyperspy/exspy/issues/55>`_)
- Fix blocked eelsdb queries (`#66 <https://github.com/hyperspy/exspy/issues/66>`_)


Improved Documentation
----------------------

- Fix broken links in the documentation and missing docstring of the :class:`~.components.PESCoreLineShape` component in the API reference. (`#55 <https://github.com/hyperspy/exspy/issues/55>`_)


0.2 (2024-04-10)
================

Bug Fixes
---------

- Fix restoring Gosh and Hartree Slater GOS from stored models. (`#32 <https://github.com/hyperspy/exspy/issues/32>`_)


Improved Documentation
----------------------

- Add eXSpy logo and adapt spelling to capital X (`#22 <https://github.com/hyperspy/exspy/issues/22>`_)
- Fix DOI and add more badges to readme file. (`#36 <https://github.com/hyperspy/exspy/issues/36>`_, `#38 <https://github.com/hyperspy/exspy/issues/38>`_)


Maintenance
-----------

- Use `ruff <https://docs.astral.sh/ruff>`_ for linting and formatting the code. Remove redundant GitHub workflow in favour of pre-commit. (`#27 <https://github.com/hyperspy/exspy/issues/27>`_)
- Fix deprecation scipy and numpy warnings. (`#33 <https://github.com/hyperspy/exspy/issues/33>`_)


0.1 (2023-12-03)
================

New features
------------
- Support for tabulated :ref:`Generalised Oscillator Strengths (GOS) <eels.GOS>` using the
  `GOSH <https://gitlab.com/gguzzina/gosh>`_ open file format. By default, a freely
  usable dataset is downloaded from `doi:10.5281/zenodo.7645765 <https://zenodo.org/record/6599071>`_
  (`HyperSpy #3082 <https://github.com/hyperspy/hyperspy/issues/3082>`_)
- Add functionality to fit the :ref:`EELS fine structure <eels.fine_structure>` using components, e.g. :py:class:`hyperspy.api.model.components1D.Gaussian`. (`HyperSpy #3206 <https://github.com/hyperspy/hyperspy/issues/3206>`_)

Enhancements
------------

- Enable ``signal_range`` arguments when using ``subpixel=True`` in :py:meth:`~.signals.EELSSpectrum.align_zero_loss_peak` (`#7 <https://github.com/hyperspy/exspy/pull/7>`_)

Maintenance
-----------

- Use towncrier to manage release notes and improve setting dev version (`#14 <https://github.com/hyperspy/exspy/issues/14>`_)
- Use reusable workflow from the hyperspy organisation for the doc workflow (`#13 <https://github.com/hyperspy/exspy/pull/13>`_)
- Consolidate packaging metadata in ``pyproject.toml``. (`#4 <https://github.com/hyperspy/exspy/pull/4>`_, `#10 <https://github.com/hyperspy/exspy/pull/10>`_)
- Use ``setuptools_scm`` to set holospy version at build time (`#10 <https://github.com/hyperspy/exspy/pull/10>`_)
- Add package and test workflow (`#10 <https://github.com/hyperspy/exspy/pull/10>`_)
- Add python 3.12 (`#10 <https://github.com/hyperspy/exspy/pull/10>`_)
- Add release workflow (`#10 <https://github.com/hyperspy/exspy/pull/10>`_)

Initiation (2023-10-28)
=======================

- eXSpy was split out of the `HyperSpy repository
  <https://github.com/hyperspy/hyperspy>`_ on Oct. 28, 2023. The X-ray energy
  dispersive spectroscopy (EDS) and energy electron loss spectroscopy (EELS)
  functionalities so far developed in HyperSpy were moved to the
  `eXSpy repository <https://github.com/hyperspy/exspy>`_.
