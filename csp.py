
from typing import Dict, List, Callable, Optional, Any


Assignment = Dict[str, int]           
DomainMap  = Dict[str, List[int]]      


def select_unassigned_variable_mrv(
    assignment: Assignment,
    variables: List[str],
    domains: DomainMap,
    legal_values_fn: Callable[[str, Assignment], List[int]],
) -> str:

    unassigned: List[str] = []
    for v in variables:
        if v not in assignment:
            unassigned.append(v)


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

    return list(domains[var])


def backtracking_search(
    variables: List[str],
    domains: DomainMap,
    consistent_fn: Callable[[str, int, Assignment], bool],
    legal_values_fn: Callable[[str, Assignment], List[int]],
) -> Optional[Assignment]:

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
