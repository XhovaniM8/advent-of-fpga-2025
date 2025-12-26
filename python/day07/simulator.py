"""
Day 7: Event-Driven Beam Simulator

This module implements beam propagation as an event stream, modeling
the neuromorphic FPGA architecture. The event-based approach processes
only active beams rather than iterating the entire grid each step.

Usage:
    python simulator.py [--input PATH] [--stats] [--trace]

Hardware Design Notes:
    - Event format maps to AER (Address-Event Representation)
    - Time surface tracks visited states for cycle detection
    - Queue depth determines BRAM requirements
"""
from dataclasses import dataclass
from collections import deque
from typing import List, Set, Tuple, Optional, Dict
from enum import IntEnum
import argparse
import os


class Direction(IntEnum):
    """Beam directions - 2 bits in hardware"""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


@dataclass
class BeamEvent:
    """
    AER-style event format.
    
    Hardware bit allocation:
        x: 7 bits (0-127, supports up to 128x128 grid)
        y: 7 bits
        direction: 2 bits
        timestamp: 16 bits (for cycle detection)
    
    Total: 32 bits per event
    """
    x: int
    y: int
    direction: Direction
    timestamp: int
    
    def to_bits(self) -> int:
        """Pack event into 32-bit word for hardware simulation"""
        return (
            (self.timestamp & 0xFFFF) << 16 |
            (self.direction & 0x3) << 14 |
            (self.y & 0x7F) << 7 |
            (self.x & 0x7F)
        )
    
    @classmethod
    def from_bits(cls, word: int) -> 'BeamEvent':
        """Unpack 32-bit word to event"""
        return cls(
            x=word & 0x7F,
            y=(word >> 7) & 0x7F,
            direction=Direction((word >> 14) & 0x3),
            timestamp=(word >> 16) & 0xFFFF
        )


class TimeSurface:
    """
    Tracks last visit timestamp per (x, y, direction).
    
    This is analogous to time surfaces in event-based vision,
    used here for cycle detection. In hardware, this maps to
    BRAM with width*height*4 entries.
    
    Memory: 143x143x4 = 81,796 entries x 16 bits = 163KB
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface: Dict[Tuple[int, int, int], int] = {}
    
    def check_and_update(self, event: BeamEvent) -> bool:
        """
        Check if cell+direction was visited, update if not.
        
        Returns:
            True if this is a new visit, False if already visited
        """
        key = (event.x, event.y, event.direction)
        if key in self.surface:
            return False
        self.surface[key] = event.timestamp
        return True
    
    def get_memory_stats(self) -> dict:
        """Return memory usage statistics for hardware sizing"""
        return {
            'entries_used': len(self.surface),
            'max_entries': self.width * self.height * 4,
            'utilization': len(self.surface) / (self.width * self.height * 4),
            'bits_per_entry': 16,
            'total_bits': self.width * self.height * 4 * 16
        }


class EventQueue:
    """
    FIFO queue for beam events.
    
    Hardware implementation: Circular buffer in BRAM
    Depth sizing based on max observed queue depth during simulation.
    """
    def __init__(self, max_depth: int = 1024):
        self.queue = deque()
        self.max_depth = max_depth
        self.peak_depth = 0
        self.total_events = 0
    
    def push(self, event: BeamEvent):
        """Add event to queue"""
        self.queue.append(event)
        self.peak_depth = max(self.peak_depth, len(self.queue))
        self.total_events += 1
    
    def pop(self) -> Optional[BeamEvent]:
        """Remove and return next event"""
        if self.queue:
            return self.queue.popleft()
        return None
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0
    
    def get_stats(self) -> dict:
        """Queue statistics for hardware sizing"""
        return {
            'peak_depth': self.peak_depth,
            'total_events': self.total_events,
            'recommended_bram_depth': 2 ** (self.peak_depth.bit_length()),
        }


class GridROM:
    """
    Read-only grid storage.
    
    Hardware: Distributed ROM or BRAM
    Each cell: 3 bits (5 cell types + empty)
    """
    CELL_EMPTY = 0
    CELL_MIRROR_FWD = 1   # /
    CELL_MIRROR_BWD = 2   # \
    CELL_SPLIT_V = 3      # |
    CELL_SPLIT_H = 4      # -
    
    CELL_MAP = {
        '.': CELL_EMPTY,
        '/': CELL_MIRROR_FWD,
        '\\': CELL_MIRROR_BWD,
        '|': CELL_SPLIT_V,
        '-': CELL_SPLIT_H,
    }
    
    def __init__(self, grid: List[str]):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self._encoded = self._encode_grid()
    
    def _encode_grid(self) -> List[List[int]]:
        """Encode grid to numeric values for hardware"""
        return [
            [self.CELL_MAP.get(c, self.CELL_EMPTY) for c in row]
            for row in self.grid
        ]
    
    def lookup(self, x: int, y: int) -> int:
        """Read cell type at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._encoded[y][x]
        return -1  # Out of bounds
    
    def get_memory_stats(self) -> dict:
        return {
            'width': self.width,
            'height': self.height,
            'total_cells': self.width * self.height,
            'bits_per_cell': 3,
            'total_bits': self.width * self.height * 3
        }


class BeamProcessor:
    """
    Core processing element for beam events.
    
    This models the combinational logic that processes one event
    and generates 0, 1, or 2 output events based on cell type.
    
    Hardware: Combinational logic block, ~50 LUTs estimated
    """
    # Direction deltas: [NORTH, EAST, SOUTH, WEST]
    DX = [0, 1, 0, -1]
    DY = [-1, 0, 1, 0]
    
    # Reflection tables (indexed by direction)
    REFLECT_FWD = [Direction.EAST, Direction.NORTH, Direction.WEST, Direction.SOUTH]  # /
    REFLECT_BWD = [Direction.WEST, Direction.SOUTH, Direction.EAST, Direction.NORTH]  # \
    
    def __init__(self, grid: GridROM):
        self.grid = grid
    
    def process(self, event: BeamEvent) -> List[BeamEvent]:
        """
        Process single event, return output events.
        
        This is the core FPGA processing element.
        Latency: 1 clock cycle (combinational)
        """
        x, y, d = event.x, event.y, event.direction
        cell = self.grid.lookup(x, y)
        
        if cell < 0:  # Out of bounds
            return []
        
        next_ts = event.timestamp + 1
        
        if cell == GridROM.CELL_EMPTY:
            return [self._propagate(x, y, d, next_ts)]
        
        elif cell == GridROM.CELL_MIRROR_FWD:  # /
            new_dir = self.REFLECT_FWD[d]
            return [self._propagate(x, y, new_dir, next_ts)]
        
        elif cell == GridROM.CELL_MIRROR_BWD:  # \
            new_dir = self.REFLECT_BWD[d]
            return [self._propagate(x, y, new_dir, next_ts)]
        
        elif cell == GridROM.CELL_SPLIT_V:  # |
            if d in [Direction.NORTH, Direction.SOUTH]:
                return [self._propagate(x, y, d, next_ts)]
            else:
                return [
                    self._propagate(x, y, Direction.NORTH, next_ts),
                    self._propagate(x, y, Direction.SOUTH, next_ts)
                ]
        
        elif cell == GridROM.CELL_SPLIT_H:  # -
            if d in [Direction.EAST, Direction.WEST]:
                return [self._propagate(x, y, d, next_ts)]
            else:
                return [
                    self._propagate(x, y, Direction.EAST, next_ts),
                    self._propagate(x, y, Direction.WEST, next_ts)
                ]
        
        return []
    
    def _propagate(self, x: int, y: int, d: Direction, ts: int) -> BeamEvent:
        """Create event for next cell in given direction"""
        return BeamEvent(
            x=x + self.DX[d],
            y=y + self.DY[d],
            direction=d,
            timestamp=ts
        )


class EventDrivenBeamSimulator:
    """
    Top-level simulator combining all components.
    
    This models the complete FPGA datapath:
        Event Queue -> Time Surface Check -> Beam Processor -> Output Events
    
    Hardware resource estimates:
        - BRAM: Queue (2KB) + Time Surface (164KB) + Grid ROM (8KB)
        - LUTs: ~200 for control + processing logic
        - Fmax: ~200MHz estimated
    """
    def __init__(self, grid: List[str], trace: bool = False):
        self.grid_rom = GridROM(grid)
        self.time_surface = TimeSurface(self.grid_rom.width, self.grid_rom.height)
        self.event_queue = EventQueue()
        self.processor = BeamProcessor(self.grid_rom)
        self.energized: Set[Tuple[int, int]] = set()
        self.trace = trace
        self.cycle_count = 0
    
    def inject_beam(self, x: int, y: int, direction: Direction):
        """Start beam at given position and direction"""
        event = BeamEvent(x, y, direction, timestamp=0)
        self.event_queue.push(event)
    
    def step(self) -> bool:
        """
        Execute one processing cycle.
        
        Returns:
            True if event was processed, False if queue empty
        """
        event = self.event_queue.pop()
        if event is None:
            return False
        
        self.cycle_count += 1
        
        # Time surface check (cycle detection)
        if not self.time_surface.check_and_update(event):
            if self.trace:
                print(f"[{self.cycle_count}] CYCLE: ({event.x},{event.y}) dir={event.direction.name}")
            return True
        
        # Track energized cells
        if 0 <= event.x < self.grid_rom.width and 0 <= event.y < self.grid_rom.height:
            self.energized.add((event.x, event.y))
        
        # Process event and generate outputs
        output_events = self.processor.process(event)
        
        if self.trace:
            cell = self.grid_rom.lookup(event.x, event.y)
            cell_char = './-\\|-'[cell] if cell >= 0 else '?'
            print(f"[{self.cycle_count}] ({event.x},{event.y}) dir={event.direction.name} "
                  f"cell='{cell_char}' -> {len(output_events)} events")
        
        for out_event in output_events:
            self.event_queue.push(out_event)
        
        return True
    
    def run(self) -> int:
        """Run until queue empty, return energized cell count"""
        while self.step():
            pass
        return len(self.energized)
    
    def get_hardware_stats(self) -> dict:
        """Collect statistics for hardware design decisions"""
        return {
            'grid': self.grid_rom.get_memory_stats(),
            'time_surface': self.time_surface.get_memory_stats(),
            'event_queue': self.event_queue.get_stats(),
            'energized_cells': len(self.energized),
            'total_cycles': self.cycle_count,
            'events_per_energized': (
                self.event_queue.get_stats()['total_events'] / len(self.energized)
                if self.energized else 0
            )
        }


def solve_part1(grid: List[str]) -> int:
    """Part 1: Beam enters top-left going right"""
    sim = EventDrivenBeamSimulator(grid)
    sim.inject_beam(0, 0, Direction.EAST)
    return sim.run()


def solve_part2(grid: List[str]) -> int:
    """Part 2: Find best entry point from any edge"""
    best = 0
    h, w = len(grid), len(grid[0])
    
    # Top edge going south
    for x in range(w):
        sim = EventDrivenBeamSimulator(grid)
        sim.inject_beam(x, 0, Direction.SOUTH)
        best = max(best, sim.run())
    
    # Bottom edge going north
    for x in range(w):
        sim = EventDrivenBeamSimulator(grid)
        sim.inject_beam(x, h - 1, Direction.NORTH)
        best = max(best, sim.run())
    
    # Left edge going east
    for y in range(h):
        sim = EventDrivenBeamSimulator(grid)
        sim.inject_beam(0, y, Direction.EAST)
        best = max(best, sim.run())
    
    # Right edge going west
    for y in range(h):
        sim = EventDrivenBeamSimulator(grid)
        sim.inject_beam(w - 1, y, Direction.WEST)
        best = max(best, sim.run())
    
    return best


def generate_test_vectors(grid: List[str], output_path: str):
    """
    Generate test vectors for hardware verification.
    
    Output format (CSV):
        input_x, input_y, input_dir, expected_energized
    """
    h, w = len(grid), len(grid[0])
    vectors = []
    
    # Test all edge entries
    for x in range(w):
        sim = EventDrivenBeamSimulator(grid)
        sim.inject_beam(x, 0, Direction.SOUTH)
        vectors.append((x, 0, Direction.SOUTH.value, sim.run()))
    
    with open(output_path, 'w') as f:
        f.write("input_x,input_y,input_dir,expected_energized\n")
        for v in vectors:
            f.write(f"{v[0]},{v[1]},{v[2]},{v[3]}\n")
    
    print(f"Generated {len(vectors)} test vectors to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Day 7 Event-Driven Beam Simulator')
    parser.add_argument('--input', '-i', default='input/day07.txt',
                        help='Path to input file')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Print hardware design statistics')
    parser.add_argument('--trace', '-t', action='store_true',
                        help='Print event trace')
    parser.add_argument('--vectors', '-v', metavar='PATH',
                        help='Generate test vectors to PATH')
    args = parser.parse_args()
    
    # Find input file
    input_path = args.input
    if not os.path.exists(input_path):
        # Try relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, '..', '..', '..', 'input', 'day07.txt')
        if os.path.exists(alt_path):
            input_path = alt_path
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    with open(input_path) as f:
        grid = [line.strip() for line in f if line.strip()]
    
    print(f"Grid size: {len(grid[0])}x{len(grid)}")
    
    if args.vectors:
        generate_test_vectors(grid, args.vectors)
        return 0
    
    # Solve
    sim = EventDrivenBeamSimulator(grid, trace=args.trace)
    sim.inject_beam(0, 0, Direction.EAST)
    part1 = sim.run()
    
    print(f"Part 1: {part1}")
    
    if args.stats:
        print("\nHardware Design Statistics:")
        stats = sim.get_hardware_stats()
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
