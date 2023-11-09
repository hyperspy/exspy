Changelog
*********

Changelog entries for the development version are available at
https://holospy.readthedocs.io/en/latest/changes.html

0.1.dev0 (UNRELEASED)
=====================

- Support for tabulated :ref:`Generalised Oscillator Strengths (GOS) <eels.GOS>` using the
  `GOSH <https://gitlab.com/gguzzina/gosh>`_ open file format. By default, a freely
  usable dataset is downloaded from `doi:10.5281/zenodo.7645765 <https://zenodo.org/record/6599071>`_
  (`HyperSpy #3082 <https://github.com/hyperspy/hyperspy/issues/3082>`_)
- Add functionality to fit the :ref:`EELS fine structure <eels.fine_structure>` using components, e.g. :py:class:`hyperspy.api.model.components1D.Gaussian`. (`HyperSpy #3206 <https://github.com/hyperspy/hyperspy/issues/3206>`_)


Initiation (2023-10-28)
=======================

- exSpy was split out of the `HyperSpy repository
  <https://github.com/hyperspy/hyperspy>`_ on Oct. 28, 2023. The X-ray energy
  dispersive spectroscopy (EDS) and energy electron loss spectroscopy (EELS)
  functionalities so far developed in HyperSpy were moved to the
  `exSpy repository <https://github.com/hyperspy/exspy>`_.
