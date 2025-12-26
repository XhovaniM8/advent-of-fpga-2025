# Advent of FPGA 2025 - Jane Street Challenge

FPGA implementations for Advent of Code 2025 puzzles using Hardcaml and SystemVerilog.

**Deadline:** January 16, 2026

## Target Days

| Day | Algorithm | Status | Notes |
|-----|-----------|--------|-------|
| 4   | Parameterized Stencil Engine | Planning | Line buffer + sliding window pattern matcher |
| 7   | Event-Driven Beam Propagation | Planning | Neuromorphic-inspired sparse event processing |
| 10  | GF(2) Gaussian Elimination | Planning | XOR-only linear algebra for lights-out |
| 12  | Dancing Links (DLX) | Planning | Knuth's exact cover algorithm in hardware |

## Directory Structure

```
advent-of-fpga-2025/
├── designs/
│   ├── day04/          # Stencil engine
│   ├── day07/          # Event-driven beam simulator
│   ├── day10/          # GF(2) solver
│   └── day12/          # Dancing Links
├── python/             # Reference models and test generation
├── tests/              # cocotb and pytest verification
└── docs/               # Design documentation
```

## Setup

### Hardcaml Environment

```bash
# Install opam
brew install opam    # macOS
apt install opam     # Ubuntu

# Initialize and install Hardcaml
opam init
eval $(opam env)
opam install hardcaml hardcaml_waveterm hardcaml_verilator

# Verify installation
opam exec -- ocamlfind list | grep hardcaml
```

### Python Test Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pytest cocotb cocotb-test
```

### Simulation Tools

```bash
# Verilator (for Verilog simulation)
brew install verilator    # macOS
apt install verilator     # Ubuntu

# Icarus Verilog (alternative)
brew install icarus-verilog
```

## Running Tests

```bash
# Python reference model tests
pytest tests/ -v

# Hardcaml compilation check
opam exec -- ocamlfind ocamlc -package hardcaml -c designs/day07/beam_engine.ml

# Verilog lint check
verilator --lint-only designs/example.sv
```

## Design Approach

### Day 7: Event-Driven Beam Propagation

Treats beam simulation as an event stream problem (similar to neuromorphic vision processing):

- **Event format:** 32-bit word (x, y, direction, timestamp)
- **Time surface:** BRAM-based visited tracking for cycle detection
- **Advantage:** O(active_beams) vs O(grid_size) computation

### Day 12: Dancing Links

Hardware implementation of Knuth's Algorithm X:

- **Node memory:** 64-bit entries with bidirectional links
- **Operations:** Cover and uncover are sequences of BRAM read/write
- **Novelty:** No existing FPGA implementation of DLX

### Day 4: Parameterized Stencil

Classic FPGA pattern with configurable parameters:

- **Line buffers:** Store (window_height - 1) rows
- **Sliding window:** Shift register chain
- **Pattern matchers:** Parallel comparison in all 8 directions

### Day 10: GF(2) Linear Algebra

Binary field arithmetic maps directly to XOR gates:

- **Row XOR:** Parallel operation across entire row width
- **No carry chains:** Pure combinational XOR logic
- **Gaussian elimination:** FSM controlling row operations

## Resource Estimates

| Day | BRAM (KB) | LUTs | Fmax (est) |
|-----|-----------|------|------------|
| 4   | ~20       | 300  | 250MHz     |
| 7   | ~180      | 500  | 200MHz     |
| 10  | ~10       | 400  | 300MHz     |
| 12  | ~100      | 800  | 100MHz     |

## References

- Knuth, "Dancing Links" (2000): https://arxiv.org/abs/cs/0011047
- Jane Street Hardcaml: https://github.com/janestreet/hardcaml
- Jane Street Advent of Hardcaml 2024: https://blog.janestreet.com/advent-of-hardcaml-2024/

## Contributing

1. Python reference model first (in `../advent-of-code/2025/dayXX/python/`)
2. Test vectors from Python (`--vectors` flag)
3. Hardcaml implementation
4. cocotb verification against test vectors
