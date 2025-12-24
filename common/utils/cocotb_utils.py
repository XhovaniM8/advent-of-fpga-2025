"""
Common utilities for Advent of FPGA testbenches
Reusable verification components and helpers
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles, ReadOnly
from cocotb.types import LogicArray
from typing import List, Tuple, Any
import random


class AXIStreamDriver:
    """
    AXI-Stream interface driver
    Useful for streaming puzzle inputs
    """
    
    def __init__(self, clk, valid, ready, data, last=None):
        self.clk = clk
        self.valid = valid
        self.ready = ready
        self.data = data
        self.last = last
    
    async def send(self, values: List[int], backpressure: float = 0.0):
        """Send a list of values with optional backpressure simulation"""
        for i, value in enumerate(values):
            self.valid.value = 1
            self.data.value = value
            
            if self.last is not None:
                self.last.value = 1 if i == len(values) - 1 else 0
            
            while True:
                await RisingEdge(self.clk)
                if self.ready.value == 1:
                    break
                    
            # Random backpressure
            if random.random() < backpressure:
                self.valid.value = 0
                await ClockCycles(self.clk, random.randint(1, 5))
        
        self.valid.value = 0


class AXIStreamMonitor:
    """
    AXI-Stream interface monitor
    Captures output data
    """
    
    def __init__(self, clk, valid, ready, data, last=None):
        self.clk = clk
        self.valid = valid
        self.ready = ready
        self.data = data
        self.last = last
        self.received = []
    
    async def collect(self, count: int = None, timeout_cycles: int = 10000):
        """Collect data from stream"""
        self.received = []
        cycles = 0
        
        while True:
            await RisingEdge(self.clk)
            cycles += 1
            
            if self.valid.value == 1 and self.ready.value == 1:
                self.received.append(int(self.data.value))
                
                if self.last is not None and self.last.value == 1:
                    break
                    
                if count is not None and len(self.received) >= count:
                    break
            
            if cycles >= timeout_cycles:
                raise TimeoutError(f"Monitor timeout after {cycles} cycles")
        
        return self.received


class MemoryModel:
    """
    Simple memory model for testing
    """
    
    def __init__(self, depth: int = 1024, width: int = 32):
        self.depth = depth
        self.width = width
        self.mem = [0] * depth
    
    def write(self, addr: int, data: int):
        """Write to memory"""
        if 0 <= addr < self.depth:
            self.mem[addr] = data & ((1 << self.width) - 1)
    
    def read(self, addr: int) -> int:
        """Read from memory"""
        if 0 <= addr < self.depth:
            return self.mem[addr]
        return 0
    
    def load_from_file(self, filename: str):
        """Load memory contents from file"""
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i >= self.depth:
                    break
                try:
                    self.mem[i] = int(line.strip(), 0)
                except ValueError:
                    pass


class PerformanceMonitor:
    """
    Monitor performance metrics
    """
    
    def __init__(self, clk):
        self.clk = clk
        self.start_cycle = 0
        self.end_cycle = 0
        self.cycles = 0
    
    async def start(self):
        """Start performance measurement"""
        await RisingEdge(self.clk)
        self.start_cycle = self.cycles
    
    async def stop(self):
        """Stop performance measurement"""
        await RisingEdge(self.clk)
        self.end_cycle = self.cycles
    
    def get_elapsed_cycles(self) -> int:
        """Get elapsed cycles"""
        return self.end_cycle - self.start_cycle
    
    async def run(self):
        """Background task to count cycles"""
        while True:
            await RisingEdge(self.clk)
            self.cycles += 1


def parse_aoc_input(filename: str) -> List[str]:
    """
    Parse Advent of Code input file
    Returns list of lines with whitespace stripped
    """
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def int_to_bits(value: int, width: int) -> LogicArray:
    """Convert integer to LogicArray of specified width"""
    return LogicArray(value & ((1 << width) - 1), width)


def bits_to_int(bits: LogicArray) -> int:
    """Convert LogicArray to integer"""
    return int(bits)


class ScoreboardChecker:
    """
    Scoreboard for checking expected vs actual results
    """
    
    def __init__(self, name: str = "Checker"):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def check(self, actual: Any, expected: Any, description: str = ""):
        """Check if actual matches expected"""
        if actual == expected:
            self.passed += 1
            return True
        else:
            self.failed += 1
            error = f"{description}: Expected {expected}, got {actual}"
            self.errors.append(error)
            return False
    
    def report(self, logger):
        """Print test results"""
        logger.info(f"{self.name} Results:")
        logger.info(f"  Passed: {self.passed}")
        logger.info(f"  Failed: {self.failed}")
        
        if self.errors:
            logger.error("Errors:")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        return self.failed == 0


async def wait_for_signal(signal, value, clk, timeout_cycles: int = 1000):
    """Wait for signal to reach specific value with timeout"""
    for _ in range(timeout_cycles):
        await RisingEdge(clk)
        if signal.value == value:
            return
    
    raise TimeoutError(
        f"Signal {signal._name} did not reach {value} within {timeout_cycles} cycles"
    )


class RandomDataGenerator:
    """Generate random test data"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
    
    def random_int(self, width: int) -> int:
        """Generate random integer for given bit width"""
        return random.randint(0, (1 << width) - 1)
    
    def random_list(self, length: int, width: int) -> List[int]:
        """Generate list of random integers"""
        return [self.random_int(width) for _ in range(length)]
