#!/bin/bash
# Quick setup script for new Advent of FPGA problems

set -e

if [ -z "$1" ]; then
    echo "Usage: ./new_day.sh <day_number>"
    echo "Example: ./new_day.sh 1"
    exit 1
fi

DAY=$(printf "%02d" $1)
DAY_DIR="problems/day${DAY}"

if [ -d "$DAY_DIR" ]; then
    echo "Error: $DAY_DIR already exists!"
    exit 1
fi

echo "Setting up Day ${DAY}..."

# Copy template
cp -r problems/template "$DAY_DIR"

# Update README with day number
sed -i "s/Day XX/Day ${DAY}/g" "$DAY_DIR/README.md"
sed -i "s/day\/XX/day\/${DAY}/g" "$DAY_DIR/README.md"

# Create input file placeholder
cat > "$DAY_DIR/input.txt" << EOF
# Paste your Advent of Code input here
# Get it from: https://adventofcode.com/2025/day/${1}/input
EOF

echo "✅ Day ${DAY} created at $DAY_DIR"
echo ""
echo "Next steps:"
echo "1. Get your input: https://adventofcode.com/2025/day/${1}/input"
echo "2. Paste it into: $DAY_DIR/input.txt"
echo "3. Implement RTL: $DAY_DIR/rtl/solution.sv"
echo "4. Write tests: $DAY_DIR/testbench/test_solution.py"
echo "5. Run tests: cd $DAY_DIR/testbench && make"
echo ""
echo "Happy coding! 🎄⚡"
