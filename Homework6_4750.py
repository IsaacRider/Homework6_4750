import time

class SudokuSolver:  
    # This class provides a Sudoku solver using backtracking with constraint propagation.
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        # Initialize the domains for each cell: if the cell is empty (0), its domain is [1-9].
        self.domains = { 
            (r, c): [1, 2, 3, 4, 5, 6, 7, 8, 9] if puzzle[r][c] == 0 else [puzzle[r][c]]
            for r in range(9) for c in range(9)
        }
    
    def is_valid(self, row, col, value):
        # Checks if placing `value` at (row, col) is valid based on Sudoku rules.
        
        # Check if `value` conflicts with the row.
        for c in range(9):
            if self.puzzle[row][c] == value:
                return False
        
        # Check if `value` conflicts with the column.
        for r in range(9):
            if self.puzzle[r][col] == value:
                return False
        
        # Check if `value` conflicts within the 3x3 box containing (row, col).
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.puzzle[r][c] == value:
                    return False
        
        return True
    
    def select_unassigned_variable(self):
        # Uses the Minimum Remaining Values (MRV) and Degree heuristics to select the next variable to assign.
        
        mrv = float('inf')  # Start with the largest possible value for MRV.
        candidate_vars = []  # List to hold variables with the smallest domain sizes.

        # Identify all unassigned variables and their domain sizes.
        for row in range(9):
            for col in range(9):
                if self.puzzle[row][col] == 0:
                    domain_size = len(self.domains[(row, col)])
                    if domain_size < mrv:
                        mrv = domain_size
                        candidate_vars = [(row, col)]
                    elif domain_size == mrv:
                        candidate_vars.append((row, col))
        
        # Apply Degree heuristic: maximize the number of constraints on unassigned neighbors.
        max_degree = -1
        selected_var = None
        for var in candidate_vars:
            row, col = var
            degree = sum(1 for r in range(9) if self.puzzle[r][col] == 0) + \
                     sum(1 for c in range(9) if self.puzzle[row][c] == 0) - 2
            if degree > max_degree:
                max_degree = degree
                selected_var = var
        
        return selected_var if selected_var else candidate_vars[0]
    
    def forward_checking(self, row, col, value):
        # Propagates the constraints caused by assigning `value` to (row, col).
        # Removes `value` from the domains of affected variables in the same row, column, and 3x3 box.
        
        removed = []
        
        # Remove `value` from the domains of variables in the same column.
        for r in range(9):
            if r != row and (r, col) in self.domains and value in self.domains[(r, col)]:
                self.domains[(r, col)].remove(value)
                removed.append((r, col, value))
        
        # Remove `value` from the domains of variables in the same row.
        for c in range(9):
            if c != col and (row, c) in self.domains and value in self.domains[(row, c)]:
                self.domains[(row, c)].remove(value)
                removed.append((row, c, value))
        
        # Remove `value` from the domains of variables in the same 3x3 box.
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and (r, c) in self.domains and value in self.domains[(r, c)]:
                    self.domains[(r, c)].remove(value)
                    removed.append((r, c, value))
        
        return removed

    def undo_forward_check(self, removed):
        # Restores the domains of variables affected by forward checking when backtracking.
        for r, c, value in removed:
            self.domains[(r, c)].append(value)

    def solve(self, limit=3600):
        # Solves the Sudoku puzzle using backtracking with a time limit (default: 3600 seconds).
        start_time = time.time()
        assignments = []  # Track the first 4 assignments for logging purposes.
        if self.backtrack(start_time, limit, assignments):
            return self.puzzle  # Return the solved puzzle if a solution is found.
        else:
            return None  # Return None if no solution is found within the time limit.
    
    def backtrack(self, start_time, limit, assignments):
        # Implements the backtracking algorithm with MRV and forward checking.
        if time.time() - start_time > limit:
            return False  # Stop if the time limit is exceeded.
        
        if all(self.puzzle[r][c] != 0 for r in range(9) for c in range(9)):
            return True  # Puzzle is solved if no unassigned variables remain.

        row, col = self.select_unassigned_variable()
        for value in sorted(self.domains[(row, col)]):
            if self.is_valid(row, col, value):
                self.puzzle[row][col] = value
                removed = self.forward_checking(row, col, value)

                # Log the first 4 variable assignments.
                if len(assignments) < 4:
                    domain_size = len(self.domains[(row, col)])
                    degree = sum(1 for r in range(9) if self.puzzle[r][col] == 0) + \
                             sum(1 for c in range(9) if self.puzzle[row][c] == 0) - 2
                    assignments.append((row, col, domain_size, degree, value))
                    print(f"Assignment {len(assignments)}: Variable=({row}, {col}), Domain Size={domain_size}, Degree={degree}, Value={value}")
                
                # Continue solving recursively if the puzzle remains consistent.
                if all(len(self.domains[(r, c)]) > 0 for r in range(9) for c in range(9) if self.puzzle[r][c] == 0):
                    if self.backtrack(start_time, limit, assignments):
                        return True

                # Undo the current assignment and propagate back the changes.
                self.puzzle[row][col] = 0
                self.undo_forward_check(removed)
        
        return False  # Trigger backtracking if no valid assignments can be made.

puzzles = [
    [[0, 0, 1, 0, 0, 2, 0, 0, 0], [0, 0, 5, 0, 0, 6, 0, 3, 0], [4, 6, 0, 0, 0, 5, 0, 0, 0],  # Puzzle 1
     [0, 0, 0, 1, 0, 4, 0, 0, 0], [6, 0, 0, 8, 0, 0, 1, 4, 3], [0, 0, 0, 0, 9, 0, 5, 0, 8],
     [8, 0, 0, 0, 4, 9, 0, 5, 0], [1, 0, 0, 3, 2, 0, 0, 0, 0], [0, 0, 9, 0, 0, 0, 3, 0, 0]],
    
    [[0, 0, 5, 0, 1, 0, 0, 0, 0], [0, 0, 2, 0, 0, 4, 0, 3, 0], [1, 0, 9, 0, 0, 0, 2, 0, 6],  # Puzzle 2
     [2, 0, 0, 0, 3, 0, 0, 0, 0], [0, 4, 0, 0, 0, 0, 7, 0, 0], [5, 0, 0, 0, 0, 7, 0, 0, 1],
     [0, 0, 0, 6, 0, 3, 0, 0, 0], [0, 6, 0, 1, 0, 0, 0, 0, 0], [3, 8, 0, 0, 0, 0, 5, 6, 0]],
    
    [[0, 0, 0, 0, 0, 0, 8, 1, 0], [0, 5, 0, 0, 0, 0, 0, 0, 0], [6, 0, 3, 0, 0, 0, 0, 5, 9],  # Puzzle 3
     [0, 0, 0, 7, 8, 0, 0, 0, 0], [3, 0, 0, 9, 0, 0, 0, 0, 0], [0, 0, 6, 0, 0, 0, 7, 0, 0],
     [0, 0, 0, 0, 6, 0, 0, 0, 3], [0, 0, 0, 0, 0, 2, 0, 0, 0], [0, 0, 5, 4, 0, 0, 0, 0, 0]]
]

for i, puzzle in enumerate(puzzles, 1):
    print(f"\nSolving Puzzle {i}...")
    solver = SudokuSolver(puzzle)
    solution = solver.solve(limit=10)
    if solution:
        for row in solution:
            print(row)
    else:
        print(f"Puzzle {i} could not be solved within the time limit.")
