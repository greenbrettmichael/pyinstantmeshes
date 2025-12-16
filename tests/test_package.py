"""
Tests for the pyinstantmeshes module and package interface.
"""

import pytest
import numpy as np


def test_package_imports():
    """Test that package imports correctly and exposes expected API."""
    import pyinstantmeshes
    
    assert hasattr(pyinstantmeshes, 'remesh')
    assert hasattr(pyinstantmeshes, 'remesh_file')
    assert hasattr(pyinstantmeshes, '__version__')
    assert pyinstantmeshes.__version__ == "0.1.0"


def test_package_all():
    """Test that __all__ contains expected exports."""
    import pyinstantmeshes
    
    assert hasattr(pyinstantmeshes, '__all__')
    assert 'remesh' in pyinstantmeshes.__all__
    assert 'remesh_file' in pyinstantmeshes.__all__


def test_module_docstring():
    """Test that module has documentation."""
    import pyinstantmeshes
    
    assert pyinstantmeshes.__doc__ is not None
    assert len(pyinstantmeshes.__doc__) > 0
