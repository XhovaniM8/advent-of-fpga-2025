#!/bin/bash
# Quick setup script for new Hardcaml problems

set -e

if [ -z "$1" ]; then
    echo "Usage: ./new_hardcaml.sh <day_number>"
    echo "Example: ./new_hardcaml.sh 7"
    echo ""
    echo "This creates a Hardcaml project in problems/dayXX-hardcaml/"
    exit 1
fi

DAY=$(printf "%02d" $1)
DAY_DIR="problems/day${DAY}-hardcaml"

if [ -d "$DAY_DIR" ]; then
    echo "Error: $DAY_DIR already exists!"
    exit 1
fi

echo "Setting up Hardcaml project for Day ${DAY}..."

# Copy template
cp -r problems/hardcaml-template "$DAY_DIR"

# Update project names in all dune files
find "$DAY_DIR" -name "dune*" -type f -exec sed -i "s/advent_day_XX/advent_day_${DAY}/g" {} \;
find "$DAY_DIR" -name "*.ml" -type f -exec sed -i "s/Advent_day_XX/Advent_day_${DAY}/g" {} \;

# Update README
sed -i "s/Day XX/Day ${DAY}/g" "$DAY_DIR/README.md"

# Create input file placeholder
cat > "$DAY_DIR/input.txt" << EOF
# Paste your Advent of Code input here
# Get it from: https://adventofcode.com/2025/day/${1}/input
EOF

echo "✅ Hardcaml project for Day ${DAY} created at $DAY_DIR"
echo ""
echo "Next steps:"
echo "1. cd $DAY_DIR"
echo "2. Get input from: https://adventofcode.com/2025/day/${1}/input"
echo "3. Paste into: input.txt"
echo "4. Edit design: lib/design.ml"
echo "5. Edit tests: test/test_design.ml"
echo "6. Build: dune build"
echo "7. Test: dune test"
echo "8. Generate Verilog: dune exec ./bin/main.exe -- emit-verilog -o solution.v"
echo ""
echo "🎁 Bonus: Hardcaml solutions get extra credit!"
echo ""
echo "Happy coding! 🎄⚡"
