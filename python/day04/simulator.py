"""
Day 4: Parameterized Stencil Engine for Pattern Matching

Implements a configurable stencil processor for word search patterns.
This models the line-buffer + sliding-window FPGA architecture.

Usage:
    python simulator.py [--input PATH] [--stats] [--window SIZE]

Hardware Design Notes:
    - Line buffers store (window_height - 1) rows
    - Sliding window extracts NxN region each cycle
    - Pattern matchers operate in parallel on window
    - Configurable window size (3x3, 5x5, etc.)
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Generator
from enum import Enum
import argparse
import os


class PatternDirection(Enum):
    """8 directions for pattern matching"""
    N = (0, -1)
    NE = (1, -1)
    E = (1, 0)
    SE = (1, 1)
    S = (0, 1)
    SW = (-1, 1)
    W = (-1, 0)
    NW = (-1, -1)


@dataclass
class MatchResult:
    """Result of pattern match"""
    x: int
    y: int
    direction: PatternDirection
    pattern: str


class LineBuffer:
    """
    FIFO line buffer for streaming stencil operations.
    
    Hardware: Implemented as circular buffer in BRAM
    Stores (window_height - 1) complete rows plus partial current row.
    
    Memory: width * (height - 1) * bits_per_char
    """
    def __init__(self, width: int, num_lines: int, bits_per_char: int = 8):
        self.width = width
        self.num_lines = num_lines
        self.bits_per_char = bits_per_char
        self.buffer: List[List[str]] = [['.' for _ in range(width)] for _ in range(num_lines)]
        self.write_ptr = 0
        self.valid_lines = 0
    
    def push_row(self, row: str):
        """Push a new row into the buffer"""
        for i, c in enumerate(row[:self.width]):
            self.buffer[self.write_ptr][i] = c
        self.write_ptr = (self.write_ptr + 1) % self.num_lines
        self.valid_lines = min(self.valid_lines + 1, self.num_lines)
    
    def get_column(self, col: int) -> List[str]:
        """Get vertical slice at column position"""
        result = []
        for i in range(self.num_lines):
            idx = (self.write_ptr - self.num_lines + i) % self.num_lines
            result.append(self.buffer[idx][col])
        return result
    
    def get_memory_stats(self) -> dict:
        return {
            'width': self.width,
            'num_lines': self.num_lines,
            'bits_per_char': self.bits_per_char,
            'total_bits': self.width * self.num_lines * self.bits_per_char,
            'bram_18k_blocks': (self.width * self.num_lines * self.bits_per_char) // 18432 + 1
        }


class SlidingWindow:
    """
    Extracts NxN window from line buffer + current row.
    
    Hardware: Shift register chain for horizontal sliding
    Each clock cycle shifts in one new column from line buffer.
    
    Resources: window_size * window_size registers
    """
    def __init__(self, size: int):
        self.size = size
        self.window: List[List[str]] = [['.' for _ in range(size)] for _ in range(size)]
        self.valid = False
        self.col_count = 0
    
    def shift_column(self, column: List[str]):
        """Shift in new column from right"""
        for row in self.window:
            row.pop(0)
        for i, c in enumerate(column[:self.size]):
            self.window[i].append(c)
        
        self.col_count += 1
        self.valid = self.col_count >= self.size
    
    def get_center(self) -> Tuple[int, int]:
        """Get center position indices"""
        c = self.size // 2
        return (c, c)
    
    def get_char(self, dx: int, dy: int) -> str:
        """Get character at offset from center"""
        cx, cy = self.get_center()
        x, y = cx + dx, cy + dy
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.window[y][x]
        return ''
    
    def get_resource_stats(self) -> dict:
        return {
            'window_size': self.size,
            'total_cells': self.size * self.size,
            'bits_per_cell': 8,
            'register_bits': self.size * self.size * 8
        }


class PatternMatcher:
    """
    Matches a pattern in a specific direction.
    
    Hardware: Comparator chain (one per pattern character)
    All comparisons happen in parallel within one clock cycle.
    
    Resources per direction: pattern_length comparators (8-bit each)
    Total: 8 directions * pattern_length * 8 LUTs
    """
    def __init__(self, pattern: str, direction: PatternDirection):
        self.pattern = pattern
        self.direction = direction
        self.dx, self.dy = direction.value
    
    def match(self, window: SlidingWindow) -> bool:
        """
        Check if pattern matches from center in given direction.
        
        Hardware: All character comparisons are parallel.
        Single cycle latency.
        """
        for i, expected_char in enumerate(self.pattern):
            dx = self.dx * i
            dy = self.dy * i
            actual_char = window.get_char(dx, dy)
            if actual_char != expected_char:
                return False
        return True
    
    def get_lut_estimate(self) -> int:
        """Estimate LUT usage for this matcher"""
        # 8-bit comparator per character, approximately 4 LUTs each
        return len(self.pattern) * 4


class StencilEngine:
    """
    Complete stencil processing engine.
    
    Combines line buffers, sliding window, and pattern matchers
    into a pipelined processing system.
    
    Pipeline stages:
        1. Read input character
        2. Update line buffer
        3. Shift sliding window
        4. Pattern matching (all directions parallel)
        5. Accumulate matches
    
    Throughput: 1 character per clock cycle (after pipeline fill)
    """
    def __init__(self, width: int, height: int, pattern: str, window_size: int = 7):
        self.width = width
        self.height = height
        self.pattern = pattern
        self.window_size = window_size
        
        # Ensure window can fit pattern in any direction
        min_window = len(pattern) * 2 - 1
        if window_size < min_window:
            window_size = min_window
            self.window_size = window_size
        
        self.line_buffer = LineBuffer(width, window_size - 1)
        self.window = SlidingWindow(window_size)
        
        # Create matchers for all 8 directions
        self.matchers = [
            PatternMatcher(pattern, d) for d in PatternDirection
        ]
        
        # State
        self.current_row: List[str] = []
        self.row_idx = 0
        self.col_idx = 0
        self.matches: List[MatchResult] = []
        self.cycles = 0
    
    def process_char(self, char: str) -> List[MatchResult]:
        """
        Process single input character.
        
        This models one clock cycle of the FPGA pipeline.
        """
        self.cycles += 1
        self.current_row.append(char)
        results = []
        
        # Build column for window: line buffer contents + current char
        if len(self.current_row) > self.col_idx:
            column = self.line_buffer.get_column(self.col_idx) + [char]
            self.window.shift_column(column)
            
            # Check all patterns in parallel
            if self.window.valid and self.row_idx >= self.window_size - 1:
                center_x = self.col_idx - self.window_size // 2
                center_y = self.row_idx - self.window_size // 2
                
                for matcher in self.matchers:
                    if matcher.match(self.window):
                        results.append(MatchResult(
                            x=center_x,
                            y=center_y,
                            direction=matcher.direction,
                            pattern=self.pattern
                        ))
            
            self.col_idx += 1
        
        return results
    
    def end_row(self):
        """Signal end of current row"""
        # Pad current row if needed
        while len(self.current_row) < self.width:
            self.current_row.append('.')
        
        # Push to line buffer
        self.line_buffer.push_row(''.join(self.current_row))
        
        # Reset for next row
        self.current_row = []
        self.row_idx += 1
        self.col_idx = 0
        self.window = SlidingWindow(self.window_size)
    
    def process_grid(self, grid: List[str]) -> List[MatchResult]:
        """Process complete grid"""
        self.matches = []
        
        for row in grid:
            for char in row:
                results = self.process_char(char)
                self.matches.extend(results)
            self.end_row()
        
        return self.matches
    
    def get_hardware_stats(self) -> dict:
        """Complete resource estimates"""
        matcher_luts = sum(m.get_lut_estimate() for m in self.matchers)
        
        return {
            'line_buffer': self.line_buffer.get_memory_stats(),
            'sliding_window': self.window.get_resource_stats(),
            'pattern_matchers': {
                'num_directions': len(self.matchers),
                'pattern_length': len(self.pattern),
                'total_luts': matcher_luts
            },
            'pipeline_depth': 5,
            'throughput': '1 char/cycle',
            'total_cycles': self.cycles,
            'matches_found': len(self.matches)
        }


def solve_part1(grid: List[str], pattern: str = "XMAS") -> int:
    """Count all occurrences of pattern in all 8 directions"""
    engine = StencilEngine(len(grid[0]), len(grid), pattern)
    matches = engine.process_grid(grid)
    return len(matches)


def solve_part2(grid: List[str]) -> int:
    """
    Part 2: Find X-MAS patterns (two MAS in X shape).
    
    This requires detecting:
        M.S    S.M    M.M    S.S
        .A.    .A.    .A.    .A.
        M.S    S.M    S.S    M.M
    
    Hardware: Additional pattern matchers for diagonal patterns
    """
    count = 0
    h, w = len(grid), len(grid[0])
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if grid[y][x] != 'A':
                continue
            
            # Get diagonal characters
            tl = grid[y-1][x-1]  # top-left
            tr = grid[y-1][x+1]  # top-right
            bl = grid[y+1][x-1]  # bottom-left
            br = grid[y+1][x+1]  # bottom-right
            
            # Check for valid X-MAS patterns
            diag1 = tl + br  # top-left to bottom-right
            diag2 = tr + bl  # top-right to bottom-left
            
            valid_diag = {'MS', 'SM'}
            if diag1 in valid_diag and diag2 in valid_diag:
                count += 1
    
    return count


def generate_test_vectors(grid: List[str], pattern: str, output_path: str):
    """Generate test vectors for hardware verification"""
    engine = StencilEngine(len(grid[0]), len(grid), pattern)
    matches = engine.process_grid(grid)
    
    with open(output_path, 'w') as f:
        f.write("# Day 4 Test Vectors\n")
        f.write(f"# Pattern: {pattern}\n")
        f.write(f"# Grid size: {len(grid[0])}x{len(grid)}\n")
        f.write(f"# Expected matches: {len(matches)}\n\n")
        
        f.write("x,y,direction\n")
        for m in matches:
            f.write(f"{m.x},{m.y},{m.direction.name}\n")
    
    print(f"Generated {len(matches)} test vectors to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Day 4 Stencil Pattern Matcher')
    parser.add_argument('--input', '-i', default='input/day04.txt',
                        help='Path to input file')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Print hardware design statistics')
    parser.add_argument('--window', '-w', type=int, default=7,
                        help='Sliding window size')
    parser.add_argument('--pattern', '-p', default='XMAS',
                        help='Pattern to search for')
    parser.add_argument('--vectors', '-v', metavar='PATH',
                        help='Generate test vectors to PATH')
    args = parser.parse_args()
    
    # Find input file
    input_path = args.input
    if not os.path.exists(input_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, '..', '..', '..', 'input', 'day04.txt')
        if os.path.exists(alt_path):
            input_path = alt_path
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    with open(input_path) as f:
        grid = [line.strip() for line in f if line.strip()]
    
    print(f"Grid size: {len(grid[0])}x{len(grid)}")
    print(f"Pattern: {args.pattern}")
    print(f"Window size: {args.window}")
    
    if args.vectors:
        generate_test_vectors(grid, args.pattern, args.vectors)
        return 0
    
    # Solve
    engine = StencilEngine(len(grid[0]), len(grid), args.pattern, args.window)
    matches = engine.process_grid(grid)
    
    print(f"\nPart 1: {len(matches)}")
    
    if args.stats:
        print("\nHardware Design Statistics:")
        stats = engine.get_hardware_stats()
        for section, data in stats.items():
            if isinstance(data, dict):
                print(f"\n  {section}:")
                for k, v in data.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {section}: {data}")
    
    part2 = solve_part2(grid)
    print(f"Part 2: {part2}")
    
    return 0


if __name__ == '__main__':
    exit(main())
