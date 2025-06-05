# Database
#
# The X-ray lines energies are taken from Chantler2005,
# Chantler, C.T., Olsen, K., Dragoset, R.A., Kishore, A.R.,
# Kotochigova, S.A., and Zucker, D.S.
#
# The line weight, more precisely the approximate line weight for K,L M
# shells are taken from epq library
#
# The field 'threshold' and 'edge' are taken from Gatan EELS atlas
# https://eels.info/atlas (retrieved in June 2020)

import json
from pathlib import Path
from hyperspy.misc.utils import DictionaryTreeBrowser


def _load_json_data(file_path):
    """Load JSON data from file and extract elements section."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("elements", {})


def _load_elements_data():
    """Load and merge elements data from JSON files."""
    # Get the directory containing this file
    current_dir = Path(__file__).parent

    # Load data from JSON files
    general_properties_path = current_dir / "elements_general_properties.json"
    xray_lines_path = current_dir / "eds" / "xray_lines.json"
    binding_energies_path = current_dir / "eels" / "eels_binding_energies.json"

    general_data = _load_json_data(general_properties_path)
    xray_data = _load_json_data(xray_lines_path)
    binding_data = _load_json_data(binding_energies_path)

    # Merge data into the expected structure
    elements = {}

    # Get all unique element symbols
    all_elements = (
        set(general_data.keys()) | set(xray_data.keys()) | set(binding_data.keys())
    )

    for element in all_elements:
        elements[element] = {}

        # Add general and physical properties
        if element in general_data:
            elem_data = general_data[element]
            if "General_properties" in elem_data:
                elements[element]["General_properties"] = elem_data[
                    "General_properties"
                ]
            if "Physical_properties" in elem_data:
                elements[element]["Physical_properties"] = elem_data[
                    "Physical_properties"
                ]

        # Add atomic properties
        atomic_props = {}

        # Add X-ray lines
        if element in xray_data:
            atomic_props["Xray_lines"] = xray_data[element]

        # Add binding energies
        if element in binding_data:
            atomic_props["Binding_energies"] = binding_data[element]

        if atomic_props:
            elements[element]["Atomic_properties"] = atomic_props

    return elements


# Load elements data from JSON files
elements = _load_elements_data()
elements_db = DictionaryTreeBrowser(elements)
elements_db.__doc__ = """
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
--------
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
----------
.. [1] Chantler, C.T., Olsen, K., Dragoset, R.A., Kishore, A.R.,
   Kotochigova, S.A., and Zucker, D.S. (2005), X-Ray Form Factor,
   Attenuation and Scattering Tables (version 2.1).
   https://dx.doi.org/10.18434/T4HS32

.. [2] Ritchie, N. EPQ is the Electron Probe Quantification library
   - the basis for DTSA-II.
   https://github.com/usnistgov/EPQ
"""

# read dictionary of atomic numbers from eXSpy, and add the elements that
# do not currently exist in the database (in case anyone is doing EDS on
# Ununpentium...)
atomic_number2name = dict((p.General_properties.Z, e) for (e, p) in elements_db)
atomic_number2name.update(
    {
        96: "Cm",
        97: "Bk",
        98: "Cf",
        99: "Es",
        100: "Fm",
        101: "Md",
        102: "No",
        103: "Lr",
        104: "Rf",
        105: "Db",
        106: "Sg",
        107: "Bh",
        108: "Hs",
        109: "Mt",
        110: "Ds",
        111: "Rg",
        112: "Cp",
        113: "Uut",
        114: "Uuq",
        115: "Uup",
        116: "Uuh",
        117: "Uus",
        118: "Uuo",
        119: "Uue",
    }
)
