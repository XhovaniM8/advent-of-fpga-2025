"""
Tests for FPGA algorithm simulators.
"""
import pytest
import os
import importlib.util

def import_simulator(day: str):
    """Import simulator.py from specific day directory"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, 'python', day, 'simulator.py')
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location(f"sim_{day}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestDay07EventDriven:
    @pytest.fixture
    def sim(self):
        module = import_simulator('day07')
        if module is None:
            pytest.skip("Day 7 simulator not found")
        return module
    
    def test_beam_event_packing(self, sim):
        event = sim.BeamEvent(x=42, y=73, direction=sim.Direction.SOUTH, timestamp=1234)
        packed = event.to_bits()
        unpacked = sim.BeamEvent.from_bits(packed)
        assert unpacked.x == event.x
        assert unpacked.y == event.y
    
    def test_time_surface_cycle_detection(self, sim):
        ts = sim.TimeSurface(10, 10)
        event1 = sim.BeamEvent(5, 5, sim.Direction.NORTH, 0)
        event2 = sim.BeamEvent(5, 5, sim.Direction.NORTH, 1)
        assert ts.check_and_update(event1) == True
        assert ts.check_and_update(event2) == False
    
    def test_grid_rom_encoding(self, sim):
        grid = ["./\\", "|-.", "..."]
        rom = sim.GridROM(grid)
        assert rom.lookup(0, 0) == sim.GridROM.CELL_EMPTY
        assert rom.lookup(1, 0) == sim.GridROM.CELL_MIRROR_FWD
    
    def test_beam_reflection(self, sim):
        grid = ["/"]
        simulator = sim.EventDrivenBeamSimulator(grid)
        simulator.inject_beam(0, 0, sim.Direction.EAST)
        simulator.run()
        assert len(simulator.energized) == 1
    
    def test_beam_split(self, sim):
        grid = ["...", ".|.", "..."]
        simulator = sim.EventDrivenBeamSimulator(grid)
        simulator.inject_beam(0, 1, sim.Direction.EAST)
        simulator.run()
        assert (1, 1) in simulator.energized


class TestDay12DancingLinks:
    @pytest.fixture
    def sim(self):
        module = import_simulator('day12')
        if module is None:
            pytest.skip("Day 12 simulator not found")
        return module
    
    def test_dlx_node_linking(self, sim):
        matrix = sim.DancingLinksMatrix(3)
        matrix.add_row(0, [0, 1])
        matrix.add_row(1, [1, 2])
        assert matrix.columns[0].size == 1
        assert matrix.columns[1].size == 2
    
    def test_simple_exact_cover(self, sim):
        matrix = sim.DancingLinksMatrix(3)
        matrix.add_row(0, [0, 1])
        matrix.add_row(1, [2])
        solver = sim.DLXSolver(matrix)
        solutions = solver.solve(find_all=True)
        assert len(solutions) == 1


class TestDay04Stencil:
    @pytest.fixture
    def sim(self):
        module = import_simulator('day04')
        if module is None:
            pytest.skip("Day 4 simulator not found")
        return module
    
    def test_line_buffer(self, sim):
        lb = sim.LineBuffer(5, 3)
        lb.push_row("ABCDE")
        lb.push_row("FGHIJ")
        lb.push_row("KLMNO")
        col = lb.get_column(2)
        assert col == ['C', 'H', 'M']
    
    def test_sliding_window(self, sim):
        window = sim.SlidingWindow(3)
        window.shift_column(['A', 'D', 'G'])
        window.shift_column(['B', 'E', 'H'])
        window.shift_column(['C', 'F', 'I'])
        assert window.valid
        assert window.get_char(0, 0) == 'E'


class TestDay10GF2:
    @pytest.fixture
    def sim(self):
        module = import_simulator('day10')
        if module is None:
            pytest.skip("Day 10 simulator not found")
        return module
    
    def test_gf2_matrix_operations(self, sim):
        m = sim.GF2Matrix(3, 3)
        m.set(0, 0, 1)
        m.set(0, 1, 1)
        m.set(1, 0, 1)
        assert m.get(0, 0) == 1
        m.xor_rows(1, 0)
        assert m.get(1, 0) == 0
    
    def test_lights_out_3x3(self, sim):
        initial = [1] * 9
        solution = sim.solve_lights_out(3, initial)
        assert solution is not None
