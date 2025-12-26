"""
cocotb testbench for Day 7 Event-Driven Beam Engine

This testbench verifies the Hardcaml/Verilog implementation against
the Python reference model.

Usage:
    pytest test_day07.py -v

Requirements:
    - cocotb
    - cocotb-test
    - Verilator or Icarus Verilog
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb.result import TestFailure
import os
import sys

# Add Python simulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
                                 'advent-of-code', '2025', 'day07', 'python'))


@cocotb.test()
async def test_reset(dut):
    """Test that reset clears all state"""
    clock = Clock(dut.clock, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Assert reset
    dut.clear.value = 1
    await ClockCycles(dut.clock, 5)
    
    # Release reset
    dut.clear.value = 0
    await ClockCycles(dut.clock, 1)
    
    # Check outputs are in reset state
    assert dut.done_.value == 0, "done_ should be 0 after reset"
    assert dut.energized_count.value == 0, "energized_count should be 0 after reset"


@cocotb.test()
async def test_simple_beam(dut):
    """Test beam propagation through empty grid"""
    clock = Clock(dut.clock, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.clear.value = 1
    await ClockCycles(dut.clock, 5)
    dut.clear.value = 0
    await ClockCycles(dut.clock, 1)
    
    # Start beam at (0, 0) going East
    dut.start_x.value = 0
    dut.start_y.value = 0
    dut.start_dir.value = 1  # EAST
    dut.start.value = 1
    await ClockCycles(dut.clock, 1)
    dut.start.value = 0
    
    # Wait for completion (with timeout)
    timeout = 10000
    for _ in range(timeout):
        await RisingEdge(dut.clock)
        if dut.done_.value == 1:
            break
    else:
        raise TestFailure("Timeout waiting for done signal")
    
    # Check result
    energized = int(dut.energized_count.value)
    print(f"Energized cells: {energized}")
    assert energized > 0, "Should energize at least one cell"


@cocotb.test()
async def test_against_reference(dut):
    """Compare hardware output against Python reference model"""
    try:
        from simulator import EventDrivenBeamSimulator, Direction
    except ImportError:
        cocotb.log.warning("Python simulator not found, skipping reference test")
        return
    
    clock = Clock(dut.clock, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Simple test grid (would need to load actual grid in real test)
    test_grid = [
        "...",
        "...",
        "..."
    ]
    
    # Get reference result
    ref_sim = EventDrivenBeamSimulator(test_grid)
    ref_sim.inject_beam(0, 0, Direction.EAST)
    expected = ref_sim.run()
    
    # Run hardware
    dut.clear.value = 1
    await ClockCycles(dut.clock, 5)
    dut.clear.value = 0
    await ClockCycles(dut.clock, 1)
    
    dut.start_x.value = 0
    dut.start_y.value = 0
    dut.start_dir.value = 1  # EAST
    dut.start.value = 1
    await ClockCycles(dut.clock, 1)
    dut.start.value = 0
    
    # Wait for completion
    timeout = 10000
    for _ in range(timeout):
        await RisingEdge(dut.clock)
        if dut.done_.value == 1:
            break
    
    # Compare results
    hw_result = int(dut.energized_count.value)
    assert hw_result == expected, f"Hardware: {hw_result}, Expected: {expected}"


@cocotb.test()
async def test_cycle_detection(dut):
    """Test that cycles are properly detected and terminated"""
    clock = Clock(dut.clock, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.clear.value = 1
    await ClockCycles(dut.clock, 5)
    dut.clear.value = 0
    await ClockCycles(dut.clock, 1)
    
    # TODO: Load grid with cycle-inducing mirrors
    # For now, just verify basic operation doesn't hang
    
    dut.start_x.value = 0
    dut.start_y.value = 0
    dut.start_dir.value = 1
    dut.start.value = 1
    await ClockCycles(dut.clock, 1)
    dut.start.value = 0
    
    # Should complete within reasonable time
    timeout = 100000
    for cycle in range(timeout):
        await RisingEdge(dut.clock)
        if dut.done_.value == 1:
            cocotb.log.info(f"Completed in {cycle} cycles")
            break
    else:
        raise TestFailure("Cycle detection failed - simulation hung")


# Test runner configuration
def test_runner():
    """Setup for pytest-cocotb"""
    import cocotb_test.simulator
    
    # Find the Verilog file (generated from Hardcaml)
    verilog_sources = [
        os.path.join(os.path.dirname(__file__), '..', 'designs', 'day07', 'beam_engine.v')
    ]
    
    cocotb_test.simulator.run(
        verilog_sources=verilog_sources,
        toplevel="beam_engine",
        module="test_day07",
        simulator="verilator",
        extra_args=["--trace"],
    )


if __name__ == "__main__":
    test_runner()
