"""
Tests for the remesh_file function.
"""

import pytest
import numpy as np
import pyinstantmeshes
import os


class TestRemeshFileBasic:
    """Test basic remesh_file functionality."""
    
    def test_remesh_file_basic(self, temp_obj_file, tmp_path):
        """Test remeshing from a file."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        assert isinstance(output_vertices, np.ndarray)
        assert isinstance(output_faces, np.ndarray)
        assert output_vertices.dtype == np.float32
        assert output_faces.dtype == np.int32
        assert output_vertices.shape[1] == 3
        assert output_faces.shape[1] in [3, 4]
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
        
        # Check that output file was created
        assert os.path.exists(output_path)
    
    def test_remesh_file_creates_output(self, temp_obj_file, tmp_path):
        """Test that remesh_file creates the output file."""
        output_path = str(tmp_path / "output_mesh.obj")
        
        pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    
    def test_remesh_file_returns_tuple(self, temp_obj_file, tmp_path):
        """Test that remesh_file returns a tuple."""
        output_path = str(tmp_path / "output.obj")
        
        result = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestRemeshFileParameters:
    """Test remesh_file with different parameters."""
    
    def test_remesh_file_with_target_vertex_count(self, temp_obj_file, tmp_path):
        """Test remesh_file with specific target vertex count."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=30, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_file_with_pure_quad(self, temp_obj_file, tmp_path):
        """Test remesh_file with pure quad output."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, pure_quad=True, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
        assert output_faces.shape[1] == 4
    
    def test_remesh_file_deterministic(self, temp_obj_file, tmp_path):
        """Test that deterministic mode produces consistent results."""
        output_path1 = str(tmp_path / "output1.obj")
        output_path2 = str(tmp_path / "output2.obj")
        
        output1_v, output1_f = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path1, target_vertex_count=50, deterministic=True
        )
        output2_v, output2_f = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path2, target_vertex_count=50, deterministic=True
        )
        
        # In deterministic mode, results should be identical
        np.testing.assert_array_equal(output1_v, output2_v)
        np.testing.assert_array_equal(output1_f, output2_f)


class TestRemeshFileValidation:
    """Test input validation for remesh_file function."""
    
    def test_remesh_file_nonexistent_input(self, tmp_path):
        """Test remesh_file with non-existent input file."""
        input_path = str(tmp_path / "nonexistent.obj")
        output_path = str(tmp_path / "output.obj")
        
        # Should raise an error when input file doesn't exist
        with pytest.raises(Exception):  # Could be RuntimeError or other exception
            pyinstantmeshes.remesh_file(input_path, output_path, target_vertex_count=50)


class TestRemeshFileOutput:
    """Test output characteristics of remesh_file function."""
    
    def test_remesh_file_output_types(self, temp_obj_file, tmp_path):
        """Test that output has correct types."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        assert output_vertices.dtype == np.float32
        assert output_faces.dtype == np.int32
    
    def test_remesh_file_output_shapes(self, temp_obj_file, tmp_path):
        """Test that output has correct shapes."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        assert output_vertices.ndim == 2
        assert output_vertices.shape[1] == 3
        assert output_faces.ndim == 2
        assert output_faces.shape[1] in [3, 4]
    
    def test_remesh_file_face_indices_valid(self, temp_obj_file, tmp_path):
        """Test that output face indices are valid."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        # All face indices should be non-negative and less than vertex count
        assert np.all(output_faces >= 0)
        assert np.all(output_faces < len(output_vertices))
    
    def test_remesh_file_vertices_finite(self, temp_obj_file, tmp_path):
        """Test that output vertices are finite numbers."""
        output_path = str(tmp_path / "output.obj")
        
        output_vertices, output_faces = pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        assert np.all(np.isfinite(output_vertices))
    
    def test_remesh_file_output_file_readable(self, temp_obj_file, tmp_path):
        """Test that the output file can be read back."""
        output_path = str(tmp_path / "output.obj")
        
        pyinstantmeshes.remesh_file(
            temp_obj_file, output_path, target_vertex_count=50, deterministic=True
        )
        
        # Try to read the output file
        with open(output_path, 'r') as f:
            content = f.read()
        
        assert len(content) > 0
        assert 'v ' in content  # Should have vertices
        assert 'f ' in content  # Should have faces
