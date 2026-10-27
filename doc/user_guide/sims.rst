.. _sims-label:

Secondary Ion Mass Spectrometry (SIMS)
**************************************

The methods described in this chapter are specific to the following signals:

* :py:class:`~.signals.SIMSSpectrum`
* :py:class:`~.signals.FIBSIMSSpectrum`

Secondary Ion Mass Spectrometry (SIMS) measures the mass-to-charge ratio
(m/z) of the secondary ions sputtered from a sample, typically with a
time-of-flight (ToF) analyser. eXSpy provides the general
:py:class:`~.signals.SIMSSpectrum` signal class and its subclass
:py:class:`~.signals.FIBSIMSSpectrum` for Focused-Ion-Beam (FIB) ToF-SIMS
depth-profiling measurements, in which the navigation axes are the depth
(slices), y and x, and the signal axis is m/z, calibrated in Daltons (Da).
Lazy versions of both classes,
:py:class:`~.signals.LazySIMSSpectrum` and
:py:class:`~.signals.LazyFIBSIMSSpectrum`, are also available.

Like the other spectroscopic signals of eXSpy, the signal axis of a SIMS
signal is binned: the value of each mass channel is the number of ions
detected in that channel.

Loading data
------------

SIMS data are loaded with the :py:func:`hyperspy.api.load` function, as
described in detail in the :external+hyperspy:ref:`loading files<loading_files>`
section of the HyperSpy documentation. Tofwerk TofDAQ HDF5 (``.h5``) files
are read by the ``rsciio.tofwerk`` reader of rosettasciio. Because several
readers use the ``.h5`` extension, the reader must be selected with the
``file_format`` argument:

.. code-block:: python

    >>> import hyperspy.api as hs
    >>> s = hs.load("tofsims.h5", file_format="Tofwerk")

The reader returns the cumulative 1D spectrum by default. The 4D
depth-profiling data cube ``(depth, y, x | m/z)``, dispatched to a
:py:class:`~.signals.FIBSIMSSpectrum`, is obtained by requesting the
nominal peak data:

.. code-block:: python

    >>> s = hs.load(
    ...     "tofsims.h5", file_format="Tofwerk", signal="nominal_peak_data")

The integration windows used by the reader are stored in the
``metadata.Signal.peak_table`` attribute of the signal, and the
time-of-flight calibration is stored under
``metadata.Acquisition_instrument.FIB_SIMS``.

Any other signal can be converted to a SIMS signal with the
:py:meth:`hyperspy.api.signals.BaseSignal.set_signal_type` method:

.. code-block:: python

    >>> s.set_signal_type("SIMS")

Large datasets can be loaded lazily, which returns a
:py:class:`~.signals.LazySIMSSpectrum` or
:py:class:`~.signals.LazyFIBSIMSSpectrum` instead:

.. code-block:: python

    >>> s = hs.load(
    ...     "tofsims.h5", file_format="Tofwerk", signal="nominal_peak_data",
    ...     lazy=True)

Visualising the data
--------------------

Because the intensity of SIMS mass spectra spans many orders of magnitude,
:py:meth:`~.signals.FIBSIMSSpectrum.plot` uses a logarithmic colour scale by
default. Any other
:py:meth:`~hyperspy.api.signals.BaseSignal.plot` keyword argument, including
``norm``, is passed to HyperSpy as usual:

.. code-block:: python

    >>> s.plot()  # logarithmic norm by default
    >>> s.plot(norm="linear")

Total Ion Count
---------------

The Total Ion Count (TIC) is the sum of the intensity over all mass
channels. It is commonly used to normalise SIMS data in order to remove the
variations of the secondary-ion yield that are caused by changes in the
sputter rate and ionisation probability during acquisition.

The TIC of each navigation pixel is returned by
:py:meth:`~.signals.SIMSSpectrum.get_tic`:

.. code-block:: python

    >>> tic = s.get_tic()

For a :py:class:`~.signals.SIMSSpectrum`, the returned signal has the same
navigation axes as ``s``. For a
:py:class:`~.signals.FIBSIMSSpectrum`, the spatial navigation axes (y, x)
are promoted to signal axes, so that a 2D image of the ion count is
returned for each depth slice.

Each spectrum can be normalised by its TIC using
:py:meth:`~.signals.SIMSSpectrum.normalize_tic`, so that the mass channels of
every spectrum sum to one:

.. code-block:: python

    >>> s_norm = s.normalize_tic()

The TIC used for the normalisation is stored in the
``metadata.Signal.TIC`` attribute of the returned signal. Pixels with zero
counts (zero TIC) are set to ``NaN``.

By default, all the mass channels are summed. A list of m/z values can be
passed with the ``peaks`` argument to compute the TIC from a subset of
masses instead:

.. code-block:: python

    >>> s_norm = s.normalize_tic(peaks=[12.0, 14.0, 28.0])

Alternatively, the spectra can be normalised by the integrated intensity of
a reference peak using
:py:meth:`~.signals.SIMSSpectrum.normalize_to_peak`, where ``mass`` is the
centre of the peak in Da and ``window`` the half-width in Da of the
integration window:

.. code-block:: python

    >>> s_norm = s.normalize_to_peak(mass=28.0, window=0.5)

The reference mass is stored in the
``metadata.Signal.reference_mass_Da`` attribute of the returned signal.

.. NOTE::

    Saturation-based exclusion of saturated pixels during normalisation
    (:py:meth:`~.signals.SIMSSpectrum.normalize_tic` argument
    ``exclude_saturated``) is not yet implemented: a warning is emitted and
    the normalisation proceeds without masking saturated pixels.

Converting counts to count rate
-------------------------------

Raw SIMS data are counts. They can be converted to a count rate, in counts
per second, using
:py:meth:`~.signals.SIMSSpectrum.to_count_rate`, which requires the
following metadata to be defined under ``Acquisition_instrument.FIB_SIMS``:

.. code-block:: text

    ToF.sample_interval_s
        Sampling interval of the time-of-flight axis (s).
    ToF.single_ion_signal
        Signal of a single ion (counts).
    ToF.tof_period_samples
        Period of the time-of-flight axis (samples).
    n_depth_slices
        Number of depth slices.
    n_segments
        Number of segments.

These metadata are defined automatically when loading Tofwerk ``.h5``
files:

.. code-block:: python

    >>> s_cr = s.to_count_rate()

The integration time is computed as the period of the ToF axis multiplied by
the sampling interval and by the number of segments and depth slices, and
the counts are divided by the single-ion signal to obtain a count rate.

Summing to a mass spectrum
--------------------------

A single mass spectrum is obtained by summing over the navigation axes with
:py:meth:`~.signals.SIMSSpectrum.get_mass_spectrum`:

.. code-block:: python

    >>> ms = s.get_mass_spectrum()

To sum only over a given navigation pixel, for example a specific (depth, y,
x) coordinate of a FIB-ToF-SIMS dataset, use the ``navigation_indices``
argument:

.. code-block:: python

    >>> ms = s.get_mass_spectrum(navigation_indices=(0, 0, 0))

Depth profiling
---------------

These methods are specific to :py:class:`~.signals.FIBSIMSSpectrum` data,
where the depth is the outermost navigation axis.

The depth profile of the Total Ion Count is obtained with
:py:meth:`~.signals.FIBSIMSSpectrum.get_depth_profile`, which returns a 1D
signal with the depth axis:

.. code-block:: python

    >>> profile = s.get_depth_profile()

The profile of a specific mass peak is obtained by passing its centre, in
Da, to the ``mass`` argument (optionally with a different integration
half-width ``window``, in Da):

.. code-block:: python

    >>> profile = s.get_depth_profile(mass=28.0, window=0.5)

The full map of the integrated intensity of a mass peak, i.e. before
summing over the y and x axes, is returned by
:py:meth:`~.signals.FIBSIMSSpectrum.integrate_peak`:

.. code-block:: python

    >>> peak_map = s.integrate_peak(28.0)

The lower and upper integration borders of each mass channel, computed
with the TOF-Tracer algorithm (the border between two adjacent peaks is
placed at the minimum of their midpoint and the upper mass constrained by
the resolving power), are returned by
:py:meth:`~.signals.FIBSIMSSpectrum.compute_integration_borders` as a
dictionary mapping each mass, in Da, to its ``(lower, upper)`` integration
borders:

.. code-block:: python

    >>> borders = s.compute_integration_borders(resolution=3000)
    >>> borders[28.0]  # (lower, upper) integration borders in Da

where ``resolution`` is the mass resolving power (m/Δm) used to constrain
the upper border of each peak.

Reintegrating peaks from an event list
---------------------------------------

The peak-integrated data cube provided by the ``rsciio.tofwerk`` reader is
computed using the integration windows defined at acquisition time. The
underlying raw list of time-of-flight events can be re-binned using
different integration windows with
:py:meth:`~.signals.FIBSIMSSpectrum.reintegrate_peaks`.

The list of events must be loaded from the same acquisition, using the
``"event_list"`` signal of the reader:

.. code-block:: python

    >>> event_list_signal = hs.load(
    ...     "tofsims.h5", file_format="Tofwerk", signal="event_list")

The integration windows are taken from the ``metadata.Signal.peak_table``
attribute of the signal, or can be passed explicitly with the
``peak_table`` argument as a list of dictionaries, each containing the
``"label"``, ``"mass"`` (Da), ``"lower_integration_limit"`` (Da) and
``"upper_integration_limit"`` (Da) keys:

.. code-block:: python

    >>> peak_table = [
    ...     {"label": "C2H2",
    ...      "mass": 26.0,
    ...      "lower_integration_limit": 25.5,
    ...      "upper_integration_limit": 26.5},
    ... ]
    >>> s_peaks = s.reintegrate_peaks(
    ...     event_list_signal, peak_table=peak_table)

:py:meth:`~.signals.FIBSIMSSpectrum.reintegrate_peaks` returns a new
:py:class:`~.signals.FIBSIMSSpectrum` (or
:py:class:`~.signals.LazyFIBSIMSSpectrum` when working lazily) with the same
navigation axes as ``s`` and a signal axis of the peak masses, sorted in
increasing order. The calibration parameters (mass axis and time-to-digital
converter clock ratio) are read from the ``original_metadata`` of
``event_list_signal``. If the ``FullSpectra`` timing attributes are missing,
``clock_ratio=1`` is assumed and a warning is emitted.

.. NOTE::

    :py:meth:`~.signals.SIMSSpectrum.label_peaks` is not implemented yet;
    calling it raises a ``NotImplementedError``.