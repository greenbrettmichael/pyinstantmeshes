"""
Shared test fixtures and utilities for pyinstantmeshes tests.
"""

import numpy as np
import pytest


@pytest.fixture
def simple_tetrahedron():
    """Create a simple tetrahedron mesh for testing."""
    vertices = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.5, 0.866, 0.0],
        [0.5, 0.433, 0.816]
    ], dtype=np.float32)
    
    faces = np.array([
        [0, 1, 2],
        [0, 1, 3],
        [0, 2, 3],
        [1, 2, 3]
    ], dtype=np.int32)
    
    return vertices, faces


@pytest.fixture
def simple_cube():
    """Create a simple cube mesh for testing."""
    vertices = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 1.0]
    ], dtype=np.float32)
    
    faces = np.array([
        # Bottom
        [0, 1, 2], [0, 2, 3],
        # Top
        [4, 6, 5], [4, 7, 6],
        # Front
        [0, 5, 1], [0, 4, 5],
        # Back
        [2, 7, 3], [2, 6, 7],
        # Left
        [0, 7, 4], [0, 3, 7],
        # Right
        [1, 6, 2], [1, 5, 6]
    ], dtype=np.int32)
    
    return vertices, faces


@pytest.fixture
def quad_mesh():
    """Create a simple quad mesh for testing."""
    vertices = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [2.0, 0.0, 0.0],
        [2.0, 1.0, 0.0]
    ], dtype=np.float32)
    
    faces = np.array([
        [0, 1, 2, 3],
        [1, 4, 5, 2]
    ], dtype=np.int32)
    
    return vertices, faces


@pytest.fixture
def temp_obj_file(tmp_path):
    """Create a temporary OBJ file for testing."""
    obj_file = tmp_path / "test_mesh.obj"
    
    # Write a simple tetrahedron
    obj_content = """# Test mesh
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.5 0.866 0.0
v 0.5 0.433 0.816
f 1 2 3
f 1 2 4
f 1 3 4
f 2 3 4
"""
    obj_file.write_text(obj_content)
    return str(obj_file)
