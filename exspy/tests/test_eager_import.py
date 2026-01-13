# -*- coding: utf-8 -*-
# Copyright 2007-2026 The eXSpy developers
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

import os
import subprocess
import sys
import textwrap


def test_eager_import_env_var_loads_submodules():
    code = textwrap.dedent(
        """
        import os
        import sys

        os.environ["EAGER_IMPORT"] = "1"

        import exspy

        expected_modules = {
            "exspy.components",
            "exspy.data",
            "exspy.material",
            "exspy.models",
            "exspy.signals",
            "exspy.utils",
        }
        missing = sorted(module for module in expected_modules if module not in sys.modules)
        if missing:
            raise RuntimeError(f"Missing eager-imported modules: {missing}")
        """
    )

    # Need to use subprocess to ensure a clean environment where no exspy submodules
    # have been imported yet (conftest.py import exspy modules.), and to ensure that
    # the EAGER_IMPORT environment variable is set before any imports happen.

    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )

    assert result.returncode == 0, result.stderr
