# %%
"""
EELS curve fitting
==================

Performs curve fitting to an EELS spectrum, plots the result and saves it as
png file.

"""

import hyperspy.api as hs

s = hs.load("coreloss_spectrum.msa", signal_type="EELS")
low_loss = hs.load("lowloss_spectrum.msa", signal_type="EELS")

s.add_elements(("Mn", "O"))
s.set_microscope_parameters(
    beam_energy=300, convergence_angle=24.6, collection_angle=13.6
)

# %%
# Create a model and fit it to the data.
#
# .. note::
#
#    By default, :ref:`generalized oscillator strength (GOS) <eels.GOS>` calculated using density functional theory (DFT)
#    are used. Use the ``GOS`` parameter to change to use other GOS, for example ``GOS="dirac"``.

m = s.create_model(low_loss=low_loss)
m.enable_fine_structure()
m.multifit(kind="smart")

# %%
# Plot the model fit result
m.plot()
