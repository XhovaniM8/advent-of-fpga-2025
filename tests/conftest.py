"""
Common pytest fixtures for Hardcaml/Verilog testing
"""
import pytest
import os

@pytest.fixture
def designs_dir():
    """Path to designs directory"""
    return os.path.join(os.path.dirname(__file__), '..', 'designs')

@pytest.fixture
def build_dir(tmp_path):
    """Temporary build directory"""
    build = tmp_path / "build"
    build.mkdir()
    return build
