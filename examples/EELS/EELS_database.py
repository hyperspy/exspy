"""
Get spectra from the EELS database
===================================

This example demonstrates how to load EELS spectra from the EELS database in eXSpy.

"""

import hyperspy.api as hs

import exspy

# %%
# Load a core-loss and low-loss EELS spectra from a Ti\ :sub:`3`\Ni\ :sub:`4` alloy from the EELS database.
cl = exspy.data.eelsdb(element=["Ti", "Ni"], spectrum_type="coreloss")[0]
ll = exspy.data.eelsdb(element=["Ti", "Ni"], spectrum_type="lowloss")[0]

# %%
# Plot both spectra. The core-loss spectrum contains the Ti L\ :sub:`2,3` edge at around 450 eV,
# and the Ni L\ :sub:`2,3` edge at around 850 eV, while the low-loss spectrum contains the zero-loss
# peak and plasmon peaks.
hs.plot.plot_spectra([ll * 20, cl], legend=["Low-loss (x20)", "Core-loss"])
