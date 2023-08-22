

from copy import deepcopy


from ...physical.network import EdgeTuple
from ...physical import quantum as qu
from ..utils.tree import TreeNode, Leaf, Branch, MetaTree
from ..utils.types import TreeShape

class SPST(MetaTree):
    """
    Swap Purification Scheme Tree
    SPST is a binary tree becasue:
    both swap and purification are binary operators
    """

    def __init__(self, leaves: 'dict[EdgeTuple, qu.FidType]', gate: 'qu.Gate'=qu.GDP) -> None:
        super().__init__(leaves, gate)

    def build_sst(self, shape=TreeShape.BALANCED, costs: 'list[qu.ExpCostType]'=None) -> TreeNode:
        """
        Build the SST with initial leaves
        costs: overide costs is not None
        """
        def _build_balanced(leaves: 'list[TreeNode]') -> TreeNode:
            current_nodes: 'list[TreeNode]' = leaves
            next_nodes: 'list[TreeNode]' = []
            # merge nodes round by round
            while len(current_nodes) >= 1:
                if len(current_nodes) == 1:
                    return current_nodes.pop()
                
                # merge nodes in current round
                while len(current_nodes) >= 2:
                    node1, node2 = current_nodes.pop(0), current_nodes.pop(0)
                    f1, f2 = node1.fid, node2.fid
                    f, p = self.gate.swap(f1, f2)
                    edge = (node1.edge_tuple[0], node2.edge_tuple[1])
                    new_node = Branch(edge, f, None, node1, node2, qu.OpType.SWAP, p)
                    new_node.cost = (node1.cost + node2.cost) / p
                    node1.parent = new_node
                    node2.parent = new_node
                    next_nodes.append(new_node)
                    # print(f'New Node {new_id} = {node1} + {node2}')
                    # print(f'Fidelity {f} = swap({f1}, {f2})')

                # one node left, add it to the next round directly
                if len(current_nodes) == 1:
                    next_nodes.append(current_nodes.pop())
                
                current_nodes, next_nodes = next_nodes, []

        def _build_linked(leaves: 'list[TreeNode]') -> TreeNode:
            while len(leaves) > 1:
                node1, node2 = leaves.pop(0), leaves.pop(0)
                f, p = self.gate.purify(node1.fid, node2.fid)
                edge = deepcopy(node1.edge_tuple)
                new_node = Branch(edge, f, None, node1, node2, qu.OpType.SWAP, p)
                new_node.cost = (node1.cost + node2.cost) / p
                node1.parent = new_node
                node2.parent = new_node
                leaves.insert(0, new_node)

            return leaves[0]

        def _build_optimal(leaves: 'list[TreeNode]',) -> TreeNode:
            nodes = leaves
            # merge two adjacent nodes round by round
            while len(nodes) > 1:
                # find two adjacent nodes with minimal cost
                min_cost = float('inf')
                min_node_idx = None
                for i in range(len(nodes)-1):
                    cost = nodes[i].cost + nodes[i+1].cost
                    if cost < min_cost:
                        min_cost = cost
                        min_node_idx = i
                # merge the two nodes
                node1, node2 = nodes.pop(min_node_idx), nodes.pop(min_node_idx)
                f, p = self.gate.swap(node1.fid, node2.fid)
                edge = deepcopy(node1.edge_tuple)
                new_node = Branch(edge, f, None, node1, node2, qu.OpType.SWAP, p)
                new_node.cost = (node1.cost + node2.cost) / p
                node1.parent = new_node
                node2.parent = new_node
                nodes.insert(min_node_idx, new_node)

            return nodes[0]

        # sort the edges by fidelity
        # edges = sorted(self.leaves.items(), key=lambda x: x[1], reverse=True)
        leaves = [Leaf(edge, fidelity, None) for edge, fidelity 
                    in zip(self.edges, self.fids)]
        if costs is not None:
            for leaf, cost in zip(leaves, costs):
                leaf.cost = cost

        if shape == TreeShape.BALANCED:
            self.root = _build_balanced(leaves)
        elif shape == TreeShape.LINKED:
            self.root = _build_linked(leaves)
        elif shape == TreeShape.ST_OPT:
            self.root = _build_optimal(leaves)
        else:
            raise NotImplementedError('shape not implemented')

        return self.root

    def grad(self, node: Branch, grad_f: qu.Fidelity=1, 
            grad_cn: qu.ExpCost=1, grad_cf: qu.ExpCost=1) -> None:
        """
        Calculate the grads of all descendants, wrt the given node
        self_grad is the grad of the node itself (from its parent)
        """
        def grad_root():
            # f, c = node.fid, node.cost
            # gf, gcn, gcf = self.gate.purify_grad(f, f, c, c, 1)
            
            node.grad_f, node.grad_cn, node.grad_cf = 1, 1, 1
            self.grad(node.left, 1, 1, 1)
            self.grad(node.right, 1, 1, 1)
        
        def grad_branch():
            # calculate the grads of children
            f1, f2 = node.left.fid, node.right.fid
            c1, c2 = node.left.cost, node.right.cost
            if node.op == qu.OpType.SWAP:
                gf1, gcn1, gcf1 = self.gate.swap_grad(f1, f2, 1)
                gf1, gcn1, gcf1 = gf1*grad_f, gcn1*grad_cn, gcf1*grad_cf        
                gf2, gcn2, gcf2 = self.gate.swap_grad(f1, f2, 2)
                gf2, gcn2, gcf2 = gf2*grad_f, gcn2*grad_cn, gcf2*grad_cf
            elif node.op == qu.OpType.PURIFY:
                gf1, gcn1, gcf1 = self.gate.purify_grad(f1, f2, c1, c2, 1) 
                gf1, gcn1, gcf1 = gf1*grad_f, gcn1*grad_cn, gcf1*grad_cf
                gf2, gcn2, gcf2 = self.gate.purify_grad(f1, f2, c1, c2, 2) 
                gf2, gcn2, gcf2 = gf2*grad_f, gcn1*grad_cn, gcf1*grad_cf
            
            # update the grads of children
            node.left.grad_f = gf1
            node.left.grad_cn = gcn1
            node.left.grad_cf = gcf1
            node.right.grad_f = gf2
            node.right.grad_cn = gcn2
            node.right.grad_cf = gcf2
            # recursively update the grads of descendants
            self.grad(node.left, gf1, gcn1, gcf1)
            self.grad(node.right, gf2, gcn2, gcf2)

        if node is None or node.is_leaf():
            return
        
        if node.is_root():
            grad_root()
        else:
            grad_branch()

    def backward(self, node: Branch) -> None:
        """
        update fidelity of all ancestors (not including itself)
        backtrace from node to root
        """
        
        # cannot and shouldn't update fidelity of a leaf node
        assert isinstance(node, Branch), 'Must backtrace from a Branch'

        node = node.parent
        while node is not None:
            if node.op == qu.OpType.SWAP:
                node.fid, node.prob = self.gate.swap(node.left.fid, node.right.fid)
            elif node.op == qu.OpType.PURIFY:
                node.fid, node.prob = self.gate.purify(node.left.fid, node.right.fid)
            node.cost = (node.left.cost + node.right.cost) / node.prob
            
            node = node.parent

    def virtual_purify(self, node: TreeNode) -> 'tuple[qu.Fidelity, qu.ExpCost]':
        """
        backtrace the impact of an purification to the root
        return the fidelity and cost of the root
        """
        
        # get f, c after the purification
        old_f, old_c = node.fid, node.cost
        f, p = self.gate.purify(old_f, old_f)
        c = (old_c + old_c) / p
        while node.parent is not None:
            # process node.parent at each iteration
            if node == node.parent.left:
                fl, fr = f, node.parent.right.fid
                cl, cr = c, node.parent.right.cost
            else:
                fl, fr = node.parent.left.fid, f
                cl, cr = node.parent.left.cost, c
            node = node.parent
            assert isinstance(node, Branch), 'Must backtrace from a Branch'
            # -------prepare fl, fr, cl, cr above -------

            if node.op == qu.OpType.SWAP:
                f, p = self.gate.swap(fl, fr)
            elif node.op == qu.OpType.PURIFY:
                f, p = self.gate.purify(fl, fr)
            c = (cl + cr) / p

        return f, c

    def purify(self, node: TreeNode) -> Branch:
        """
        purify a node in the tree
        return the new node (parent of the given node and node's copy)
        """
        parent = node.parent

        copy_node = self.copy_subtree(node)
        f1, f2 = node.fid, copy_node.fid
        fid, prob = self.gate.purify(f1, f2)
        edge = deepcopy(node.edge_tuple)
        new_node = Branch(edge, fid, parent, copy_node, node, qu.OpType.PURIFY, prob)

        copy_node.parent = new_node
        node.parent = new_node
        if parent is not None:
            if parent.left == node:
                parent.left = new_node
            else:
                parent.right = new_node
        else:
            self.root = new_node

        return new_node

    def calc_efficiency(self, node: TreeNode):
        """
        Calculate the efficiency of all descendants, wrt the given node
        """
        if node is None:
            return

        # calculate the efficiency
        node.efficiency = node.grad_f / node.cost
        # calculate adjusted efficiency
        # virtual purify method
        # rf, rc = self.virtual_purify(node)
        # df = rf - self.root.fid
        # dc = rc - self.root.cost
        # grad method
        pf, p = self.gate.purify(node.fid, node.fid)
        df = (pf - node.fid)*node.grad_f
        dc = (pf - node.fid)*node.grad_cf + node.cost*node.grad_cn
        node.adjust_eff = df / dc

        # recursive on descendants
        self.calc_efficiency(node.left)
        self.calc_efficiency(node.right)


