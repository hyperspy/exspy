# ruff: noqa
# Remove in exspy 1.0

import pytest

from hyperspy.exceptions import VisibleDeprecationWarning


def test_import_element():
    with pytest.warns(VisibleDeprecationWarning) as record:
        from exspy.misc.elements import elements_db

    assert "use `exspy.material` instead" in record[0].message.args[0]


def test_import_material():
    with pytest.warns(VisibleDeprecationWarning) as record:
        from exspy.misc.material import (
            atomic_to_weight,
            density_of_mixture,
            mass_absorption_coefficient,
            mass_absorption_mixture,
            weight_to_atomic,
        )

    assert "use `exspy.material` instead" in record[0].message.args[0]


def test_import_eds_utils():
    with pytest.warns(VisibleDeprecationWarning) as record:
        from exspy.misc.eds.utils import (
            cross_section_to_zeta,
            electron_range,
            get_xray_lines_near_energy,
            take_off_angle,
            xray_range,
            zeta_to_cross_section,
        )

    assert "use `exspy.utils.eds` instead" in record[0].message.args[0]


def test_import_eels_tools():
    with pytest.warns(VisibleDeprecationWarning) as record:
        from exspy.misc.eels.tools import (
            effective_angle,
            get_edges_near_energy,
            get_info_from_edges,
        )

    assert "use `exspy.utils.eels` instead" in record[0].message.args[0]


def test_import_eels_electron_inelastic_mean_free_path():
    with pytest.warns(VisibleDeprecationWarning) as record:
        from exspy.misc.eels.electron_inelastic_mean_free_path import (
            iMFP_angular_correction,
            iMFP_Iakoubovskii,
            iMFP_TPP2M,
        )

    assert "use `exspy.utils.eels` instead" in record[0].message.args[0]
