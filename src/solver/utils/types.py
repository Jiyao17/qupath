
from typing import NewType
from enum import Enum

from ..physical import quantum as qu
from ..physical import network as net

Alloc = NewType('AllocType', dict[net.EdgeTuple, qu.Cost])
ExpAlloc = NewType('ExpAllocType', dict[net.EdgeTuple, qu.ExpCost])

class TreeShape(Enum):
    LINKED = 1
    BALANCED = 2

    ST_OPT = 100
    PT_OPT = 200
