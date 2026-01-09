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

from ._elements import elements, elements_db

__all__ = ["elements", "elements_db"]
