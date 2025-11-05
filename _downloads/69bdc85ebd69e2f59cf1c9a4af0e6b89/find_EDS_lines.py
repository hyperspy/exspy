"""
Find EDS lines
==============

This example demonstrates how to find EDS lines.

"""

import exspy

# %%
# Show the X-ray lines near 6.4 keV:
exspy.utils.eds.print_lines_near_energy(energy=6.4)

# %%
# Show the main (high weight) X-ray lines near 6.4 keV:
exspy.utils.eds.print_lines_near_energy(energy=6.4, weight_threshold=0.5)


# %%
# Show all X-ray lines for a given element
exspy.utils.eds.print_lines(elements=["Fe"])


# %%
# Show all X-ray lines for multiple elements
exspy.utils.eds.print_lines(elements=["Fe", "Pt"])

# %%
# Show all X-ray lines from a signal of the elements defined in the metadata
s = exspy.data.EDS_TEM_FePt_nanoparticles()
s.plot(xray_lines=True)

s.print_lines()

# %%
# Display the X-ray lines close to 8 keV, which corresponds to the Cu Kα line
# coming from the TEM grid

s.print_lines_near_energy(8.0)
