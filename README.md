# Advent of FPGA 2025 🎄⚡

My solutions for the [Jane Street Advent of FPGA Challenge 2025](https://blog.janestreet.com/announcing-the-advent-of-fpga-challenge/)

## 🎯 Challenge Overview

- **Timeline:** Submit by January 16, 2026
- **Goal:** Implement Advent of Code puzzles in synthesizable RTL
- **Minimum:** At least 1 puzzle (you choose!)
- **Languages:** Any HDL (Verilog, SystemVerilog, VHDL, Chisel, etc.)
- **🎁 Bonus:** Solutions in Hardcaml (OCaml-based HDL) get extra credit!

### Pick Your Problems!

**You don't need to do all 25 days!** Choose the problems that interest you:
- Minimum: 1 puzzle
- Maximum: All 25 puzzles
- Sweet spot: 3-5 well-documented, creative solutions

See [`docs/FLEXIBLE_WORKFLOW.md`](docs/FLEXIBLE_WORKFLOW.md) for strategies on picking problems.

## 📁 Repository Structure

```
problems/
├── day01/          # Each day's solution
│   ├── rtl/        # RTL source files
│   ├── testbench/  # cocotb tests
│   ├── input.txt   # Puzzle input
│   └── README.md   # Design documentation
├── day02/
└── template/       # Template for new problems
```

## 🚀 Quick Start

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    iverilog \
    verilator \
    gtkwave \
    python3-pip

# Install Python dependencies
pip install -r requirements.txt
```

### Testing a Solution

```bash
cd problems/day01/testbench
make                    # Run with Icarus Verilog
make SIM=verilator      # Run with Verilator
make view               # View waveforms
```

### Adding a New Problem

**Option A: SystemVerilog**
```bash
# Copy template
./new_day.sh 7              # Creates problems/day07/

cd problems/day07
# 1. Get your puzzle input from adventofcode.com/2025/day/7/input
# 2. Paste into input.txt
# 3. Update rtl/solution.sv with your design
# 4. Update testbench/test_solution.py with tests
# 5. Document your approach in README.md

# Test it
cd testbench && make
```

**Option B: Hardcaml (Bonus Points!)**
```bash
# Create Hardcaml project
./new_hardcaml.sh 7         # Creates problems/day07-hardcaml/

cd problems/day07-hardcaml
# 1. Get your puzzle input
# 2. Paste into input.txt
# 3. Edit lib/design.ml - your hardware design
# 4. Edit test/test_design.ml - your tests
# 5. Document in README.md

# Build and test
dune build
dune test
dune exec ./bin/main.exe -- emit-verilog -o solution.v
```

## 🔧 Development Workflow

### 1. Start with the Algorithm

```python
# Prototype in Python first (optional but helpful)
def solve_part1(input_data):
    # Your algorithm
    return result
```

### 2. Design the Hardware Architecture

- Define I/O interfaces
- Choose state machine structure
- Plan datapath and memory
- Consider parallelism opportunities

### 3. Implement RTL

```systemverilog
// Use the template as starting point
module solution #(
    parameter DATA_WIDTH = 32
)(
    input  logic clk,
    input  logic rst_n,
    // ... your interfaces
);
```

### 4. Write Tests

```python
# cocotb tests - HDL agnostic!
@cocotb.test()
async def test_sample(dut):
    # Setup
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Test logic
    # ...
```

### 5. Verify with CI/CD

Push to GitHub and let CI run:
- ✅ Automated testing with multiple simulators
- ✅ Lint checking
- ✅ Waveform generation on failures
- ✅ **Performance metrics** - latency, throughput automatically measured
- ✅ **Scalability tests** - automatic 1x, 10x, 100x testing
- ✅ **Performance dashboard** - aggregate reports
- ✅ Optional synthesis checks

## 📊 Performance & Scalability Testing (NEW!)

**Automatically measures what Jane Street judges care about!**

Every push to GitHub automatically:
- 📈 Measures **latency** (cycles from start to output)
- 📈 Calculates **throughput** (items processed per cycle)  
- 🔬 Tests **scalability** with 1x, 10x, 100x inputs
- 📊 Generates **performance dashboard** with all metrics
- ⭐ Grades **scaling efficiency** (excellent/good/linear/poor)

```python
# Just write tests using our utilities
from performance_utils import PerformanceMonitor, ScalabilityTester

@cocotb.test()
async def test_performance(dut):
    monitor = PerformanceMonitor(dut)
    # ... your test ...
    monitor.report_latency(cycles)
    monitor.report_throughput(items, cycles)

@cocotb.test()
async def test_scalability(dut):
    tester = ScalabilityTester(dut)
    result, cycles = await tester.test_with_scale(run_test, base_size=100)
```

CI runs these automatically and generates reports! See [`docs/PERFORMANCE_TESTING.md`](docs/PERFORMANCE_TESTING.md) for complete guide.

## 🎨 Supported HDLs

| Language       | Support | Notes |
|----------------|---------|-------|
| SystemVerilog  | ✅ Full | Recommended for most problems |
| Verilog        | ✅ Full | Classic HDL |
| VHDL           | ✅ Full | Use GHDL simulator |
| Chisel         | ⚡ Via Verilog | Generate Verilog output |
| Amaranth       | ⚡ Via Verilog | Generate Verilog output |
| **Hardcaml**   | **🌟 Bonus!** | **OCaml-based, extra credit!** |

### 🎁 Hardcaml (Bonus Points!)

Hardcaml is Jane Street's OCaml-based hardware DSL. Solutions in Hardcaml get **extra credit**!

**Quick start:**
```bash
# Create a Hardcaml project for Day 5
./new_hardcaml.sh 5

cd problems/day05-hardcaml

# Install dependencies (first time only)
opam install hardcaml hardcaml_waveterm ppx_jane core stdio

# Build and test
dune build
dune test

# Generate Verilog
dune exec ./bin/main.exe -- emit-verilog -o solution.v
```

See [`problems/hardcaml-template/README.md`](problems/hardcaml-template/README.md) for detailed Hardcaml guide.

## 📊 CI/CD Pipeline

The repository includes automated workflows:

### Test Workflow (`.github/workflows/test.yml`)
- Automatically discovers all problems
- Runs tests with Icarus and Verilator
- Generates waveforms on failure
- Lints RTL code
- Tracks coverage

### Synthesis Workflow (`.github/workflows/synthesis.yml`)
- Optional resource estimation
- Uses Yosys for synthesis
- Reports LUT/FF usage
- Helps optimize designs

## 📋 Flexible Workflow

**You choose which problems to solve!** Work on what interests you:

```bash
# Example: Pick Days 3, 7, and 12
./new_day.sh 3                    # SystemVerilog
./new_hardcaml.sh 7               # Hardcaml (bonus!)
./new_day.sh 12                   # SystemVerilog

# Work on them in any order
# Commit whenever ready
# CI tests everything automatically
```

**Strategies:**
- **Breadth:** 8-10 problems in SystemVerilog
- **Depth:** 2-3 problems, highly optimized, multiple implementations
- **Hardcaml Focus:** 3-4 problems in Hardcaml for maximum bonus
- **Mix:** Some SV, some Hardcaml, showcase different approaches

See [`docs/FLEXIBLE_WORKFLOW.md`](docs/FLEXIBLE_WORKFLOW.md) for detailed strategies!

## 🏆 Completed Solutions

| Day | Part 1 | Part 2 | Notes |
|-----|--------|--------|-------|
| 01  | ⬜ | ⬜ | |
| 02  | ⬜ | ⬜ | |
| ... | ⬜ | ⬜ | |

## 💡 Design Philosophy

### Hardware-First Thinking

- **Exploit Parallelism:** Use multiple processing units
- **Pipeline Everything:** Break into stages for throughput
- **Memory is Expensive:** Minimize BRAM usage
- **Think Streaming:** Process data as it arrives

### Scalability Strategies

- Parameterize designs for easy scaling
- Test with 10× and 100× larger inputs
- Consider FPGA resource constraints
- Optimize area vs. performance trade-offs

## 🛠️ Useful Commands

```bash
# Run all tests
make -C problems/*/testbench

# Clean everything
find problems -name "Makefile" -execdir make clean \;

# Generate synthesis report for a problem
cd problems/day01/rtl
yosys -s synth.ys

# View waveforms
gtkwave problems/day01/testbench/dump.fst
```

## 📚 Resources

### Jane Street Challenge
- [Challenge Announcement](https://blog.janestreet.com/announcing-the-advent-of-fpga-challenge/)
- [Hardcaml Resources](https://github.com/janestreet/hardcaml)
- [Hardcaml Template](https://github.com/janestreet/hardcaml_template)
- [Submission Form](https://janestreet.com/advent-of-fpga-2025)

### HDL Learning
- [cocotb Documentation](https://docs.cocotb.org/)
- [Verilator Manual](https://verilator.org/guide/latest/)
- [Hardcaml Documentation](https://github.com/janestreet/hardcaml)
- [OCaml Learn](https://ocaml.org/docs)
- [ASIC World Tutorials](http://www.asic-world.com/)

### Advent of Code
- [Advent of Code 2025](https://adventofcode.com/2025)

## 🤝 Contributing

This is a personal challenge repo, but feel free to:
- Open issues for bugs in the template/CI
- Suggest improvements to the workflow
- Share your own approaches (after Jan 16, 2026)

## 📝 License

MIT License - See LICENSE file

## ✨ Tips for Success

1. **Start Simple:** Get basic I/O working first
2. **Test Early:** Write tests as you develop
3. **Document Everything:** Your README explains your creativity
4. **Think Hardware:** Don't just translate software to HDL
5. **Have Fun:** These are puzzles - enjoy the challenge!

---

Made with ❄️ for the Jane Street Advent of FPGA Challenge 2025
