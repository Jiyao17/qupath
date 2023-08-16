

from .quantum import *
from .types import *




# perfect hardware
HWP = HWParam((1, 1, 1, 1))
# noisy hardware, high accuracy
HWH = HWParam((0.999, 0.999, 0.999, 0.995))
# noisy hardware, medium accuracy
HWM = HWParam((0.995, 0.995, 0.995, 0.99))
# noisy hardware, low accuracy
HWL = HWParam((0.99, 0.99, 0.99, 0.975))

# Dephased operation, perfect
GDP = Gate(EntType.DEPHASED, HWP)
# Werner operation, perfect
GWP = Gate(EntType.WERNER, HWP)
# Werner operation, noisy, high accuracy
GWH = Gate(EntType.WERNER, HWH)
# Werner operation, noisy, medium accuracy
GWM = Gate(EntType.WERNER, HWM)
# Werner operation, noisy, low accuracy
GWL = Gate(EntType.WERNER, HWL)