
class PathSolver(ABC):
    def __init__(self, edges: StaticQuPath, gate: qu.Gate) -> None:
        self.edges = edges
        self.gate = gate

    @abstractmethod
    def solve(self) -> ExpAllocType:
        pass