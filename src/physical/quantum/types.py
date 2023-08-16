

from typing import NewType, Tuple


# types defined for quantum
Fidelity = NewType('FidType', float)
Prob = NewType('ProbType', float)
Cost = NewType('CostType', int)
ExpCost = NewType('ExpCostType', float)
OpResult = NewType('OpResultType', Tuple[Fidelity, Prob])