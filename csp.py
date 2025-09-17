"""
csp.py
A tiny, readable CSP backtracking solver with MRV.

We follow the class pseudocode structure:

SELECT-UNASSIGNED-VARIABLE(A, X, C): pick var with minimum legal values (MRV)
ORDER-DOMAIN-VALUES(X_i, A, D, C): return domain values in simple order
CONSISTENT(X_i <- v, A, C): check constraints with current partial assignment
BACKTRACK(A): depth-first search with backtracking

This file is *generic* except for the 'legal_values_fn' and 'consistent_fn'
which are provided by the problem (e.g., sudoku.py).
"""

from typing import Dict, List, Callable, Optional, Any


Assignment = Dict[str, int]              # e.g., {"r1c1": 5, ...}
DomainMap  = Dict[str, List[int]]        # e.g., {"r1c1": [1..9], "r1c2": [1..9], ...}


def select_unassigned_variable_mrv(
    assignment: Assignment,
    variables: List[str],
    domains: DomainMap,
    legal_values_fn: Callable[[str, Assignment], List[int]],
) -> str:
    """
    MRV: choose the unassigned variable with the fewest legal values (ties arbitrary).
    """
    unassigned: List[str] = []
    for v in variables:
        if v not in assignment:
            unassigned.append(v)

    # If everything is assigned, caller shouldn't ask for a variable — but be safe.
    if not unassigned:
        return ""

    # Compute the count of legal values for each unassigned var and pick the minimum.
    best_var = unassigned[0]
    best_count = len(legal_values_fn(best_var, assignment))

    for v in unassigned[1:]:
        count = len(legal_values_fn(v, assignment))
        if count < best_count:
            best_var = v
            best_count = count

    return best_var


def order_domain_values_simple(var: str, domains: DomainMap) -> List[int]:
    """
    Return values in the variable's domain as-is (no LCV here for simplicity).
    """
    return list(domains[var])


def backtracking_search(
    variables: List[str],
    domains: DomainMap,
    consistent_fn: Callable[[str, int, Assignment], bool],
    legal_values_fn: Callable[[str, Assignment], List[int]],
) -> Optional[Assignment]:
    """
    Backtracking search with MRV, matching the class pseudocode structure.
    """
    # Start with an empty partial assignment
    assignment: Assignment = {}

    def backtrack(A: Assignment) -> Optional[Assignment]:
        # Goal test: complete assignment
        if len(A) == len(variables):
            return A

        # 1) SELECT-UNASSIGNED-VARIABLE using MRV
        var = select_unassigned_variable_mrv(A, variables, domains, legal_values_fn)
        if var == "":
            return None  # Safety (shouldn't happen if goal test is correct)

        # 2) ORDER-DOMAIN-VALUES (simple order; no LCV)
        for value in order_domain_values_simple(var, domains):
            # 3) CONSISTENT?
            if consistent_fn(var, value, A):
                # choose
                A[var] = value
                # recurse
                result = backtrack(A)
                if result is not None:
                    return result
                # undo
                del A[var]

        # dead end
        return None

    return backtrack(assignment)
