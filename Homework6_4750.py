import time

class SudokuSolver: # This class holds the sudoku tree solution
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.domains = { (r, c): [1,2,3,4,5,6,7,8,9] if puzzle[r][c] == 0 else [puzzle[r][c]]
                        for r in range(9) for c in range(9)}
    
    def is_valid(self, row, col, value): # Checks if the number is valid with the current combination
        # Check row
        for c in range(9):
            if self.puzzle[row][c] == value:
                return False
        # Check column
        for r in range(9):
            if self.puzzle[r][col] == value:
                return False
        # Check 3x3 square
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.puzzle[r][c] == value:
                    return False
        return True
    
    def select_unassigned_variable(self):
        mrv = float('inf')
        candidate_vars = []
        for row in range(9):
            for col in range(9):
                if self.puzzle[row][col] == 0:
                    domain_size = len(self.domains[(row, col)])
                    if domain_size < mrv:
                        mrv = domain_size
                        candidate_vars = [(row, col)]
                    elif domain_size == mrv:
                        candidate_vars.append((row, col))
        
        # Apply Degree heuristic
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
        removed = []
        for r in range(9):
            if r != row and (r, col) in self.domains and value in self.domains[(r, col)]:
                self.domains[(r, col)].remove(value)
                removed.append((r, col, value))
        
        for c in range(9):
            if c != col and (row, c) in self.domains and value in self.domains[(row, c)]:
                self.domains[(row, c)].remove(value)
                removed.append((row, c, value))
        
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and (r, c) in self.domains and value in self.domains[(r, c)]:
                    self.domains[(r, c)].remove(value)
                    removed.append((r, c, value))
        
        return removed

    def undo_forward_check(self, removed):
        for r, c, value in removed:
            self.domains[(r, c)].append(value)

    def solve(self, limit=3600):
        start_time = time.time()
        if self.backtrack(start_time, limit):
            return self.puzzle
        else:
            return None
    
    def backtrack(self, start_time, limit):
        if time.time() - start_time > limit:
            return False
        
        if all(self.puzzle[r][c] != 0 for r in range(9) for c in range(9)):
            return True

        row, col = self.select_unassigned_variable()
        for value in sorted(self.domains[(row, col)]):
            if self.is_valid(row, col, value):
                self.puzzle[row][col] = value
                removed = self.forward_checking(row, col, value)

                if all(len(self.domains[(r, c)]) > 0 for r in range(9) for c in range(9) if self.puzzle[r][c] == 0):
                    if self.backtrack(start_time, limit):
                        return True

                self.puzzle[row][col] = 0
                self.undo_forward_check(removed)
                
        return False

# Test puzzles
puzzles = [
    [[0, 0, 1, 0, 0, 2, 0, 0, 0], [0, 0, 5, 0, 0, 6, 0, 3, 0], [4, 6, 0, 0, 0, 5, 0, 0, 0], # Puzzle 1
     [0, 0, 0, 1, 0, 4, 0, 0, 0], [6, 0, 0, 8, 0, 0, 1, 4, 3], [0, 0, 0, 0, 9, 0, 5, 0, 8],
     [8, 0, 0, 0, 4, 9, 0, 5, 0], [1, 0, 0, 3, 2, 0, 0, 0, 0], [0, 0, 9, 0, 0, 0, 3, 0, 0]],
    
    [[0, 0, 5, 0, 1, 0, 0, 0, 0], [0, 0, 2, 0, 0, 4, 0, 3, 0], [1, 0, 9, 0, 0, 0, 2, 0, 6], # Puzzle 2
     [2, 0, 0, 0, 3, 0, 0, 0, 0], [0, 4, 0, 0, 0, 0, 7, 0, 0], [5, 0, 0, 0, 0, 7, 0, 0, 1],
     [0, 0, 0, 6, 0, 3, 0, 0, 0], [0, 6, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 7, 0, 0, 5, 0]],
         
    [[6, 7, 0, 0, 0, 0, 0, 0, 0], [0, 2, 5, 0, 0, 0, 0, 0, 0], [0, 9, 0, 5, 6, 0, 2, 0, 0], # Puzzle 3
     [3, 0, 0, 0, 8, 0, 9, 0, 0], [0, 0, 0, 0, 0, 0, 8, 0, 1], [0, 0, 0, 4, 7, 0, 0, 0, 0],
     [0, 0, 8, 6, 0, 0, 0, 9, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], [1, 0, 6, 0, 5, 0, 0, 7, 0]],
]

count = 1
for puzzle in puzzles:
    print(f"Puzzle {count} Before:")
    for row in puzzle:
        print(row)
    solver = SudokuSolver(puzzle)
    solution = solver.solve()

    if solution:
        print(f"Puzzle {count} After:")
        for row in solution:
            print(row)
    else:
        print("No solution found within the time limit.")
    count = count + 1