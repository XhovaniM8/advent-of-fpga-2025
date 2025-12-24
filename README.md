# Advent of FPGA 2025

Solutions for the Jane Street Advent of FPGA Challenge 2025.

## Competition Details

**Deadline:** January 16, 2026  
**Requirements:** Synthesizable RTL solutions to Advent of Code 2025 puzzles  
**Submission:** Code (open source), testbench, documentation  

### Judging Criteria

- Creativity and inventiveness of hardware architecture
- Performance and area trade-offs
- Scalability (handling 10x, 100x, 1000x larger inputs)
- Effective use of FPGA parallelism and pipelining
- Quality of documentation and explanation

### Bonus Points

Implementations in Hardcaml (OCaml-based hardware DSL) receive extra consideration.

## Repository Usage

### Adding Designs

Place HDL files in `designs/`:

```
designs/day01_solution.sv      # Verilog/SystemVerilog
designs/day03_parser.v          # Verilog
designs/day07_tree.ml           # Hardcaml (bonus points)
```

### Automated Testing

Push to GitHub triggers CI that:

- Compiles all `.sv` and `.v` files with Verilator
- Lints for syntax errors and warnings
- Compiles all `.ml` files with Hardcaml/OCaml
- Runs functional tests from `tests/` directory (if present)
- Reports results in GitHub Actions

### Functional Tests (Optional)

Add cocotb tests in `tests/` directory:

```python
# tests/test_day01.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_basic(dut):
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    
    # Test logic here
    assert dut.output.value == expected
```

### Local Testing

```bash
# Verilog
verilator --lint-only -Wall designs/your_design.sv

# Hardcaml
opam exec -- ocamlfind ocamlc -package hardcaml -c designs/your_design.ml

# Functional tests
cd tests && pytest test_day01.py
```

## Structure

```
designs/     Design files (.sv, .v, .ml)
tests/       Optional functional tests (.py)
```

## Resources

- [Competition announcement](https://blog.janestreet.com/announcing-the-advent-of-fpga-challenge/)
- [Advent of Code 2025](https://adventofcode.com/2025)
- [Hardcaml documentation](https://github.com/janestreet/hardcaml)
- [Submission form](https://janestreet.com/advent-of-fpga-2025)

## License

MIT
