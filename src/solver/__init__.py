

# this file contains all path solvers

from abc import ABC, abstractmethod
from typing import NewType

from physical import StaticQuPath
import physical.quantum as qu
import physical.network as net

AllocType = NewType('AllocType', dict[net.EdgeTuple, qu.Cost])
ExpAllocType = NewType('ExpAllocType', dict[net.EdgeTuple, qu.ExpCost])


class PathSolver(ABC):
    def __init__(self, edges: StaticQuPath, gate: qu.Gate) -> None:
        self.edges = edges
        self.gate = gate

    @abstractmethod
    def solve(self) -> ExpAllocType:
        pass





