

# quantum related settings and functions
# including entanglement state type, operations, measurement accuracy, etc.


from enum import Enum
from collections.abc import Iterable
from copy import deepcopy

from .types import Fidelity, ExpCost, OpResult


class EntType(Enum):
    # input state type of quantum operations
    DEPHASED = 1
    WERNER = 2


class OpType(Enum):
    # quantum operations
    SWAP = 1
    PURIFY = 2
    

class HWParam:
    # Hardware setting
    def __init__(self, params: 'Iterable[float]') -> None:
        """
        params: accuracy of:  one-qubit, two-qubit, and Bell state measurement
        """
        assert len(params) == 4
        for param in params:
            assert 0 <= param <= 1
        self.params = deepcopy(params)
        self.accu_1qubit = self.params[0]
        self.accu_2qubit = self.params[1]
        self.accu_BSM = self.params[2]
        self.prob_swap = self.params[3]

        self.p = self.params[0] * self.params[1]
        self.eta = self.params[2]


        if self.params[0] == self.params[1] == self.params[2] == self.params[3] == 1:
            self.noisy = False
        else:
            self.noisy = True


class Gate:
    def __init__(self, ent_type: EntType, hdw: HWParam) -> None:
        self.ent_type = ent_type
        self.hw = deepcopy(hdw)

        # self.noisy = ms_accu.noisy
        # self.p = ms_accu.p
        # self.eta = ms_accu.eta

        if self.ent_type == EntType.DEPHASED:
            assert self.hw.noisy == False, \
                "Noisy measurement not supported in dephased system"

    def swap(self, f1, f2) -> 'OpResult':
        if self.ent_type == EntType.DEPHASED:
            f = self._swap_dephased(f1, f2)
        elif self.ent_type == EntType.WERNER:
            f = self._swap_werner(f1, f2)
        else:
            raise ValueError('ent_type must be DEPHASED or WERNER')
        
        return f, self.hw.prob_swap
    
    def seq_swap(self, fids):
        f = fids[0]
        prob = 1
        for i in range(1, len(fids)):
            f, p = self.swap(f, fids[i])
            prob *= p
        return f, prob
    
    def seq_swap_grad(self, fids, partial):
        prod = 1
        for i in range(len(fids)):
            if i == partial:
                pass
            else:
                if self.ent_type == EntType.DEPHASED:
                    prod *= fids[i] - 1/2
                elif self.ent_type == EntType.WERNER:
                    prod *= fids[i] - 1/4
                else:
                    raise ValueError('ent_type must be DEPHASED or WERNER')
                
        return prod

    def swap_grad(self, f1, f2, partial,) -> 'tuple[Fidelity, ExpCost, ExpCost]':
        if self.ent_type == EntType.DEPHASED:
            grad_f = self._swap_dephased_grad(f1, f2, partial)
        elif self.ent_type == EntType.WERNER:
            grad_f = self._swap_werner_grad(f1, f2, partial)
        else:
            raise ValueError('ent_type must be DEPHASED or WERNER')
        grad_cn = 1/self.hw.prob_swap
        return grad_f, grad_cn, 0

    def balanced_swap(self, fids: 'list[float]') -> 'OpResult':
        assert len(fids) > 0
        next_fids = []
        prob = 1
        while len(fids) > 1:
            while len(fids) > 1:
                f1, f2 = fids.pop(0), fids.pop(0)
                f, p = self.swap(f1, f2)
                next_fids.append(f)
                prob *= p

            fids = next_fids
            next_fids = []

        return fids[0], prob

    def purify(self, f1, f2) -> 'OpResult':
        if self.ent_type == EntType.DEPHASED:
            return self._purify_dephased(f1, f2)
        elif self.ent_type == EntType.WERNER:
            return self._purify_werner(f1, f2)
        else:
            raise ValueError('ent_type must be DEPHASED or WERNER')
    
    def seq_purify(self, fids) -> 'OpResult':
        f = fids[0]
        prob = 1
        for i in range(1, len(fids)):
            f, p = self.purify(f, fids[i])
            prob *= p
        return f, prob
    
    def balanced_purify(self, fids: 'list[float]') -> 'OpResult':
        assert len(fids) > 0
        next_fids = []
        prob = 1
        while len(fids) > 1:
            while len(fids) > 1:
                fid1, fid2 = fids.pop(0), fids.pop(0)
                f, p = self.purify(fid1, fid2)
                next_fids.append(f)
                prob *= p

            if len(fids) == 1:
                next_fids.append(fids.pop(0))

            fids = next_fids
            next_fids = []

        return fids[0], prob



    def purify_grad(self, f1, f2, n1, n2, partial,) -> 'tuple[Fidelity, ExpCost, ExpCost]':
        if self.ent_type == EntType.DEPHASED:
            grad_f, grad_cn, grad_cf = self._purify_dephased_grad(f1, f2, n1, n2, partial)
        elif self.ent_type == EntType.WERNER:
            grad_f, grad_cn, grad_cf = self._purify_werner_grad(f1, f2, n1, n2, partial)
        else:
            raise ValueError('ent_type must be DEPHASED or WERNER')
        
        return grad_f, grad_cn, grad_cf

    def _swap_dephased(self, f1, f2) -> Fidelity:
        f = f1*f2 + (1-f1)*(1-f2)
        return f
    
    def _swap_werner(self, f1, f2) -> Fidelity:
        p = self.hw.p
        eta = self.hw.eta
        
        f = 1/4 + (1/36) * p * (4*eta**2-1) * (4*f1 - 1) * (4*f2 - 1)
        return f

    def _swap_dephased_grad(self, f1, f2, partial) -> Fidelity:
        if partial == 1:
            grad_f = f2 - (1-f2)
        elif partial == 2:
            grad_f = f1 - (1-f1)
        else:
            raise ValueError('partial must be 1 or 2')
        return grad_f

    def _swap_werner_grad(self, f1, f2, partial) -> Fidelity:
        p = self.hw.p
        eta = self.hw.eta

        if partial == 1:
            grad = (1/9) * p * (4*eta**2-1) * (4*f2 - 1)
        elif partial == 2:
            grad = (1/9) * p * (4*eta**2-1) * (4*f1 - 1)
        else:
            raise ValueError('p must be 1 or 2')
        return grad

    def _purify_dephased(self, f1, f2) -> 'OpResult':
        prob = f1 * f2 + (1 - f1) * (1 - f2)
        f = (f1 * f2) / prob
        return f, prob

    def _purify_werner(self, f1, f2) -> 'OpResult':
        e1, e2 = (1-f1)/3, (1-f2)/3
        p = self.hw.p
        eta = self.hw.eta

        nume = (eta**2 + (1-eta)**2)*(f1*f2 + e1*e2) + 2*eta*(1-eta)*(f1*e2 + f2*e1) + (1-p**2)/(8*p**2)
        deno = (eta**2 + (1-eta)**2)*(f1*f2 + f1*e2 + f2*e1 + 5*e1*e2) + 2*eta*(1-eta)*(2*f1*e2 + 2*f2*e1 + 4*e1*e2) + (1-p**2)/(2*p**2)
        
        f = nume / deno
        prob = deno * p**2
        return f, prob

    def _purify_dephased_grad(self, f1, f2, n1, n2, partial) \
            -> 'tuple[Fidelity, ExpCost, ExpCost]':
        deno = ((f1 * f2 + (1 - f1) * (1 - f2)))**2
        if partial == 1:
            nume_f = f2 * (f1 * f2 + (1 - f1) * (1 - f2)) - f1*f2 * (f2 - (1 - f2))
            grad_cf = (n1+n2)*(-1/deno)*(2*f2 - 1)
        elif partial == 2:
            nume_f = f1 * (f1 * f2 + (1 - f1) * (1 - f2)) - f1*f2 * (f1 - (1 - f1))
            grad_cf = (n1+n2)*(-1/deno)*(2*f1 - 1)
        else:
            raise ValueError('partial must be 1 or 2')
        
        grad_cn = 1/(f1 * f2 + (1 - f1) * (1 - f2))
        grad_f = nume_f / deno
        return grad_f, grad_cn, grad_cf
    
    def _purify_werner_grad(self, f1, f2, n1, n2, partial) \
            -> 'tuple[Fidelity, ExpCost, ExpCost]':
        e1, e2 = (1-f1)/3, (1-f2)/3
        p = self.hw.p
        eta = self.hw.eta

        eta_m = (eta**2 + (1-eta)**2)
        p_m = (1-p**2)/(p**2)
        
        nume_purify = eta_m*(f1*f2 + e1*e2) + 2*eta*(1-eta)*(f1*e2 + f2*e1) + p_m/8
        deno_purify = eta_m*(f1*f2 + f1*e2 + f2*e1 + 5*e1*e2) + 2*eta*(1-eta)*(2*f1*e2 + 2*f2*e1 + 4*e1*e2) + p_m/2
        deno = deno_purify ** 2
        if partial == 1:
            p_nume_purify_1 = eta_m*(f2 - (1/3)*e2) + 2*eta*(1-eta)*(e2-1/3*f2)
            p_deno_purify_1 = eta_m*(f2 + e2 -1/3*f2 - (5/3)*e2) + 2*eta*(1-eta)*(2*e2 - 2/3*f2 - 4/3*e2)
            nume = p_nume_purify_1 * deno_purify - nume_purify * p_deno_purify_1
            grad_cf = (n1+n2)*(-1/deno)*(p**2*p_deno_purify_1)
        elif partial == 2:
            p_nume_purify_2 = eta_m*(f1 - (1/3)*e1) + 2*eta*(1-eta)*(e1-1/3*f1)
            p_deno_purify_2 = eta_m*(f1 + e1 -1/3*f1 - (5/3)*e1) + 2*eta*(1-eta)*(2*e1 - 2/3*f1 - 4/3*e1)
            nume = p_nume_purify_2 * deno_purify - nume_purify * p_deno_purify_2
            grad_cf = (n1+n2)*(-1/deno)*(p**2*p_deno_purify_2)
        else:
            raise ValueError('p must be 1 or 2')

        grad_f = nume / deno
        grad_cn = 1/deno_purify
        return grad_f, grad_cn, grad_cf






if __name__ == '__main__':
    wsys = Gate(EntType.WERNER, HWParam((0.99, 0.99, 0.99, 0.9)))
    wsys_noiseless = Gate(EntType.WERNER, HWParam((1, 1, 1, 1)))
    dsys = Gate(EntType.DEPHASED, HWParam((1, 1, 1, 1)))
    op = wsys
    
    f1, f2, f3, f4 = 0.9, 0.9, 0.9, 0.9

    f12, p12 = op.swap(f1, f2)
    n12 = 2/p12
    f34, p34 = op.swap(f3, f4)
    n34 = 2/p34

    f, p = op.swap(f12, f34)
    n = (n12 + n34) / p
    print(f, n)

    f12, p12 = op.swap(f1, f2)
    n12 = 2/p12
    f123, p123 = op.swap(f12, f3)
    n123 = (n12 + 1) / p123
    f, p = op.swap(f123, f4)
    n = (n123 + 1) / p
    print(f, n)


    ns = 0
    p = op.hw.prob_swap
    simu = 100
    import numpy as np
    ns = np.zeros((simu, simu))
    for m in range(0, simu):
        for n in range(0, simu):
            ns[m, n] = (1-p)**m*p * (1-p)**n*p * ((m+1)*2 + (n+1)*2)
    print(sum(ns.flatten()) / p)

    en = (2/p + 2/p) / p
    print(en)

