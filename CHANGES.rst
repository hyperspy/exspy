Changelog
*********

Changelog entries for the development version are available at
https://exspy.readthedocs.io/en/latest/changes.html


.. towncrier-draft-entries:: |release| [UNRELEASED]

.. towncrier release notes start

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

- exSpy was split out of the `HyperSpy repository
  <https://github.com/hyperspy/hyperspy>`_ on Oct. 28, 2023. The X-ray energy
  dispersive spectroscopy (EDS) and energy electron loss spectroscopy (EELS)
  functionalities so far developed in HyperSpy were moved to the
  `exSpy repository <https://github.com/hyperspy/exspy>`_.
