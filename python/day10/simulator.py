"""
Day 10: GF(2) Gaussian Elimination / Hyperdimensional Computing

Solves "lights out" style puzzles using:
1. GF(2) Gaussian elimination (XOR-based linear algebra)
2. Optional: Hyperdimensional computing approach

Usage:
    python simulator.py [--input PATH] [--stats] [--method gauss|hdc]

Hardware Design Notes:
    - GF(2) ops are pure XOR logic (no carry chains)
    - Matrix stored in BRAM, row ops parallel XOR
    - HDC uses wide bit vectors with popcount
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
import argparse
import os
import random


class GF2Matrix:
    """
    Matrix over GF(2) - binary field where addition = XOR.
    
    Hardware implementation:
        - Each row stored as single wide word (up to 256 bits)
        - Row XOR: parallel XOR of entire row in one cycle
        - Pivot finding: priority encoder on column
    
    Resources:
        - BRAM: rows * cols bits for matrix
        - LUTs: cols for parallel XOR per row
    """
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.data: List[int] = [0] * rows  # Each row as bit vector
    
    def set(self, row: int, col: int, val: int):
        """Set matrix element"""
        if val:
            self.data[row] |= (1 << col)
        else:
            self.data[row] &= ~(1 << col)
    
    def get(self, row: int, col: int) -> int:
        """Get matrix element"""
        return (self.data[row] >> col) & 1
    
    def xor_rows(self, target: int, source: int):
        """XOR source row into target row - single cycle in hardware"""
        self.data[target] ^= self.data[source]
    
    def swap_rows(self, r1: int, r2: int):
        """Swap two rows"""
        self.data[r1], self.data[r2] = self.data[r2], self.data[r1]
    
    def find_pivot(self, col: int, start_row: int) -> Optional[int]:
        """Find row with 1 in given column, starting from start_row"""
        for r in range(start_row, self.rows):
            if self.get(r, col):
                return r
        return None
    
    def to_string(self) -> str:
        """String representation for debugging"""
        lines = []
        for r in range(self.rows):
            row_str = ''.join(str(self.get(r, c)) for c in range(self.cols))
            lines.append(row_str)
        return '\n'.join(lines)
    
    def get_memory_stats(self) -> dict:
        return {
            'rows': self.rows,
            'cols': self.cols,
            'bits_per_row': self.cols,
            'total_bits': self.rows * self.cols,
            'bram_18k_blocks': (self.rows * self.cols) // 18432 + 1
        }


class GF2GaussianElimination:
    """
    Gaussian elimination over GF(2).
    
    Solves systems of linear equations where all arithmetic is mod 2.
    Perfect for "lights out" puzzles where button presses toggle states.
    
    Hardware FSM states:
        FIND_PIVOT: Search for pivot in current column
        SWAP_ROWS: Move pivot row to diagonal
        ELIMINATE: XOR pivot row into all other rows with 1 in column
        NEXT_COL: Move to next column
        BACK_SUB: Back substitution (if needed)
        DONE: Solution found or no solution
    
    Latency: O(n^2) row operations, each O(1) cycles
    """
    def __init__(self, matrix: GF2Matrix, augmented_col: int, trace: bool = False):
        self.matrix = matrix
        self.augmented_col = augmented_col
        self.trace = trace
        self.operations = 0
        self.row_xors = 0
    
    def eliminate(self) -> Optional[List[int]]:
        """
        Perform Gaussian elimination.
        
        Returns solution vector or None if no solution.
        """
        n = self.matrix.rows
        pivot_row = 0
        
        # Forward elimination
        for col in range(self.augmented_col):
            if self.trace:
                print(f"\nColumn {col}:")
                print(self.matrix.to_string())
            
            # Find pivot
            pivot = self.matrix.find_pivot(col, pivot_row)
            self.operations += 1
            
            if pivot is None:
                continue  # Free variable
            
            # Swap to diagonal
            if pivot != pivot_row:
                self.matrix.swap_rows(pivot, pivot_row)
                self.operations += 1
                if self.trace:
                    print(f"  Swap rows {pivot} and {pivot_row}")
            
            # Eliminate other rows
            for r in range(n):
                if r != pivot_row and self.matrix.get(r, col):
                    self.matrix.xor_rows(r, pivot_row)
                    self.row_xors += 1
                    self.operations += 1
                    if self.trace:
                        print(f"  XOR row {pivot_row} into row {r}")
            
            pivot_row += 1
        
        if self.trace:
            print(f"\nReduced form:")
            print(self.matrix.to_string())
        
        # Extract solution from augmented column
        solution = []
        for r in range(n):
            # Find which variable this row solves for
            var = -1
            for c in range(self.augmented_col):
                if self.matrix.get(r, c):
                    if var == -1:
                        var = c
                    else:
                        var = -1  # Multiple variables - free
                        break
            
            if var >= 0:
                solution.append((var, self.matrix.get(r, self.augmented_col)))
        
        # Build full solution vector
        result = [0] * self.augmented_col
        for var, val in solution:
            result[var] = val
        
        return result
    
    def get_stats(self) -> dict:
        return {
            'total_operations': self.operations,
            'row_xors': self.row_xors,
            'matrix_size': f"{self.matrix.rows}x{self.matrix.cols}"
        }


class HyperdimensionalComputing:
    """
    Hyperdimensional computing approach for combinatorial search.
    
    Uses high-dimensional binary vectors (1000-10000 bits) with:
        - XOR for binding (association)
        - Majority vote for bundling (superposition)
        - Hamming distance for similarity
    
    Hardware advantages:
        - All operations are bit-parallel
        - No floating point
        - Noise tolerant
    
    Resources:
        - BRAM: item_memory (num_items * dim bits)
        - LUTs: XOR array (dim), popcount tree (log(dim) levels)
    """
    def __init__(self, dimension: int = 1024, num_items: int = 180):
        self.dim = dimension
        self.num_items = num_items
        self.item_memory: List[int] = []
        self._init_item_memory()
    
    def _init_item_memory(self):
        """Initialize random hypervectors for each item"""
        random.seed(42)  # Reproducible for hardware verification
        for _ in range(self.num_items):
            # Generate random bit vector
            hv = random.getrandbits(self.dim)
            self.item_memory.append(hv)
    
    def bind(self, hv1: int, hv2: int) -> int:
        """XOR binding - associates two concepts"""
        return hv1 ^ hv2
    
    def bundle(self, hvs: List[int]) -> int:
        """Majority vote bundling - creates superposition"""
        if not hvs:
            return 0
        
        # Count bits at each position
        counts = [0] * self.dim
        for hv in hvs:
            for i in range(self.dim):
                if (hv >> i) & 1:
                    counts[i] += 1
        
        # Majority vote
        threshold = len(hvs) // 2
        result = 0
        for i in range(self.dim):
            if counts[i] > threshold:
                result |= (1 << i)
        
        return result
    
    def hamming_distance(self, hv1: int, hv2: int) -> int:
        """
        Hamming distance - number of differing bits.
        
        Hardware: XOR then popcount
        Popcount uses tree of adders, O(log(dim)) depth
        """
        diff = hv1 ^ hv2
        return bin(diff).count('1')
    
    def similarity(self, hv1: int, hv2: int) -> float:
        """Normalized similarity (0 to 1)"""
        dist = self.hamming_distance(hv1, hv2)
        return 1.0 - (dist / self.dim)
    
    def encode_state(self, active_items: Set[int]) -> int:
        """Encode a set of active items as hypervector"""
        if not active_items:
            return 0
        return self.bundle([self.item_memory[i] for i in active_items])
    
    def find_closest(self, target: int, candidates: List[int]) -> int:
        """Find candidate with minimum Hamming distance to target"""
        min_dist = float('inf')
        best_idx = 0
        
        for i, candidate in enumerate(candidates):
            dist = self.hamming_distance(target, candidate)
            if dist < min_dist:
                min_dist = dist
                best_idx = i
        
        return best_idx
    
    def get_memory_stats(self) -> dict:
        return {
            'dimension': self.dim,
            'num_items': self.num_items,
            'item_memory_bits': self.dim * self.num_items,
            'popcount_depth': self.dim.bit_length(),
            'bram_18k_blocks': (self.dim * self.num_items) // 18432 + 1
        }


def create_lights_out_matrix(grid_size: int) -> Tuple[GF2Matrix, List[int]]:
    """
    Create coefficient matrix for lights out puzzle.
    
    Each button toggles itself and adjacent cells.
    Matrix A where A[i][j] = 1 if button j affects cell i.
    """
    n = grid_size * grid_size
    matrix = GF2Matrix(n, n + 1)  # +1 for augmented column
    
    for i in range(grid_size):
        for j in range(grid_size):
            cell = i * grid_size + j
            
            # Button at (i,j) affects:
            matrix.set(cell, cell, 1)  # itself
            
            if i > 0:  # above
                matrix.set((i-1) * grid_size + j, cell, 1)
            if i < grid_size - 1:  # below
                matrix.set((i+1) * grid_size + j, cell, 1)
            if j > 0:  # left
                matrix.set(cell - 1, cell, 1)
            if j < grid_size - 1:  # right
                matrix.set(cell + 1, cell, 1)
    
    return matrix, [i for i in range(n)]


def solve_lights_out(grid_size: int, initial_state: List[int], trace: bool = False) -> Optional[List[int]]:
    """
    Solve lights out puzzle using GF(2) Gaussian elimination.
    
    Args:
        grid_size: Size of square grid
        initial_state: List of cell values (0 or 1)
        trace: Print intermediate steps
    
    Returns:
        List of button presses needed, or None if no solution
    """
    matrix, _ = create_lights_out_matrix(grid_size)
    n = grid_size * grid_size
    
    # Set augmented column to target state (we want all zeros)
    # So we need to toggle cells that are currently 1
    for i, val in enumerate(initial_state):
        matrix.set(i, n, val)
    
    solver = GF2GaussianElimination(matrix, n, trace)
    return solver.eliminate()


def main():
    parser = argparse.ArgumentParser(description='Day 10 GF(2) / HDC Solver')
    parser.add_argument('--input', '-i', default='input/day10.txt',
                        help='Path to input file')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Print hardware design statistics')
    parser.add_argument('--trace', '-t', action='store_true',
                        help='Print operation trace')
    parser.add_argument('--method', '-m', choices=['gauss', 'hdc'], default='gauss',
                        help='Solution method')
    parser.add_argument('--demo', '-d', action='store_true',
                        help='Run demo with 3x3 lights out puzzle')
    args = parser.parse_args()
    
    if args.demo:
        print("Demo: 3x3 Lights Out Puzzle")
        print("=" * 40)
        
        # Example initial state (1 = light on)
        initial = [
            1, 0, 1,
            0, 1, 0,
            1, 0, 1
        ]
        
        print("Initial state:")
        for i in range(0, 9, 3):
            print(f"  {''.join(str(x) for x in initial[i:i+3])}")
        
        solution = solve_lights_out(3, initial, trace=args.trace)
        
        if solution:
            print(f"\nSolution (buttons to press):")
            for i in range(0, 9, 3):
                print(f"  {''.join(str(x) for x in solution[i:i+3])}")
            print(f"Total presses: {sum(solution)}")
        else:
            print("No solution found")
        
        if args.stats:
            matrix, _ = create_lights_out_matrix(3)
            print(f"\nMatrix stats: {matrix.get_memory_stats()}")
        
        return 0
    
    if args.method == 'hdc':
        print("Hyperdimensional Computing Demo")
        print("=" * 40)
        
        hdc = HyperdimensionalComputing(dimension=1024, num_items=180)
        
        # Demo: encode some states
        state1 = hdc.encode_state({0, 1, 2})
        state2 = hdc.encode_state({0, 1, 3})
        state3 = hdc.encode_state({10, 20, 30})
        
        print(f"Similarity(state1, state2): {hdc.similarity(state1, state2):.3f}")
        print(f"Similarity(state1, state3): {hdc.similarity(state1, state3):.3f}")
        
        if args.stats:
            print(f"\nHDC stats: {hdc.get_memory_stats()}")
        
        return 0
    
    # Load actual puzzle input
    input_path = args.input
    if not os.path.exists(input_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, '..', '..', '..', 'input', 'day10.txt')
        if os.path.exists(alt_path):
            input_path = alt_path
    
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        print("Use --demo flag to run demonstration")
        return 1
    
    print(f"Loading input from {input_path}")
    # TODO: Add actual Day 10 puzzle parsing
    
    return 0


if __name__ == '__main__':
    exit(main())
