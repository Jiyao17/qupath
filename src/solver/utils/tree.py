from copy import deepcopy

from ..physical import quantum as qu
from ..physical.network import EdgeTuple


class TreeNode:
    node_id = -1
    @staticmethod
    def new_id():
        TreeNode.node_id += 1
        return TreeNode.node_id

    def __init__(self, edge_tuple: EdgeTuple, fid: qu.FidType,
                parent=None, left=None, right=None, node_id=None) -> None:
        # node info
        if node_id is None:
            node_id = TreeNode.new_id()
        else:
            assert node_id > TreeNode.node_id
            self.node_id = node_id
        self.edge_tuple: EdgeTuple = edge_tuple
        self.fid: qu.FidType = fid

        # tree structure
        self.parent: TreeNode = parent
        self.left: TreeNode = left
        self.right: TreeNode = right

        # optimization info
        self.cost: qu.ExpCostType = 1
        self.grad_f: qu.FidType = 1
        self.grad_cn: qu.ExpCostType = 1
        self.grad_cf: qu.ExpCostType = 1
        self.efficiency: float = 1
        self.adjust: float = 1
        self.adjust_eff: float = 1
        self.test_rank_attr: float = 1

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def is_root(self) -> bool:
        return self.parent is None

    def __str__(self) -> str:
        s = f'{self.node_id} {self.edge_tuple}: '
        if self.is_root():
            s += f'f={self.fid}, '
        # keep 2 decimal places
        else:
            s += f'f={self.fid:.2f}, '

        # s += f'g={self.grad:.5f}, e={self.efficiency:.5f}, a={self.adjust:.5f}, ae={self.adjust_eff:.5f}'

        return s


class Leaf(TreeNode):
    """
    Leaf Node in the SPS Tree
    """

    def __init__(self, edge_tuple: EdgeTuple, fid: qu.FidType,
                    parent: TreeNode,) -> None:
        super().__init__(edge_tuple, fid, parent, None, None)


    def __str__(self) -> str:
        # keep 2 decimal places
        # return f'Leaf ' + super().__str__()
        return "L"


class Branch(TreeNode):
    """
    Branch Node in the SPS Tree
    """

    def __init__(self, edge_tuple: EdgeTuple, fid: qu.FidType, 
                parent: TreeNode, left: TreeNode, right: TreeNode,
                op: qu.OpType, prob: float) -> None:
        super().__init__(edge_tuple, fid, parent, left, right)

        self.op: qu.OpType = op
        self.prob: float = prob

        self.cost = (self.left.cost + self.right.cost) / self.prob
    
    def __str__(self) -> str:
        # keep 2 decimal places
        # return f'Branch ' + super().__str__()
        return self.op.name[0]


class MetaTree():
    
    @staticmethod
    def print_tree(root=None, indent=0):
        root: TreeNode = root # type hinting here
        if root is None:
            return
        print('  ' * indent + str(root))
        MetaTree.print_tree(root.left, indent + 1)
        MetaTree.print_tree(root.right, indent + 1)

    @staticmethod
    def copy_subtree(node: TreeNode) -> TreeNode:
        """
        Be aware: all nodes in the copy keep the same node_id
        """
        if node is None:
            return None
        
        parent = node.parent
        node.parent = None
        # new_node = deepcopy(node)
        # node.parent = parent
        # lc = node.left
        # rc = node.right
        
        # prevent infinite recursion
        # node.parent = None
        # node.left = None
        # node.right = None
        new_node = deepcopy(node)
        node.parent = parent
        # node.left = lc
        # node.right = rc

        # new_node.left = SPST.copy_subtree(node.left)
        # new_node.right = SPST.copy_subtree(node.right)
        
        return new_node

    @staticmethod
    def find_max(node: TreeNode, attr: str="adjust_eff", search_range=[TreeNode]) -> TreeNode:
        """
        find the node with max attr in the subtree
        attr: must be a member of Node
        """
        def in_range(node: TreeNode, range: 'list') -> bool:
            for type in range:
                if isinstance(node, type):
                    return True
            return False

        if node is None:
            return None
        if node.is_leaf():
            if in_range(node, search_range):
                return node
            else:
                return None
        
        candidates = []
        if in_range(node, search_range):
            candidates.append(node)
        left = MetaTree.find_max(node.left, attr, search_range)
        if in_range(left, search_range):
            candidates.append(left)
        right = MetaTree.find_max(node.right, attr, search_range)
        if in_range(right, search_range):
            candidates.append(right)

        if len(candidates) == 0:
            return None
        
        max_node = candidates[0]
        for node in candidates:
            if getattr(node, attr) > getattr(max_node, attr):
                max_node = node        
        return max_node

        # if getattr(left, attr) > getattr(right, attr):
        #     return left
        # else:
        #     return right

    def __init__(self, leaves: 'dict[EdgeTuple, float]', op: 'qu.Gate'=qu.GDP) -> None:
        self.leaves = leaves
        self.gate = op

        self.edges = list(self.leaves.keys())
        self.fids = list(self.leaves.values())

        self.root = None

