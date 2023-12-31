
from abc import ABC, abstractmethod

from ..physical import StaticQuPath
from ..physical import quantum as qu
from .utils.types import ExpAlloc


class PathSolver(ABC):
    def __init__(self, edges: StaticQuPath, gate: qu.Gate) -> None:
        self.edges = edges
        self.gate = gate

    @abstractmethod
    def solve(self) -> ExpAlloc:
        pass