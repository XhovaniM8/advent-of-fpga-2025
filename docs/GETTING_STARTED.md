# Getting Started Guide

## Step-by-Step Setup

### 1. Initial Repository Setup

```bash
# Clone or create your repo
git init advent-of-fpga-2025
cd advent-of-fpga-2025

# Copy all the template files here
# (Use the structure created in this setup)

# Initialize git
git add .
git commit -m "Initial setup for Advent of FPGA 2025"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/advent-of-fpga-2025.git
git push -u origin main
```

### 2. Install Local Dependencies

#### Ubuntu/Debian

```bash
# Update package list
sudo apt-get update

# Install simulators
sudo apt-get install -y \
    iverilog \
    verilator \
    gtkwave

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install Python dependencies
pip3 install -r requirements.txt
```

#### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install icarus-verilog
brew install verilator
brew install gtkwave

# Install Python dependencies
pip3 install -r requirements.txt
```

#### Windows (WSL2 Recommended)

```bash
# Install WSL2 with Ubuntu
wsl --install

# Then follow Ubuntu instructions above
```

### 3. Verify Installation

```bash
# Test simulators
iverilog -v
verilator --version

# Test cocotb
python3 -c "import cocotb; print(cocotb.__version__)"

# Run example test
cd problems/day01/testbench
make
```

Expected output:
```
✅ Basic accumulator test PASSED!
✅ Multiple runs test PASSED!
✅ Edge cases test PASSED!
```

### 4. Working on a New Problem

#### Quick Method (Using Script)

```bash
# Create Day 2
./new_day.sh 2

# This creates:
# problems/day02/
#   ├── rtl/solution.sv
#   ├── testbench/test_solution.py
#   ├── testbench/Makefile
#   ├── input.txt
#   └── README.md
```

#### Manual Method

```bash
# Copy template
cp -r problems/template problems/day02

# Get your puzzle input
# Visit: https://adventofcode.com/2025/day/2/input
# Paste into: problems/day02/input.txt
```

### 5. Development Workflow

#### A. Design Phase

1. **Read the problem** on adventofcode.com
2. **Sketch algorithm** on paper
3. **Plan hardware architecture**:
   - What states do you need?
   - How will data flow?
   - What resources (memory, DSP)?
   - Can you parallelize?

#### B. Implementation

```bash
cd problems/day02
```

1. **Edit RTL** (`rtl/solution.sv`):
```systemverilog
// Update module interfaces
// Implement state machine
// Add datapath logic
```

2. **Write tests** (`testbench/test_solution.py`):
```python
@cocotb.test()
async def test_part1(dut):
    # Your test here
```

3. **Run tests locally**:
```bash
cd testbench
make                 # Quick test with Icarus
make SIM=verilator   # Faster simulation
make view            # Debug with waveforms
```

#### C. Debugging

When tests fail:

```bash
# Run with waveforms
make WAVES=1

# View waveforms
make view
# or
gtkwave dump.fst
```

**Debugging tips:**
- Add `dut._log.info()` in tests to track progress
- Use `$display()` in RTL for internal signals
- Check waveforms at failure point
- Verify reset behavior
- Check handshaking logic

#### D. Commit and Push

```bash
git add problems/day02
git commit -m "Add Day 2 solution"
git push
```

GitHub Actions will automatically:
- ✅ Run all tests
- ✅ Test with multiple simulators
- ✅ Lint your code
- ✅ Generate reports

### 6. Tips for Success

#### Hardware Design Patterns

**Pattern 1: Streaming Processor**
```systemverilog
// Good for line-by-line processing
always_ff @(posedge clk) begin
    if (input_valid && input_ready) begin
        // Process one item
    end
end
```

**Pattern 2: Batch Accumulator**
```systemverilog
// Load all data, then process
state: LOAD -> PROCESS -> OUTPUT
```

**Pattern 3: Pipeline**
```systemverilog
// Multi-stage processing
stage1 -> stage2 -> stage3 -> output
```

#### Performance Optimization

1. **Parallelize**: Process multiple items per cycle
2. **Pipeline**: Break into stages, 1 cycle each
3. **Reduce latency**: Minimize state transitions
4. **Use BRAM efficiently**: Read/write in parallel

#### Common Pitfalls

❌ **Don't:**
- Use blocking assignments in sequential logic
- Forget reset conditions
- Create combinational loops
- Ignore timing constraints

✅ **Do:**
- Use non-blocking (`<=`) in sequential blocks
- Reset all registers
- Draw timing diagrams
- Think in clock cycles

### 7. Testing Strategies

#### Minimum Tests

```python
@cocotb.test()
async def test_sample_input(dut):
    # Use AoC sample with known answer
    pass

@cocotb.test()
async def test_full_input(dut):
    # Use your actual puzzle input
    pass
```

#### Comprehensive Tests

```python
@cocotb.test()
async def test_edge_cases(dut):
    # Empty input, max values, etc.
    pass

@cocotb.test()
async def test_performance(dut):
    # Measure cycles, throughput
    pass
```

### 8. CI/CD Integration

Your `.github/workflows/test.yml` automatically:

1. **Discovers** all problems with Makefiles
2. **Tests** with Icarus and Verilator
3. **Uploads** waveforms on failure
4. **Runs** linting
5. **Reports** results in GitHub

View results:
- Go to GitHub → Actions tab
- Click on latest workflow run
- Download artifacts if tests failed

### 9. Optional: Synthesis

Test resource usage:

```bash
cd problems/day02/rtl

# Create synthesis script
cat > synth.ys << 'EOF'
read_verilog -sv solution.sv
synth_ice40 -top solution
stat
EOF

# Run synthesis
yosys -s synth.ys
```

### 10. Submission Preparation

Before January 16, 2026:

1. **Clean up code**:
   ```bash
   # Remove commented code
   # Add comments explaining complex logic
   # Update README with final results
   ```

2. **Document thoroughly**:
   - Explain algorithm choice
   - Show resource usage
   - Demonstrate scalability
   - Include performance metrics

3. **Test everything**:
   ```bash
   # Run all tests
   make -C problems/*/testbench clean
   make -C problems/*/testbench
   ```

4. **Submit**:
   - Fill out [submission form](https://janestreet.com/advent-of-fpga-2025)
   - Include GitHub repo link
   - Describe your most creative solution

### 11. Troubleshooting

**Problem: Tests fail with "No module named cocotb"**
```bash
pip3 install --upgrade cocotb
```

**Problem: Simulator not found**
```bash
# Install missing simulator
sudo apt-get install iverilog
```

**Problem: CI failing but tests pass locally**
```bash
# Check exact error in GitHub Actions log
# Often permissions or file path issues
```

**Problem: Waveforms not generating**
```bash
# Ensure WAVES=1 is set
make WAVES=1
```

### 12. Resources

- **cocotb Docs**: https://docs.cocotb.org/
- **Icarus Verilog**: http://iverilog.icarus.com/
- **Verilator**: https://verilator.org/
- **SystemVerilog**: https://www.chipverify.com/systemverilog/
- **AoC 2025**: https://adventofcode.com/2025

### 13. Need Help?

- Check example Day 01
- Read common/utils/cocotb_utils.py for helpers
- Contact advent-of-fpga@janestreet.com
- Review past AoC solutions online (after attempting!)

---

**Now you're ready to start! 🎄⚡**

Try running the Day 01 example, then create your first solution with `./new_day.sh 1`!
