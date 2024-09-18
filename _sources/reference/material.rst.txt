:mod:`exspy.material`
---------------------

.. currentmodule:: exspy.material

.. autosummary::

    atomic_to_weight
    density_of_mixture
    elements
    mass_absorption_coefficient
    mass_absorption_mixture
    weight_to_atomic

.. automodule:: exspy.material
   :members:

.. autoattribute:: exspy.material.elements
   :annotation:

Database of element properties.

The following properties are included:

.. code::

    ├── Atomic_properties
    │   ├── Binding_energies
    │   └── Xray_lines
    ├── General_properties
    │   ├── Z
    │   ├── atomic_weight
    │   └── name
    └── Physical_properties
        └── density_gcm3

The X-ray lines energies are taken from Chantler et al. [1]_.

The line weight, more precisely the approximate line weight for K, L, M
shells are taken from the Electron Probe Quantification (EPQ) library [2]_.

The field ``threshold`` and ``edge`` are taken from the Gatan EELS atlas
https://eels.info/atlas, as retrieved in June 2020.

Examples

>>> exspy.material.elements.Fe.General_properties
├── Z = 26
├── atomic_weight = 55.845
└── name = iron
>>> exspy.material.elements.Fe.Physical_properties
└── density (g/cm^3) = 7.874
>>> exspy.material.elements.Fe.Atomic_properties.Xray_lines
├── Ka
│   ├── energy (keV) = 6.404
│   └── weight = 1.0
├── Kb
│   ├── energy (keV) = 7.0568
│   └── weight = 0.1272
├── La
│   ├── energy (keV) = 0.705
│   └── weight = 1.0
├── Lb3
│   ├── energy (keV) = 0.792
│   └── weight = 0.02448
├── Ll
│   ├── energy (keV) = 0.615
│   └── weight = 0.3086
└── Ln
    ├── energy (keV) = 0.62799
    └── weight = 0.12525

    
References

.. [1] Chantler, C.T., Olsen, K., Dragoset, R.A., Kishore, A.R.,
   Kotochigova, S.A., and Zucker, D.S. (2005), X-Ray Form Factor,
   Attenuation and Scattering Tables (version 2.1).
   https://dx.doi.org/10.18434/T4HS32

.. [2] Ritchie, N. EPQ is the Electron Probe Quantification library
   - the basis for DTSA-II.
   https://github.com/usnistgov/EPQ
