# -*- coding: utf-8 -*-
# Copyright 2007-2024 The eXSpy developers
#
# This file is part of eXSpy.
#
# eXSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eXSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with eXSpy. If not, see <https://www.gnu.org/licenses/#GPL>.

from pathlib import Path

import hyperspy.api as hs
import numpy as np


TEST_DATA_DIR = Path(__file__).parent


def test_restore_EELS_model(tmp_path):
    s = hs.load(TEST_DATA_DIR / "coreloss_spectrum.msa", signal_type="EELS")
    ll = hs.load(TEST_DATA_DIR / "lowloss_spectrum.msa", signal_type="EELS")

    s.add_elements(("Mn", "O"))
    s.set_microscope_parameters(
        beam_energy=300, convergence_angle=24.6, collection_angle=13.6
    )

    m = s.create_model(low_loss=ll)
    m.enable_fine_structure()
    m.multifit(kind="smart")

    model_name = "fit1"
    m.store(model_name)
    fname = tmp_path / "test_save_eelsmodel.hspy"
    s.save(tmp_path / fname)
    m2 = s.models.restore(model_name)

    np.testing.assert_allclose(m.as_signal(), m2.as_signal())

    s2 = hs.load(fname)
    m3 = s2.models.restore(model_name)
    np.testing.assert_allclose(m.as_signal(), m3.as_signal())


def test_restore_EELS_model_dirac(tmp_path):
    s = hs.load(TEST_DATA_DIR / "coreloss_spectrum.msa", signal_type="EELS")
    ll = hs.load(TEST_DATA_DIR / "lowloss_spectrum.msa", signal_type="EELS")

    s.add_elements(("Mn", "O"))
    s.set_microscope_parameters(
        beam_energy=300, convergence_angle=24.6, collection_angle=13.6
    )

    m = s.create_model(low_loss=ll, GOS="dirac")
    m.enable_fine_structure()
    m.multifit(kind="smart")

    model_name = "fit1"
    m.store(model_name)
    fname = tmp_path / "test_save_eelsmodel.hspy"
    s.save(tmp_path / fname)
    m2 = s.models.restore(model_name)

    np.testing.assert_allclose(m.as_signal(), m2.as_signal())

    s2 = hs.load(fname)
    m3 = s2.models.restore(model_name)
    np.testing.assert_allclose(m.as_signal(), m3.as_signal())
