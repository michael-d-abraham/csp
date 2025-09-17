"""
sudoku.py
9×9 Sudoku as a CSP ⟨X, D, C⟩ with a very simple, readable setup.

- Variables X: one per cell "r{row}c{col}" for rows 1..9, cols 1..9
- Domains D: 1..9 for empties; fixed singleton for givens
- Constraints C: all-different on each row, each column, each 3×3 block
  Implemented as "no two peers share the same value"

We connect this to the generic solver in csp.py:
- consistent_fn(var, value, assignment): Sudoku row/col/block check
- legal_values_fn(var, assignment): values not used by assigned peers

Run this file to solve the puzzle defined in PUZZLE below.
Use 0 or '.' for empty cells.
"""

from typing import Dict, List, Set, Tuple
from csp import backtracking_search, DomainMap, Assignment


# ---------- 1) Define the Sudoku variables (X) ----------
def all_variables() -> List[str]:
    vars_list: List[str] = []
    for r in range(1, 10):
        for c in range(1, 10):
            vars_list.append(f"r{r}c{c}")
    return vars_list


# ---------- 2) Build peer relationships for constraints (C) ----------
def build_peers() -> Dict[str, Set[str]]:
    """
    For each cell, its peers are all cells in the same row, same column,
    or same 3x3 block (excluding itself).
    """
    peers: Dict[str, Set[str]] = {}

    # helper to list all cells in row r, col c
    def var_name(r: int, c: int) -> str:
        return f"r{r}c{c}"

    rows = range(1, 10)
    cols = range(1, 10)

    # Precompute row sets, col sets, block sets
    row_sets: Dict[int, Set[str]] = {
        r: {var_name(r, c) for c in cols} for r in rows
    }
    col_sets: Dict[int, Set[str]] = {
        c: {var_name(r, c) for r in rows} for c in cols
    }
    block_sets: Dict[Tuple[int, int], Set[str]] = {}  # key: (block_row, block_col)
    for br in [1, 4, 7]:            # top-left row index of block
        for bc in [1, 4, 7]:        # top-left col index of block
            cells = set()
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    cells.add(var_name(r, c))
            block_sets[(br, bc)] = cells

    # Build peers for every cell
    for r in rows:
        for c in cols:
            v = var_name(r, c)

            # find the block key this cell belongs to
            br = ((r - 1) // 3) * 3 + 1
            bc = ((c - 1) // 3) * 3 + 1

            peer_cells = set()
            peer_cells.update(row_sets[r])
            peer_cells.update(col_sets[c])
            peer_cells.update(block_sets[(br, bc)])
            if v in peer_cells:
                peer_cells.remove(v)  # exclude itself

            peers[v] = peer_cells

    return peers


PEERS = build_peers()
VARIABLES = all_variables()


# ---------- 3) Parse a puzzle and create domains (D) ----------
def parse_puzzle_to_domains(puzzle_rows: List[str]) -> Tuple[DomainMap, Assignment]:
    """
    puzzle_rows: 9 strings of length 9; '0' or '.' means empty cell.

    Returns:
      - domains: list of allowed values for each variable.
      - assignment: pre-filled values from the puzzle (givens).
    """
    domains: DomainMap = {}
    assignment: Assignment = {}

    allowed = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    if len(puzzle_rows) != 9:
        raise ValueError("Puzzle must have 9 rows")

    for r in range(1, 10):
        row = puzzle_rows[r - 1]
        if len(row) != 9:
            raise ValueError("Each puzzle row must have length 9")

        for c in range(1, 10):
            ch = row[c - 1]
            var = f"r{r}c{c}"

            if ch in "0.":
                domains[var] = list(allowed)
            else:
                v = int(ch)
                if v < 1 or v > 9:
                    raise ValueError("Digits must be 1..9 or '.'/0 for empty")
                # Fixed (given) value: domain is singleton; also put in initial assignment.
                domains[var] = [v]
                assignment[var] = v

    return domains, assignment


# ---------- 4) Problem-specific constraint helpers (C) ----------
def is_consistent_sudoku(var: str, value: int, assignment: Assignment) -> bool:
    """
    CONSISTENT(X_i <- value, A, C):
    True if assigning `value` to `var` does NOT conflict with already-assigned peers.
    """
    for peer in PEERS[var]:
        if peer in assignment and assignment[peer] == value:
            return False
    return True


def legal_values_sudoku(var: str, assignment: Assignment, domains: DomainMap) -> List[int]:
    """
    LEGAL_VALUES(X_i | A, C):
    Values from the domain of `var` that don't violate current assignments.
    """
    legal: List[int] = []
    for v in domains[var]:
        if is_consistent_sudoku(var, v, assignment):
            legal.append(v)
    return legal


# ---------- 5) Pretty-print helpers ----------
def print_grid(assignment: Assignment) -> None:
    """
    Print the Sudoku grid from an assignment (assumes complete).
    """
    def val(r: int, c: int) -> int:
        return assignment.get(f"r{r}c{c}", 0)

    for r in range(1, 10):
        if r in (4, 7):
            print("-" * 21)
        row_vals = []
        for c in range(1, 10):
            if c in (4, 7):
                row_vals.append("|")
            row_vals.append(str(val(r, c)))
        print(" ".join(row_vals))


# ---------- 6) Example puzzle and solve ----------
if __name__ == "__main__":
    # 0 or '.' means empty. This one is moderately easy.
    PUZZLE = [
        "530070000",
        "600195000",
        "098000060",
        "800060003",
        "400803001",
        "700020006",
        "060000280",
        "000419005",
        "000080079",
    ]

    # Build domains and initial assignment from givens
    domains, given_assignment = parse_puzzle_to_domains(PUZZLE)

    # We’ll pass wrappers to match the solver’s call signature
    def consistent_fn(var: str, value: int, A: Assignment) -> bool:
        # Combine current A with the fixed givens implicitly (A already grows over time).
        # We only need to check against A because givens were inserted as part of solving.
        # However, to ensure givens are respected, we seed A with them before calling the solver.
        return is_consistent_sudoku(var, value, A)

    def legal_values_fn(var: str, A: Assignment) -> List[int]:
        return legal_values_sudoku(var, A, domains)

    # Seed the search with givens by starting the recursion from that partial assignment.
    # The solver starts with an empty dict, so we project givens via domains = [singleton]
    # and simply let the solver assign them first (MRV will pick singletons early).
    # If you want to *force* givens into the initial assignment explicitly, you can:
    #    start_assignment = dict(given_assignment)
    # and modify the solver to accept a starting assignment. For simplicity, we keep
    # the solver unchanged and rely on MRV (singletons = 1 legal value).

    solution = backtracking_search(
        variables=VARIABLES,
        domains=domains,
        consistent_fn=consistent_fn,
        legal_values_fn=legal_values_fn,
    )

    if solution is None:
        print("No solution found.")
    else:
        print("Solved Sudoku:")
        print_grid(solution)
