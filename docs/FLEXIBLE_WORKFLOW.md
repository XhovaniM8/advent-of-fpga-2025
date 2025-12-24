# Flexible Workflow: Pick Your Problems! 🎯

**You don't need to do all 25 days!** The competition lets you choose:
- As few as **1 puzzle** (minimum)
- As many as **25 puzzles** (all of them!)
- Any combination you want

## Quick Strategy Guide

### Which Problems to Pick?

**Criteria to Consider:**

1. **Interesting Algorithms**
   - String parsing? Graph algorithms? Math puzzles?
   - Pick ones that excite you!

2. **Hardware Suitability**
   - Some AoC problems parallelize well (⭐ great for FPGAs)
   - Some are inherently sequential (⚠️ harder to optimize)

3. **Your Strengths**
   - Good at SystemVerilog? Stick with that!
   - Want to learn Hardcaml? Try a simpler problem first

4. **Time Available**
   - Each problem takes 4-20 hours depending on complexity
   - Be realistic about your deadline (Jan 16, 2026)

### Recommended Approach

```
Week 1: Browse AoC 2025, pick 3-5 interesting problems
Week 2: Implement 1-2 in SystemVerilog (get comfortable)
Week 3: Try 1 in Hardcaml (bonus points!)
Week 4: Polish documentation, add more if time allows
```

## Setup for "Cherry Picking" Problems

### Option 1: SystemVerilog Problems

```bash
# Pick Day 7 (for example)
./new_day.sh 7

cd problems/day07
# Get input from adventofcode.com/2025/day/7/input
# Paste into input.txt

# Work on it
vim rtl/solution.sv
vim testbench/test_solution.py

# Test
cd testbench && make
```

### Option 2: Hardcaml Problems

```bash
# Pick Day 12 for Hardcaml
cp -r problems/hardcaml-template problems/day12-hardcaml

cd problems/day12-hardcaml

# Update names in dune files
sed -i 's/day_XX/day_12/g' dune-project lib/dune bin/dune test/dune

# Work on it
vim lib/design.ml
vim test/test_design.ml

# Test
dune build
dune test

# Generate Verilog
dune exec ./bin/main.exe -- emit-verilog -o solution.v
```

### Option 3: Mix Both!

Do some in SystemVerilog, some in Hardcaml:

```
problems/
├── day03/              # SystemVerilog
├── day07-hardcaml/     # Hardcaml (bonus!)
├── day11/              # SystemVerilog
├── day15-hardcaml/     # Hardcaml (bonus!)
└── day23/              # SystemVerilog
```

CI automatically detects and tests all of them!

## Working on Multiple Problems

### Recommended Git Workflow

```bash
# Each problem gets its own branch
git checkout -b day07
./new_day.sh 7
# Work on Day 7
git add problems/day07
git commit -m "Add Day 7: [puzzle name]"
git push origin day07

# Start another problem
git checkout main
git checkout -b day12
# Work on Day 12
```

### OR: Work on main branch

```bash
# If you prefer simpler workflow
./new_day.sh 7
./new_day.sh 12
./new_day.sh 15

# Work on any of them
# Commit whenever ready
git add .
git commit -m "Progress on days 7, 12, 15"
git push
```

## Progress Tracking

### Update Main README

Edit `README.md` to track your progress:

```markdown
## 🏆 Completed Solutions

| Day | Language | Status | Highlights |
|-----|----------|--------|------------|
| 03  | SV       | ✅     | Pipeline implementation |
| 07  | Hardcaml | ✅     | Parallel tree reduction |
| 12  | SV       | 🚧     | Work in progress |
| 15  | Hardcaml | ✅     | State machine |
```

### Mark as WIP (Work in Progress)

In each problem's README:

```markdown
# Day 12: [Problem Name]

**Status:** 🚧 Work in Progress

**Completed:**
- [x] Part 1
- [ ] Part 2 (in progress)

**TODO:**
- [ ] Optimize for throughput
- [ ] Add performance tests
```

## Time Management Tips

### Start Small, Grow Later

```bash
# Week 1: Get ONE working
./new_day.sh 1
# Make it work, document it, commit it
# ✅ You now have a submittable solution!

# Week 2: Add more
./new_day.sh 5
./new_day.sh 8

# Week 3: Try Hardcaml
cp -r problems/hardcaml-template problems/day10-hardcaml

# Week 4: Polish and optimize
```

### Prioritization Matrix

| Problem Complexity | Your Interest | Priority |
|-------------------|---------------|----------|
| Easy + High       | ⭐⭐⭐⭐⭐     | DO FIRST |
| Medium + High     | ⭐⭐⭐⭐       | DO SECOND|
| Hard + High       | ⭐⭐⭐         | DO IF TIME|
| Easy + Low        | ⭐⭐           | SKIP     |

## Example Strategies

### Strategy A: "Quality over Quantity"

- Pick 2-3 interesting problems
- Implement in **both** SystemVerilog AND Hardcaml
- Extensive optimization and documentation
- Multiple architecture explorations

### Strategy B: "Breadth"

- Pick 8-10 diverse problems
- All in SystemVerilog (faster development)
- Good documentation
- Focus on creativity across different problem types

### Strategy C: "Hardcaml Focus"

- Pick 3-4 problems
- All in Hardcaml (maximum bonus points!)
- Showcase language features
- Compare with Verilog approach

### Strategy D: "The Completionist"

- Do all 25 days!
- Mix of languages
- Not necessary but impressive

## Working Incrementally

### Day-by-Day Workflow

**Day N drops on AoC:**

```bash
# Morning: Read problem
# - Is it interesting? 
# - Does it map well to hardware?

# If YES:
./new_day.sh N

# Afternoon: Prototype algorithm
# - Write Python/pseudocode first
# - Understand the algorithm

# Evening: Start HDL implementation
# - Create basic structure
# - Get I/O working

# Next day: Complete and test
# - Finish implementation
# - Write tests
# - Document

# Commit!
git add problems/dayN
git commit -m "Complete Day N"
git push
```

### Batched Workflow

**Wait until all 25 drop, then:**

```bash
# Week 1: Survey and select
# - Read all problems
# - Pick your favorites
# - Create directories for chosen ones

./new_day.sh 3
./new_day.sh 7
./new_day.sh 12
./new_day.sh 18
./new_day.sh 23

# Week 2-3: Implement
# - Work on easiest first
# - Build momentum

# Week 4: Polish
# - Documentation
# - Optimization
# - Final testing
```

## Multi-Language Strategy

### Systematic Comparison

Pick ONE problem, implement in multiple languages:

```
problems/
├── day07/              # SystemVerilog version
└── day07-hardcaml/     # Hardcaml version
```

In your documentation, compare:
- Code size
- Development time
- Resource usage
- Design elegance

### Language Learning Path

1. **Start familiar**: Do first 2-3 in SystemVerilog
2. **Try Hardcaml**: Pick a simple problem
3. **Get comfortable**: Do more in Hardcaml
4. **Mix freely**: Use whichever fits the problem

## CI/CD for Selected Problems

The CI automatically:

**For SystemVerilog:**
- Finds all `problems/dayXX/testbench/Makefile`
- Runs tests with Icarus and Verilator
- Uploads waveforms on failure

**For Hardcaml:**
- Finds all `problems/*/dune-project`
- Builds with dune
- Runs tests
- Generates Verilog
- Verifies with Verilator

**You don't configure anything!** Just:
1. Create the problem directory
2. Push to GitHub
3. CI handles the rest

## Submission Checklist

Before January 16, 2026, ensure **each problem** you submit has:

```bash
problems/dayXX/
├── README.md           # ✅ Explains approach
├── rtl/ or lib/        # ✅ Your code
├── testbench/ or test/ # ✅ Tests that pass
└── input.txt           # ✅ Your puzzle input (optional)
```

Final submission:
- [ ] All code is open source (MIT license)
- [ ] Each solution documented
- [ ] All tests passing (check CI)
- [ ] Can synthesize (at least one)
- [ ] Can explain all designs

## Quick Commands Reference

```bash
# Create new SystemVerilog problem
./new_day.sh 7

# Create new Hardcaml problem  
cp -r problems/hardcaml-template problems/day12-hardcaml
cd problems/day12-hardcaml
# Update dune files

# Test SystemVerilog
cd problems/day07/testbench && make

# Test Hardcaml
cd problems/day12-hardcaml && dune test

# Check CI status
# Visit: github.com/YOUR_USERNAME/advent-of-fpga-2025/actions

# Count completed problems
ls problems/ | grep -E "day[0-9]+" | wc -l
```

## Remember: It's About Creativity!

Jane Street judges on:
- ✨ **Creativity** - Novel approaches
- 🎨 **Design** - Clean architecture
- 📊 **Optimization** - Performance/area trade-offs
- 📝 **Documentation** - Clear explanations

**Not** on:
- ❌ Number of solutions (more ≠ better)
- ❌ Perfect optimization
- ❌ Using every feature

### Focus On

- Pick problems that inspire you
- Explore interesting hardware architectures
- Document your thought process
- Have fun!

---

**You're in control! Pick your problems and start coding! 🎄⚡**
