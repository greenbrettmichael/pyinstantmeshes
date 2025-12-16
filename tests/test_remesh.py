"""
Tests for the remesh function.
"""

import pytest
import numpy as np
import pyinstantmeshes


class TestRemeshBasic:
    """Test basic remesh functionality."""
    
    def test_remesh_tetrahedron(self, simple_tetrahedron):
        """Test remeshing a simple tetrahedron."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        assert isinstance(output_vertices, np.ndarray)
        assert isinstance(output_faces, np.ndarray)
        assert output_vertices.dtype == np.float32
        assert output_faces.dtype == np.int32
        assert output_vertices.shape[1] == 3
        assert output_faces.shape[1] in [3, 4]  # Can be triangles or quads
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_cube(self, simple_cube):
        """Test remeshing a simple cube."""
        vertices, faces = simple_cube
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=100, deterministic=True
        )
        
        assert isinstance(output_vertices, np.ndarray)
        assert isinstance(output_faces, np.ndarray)
        assert output_vertices.shape[1] == 3
        assert output_faces.shape[1] in [3, 4]
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_quad_mesh(self, quad_mesh):
        """Test remeshing a quad mesh."""
        vertices, faces = quad_mesh
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        assert isinstance(output_vertices, np.ndarray)
        assert isinstance(output_faces, np.ndarray)
        assert output_vertices.shape[1] == 3
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_returns_tuple(self, simple_tetrahedron):
        """Test that remesh returns a tuple of two arrays."""
        vertices, faces = simple_tetrahedron
        
        result = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestRemeshParameters:
    """Test remesh with different parameters."""
    
    def test_remesh_with_target_vertex_count(self, simple_tetrahedron):
        """Test remesh with specific target vertex count."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=20, deterministic=True
        )
        
        # Output should have approximately the target vertex count
        # (may not be exact due to algorithm constraints)
        assert len(output_vertices) > 0
        assert len(output_vertices) <= 100  # Should be reasonable
    
    def test_remesh_with_target_face_count(self, simple_tetrahedron):
        """Test remesh with target face count."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_face_count=20, deterministic=True
        )
        
        assert len(output_faces) > 0
    
    def test_remesh_with_target_edge_length(self, simple_cube):
        """Test remesh with target edge length."""
        vertices, faces = simple_cube
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_edge_length=0.2, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_with_rosy_6(self, simple_tetrahedron):
        """Test remesh with rosy=6."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, rosy=6, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_with_posy_3(self, simple_tetrahedron):
        """Test remesh with posy=3 for triangles."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, posy=3, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
        assert output_faces.shape[1] == 3  # Should produce triangles
    
    def test_remesh_with_crease_angle(self, simple_cube):
        """Test remesh with crease angle."""
        vertices, faces = simple_cube
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, crease_angle=30.0, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_extrinsic_mode(self, simple_tetrahedron):
        """Test remesh with extrinsic mode."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, extrinsic=True, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_align_to_boundaries(self, simple_cube):
        """Test remesh with align to boundaries."""
        vertices, faces = simple_cube
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, align_to_boundaries=True, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_smooth_iterations(self, simple_tetrahedron):
        """Test remesh with different smooth iterations."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, smooth_iterations=5, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
    
    def test_remesh_pure_quad(self, simple_cube):
        """Test remesh with pure quad output."""
        vertices, faces = simple_cube
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, pure_quad=True, deterministic=True
        )
        
        assert len(output_vertices) > 0
        assert len(output_faces) > 0
        # In pure quad mode, all faces should be quads
        assert output_faces.shape[1] == 4
    
    def test_remesh_deterministic(self, simple_tetrahedron):
        """Test that deterministic mode produces consistent results."""
        vertices, faces = simple_tetrahedron
        
        output1_v, output1_f = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        output2_v, output2_f = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        # In deterministic mode, results should be identical
        np.testing.assert_array_equal(output1_v, output2_v)
        np.testing.assert_array_equal(output1_f, output2_f)


class TestRemeshValidation:
    """Test input validation for remesh function."""
    
    def test_remesh_invalid_vertices_shape(self):
        """Test remesh with invalid vertices shape."""
        vertices = np.array([[0, 0], [1, 0]], dtype=np.float32)  # Wrong shape
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        with pytest.raises(RuntimeError, match="Vertices must be a Nx3 array"):
            pyinstantmeshes.remesh(vertices, faces)
    
    def test_remesh_invalid_vertices_1d(self):
        """Test remesh with 1D vertices array."""
        vertices = np.array([0, 0, 0, 1, 0, 0], dtype=np.float32)  # 1D
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        with pytest.raises(RuntimeError, match="Vertices must be a Nx3 array"):
            pyinstantmeshes.remesh(vertices, faces)
    
    def test_remesh_invalid_faces_shape(self):
        """Test remesh with invalid faces shape."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1]], dtype=np.int32)  # Wrong shape (not 3 or 4)
        
        with pytest.raises(RuntimeError, match="Faces must be a Nx3 or Nx4 array"):
            pyinstantmeshes.remesh(vertices, faces)
    
    def test_remesh_invalid_faces_1d(self):
        """Test remesh with 1D faces array."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([0, 1, 2], dtype=np.int32)  # 1D
        
        with pytest.raises(RuntimeError, match="Faces must be a Nx3 or Nx4 array"):
            pyinstantmeshes.remesh(vertices, faces)


class TestRemeshOutput:
    """Test output characteristics of remesh function."""
    
    def test_remesh_output_types(self, simple_tetrahedron):
        """Test that output has correct types."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        assert output_vertices.dtype == np.float32
        assert output_faces.dtype == np.int32
    
    def test_remesh_output_shapes(self, simple_tetrahedron):
        """Test that output has correct shapes."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        assert output_vertices.ndim == 2
        assert output_vertices.shape[1] == 3
        assert output_faces.ndim == 2
        assert output_faces.shape[1] in [3, 4]
    
    def test_remesh_face_indices_valid(self, simple_tetrahedron):
        """Test that output face indices are valid."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        # All face indices should be non-negative and less than vertex count
        assert np.all(output_faces >= 0)
        assert np.all(output_faces < len(output_vertices))
    
    def test_remesh_vertices_finite(self, simple_tetrahedron):
        """Test that output vertices are finite numbers."""
        vertices, faces = simple_tetrahedron
        
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices, faces, target_vertex_count=50, deterministic=True
        )
        
        assert np.all(np.isfinite(output_vertices))
