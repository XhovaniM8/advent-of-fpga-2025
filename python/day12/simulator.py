"""
Day 12: Dancing Links (DLX) Exact Cover Solver

Implements Knuth's Algorithm X with Dancing Links for polyomino packing.
This serves as the reference model for the FPGA implementation.

Reference: Knuth, "Dancing Links" (2000) - https://arxiv.org/abs/cs/0011047

Usage:
    python simulator.py [--input PATH] [--stats] [--trace]

Hardware Design Notes:
    - Node links stored in BRAM (left, right, up, down, column, row)
    - Column headers in separate BRAM
    - Solution stack for backtracking
    - FSM states: SELECT_COL, COVER, RECURSE, UNCOVER, BACKTRACK
"""
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, Dict
import argparse
import os


@dataclass
class DLXNode:
    """
    Doubly-linked node for Dancing Links.
    
    Hardware representation (per node):
        left:   10 bits (node index)
        right:  10 bits
        up:     10 bits
        down:   10 bits
        column: 10 bits (column header index)
        row:    10 bits (row identifier)
    
    Total: 60 bits per node, fits in single BRAM word
    """
    left: int = -1
    right: int = -1
    up: int = -1
    down: int = -1
    column: int = -1
    row: int = -1


@dataclass
class DLXColumn:
    """
    Column header with size tracking.
    
    Hardware representation:
        size:  10 bits (number of 1s in column)
        left:  10 bits
        right: 10 bits
        first: 10 bits (first node in column)
        name:  10 bits (column identifier)
    
    Total: 50 bits per column header
    """
    size: int = 0
    left: int = -1
    right: int = -1
    first: int = -1
    name: int = 0


class DancingLinksMatrix:
    """
    Sparse matrix representation using Dancing Links.
    
    This class manages the node and column arrays that will
    map directly to BRAM in the FPGA implementation.
    """
    def __init__(self, num_columns: int):
        self.num_columns = num_columns
        self.nodes: List[DLXNode] = []
        self.columns: List[DLXColumn] = []
        self.header_idx = 0
        
        # Create header node (index 0)
        self.nodes.append(DLXNode())
        
        # Create column headers
        for i in range(num_columns):
            col = DLXColumn(name=i)
            col_idx = len(self.nodes)
            self.nodes.append(DLXNode(column=col_idx, row=-1))
            self.columns.append(col)
        
        # Link column headers horizontally
        for i, col in enumerate(self.columns):
            node_idx = i + 1  # +1 for header
            col.left = (i - 1) % num_columns + 1 if i > 0 else num_columns
            col.right = (i + 1) % num_columns + 1 if i < num_columns - 1 else 1
            col.first = node_idx  # Initially points to self
            
            self.nodes[node_idx].left = col.left
            self.nodes[node_idx].right = col.right
            self.nodes[node_idx].up = node_idx
            self.nodes[node_idx].down = node_idx
        
        # Link header to first and last columns
        self.nodes[0].right = 1
        self.nodes[0].left = num_columns
        self.nodes[1].left = 0
        self.nodes[num_columns].right = 0
    
    def add_row(self, row_id: int, columns: List[int]):
        """
        Add a row with 1s in specified columns.
        
        In hardware, this would be done during initialization
        by loading from configuration ROM.
        """
        if not columns:
            return
        
        first_node_idx = None
        prev_node_idx = None
        
        for col_idx in columns:
            # Create new node
            node = DLXNode(column=col_idx + 1, row=row_id)
            node_idx = len(self.nodes)
            self.nodes.append(node)
            
            # Link vertically into column
            col_header_idx = col_idx + 1
            col = self.columns[col_idx]
            
            # Insert before column header (at bottom of column)
            last_in_col = self.nodes[col_header_idx].up
            node.up = last_in_col
            node.down = col_header_idx
            self.nodes[last_in_col].down = node_idx
            self.nodes[col_header_idx].up = node_idx
            
            col.size += 1
            
            # Link horizontally
            if first_node_idx is None:
                first_node_idx = node_idx
                prev_node_idx = node_idx
            else:
                self.nodes[prev_node_idx].right = node_idx
                node.left = prev_node_idx
                prev_node_idx = node_idx
        
        # Complete horizontal cycle
        if first_node_idx is not None and prev_node_idx is not None:
            self.nodes[prev_node_idx].right = first_node_idx
            self.nodes[first_node_idx].left = prev_node_idx
    
    def get_memory_stats(self) -> dict:
        """Memory requirements for hardware"""
        return {
            'num_nodes': len(self.nodes),
            'num_columns': self.num_columns,
            'bits_per_node': 60,
            'total_node_bits': len(self.nodes) * 60,
            'bits_per_column': 50,
            'total_column_bits': self.num_columns * 50,
            'total_bram_bits': len(self.nodes) * 60 + self.num_columns * 50
        }


class DLXSolver:
    """
    Algorithm X solver using Dancing Links.
    
    This models the FPGA state machine:
        IDLE -> SELECT_COL -> COVER -> RECURSE -> UNCOVER -> BACKTRACK -> DONE
    
    Hardware resource estimates:
        - BRAM: Node memory + Column headers + Solution stack
        - LUTs: ~500 for FSM and link manipulation
        - Fmax: ~100MHz (BRAM-limited)
    """
    def __init__(self, matrix: DancingLinksMatrix, trace: bool = False):
        self.matrix = matrix
        self.trace = trace
        self.solution: List[int] = []
        self.solutions: List[List[int]] = []
        self.operations = 0  # Track for hardware cycle estimation
        
    def cover(self, col_idx: int):
        """
        Cover a column: remove it and all rows containing 1s in it.
        
        Hardware: This is a sequence of BRAM read/write operations.
        Latency: O(column_size * row_width) cycles
        """
        self.operations += 1
        
        # Get column header node
        col = self.matrix.columns[col_idx]
        col_node_idx = col_idx + 1
        col_node = self.matrix.nodes[col_node_idx]
        
        # Unlink column header horizontally
        self.matrix.nodes[col_node.left].right = col_node.right
        self.matrix.nodes[col_node.right].left = col_node.left
        
        if self.trace:
            print(f"  COVER column {col_idx} (size={col.size})")
        
        # For each row in this column
        row_node_idx = col_node.down
        while row_node_idx != col_node_idx:
            row_node = self.matrix.nodes[row_node_idx]
            
            # For each node in this row
            node_idx = row_node.right
            while node_idx != row_node_idx:
                node = self.matrix.nodes[node_idx]
                
                # Unlink vertically
                self.matrix.nodes[node.up].down = node.down
                self.matrix.nodes[node.down].up = node.up
                self.matrix.columns[node.column - 1].size -= 1
                
                self.operations += 1
                node_idx = node.right
            
            row_node_idx = row_node.down
    
    def uncover(self, col_idx: int):
        """
        Uncover a column: restore it (reverse of cover).
        
        Critical: Must be done in reverse order of cover.
        """
        self.operations += 1
        
        col = self.matrix.columns[col_idx]
        col_node_idx = col_idx + 1
        col_node = self.matrix.nodes[col_node_idx]
        
        if self.trace:
            print(f"  UNCOVER column {col_idx}")
        
        # For each row in this column (reverse order)
        row_node_idx = col_node.up
        while row_node_idx != col_node_idx:
            row_node = self.matrix.nodes[row_node_idx]
            
            # For each node in this row (reverse order)
            node_idx = row_node.left
            while node_idx != row_node_idx:
                node = self.matrix.nodes[node_idx]
                
                # Re-link vertically
                self.matrix.nodes[node.up].down = node_idx
                self.matrix.nodes[node.down].up = node_idx
                self.matrix.columns[node.column - 1].size += 1
                
                self.operations += 1
                node_idx = node.left
            
            row_node_idx = row_node.up
        
        # Re-link column header
        self.matrix.nodes[col_node.left].right = col_node_idx
        self.matrix.nodes[col_node.right].left = col_node_idx
    
    def choose_column(self) -> Optional[int]:
        """
        Choose column with minimum size (S heuristic).
        
        Hardware: Linear scan of column headers.
        Optimization: Could use priority queue for O(1) selection.
        """
        self.operations += 1
        
        header = self.matrix.nodes[0]
        if header.right == 0:
            return None  # All columns covered
        
        min_size = float('inf')
        best_col = None
        
        col_node_idx = header.right
        while col_node_idx != 0:
            col_idx = col_node_idx - 1
            if col_idx < len(self.matrix.columns):
                col = self.matrix.columns[col_idx]
                if col.size < min_size:
                    min_size = col.size
                    best_col = col_idx
            col_node_idx = self.matrix.nodes[col_node_idx].right
        
        return best_col
    
    def search(self, depth: int = 0, find_all: bool = False) -> bool:
        """
        Recursive search - maps to FSM in hardware.
        
        FSM states:
            SELECT_COL: Choose column with min size
            COVER: Cover selected column
            TRY_ROW: Select a row in the column
            COVER_ROW: Cover all columns in selected row
            RECURSE: Push state, recurse
            UNCOVER_ROW: Restore columns in row
            NEXT_ROW: Try next row
            UNCOVER: Restore column
            BACKTRACK: Pop state, continue
            DONE: Solution found or search complete
        """
        header = self.matrix.nodes[0]
        
        # Check if all columns covered
        if header.right == 0:
            self.solutions.append(list(self.solution))
            if self.trace:
                print(f"SOLUTION FOUND: {self.solution}")
            return True
        
        # Choose column
        col_idx = self.choose_column()
        if col_idx is None or self.matrix.columns[col_idx].size == 0:
            return False  # Dead end
        
        if self.trace:
            print(f"[depth={depth}] SELECT column {col_idx} (size={self.matrix.columns[col_idx].size})")
        
        self.cover(col_idx)
        
        # Try each row in this column
        col_node_idx = col_idx + 1
        row_node_idx = self.matrix.nodes[col_node_idx].down
        
        found = False
        while row_node_idx != col_node_idx:
            row_node = self.matrix.nodes[row_node_idx]
            row_id = row_node.row
            
            self.solution.append(row_id)
            
            if self.trace:
                print(f"[depth={depth}] TRY row {row_id}")
            
            # Cover all columns in this row
            node_idx = row_node.right
            while node_idx != row_node_idx:
                node = self.matrix.nodes[node_idx]
                self.cover(node.column - 1)
                node_idx = node.right
            
            # Recurse
            if self.search(depth + 1, find_all):
                found = True
                if not find_all:
                    return True
            
            # Backtrack: uncover in reverse order
            self.solution.pop()
            node_idx = row_node.left
            while node_idx != row_node_idx:
                node = self.matrix.nodes[node_idx]
                self.uncover(node.column - 1)
                node_idx = node.left
            
            row_node_idx = row_node.down
        
        self.uncover(col_idx)
        return found
    
    def solve(self, find_all: bool = False) -> List[List[int]]:
        """Run solver and return solutions"""
        self.solutions = []
        self.solution = []
        self.operations = 0
        self.search(find_all=find_all)
        return self.solutions
    
    def get_stats(self) -> dict:
        """Statistics for hardware design"""
        return {
            'solutions_found': len(self.solutions),
            'total_operations': self.operations,
            'max_recursion_depth': max(len(s) for s in self.solutions) if self.solutions else 0,
        }


def create_polyomino_matrix(grid_size: int, pieces: List[List[Tuple[int, int]]]) -> Tuple[DancingLinksMatrix, Dict[int, Tuple[int, int, int]]]:
    """
    Create exact cover matrix for polyomino packing.
    
    Columns:
        0 to grid_size^2-1: Cell coverage constraints
        grid_size^2 to end: Piece usage constraints
    
    Rows:
        Each row represents placing a piece at a specific position/orientation
    
    Returns:
        Matrix and mapping from row_id to (piece_idx, x, y)
    """
    num_cells = grid_size * grid_size
    num_pieces = len(pieces)
    num_cols = num_cells + num_pieces
    
    matrix = DancingLinksMatrix(num_cols)
    row_map: Dict[int, Tuple[int, int, int]] = {}
    row_id = 0
    
    for piece_idx, piece in enumerate(pieces):
        for y in range(grid_size):
            for x in range(grid_size):
                # Try placing piece with top-left at (x, y)
                cells = []
                valid = True
                
                for dx, dy in piece:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid_size and 0 <= ny < grid_size:
                        cells.append(ny * grid_size + nx)
                    else:
                        valid = False
                        break
                
                if valid and len(set(cells)) == len(cells):  # No overlapping cells
                    # This placement covers: cells + piece constraint
                    cols = cells + [num_cells + piece_idx]
                    matrix.add_row(row_id, cols)
                    row_map[row_id] = (piece_idx, x, y)
                    row_id += 1
    
    return matrix, row_map


def visualize_solution(grid_size: int, pieces: List[List[Tuple[int, int]]], 
                       solution: List[int], row_map: Dict[int, Tuple[int, int, int]]) -> List[str]:
    """Create ASCII visualization of solution"""
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    piece_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    for row_id in solution:
        piece_idx, x, y = row_map[row_id]
        piece = pieces[piece_idx]
        char = piece_chars[piece_idx % len(piece_chars)]
        
        for dx, dy in piece:
            grid[y + dy][x + dx] = char
    
    return [''.join(row) for row in grid]


def main():
    parser = argparse.ArgumentParser(description='Day 12 Dancing Links Solver')
    parser.add_argument('--input', '-i', default='input/day12.txt',
                        help='Path to input file')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Print hardware design statistics')
    parser.add_argument('--trace', '-t', action='store_true',
                        help='Print operation trace')
    parser.add_argument('--demo', '-d', action='store_true',
                        help='Run demo with simple polyomino problem')
    args = parser.parse_args()
    
    if args.demo:
        print("Demo: Packing tetrominoes into 4x4 grid")
        print("=" * 40)
        
        # Example pieces (tetrominoes)
        pieces = [
            [(0, 0), (1, 0), (2, 0), (3, 0)],  # I piece
            [(0, 0), (1, 0), (0, 1), (1, 1)],  # O piece
            [(0, 0), (1, 0), (2, 0), (2, 1)],  # L piece
            [(0, 0), (1, 0), (2, 0), (0, 1)],  # J piece
        ]
        
        matrix, row_map = create_polyomino_matrix(4, pieces)
        
        print(f"Matrix: {len(matrix.nodes)} nodes, {matrix.num_columns} columns")
        print(f"Memory: {matrix.get_memory_stats()}")
        
        solver = DLXSolver(matrix, trace=args.trace)
        solutions = solver.solve(find_all=True)
        
        print(f"\nFound {len(solutions)} solutions")
        print(f"Operations: {solver.operations}")
        
        if solutions:
            print("\nFirst solution:")
            viz = visualize_solution(4, pieces, solutions[0], row_map)
            for row in viz:
                print(f"  {row}")
        
        return 0
    
    # Load actual puzzle input
    input_path = args.input
    if not os.path.exists(input_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, '..', '..', '..', 'input', 'day12.txt')
        if os.path.exists(alt_path):
            input_path = alt_path
    
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        print("Use --demo flag to run demonstration")
        return 1
    
    # Parse puzzle-specific input here
    print(f"Loading input from {input_path}")
    # TODO: Add actual Day 12 puzzle parsing
    
    return 0


if __name__ == '__main__':
    exit(main())
