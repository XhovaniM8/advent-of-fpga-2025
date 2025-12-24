# Quick Reference

## Common Commands

### Setup New Day
```bash
./new_day.sh 3              # Create Day 3 from template
```

### Testing
```bash
# From testbench directory
make                        # Run tests (Icarus)
make SIM=verilator          # Run tests (Verilator)
make WAVES=1                # Generate waveforms
make view                   # Open waveforms in GTKWave
make clean                  # Clean build files
```

### Development
```bash
# Run single test
make TESTCASE=test_basic

# Enable coverage
make COVERAGE=1 SIM=verilator

# Run with more verbose output
make COCOTB_LOG_LEVEL=DEBUG
```

### Debugging
```bash
# View waveforms
gtkwave dump.fst            # FST format (faster)
gtkwave dump.vcd            # VCD format

# Check syntax
verilator --lint-only rtl/solution.sv

# View test output
cat sim_build/sim.log
```

### Git Workflow
```bash
# Start new problem
git checkout -b day03
./new_day.sh 3

# Commit progress
git add problems/day03
git commit -m "WIP: Day 3 initial implementation"

# Push and trigger CI
git push origin day03
```

### Synthesis (Optional)
```bash
cd problems/day01/rtl

# Yosys synthesis
yosys -p "read_verilog -sv solution.sv; synth_ice40; stat"

# With JSON output
yosys -p "read_verilog -sv solution.sv; synth_ice40 -json design.json"
```

## cocotb Snippets

### Basic Test Structure
```python
@cocotb.test()
async def test_name(dut):
    # Clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Test logic
    dut.input.value = 42
    await RisingEdge(dut.clk)
    
    # Assert
    assert dut.output.value == expected
```

### Waiting for Signals
```python
# Wait for valid
while dut.valid.value != 1:
    await RisingEdge(dut.clk)

# Wait N cycles
await ClockCycles(dut.clk, 10)

# Wait for edge
await RisingEdge(dut.clk)
await FallingEdge(dut.clk)
```

### Reading Files
```python
with open("../input.txt", "r") as f:
    lines = [line.strip() for line in f]
    
for line in lines:
    dut.data.value = int(line)
    await RisingEdge(dut.clk)
```

## SystemVerilog Patterns

### State Machine
```systemverilog
typedef enum logic [1:0] {
    IDLE, WORK, DONE
} state_t;

state_t state, next_state;

always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) state <= IDLE;
    else state <= next_state;

always_comb begin
    next_state = state;
    case (state)
        IDLE: if (start) next_state = WORK;
        WORK: if (done) next_state = DONE;
        DONE: next_state = IDLE;
    endcase
end
```

### Valid/Ready Handshake
```systemverilog
// Producer
assign valid = (state == SENDING);
if (valid && ready) begin
    // Transfer happens
end

// Consumer  
assign ready = (state == RECEIVING);
if (valid && ready) begin
    // Accept data
end
```

### Pipeline Stage
```systemverilog
always_ff @(posedge clk) begin
    stage1_data <= input_data;
    stage2_data <= stage1_data + offset;
    stage3_data <= stage2_data * factor;
    output_data <= stage3_data;
end
```

## File Locations

| What | Where |
|------|-------|
| Your RTL | `problems/dayXX/rtl/solution.sv` |
| Your tests | `problems/dayXX/testbench/test_solution.py` |
| Puzzle input | `problems/dayXX/input.txt` |
| Documentation | `problems/dayXX/README.md` |
| Shared utils | `common/utils/cocotb_utils.py` |
| CI config | `.github/workflows/test.yml` |

## Simulator Comparison

| Feature | Icarus | Verilator |
|---------|--------|-----------|
| Speed | Slower | Faster |
| Setup | Easy | Easy |
| Coverage | Basic | Advanced |
| Debug | Good | Limited |
| 4-state | Yes | 2-state only |

Use Icarus for debugging, Verilator for fast iteration.

## CI/CD Status

Check: `https://github.com/YOUR_USERNAME/advent-of-fpga-2025/actions`

Badges to add to README:
```markdown
![Tests](https://github.com/YOUR_USERNAME/advent-of-fpga-2025/workflows/Test%20HDL%20Designs/badge.svg)
```

## Competition Checklist

Before submission:
- [ ] Code is open source (MIT/Apache license)
- [ ] README explains approach
- [ ] Testbench included and passing
- [ ] Can synthesize (at least one problem)
- [ ] Original work, can explain design
- [ ] Submitted by January 16, 2026

Bonus points:
- [ ] Implemented in Hardcaml
- [ ] Demonstrates scalability (10×, 100× larger inputs)
- [ ] Shows FPGA-specific optimizations
- [ ] Explores multiple architecture trade-offs

## Useful Links

Quick access:
- [AoC 2025](https://adventofcode.com/2025)
- [Challenge Page](https://blog.janestreet.com/announcing-the-advent-of-fpga-challenge/)
- [Submission Form](https://janestreet.com/advent-of-fpga-2025)
- [cocotb Docs](https://docs.cocotb.org/)
- [Hardcaml Tutorial](https://github.com/janestreet/hardcaml)

---

Keep this handy while working! 📌
