
from typing import Dict, List, Set, Tuple
from csp import backtracking_search, DomainMap, Assignment


def get_all_cells() -> List[str]:
    cells = []
    for row in range(1, 10):
        for col in range(1, 10):
            cells.append(f"r{row}c{col}")
    return cells


def get_peers() -> Dict[str, Set[str]]:
    peers = {}
    
    for row in range(1, 10):
        for col in range(1, 10):
            cell = f"r{row}c{col}"
            peer_cells = set()
            
            # Add all cells in same row
            for c in range(1, 10):
                peer_cells.add(f"r{row}c{c}")
            
            # Add all cells in same column
            for r in range(1, 10):
                peer_cells.add(f"r{r}c{col}")
            
            # Add all cells in same 3x3 block
            block_start_row = ((row - 1) // 3) * 3 + 1
            block_start_col = ((col - 1) // 3) * 3 + 1
            
            for r in range(block_start_row, block_start_row + 3):
                for c in range(block_start_col, block_start_col + 3):
                    peer_cells.add(f"r{r}c{c}")
            
            # Remove the cell itself from its peers
            peer_cells.discard(cell)
            peers[cell] = peer_cells
    
    return peers


def parse_sudoku_puzzle(puzzle_strings: List[str]) -> Tuple[DomainMap, Assignment]:
    domains = {}
    given_values = {}
    
    if len(puzzle_strings) != 9:
        raise ValueError("Puzzle must have exactly 9 rows")
    
    for row in range(1, 10):
        row_string = puzzle_strings[row - 1]
        if len(row_string) != 9:
            raise ValueError(f"Row {row} must have exactly 9 characters")
        
        for col in range(1, 10):
            cell = f"r{row}c{col}"
            char = row_string[col - 1]
            
            if char in "0.":
                # Empty cell - can be any number 1-9
                domains[cell] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            else:
                # Given cell - must be the specified number
                try:
                    value = int(char)
                    if value < 1 or value > 9:
                        raise ValueError(f"Invalid digit {value} in cell {cell}")
                    domains[cell] = [value]
                    given_values[cell] = value
                except ValueError:
                    raise ValueError(f"Invalid character '{char}' in cell {cell}")
    
    return domains, given_values


def is_valid_move(cell: str, value: int, current_assignment: Assignment) -> bool:

    peers = get_peers()
    
    for peer_cell in peers[cell]:
        if peer_cell in current_assignment and current_assignment[peer_cell] == value:
            return False
    
    return True


def get_valid_values(cell: str, current_assignment: Assignment, domains: DomainMap) -> List[int]:

    valid_values = []
    
    for value in domains[cell]:
        if is_valid_move(cell, value, current_assignment):
            valid_values.append(value)
    
    return valid_values


def print_sudoku(assignment: Assignment) -> None:
    """Print a Sudoku solution in simple format"""
    for row in range(1, 10):
        row_values = []
        for col in range(1, 10):
            cell = f"r{row}c{col}"
            value = assignment.get(cell, ".")
            row_values.append(str(value))
        print(" ".join(row_values))


def solve_sudoku(puzzle_strings: List[str]):

    # Parse the puzzle
    domains, given_values = parse_sudoku_puzzle(puzzle_strings)
    
    # Get all cells
    all_cells = get_all_cells()
    
    # Create functions for the solver
    def check_valid(cell: str, value: int, assignment: Assignment) -> bool:
        return is_valid_move(cell, value, assignment)
    
    def get_legal_values(cell: str, assignment: Assignment) -> List[int]:
        return get_valid_values(cell, assignment, domains)
    
    # Solve using backtracking search
    solution = backtracking_search(
        variables=all_cells,
        domains=domains,
        consistent_fn=check_valid,
        legal_values_fn=get_legal_values
    )
    
    return solution


# Example usage
if __name__ == "__main__":
    # Example Sudoku puzzle (0 or '.' means empty)
    puzzle = [
        "530070000",
        "600195000", 
        "098000060",
        "800060003",
        "400803001",
        "700020006",
        "060000280",
        "000419005",
        "000080079"
    ]
    
    print("Solving Sudoku puzzle...")
    solution = solve_sudoku(puzzle)
    
    if solution:
        print_sudoku(solution)
    else:
        print("No solution found!")