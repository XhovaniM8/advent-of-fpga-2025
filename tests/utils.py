"""
Helper utilities for testing Hardcaml designs
"""
import subprocess
import os

def compile_hardcaml_to_verilog(ml_file, output_verilog, build_dir=None):
    """
    Compile a Hardcaml .ml file to Verilog
    
    Args:
        ml_file: Path to .ml file
        output_verilog: Output .v file path
        build_dir: Optional build directory
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # This is a placeholder - actual Hardcaml compilation depends on your setup
        # You might need to create a dune project or use ocamlfind directly
        cmd = [
            'opam', 'exec', '--',
            'ocamlfind', 'ocamlopt',
            '-package', 'hardcaml',
            '-linkpkg',
            ml_file,
            '-o', output_verilog.replace('.v', '')
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Compilation failed: {e}")
        return False

def run_verilator_lint(verilog_file):
    """
    Run Verilator lint on a Verilog file
    
    Returns:
        (success, output)
    """
    try:
        result = subprocess.run(
            ['verilator', '--lint-only', verilog_file],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "Verilator not found"

def simulate_verilog(verilog_file, test_data):
    """
    Simulate Verilog file with test data using Icarus Verilog
    
    Args:
        verilog_file: Path to .v file
        test_data: Test input data
    
    Returns:
        Simulation results
    """
    # This would use iverilog + vvp or cocotb
    # Implementation depends on your testbench structure
    pass
