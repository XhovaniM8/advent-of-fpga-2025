# Performance Testing & Scalability - Automated in CI/CD 🚀

## What Gets Automatically Measured

Every time you push to GitHub, the CI/CD pipeline automatically:

### ✅ Functional Tests
- Basic correctness
- Sample inputs
- Edge cases
- Full puzzle inputs

### 📊 Performance Metrics
- **Latency**: Cycles from start to first output
- **Throughput**: Items processed per cycle
- **Total cycles**: Complete execution time

### 🔬 Scalability Tests
- **1x baseline**: Your normal input
- **10x scale**: 10× larger inputs
- **100x scale**: 100× larger inputs (with timeout protection)

### 📈 Aggregate Reports
- Performance dashboard across all problems
- Comparison between simulators
- Scaling efficiency analysis

## How It Works

### 1. Write Performance Tests

The template includes performance tests:

```python
@cocotb.test()
async def test_performance(dut):
    """Measure latency and throughput"""
    
    monitor = PerformanceMonitor(dut)
    cocotb.start_soon(monitor.count_cycles_background())
    
    # Your test...
    
    monitor.report_latency(cycles)
    monitor.report_throughput(items, cycles)
```

### 2. Write Scalability Tests

```python
@cocotb.test()
async def test_scalability(dut):
    """Test with scaled inputs"""
    
    tester = ScalabilityTester(dut)
    scale = tester.get_scale_factor()  # CI sets this to 1, 10, 100
    
    async def run_test(dut, input_size):
        # Your algorithm with scaled data
        pass
    
    result, cycles = await tester.test_with_scale(run_test, base_size=100)
```

### 3. Push to GitHub

```bash
git add .
git commit -m "Add Day 7 solution"
git push
```

CI automatically runs your tests with different scales!

### 4. View Results

Check the **Actions** tab on GitHub:
- Click on your workflow run
- View the **Performance Dashboard** in the summary
- Download detailed reports from artifacts

## Performance Utils API

### PerformanceMonitor

```python
from performance_utils import PerformanceMonitor

# Initialize
monitor = PerformanceMonitor(dut, "My Design")
cocotb.start_soon(monitor.count_cycles_background())

# Measure
await monitor.start()
# ... your code ...
cycles = await monitor.stop()

# Report metrics (CI parses these logs!)
monitor.report_latency(latency_cycles)
monitor.report_throughput(items_processed, total_cycles)
monitor.report_scalability(scale_factor, cycles)
```

### ScalabilityTester

```python
from performance_utils import ScalabilityTester

tester = ScalabilityTester(dut)

# Get scale factor from environment (CI sets this)
scale = tester.get_scale_factor()  # 1, 10, 100, or 1000

# Run test with automatic scaling
async def my_test(dut, input_size):
    # Test logic here
    return result

result, cycles = await tester.test_with_scale(my_test, base_input_size=100)
```

### Helper Functions

```python
from performance_utils import measure_latency, measure_throughput, DataGenerator

# Measure latency
cycles = await measure_latency(dut, dut.clk, dut.start, dut.done, timeout=1000)

# Measure throughput
throughput = await measure_throughput(dut, dut.clk, items=100, cycles=500)

# Generate scaled data
base_data = [1, 2, 3, 4, 5]
scaled_data = DataGenerator.scale_data(base_data, scale_factor=10)
```

## CI/CD Environment Variables

The CI sets these automatically:

| Variable | Values | When Used |
|----------|--------|-----------|
| `SCALE_FACTOR` | 1, 10, 100 | Scalability tests |
| `SIM` | icarus, verilator | Which simulator |

Access in your tests:

```python
import os

scale = int(os.getenv('SCALE_FACTOR', '1'))
sim = os.getenv('SIM', 'icarus')
```

## Example: Complete Performance Test

```python
@cocotb.test()
async def test_performance(dut):
    """
    Complete performance measurement example
    """
    
    # Setup
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Initialize monitor
    monitor = PerformanceMonitor(dut, "MyDesign")
    cocotb.start_soon(monitor.count_cycles_background())
    
    # Test data
    test_data = [i for i in range(100)]
    
    # Measure latency
    dut._log.info("📊 Measuring latency...")
    latency = await measure_latency(
        dut, dut.clk, dut.start, dut.done, timeout=1000
    )
    monitor.report_latency(latency)
    
    # Measure throughput
    dut._log.info("📊 Measuring throughput...")
    await monitor.start()
    
    # Process data
    for data in test_data:
        dut.input_valid.value = 1
        dut.input_data.value = data
        await RisingEdge(dut.clk)
    
    dut.input_valid.value = 0
    await ClockCycles(dut.clk, 100)
    
    total_cycles = await monitor.stop()
    throughput = await measure_throughput(dut, dut.clk, len(test_data), total_cycles)
    monitor.report_throughput(len(test_data), total_cycles)
    
    # CI will parse and display these metrics!
    dut._log.info(f"✅ Performance Summary:")
    dut._log.info(f"   Latency: {latency} cycles")
    dut._log.info(f"   Throughput: {throughput:.3f} items/cycle")
    dut._log.info(f"   Total: {total_cycles} cycles for {len(test_data)} items")
```

## Example: Complete Scalability Test

```python
@cocotb.test()
async def test_scalability(dut):
    """
    Test with 1x, 10x, 100x inputs automatically
    """
    
    # Setup
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Scalability tester
    tester = ScalabilityTester(dut)
    scale = tester.get_scale_factor()
    
    dut._log.info(f"🔬 Running at {scale}x scale")
    
    async def run_algorithm(dut, input_size):
        """Your algorithm implementation"""
        
        # Generate test data
        base_data = [1, 2, 3, 4, 5]
        test_data = DataGenerator.scale_data(base_data, scale)
        
        dut._log.info(f"Processing {len(test_data)} items...")
        
        # Process through your design
        for data in test_data:
            dut.input_valid.value = 1
            dut.input_data.value = data
            await RisingEdge(dut.clk)
        
        dut.input_valid.value = 0
        
        # Wait for completion
        timeout = input_size + 1000
        for _ in range(timeout):
            await RisingEdge(dut.clk)
            if dut.done.value == 1:
                break
        
        return dut.result.value
    
    # Run with automatic scaling
    base_size = 100
    result, cycles = await tester.test_with_scale(run_algorithm, base_size)
    
    # Report (CI parses this!)
    dut._log.info(f"✅ Scalability {scale}x:")
    dut._log.info(f"   Input: {base_size * scale} items")
    dut._log.info(f"   Cycles: {cycles}")
    dut._log.info(f"   Efficiency: {cycles / (base_size * scale):.2f} cycles/item")
```

## Viewing Results

### In GitHub Actions

1. Go to **Actions** tab
2. Click on your workflow run
3. Scroll down to **Summary**
4. See the **Performance Dashboard**

Example dashboard:

```
# 🎄 Advent of FPGA - Performance Dashboard

## 📊 Performance Summary

| Problem | Simulator | Latency (cycles) | Throughput | Status |
|---------|-----------|------------------|------------|--------|
| day01   | icarus    | 5                | 0.91       | ✅     |
| day01   | verilator | 5                | 0.91       | ✅     |
| day07   | icarus    | 12               | 1.25       | ✅     |

## 🚀 Scalability Results

| Problem | Simulator | 1x  | 10x  | 100x  | Scaling    |
|---------|-----------|-----|------|-------|------------|
| day01   | icarus    | 15  | 140  | -     | ✅ Good    |
| day07   | verilator | 50  | 520  | 5200  | 🌟 Excellent |
```

### Download Detailed Reports

Under **Artifacts**, download:
- `performance-dayXX-icarus` - JSON and markdown reports
- `performance-dayXX-verilator` - JSON and markdown reports
- `performance-dashboard` - Aggregate report

### In Pull Requests

CI automatically comments on PRs with performance metrics!

## Scaling Grades

CI automatically grades your scaling efficiency:

- **🌟 Excellent**: Sub-linear scaling (better than expected!)
- **✅ Good**: Near-linear with optimizations
- **⚠️ Linear**: Standard linear scaling
- **❌ Poor**: Worse than linear (exponential)

## Tips for Good Performance

### 1. Pipeline Your Design

```systemverilog
// Bad: Sequential
always_ff @(posedge clk) begin
    stage1 <= process1(input);
    stage2 <= process2(stage1);
    stage3 <= process3(stage2);
end

// Good: Pipelined
always_ff @(posedge clk) begin
    stage1 <= process1(input);
end
always_ff @(posedge clk) begin
    stage2 <= process2(stage1);
end
always_ff @(posedge clk) begin
    stage3 <= process3(stage2);
end
```

### 2. Parallelize When Possible

```systemverilog
// Process multiple items per cycle
logic [31:0] results [0:3];
always_comb begin
    for (int i = 0; i < 4; i++) begin
        results[i] = inputs[i] * coefficients[i];
    end
end
```

### 3. Minimize State Transitions

```systemverilog
// Fewer states = faster
typedef enum {IDLE, WORK, DONE} state_t;
// Better than: {IDLE, LOAD, COMPUTE1, COMPUTE2, STORE, DONE}
```

### 4. Use Efficient Data Structures

```systemverilog
// Use BRAM for large arrays
// Use registers for frequently accessed data
// Consider FIFOs for streaming
```

## What Jane Street Judges Look For

From the competition criteria:

1. **✅ Scalability** - Handle 10×, 100×, 1000× inputs
   - *CI tests this automatically!*

2. **✅ Performance** - Area/performance trade-offs
   - *CI measures latency and throughput!*

3. **✅ Architecture** - Exploit FPGA parallelism
   - *Document this in your README*

4. **✅ Documentation** - Explain your approach
   - *Use CI metrics in your docs*

## Adding Metrics to Your README

After CI runs, add metrics to your problem's README:

```markdown
## Performance

### Measured Metrics
- **Latency**: 5 cycles
- **Throughput**: 0.91 items/cycle
- **Clock frequency**: 100 MHz (target)

### Scalability
| Input Size | Cycles | Cycles/Item |
|------------|--------|-------------|
| 100 (1x)   | 150    | 1.50        |
| 1000 (10x) | 1400   | 1.40        |
| 10000(100x)| 14000  | 1.40        |

**Scaling**: ✅ Good - Sub-linear due to pipelining

### Optimizations
- 4-stage pipeline for throughput
- Parallel accumulation reduces latency
- BRAM usage: 2 blocks (512 words each)
```

## Troubleshooting

**Performance tests not running?**
- Make sure you have `test_performance` function
- Check that performance_utils is imported
- Look for errors in CI logs

**Scalability tests timing out?**
- Increase timeout in your test
- Optimize your algorithm
- CI has 600s limit for 100x tests

**Metrics not showing in dashboard?**
- Ensure you're using `monitor.report_*` functions
- Check log format: "Latency: 5 cycles"
- Verify tests ran (check CI logs)

## Summary

✅ **Automatic testing** - Push and CI handles it  
✅ **Performance metrics** - Latency, throughput measured  
✅ **Scalability** - 1x, 10x, 100x tested automatically  
✅ **Reports** - Dashboard + detailed JSON/markdown  
✅ **Competition ready** - Meets Jane Street criteria  

**Just write your tests using the utilities and push - CI does the rest!** 🚀
