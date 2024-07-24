Changelog
*********

Changelog entries for the development version are available at
https://exspy.readthedocs.io/en/latest/changes.html


.. towncrier-draft-entries:: |release| [UNRELEASED]

.. towncrier release notes start

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
