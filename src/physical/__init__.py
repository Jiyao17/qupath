


import typing

from . import network
from . import quantum


# types defined for QuPath
QuPath = typing.NewType('QuPath', list[tuple[network.NodePair, quantum.Fidelity]])
StaticQuPath = typing.NewType('StaticQuPath', tuple[tuple[network.NodePair, quantum.Fidelity]])

