# -*- coding: utf-8 -*-
# Copyright 2007-2021 The HyperSpy developers
#
# This file is part of  HyperSpy.
#
#  HyperSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  HyperSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  HyperSpy.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import pytest

import hyperspy.api as hs

try:
    import cupy as cp
except ImportError:
    pytest.skip("cupy is required", allow_module_level=True)


class TestCupy:
    def setup_method(self, method):
        N = 100
        ndim = 3
        data = cp.arange(N**3).reshape([N]*ndim)
        s = hs.signals.Signal1D(data)
        self.s = s

    def test_call_signal(self):
        s = self.s
        np.testing.assert_allclose(s(), np.arange(100))

    def test_roi(self):
        s = self.s
        roi = hs.roi.CircleROI(40, 60, 15)
        sr = roi(s)
        sr.plot()
        assert isinstance(sr.data, cp.ndarray)
        sr0 = cp.asnumpy(sr.inav[0, 0].data)
        np.testing.assert_allclose(np.nan_to_num(sr0), np.zeros_like(sr0))
        assert sr.isig[0].nansum() == 4.360798E08

    def test_as_signal(self):
        s = self.s
        _ = s.as_signal2D([0, 1])

    @pytest.mark.parametrize('parallel', [True, False, None])
    def test_map(self, parallel):
        s = self.s
        data_ref = s.data.copy()

        def dummy_function(data):
            return data * 10

        s.map(dummy_function, parallel, inplace=True,
              output_signal_size=s.axes_manager.signal_shape,
              output_dtype=s.data.dtype)

        assert (s.data == data_ref * 10).all()
