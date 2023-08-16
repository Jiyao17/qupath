

from typing import NewType

# types defined for networks
NodeID = NewType('NodeID', int)
# KeyID = NewType('KeyID', int)
NodePair = NewType('NodePair', tuple[NodeID, NodeID])
EdgeTuple = NewType('EdgeTuple', tuple[NodeID, NodeID])
# MultiEdgeTuple = NewType('MultiEdgeTuple', tuple[NodeID, NodeID, KeyID])
StaticPath = NewType('StaticPath', tuple[EdgeTuple])
Path = NewType('Path', list[EdgeTuple])