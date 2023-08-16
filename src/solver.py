

# this file contains all path solvers

from abc import ABC, abstractmethod
from typing import NewType

from physical import StaticQuPathType
from physical.network.network import EdgeTuple
import physical.quantum.quantum as qu


AllocType = NewType('AllocType', dict[EdgeTuple, qu.CostType])
ExpAllocType = NewType('ExpAllocType', dict[EdgeTuple, qu.ExpCostType])


class PathSolver(ABC):
    def __init__(self, edges: StaticQuPathType, gate: qu.Gate) -> None:
        self.edges = edges
        self.gate = gate

    @abstractmethod
    def solve(self) -> ExpAllocType:
        pass


class ThreeStageSolver(PathSolver):
    def __init__(self,
        edges: StaticQuPathType, gate: qu.Gate,
        st_shape,
        ) -> None:
        super().__init__(edges, gate)
