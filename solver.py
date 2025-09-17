
import time
from cs4300_csp_parser import parse_cs4300
from cs4300_csp import CSP, Assignment


def get_legal_values(variable, current_assignment, domains, constraints):
    legal_values = []
    
    for value in domains[variable]:
        test_assignment = dict(current_assignment)
        test_assignment[variable] = value
        
        is_valid = True
        for constraint in constraints:
            if variable in constraint.scope:
                if not constraint.pred(test_assignment):
                    is_valid = False
                    break
        
        if is_valid:
            legal_values.append(value)
    
    return legal_values


def choose_variable_mrv(unassigned_vars, current_assignment, domains, constraints):
    if not unassigned_vars:
        return None
    
    best_variable = unassigned_vars[0]
    best_count = len(get_legal_values(best_variable, current_assignment, domains, constraints))
    
    for var in unassigned_vars[1:]:
        count = len(get_legal_values(var, current_assignment, domains, constraints))
        if count < best_count:
            best_variable = var
            best_count = count
    
    return best_variable


def choose_variable_simple(unassigned_vars, current_assignment, domains, constraints):
    return unassigned_vars[0] if unassigned_vars else None


def solve_csp(csp_file, use_mrv=True):
    csp = parse_cs4300(csp_file)
    
    # Track performance
    nodes_visited = 0
    backtracks = 0
    start_time = time.time()
    
    domains = {var: list(domain) for var, domain in csp.domains.items()}
    choose_var = choose_variable_mrv if use_mrv else choose_variable_simple
    assignment = {}
    
    def backtrack():
        nonlocal nodes_visited, backtracks
        nodes_visited += 1
        
        if len(assignment) == len(domains):
            return dict(assignment)
        
        unassigned = [var for var in domains if var not in assignment]
        if not unassigned:
            return None
        
        var = choose_var(unassigned, assignment, domains, csp.constraints)
        if var is None:
            return None
        
        for value in domains[var]:
            test_assignment = dict(assignment)
            test_assignment[var] = value
            
            is_valid = True
            for constraint in csp.constraints:
                if var in constraint.scope:
                    if not constraint.pred(test_assignment):
                        is_valid = False
                        break
            
            if is_valid:
                assignment[var] = value
                result = backtrack()
                if result is not None:
                    return result
                del assignment[var]
                backtracks += 1
        
        return None
    
    solution = backtrack()
    runtime = time.time() - start_time
    
    return solution, {
        'nodes_visited': nodes_visited,
        'backtracks': backtracks,
        'runtime': runtime,
        'found_solution': solution is not None
    }


def analyze_puzzle(csp_file):
    print(f"\nAnalyzing: {csp_file}")
    print("-" * 40)
    
    solution1, stats1 = solve_csp(csp_file, use_mrv=False)
    
    # Solve with MRV
    solution2, stats2 = solve_csp(csp_file, use_mrv=True)
    
    # Print results
    print(f"Without MRV: {stats1['nodes_visited']:,} nodes, {stats1['backtracks']:,} backtracks, {stats1['runtime']:.3f}s")
    print(f"With MRV:    {stats2['nodes_visited']:,} nodes, {stats2['backtracks']:,} backtracks, {stats2['runtime']:.3f}s")
    
    if stats1['found_solution'] and stats2['found_solution']:
        time_improvement = ((stats1['runtime'] - stats2['runtime']) / stats1['runtime']) * 100
        node_improvement = ((stats1['nodes_visited'] - stats2['nodes_visited']) / stats1['nodes_visited']) * 100
        
        print(f"Improvements: {time_improvement:.1f}% faster, {node_improvement:.1f}% fewer nodes")
        
        # Check if solutions are the same
        if solution1 == solution2:
            print("Solution order: Same solution found by both methods")
        else:
            print("Solution order: Different solutions found (heuristic changed search order)")
        
        # Save and report solution
        print(f"Solution saved: {len(solution1)} variables assigned")
        
        # Show solution in appropriate format
        if "sudoku" in csp_file.lower():
            print("Sudoku Solution:")
            for row in range(1, 10):
                row_values = []
                for col in range(1, 10):
                    cell = f"r{row}c{col}"
                    value = solution1.get(cell, ".")
                    row_values.append(str(value))
                print(" ".join(row_values))
        else:
            print(f"Solution: {solution1}")
        
    elif stats1['found_solution']:
        print("Only simple method found solution")
    elif stats2['found_solution']:
        print("Only MRV found solution")
    else:
        print("No solution found")


def main():
    """Run analysis on CSP instances"""
    print("CSP Solver Analysis")
    print("=" * 50)
    
    # Analyze puzzles
    analyze_puzzle("send_more_money.csp")
    analyze_puzzle("sudoku_medium.csp")
    analyze_puzzle("sudoku_hard.csp")
    
    print("\n" + "=" * 50)
    print("Analysis complete!")


if __name__ == "__main__":
    main()