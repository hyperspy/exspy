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

Database of element properties. The following properties are included:

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

Examples:

.. code::

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
