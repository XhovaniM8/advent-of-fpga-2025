"""
Performance and Scalability Testing Utilities for Advent of FPGA
Makes it easy to measure and report performance metrics in CI/CD
"""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
import os
import time


class PerformanceMonitor:
    """
    Monitor and report performance metrics for CI/CD
    """
    
    def __init__(self, dut, name="Design"):
        self.dut = dut
        self.name = name
        self.start_cycle = 0
        self.end_cycle = 0
        self.cycle_count = 0
        self.start_time = 0
        self.end_time = 0
        self.metrics = {}
    
    async def start(self):
        """Start performance measurement"""
        await RisingEdge(self.dut.clk)
        self.start_cycle = self.cycle_count
        self.start_time = time.time()
        self.dut._log.info(f"📊 Performance monitoring started at cycle {self.start_cycle}")
    
    async def stop(self):
        """Stop performance measurement and report"""
        await RisingEdge(self.dut.clk)
        self.end_cycle = self.cycle_count
        self.end_time = time.time()
        
        cycles_elapsed = self.end_cycle - self.start_cycle
        time_elapsed = self.end_time - self.start_time
        
        self.metrics["cycles"] = cycles_elapsed
        self.metrics["simulation_time_sec"] = time_elapsed
        
        # Report in format that CI can parse
        self.dut._log.info(f"✅ Performance: {cycles_elapsed} cycles in {time_elapsed:.3f}s")
        
        return cycles_elapsed
    
    def get_cycles(self):
        """Get elapsed cycles"""
        return self.end_cycle - self.start_cycle
    
    def report_latency(self, cycles):
        """Report latency metric"""
        self.dut._log.info(f"📈 Latency: {cycles} cycles")
        self.metrics["latency"] = cycles
    
    def report_throughput(self, items, cycles):
        """Report throughput metric"""
        throughput = items / cycles if cycles > 0 else 0
        self.dut._log.info(f"📈 Throughput: {throughput:.3f} items/cycle ({items} items in {cycles} cycles)")
        self.metrics["throughput"] = throughput
    
    def report_scalability(self, scale_factor, cycles):
        """Report scalability metric"""
        self.dut._log.info(f"📈 Scale: {scale_factor}x in {cycles} cycles")
        self.metrics[f"scale_{scale_factor}x"] = cycles
    
    async def count_cycles_background(self):
        """Background coroutine to count clock cycles"""
        while True:
            await RisingEdge(self.dut.clk)
            self.cycle_count += 1


class ScalabilityTester:
    """
    Run tests with different input sizes to measure scalability
    """
    
    def __init__(self, dut):
        self.dut = dut
        self.results = {}
    
    def get_scale_factor(self):
        """Get scale factor from environment variable (set by CI)"""
        return int(os.getenv('SCALE_FACTOR', '1'))
    
    async def test_with_scale(self, test_func, base_input_size=100):
        """
        Run a test function with scaled input
        
        Args:
            test_func: async function(dut, input_size) that runs the test
            base_input_size: baseline input size for 1x test
        """
        scale = self.get_scale_factor()
        input_size = base_input_size * scale
        
        self.dut._log.info(f"🔬 Running scalability test: {scale}x ({input_size} items)")
        
        monitor = PerformanceMonitor(self.dut, f"Scalability-{scale}x")
        cocotb.start_soon(monitor.count_cycles_background())
        
        await monitor.start()
        result = await test_func(self.dut, input_size)
        cycles = await monitor.stop()
        
        # Report for CI
        monitor.report_scalability(scale, cycles)
        
        # Calculate efficiency
        if scale > 1:
            expected_cycles = cycles / scale
            self.dut._log.info(f"📊 Scaling efficiency: {expected_cycles:.1f} cycles/1x unit")
        
        self.results[f"{scale}x"] = {
            "cycles": cycles,
            "input_size": input_size,
            "cycles_per_item": cycles / input_size if input_size > 0 else 0
        }
        
        return result, cycles


def measure_performance(test_func):
    """
    Decorator to automatically measure performance of a test
    
    Usage:
        @cocotb.test()
        @measure_performance
        async def test_my_design(dut):
            # Your test code
            pass
    """
    async def wrapper(dut):
        monitor = PerformanceMonitor(dut, test_func.__name__)
        
        # Start background cycle counter
        cocotb.start_soon(monitor.count_cycles_background())
        
        await monitor.start()
        result = await test_func(dut)
        await monitor.stop()
        
        return result
    
    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = test_func.__doc__
    return wrapper


async def measure_latency(dut, clk, start_signal, done_signal, timeout=10000):
    """
    Measure latency from start signal to done signal
    
    Args:
        dut: Design under test
        clk: Clock signal
        start_signal: Signal that triggers operation
        done_signal: Signal that indicates completion
        timeout: Maximum cycles to wait
    
    Returns:
        Number of cycles between start and done
    """
    start_signal.value = 1
    await RisingEdge(clk)
    start_signal.value = 0
    
    cycles = 0
    while cycles < timeout:
        await RisingEdge(clk)
        cycles += 1
        
        if done_signal.value == 1:
            dut._log.info(f"📈 Latency: {cycles} cycles")
            return cycles
    
    raise TimeoutError(f"Done signal not asserted within {timeout} cycles")


async def measure_throughput(dut, clk, items, cycles):
    """
    Calculate and report throughput
    
    Args:
        dut: Design under test
        clk: Clock signal
        items: Number of items processed
        cycles: Number of cycles taken
    
    Returns:
        Throughput in items/cycle
    """
    throughput = items / cycles if cycles > 0 else 0
    dut._log.info(f"📈 Throughput: {throughput:.3f} items/cycle")
    return throughput


class DataGenerator:
    """
    Generate test data at different scales
    """
    
    @staticmethod
    def scale_data(base_data, scale_factor):
        """
        Scale test data by a factor
        
        Args:
            base_data: List of base test data
            scale_factor: Multiplication factor
        
        Returns:
            Scaled data list
        """
        if scale_factor == 1:
            return base_data
        
        # Repeat and vary the data
        scaled = []
        for i in range(scale_factor):
            for item in base_data:
                # Add slight variation to make it more realistic
                scaled.append(item + i)
        
        return scaled
    
    @staticmethod
    def generate_random(count, width=32, seed=None):
        """Generate random test data"""
        import random
        if seed is not None:
            random.seed(seed)
        
        max_val = (1 << width) - 1
        return [random.randint(0, max_val) for _ in range(count)]


class ComparisonTester:
    """
    Compare performance of different implementations
    """
    
    def __init__(self, dut):
        self.dut = dut
        self.implementations = {}
    
    async def test_implementation(self, name, test_func, input_data):
        """Test a specific implementation"""
        monitor = PerformanceMonitor(self.dut, name)
        cocotb.start_soon(monitor.count_cycles_background())
        
        await monitor.start()
        result = await test_func(self.dut, input_data)
        cycles = await monitor.stop()
        
        self.implementations[name] = {
            "cycles": cycles,
            "result": result
        }
        
        return result, cycles
    
    def print_comparison(self):
        """Print comparison table"""
        if not self.implementations:
            return
        
        self.dut._log.info("=" * 60)
        self.dut._log.info("PERFORMANCE COMPARISON")
        self.dut._log.info("=" * 60)
        
        baseline = None
        for name, data in self.implementations.items():
            cycles = data["cycles"]
            
            if baseline is None:
                baseline = cycles
                speedup = 1.0
            else:
                speedup = baseline / cycles if cycles > 0 else float('inf')
            
            self.dut._log.info(f"{name:30s}: {cycles:8d} cycles (speedup: {speedup:.2f}x)")
        
        self.dut._log.info("=" * 60)


# Example usage template
EXAMPLE_PERFORMANCE_TEST = """
@cocotb.test()
async def test_performance(dut):
    '''Measure latency and throughput'''
    
    # Setup
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Performance monitoring
    monitor = PerformanceMonitor(dut)
    cocotb.start_soon(monitor.count_cycles_background())
    
    # Test data
    test_data = [1, 2, 3, 4, 5]
    
    # Measure latency
    latency = await measure_latency(
        dut,
        dut.clk,
        dut.start,
        dut.done,
        timeout=1000
    )
    monitor.report_latency(latency)
    
    # Measure throughput
    await monitor.start()
    # ... process test_data ...
    cycles = await monitor.stop()
    
    throughput = await measure_throughput(dut, dut.clk, len(test_data), cycles)
    monitor.report_throughput(len(test_data), cycles)


@cocotb.test()
async def test_scalability(dut):
    '''Test with 1x, 10x, 100x, 1000x inputs'''
    
    # Setup
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Scalability testing
    tester = ScalabilityTester(dut)
    
    async def run_test(dut, input_size):
        # Generate scaled test data
        test_data = DataGenerator.generate_random(input_size)
        
        # Run your algorithm
        # ... your test code here ...
        
        return result
    
    # CI will set SCALE_FACTOR to 1, 10, 100, 1000
    result, cycles = await tester.test_with_scale(run_test, base_input_size=100)
    
    dut._log.info(f"✅ Scalability test passed: {cycles} cycles")
"""
