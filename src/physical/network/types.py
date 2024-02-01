

from typing import NewType, Tuple, List

# types defined for networks
NodeID = NewType('NodeID', int)
# KeyID = NewType('KeyID', int)
NodePair = NewType('NodePair', Tuple[NodeID, NodeID])
EdgeTuple = NewType('EdgeTuple', Tuple[NodeID, NodeID])
# MultiEdgeTuple = NewType('MultiEdgeTuple', tuple[NodeID, NodeID, KeyID])
StaticPath = NewType('StaticPath', Tuple[EdgeTuple])
Path = NewType('Path', List[EdgeTuple])