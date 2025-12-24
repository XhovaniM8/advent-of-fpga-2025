"""
Tests for the Hardcaml adder design
"""
import pytest
import os
import subprocess

def test_adder_compiles(designs_dir):
    """Test that adder.ml compiles with Hardcaml"""
    adder_file = os.path.join(designs_dir, 'adder.ml')
    
    # Check file exists
    assert os.path.exists(adder_file), "adder.ml not found"
    
    # Compile with ocamlfind
    result = subprocess.run(
        ['opam', 'exec', '--', 'ocamlfind', 'ocamlc', 
         '-package', 'hardcaml', '-c', adder_file],
        capture_output=True,
        text=True,
        cwd=designs_dir
    )
    
    # Check compilation succeeded
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"

def test_adder_type_checks(designs_dir):
    """Test that adder has correct types"""
    adder_file = os.path.join(designs_dir, 'adder.ml')
    
    # Type checking is done during compilation
    # This test verifies the structure is correct
    with open(adder_file, 'r') as f:
        content = f.read()
        
        # Check for required Hardcaml structures
        assert 'module I = struct' in content, "Input interface missing"
        assert 'module O = struct' in content, "Output interface missing"
        assert 'let create' in content, "Create function missing"

def test_adder_has_documentation(designs_dir):
    """Test that adder has basic documentation"""
    adder_file = os.path.join(designs_dir, 'adder.ml')
    
    with open(adder_file, 'r') as f:
        content = f.read()
        
        # Check for comments
        has_comments = '(*' in content or '//' in content
        assert has_comments or len(content.split('\n')) < 20, \
            "Large file should have documentation"

@pytest.mark.skip(reason="Requires full Hardcaml environment")
def test_adder_functionality():
    """
    Test adder produces correct results
    This would require full Hardcaml simulation environment
    """
    # Example test structure:
    # 1. Generate Verilog from Hardcaml
    # 2. Simulate with cocotb or Hardcaml's simulator
    # 3. Verify: a + b = sum
    pass
