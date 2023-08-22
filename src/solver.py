

# this file contains all path solvers

from abc import ABC, abstractmethod
from typing import NewType

from physical import StaticQuPath
from physical.network import EdgeTuple
import physical.quantum as qu


AllocType = NewType('AllocType', dict[EdgeTuple, qu.Cost])
ExpAllocType = NewType('ExpAllocType', dict[EdgeTuple, qu.ExpCost])


class PathSolver(ABC):
    def __init__(self, edges: StaticQuPath, gate: qu.Gate) -> None:
        self.edges = edges
        self.gate = gate

    @abstractmethod
    def solve(self) -> ExpAllocType:
        pass


class ThreeStageSolver(PathSolver):
    def __init__(self,
        edges: StaticQuPath, gate: qu.Gate,
        st_shape,
        ) -> None:
        super().__init__(edges, gate)
