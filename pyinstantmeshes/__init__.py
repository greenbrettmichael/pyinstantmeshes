"""
pyinstantmeshes - Python bindings for Instant Meshes

This package provides a Python interface to the Instant Meshes library
for automatic retopology and remeshing of 3D meshes.

Example:
    >>> import pyinstantmeshes
    >>> import numpy as np
    >>> 
    >>> # Load or create mesh data
    >>> vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    >>> faces = np.array([[0, 1, 2]], dtype=np.int32)
    >>> 
    >>> # Remesh with target vertex count
    >>> new_vertices, new_faces = pyinstantmeshes.remesh(
    ...     vertices, faces, target_vertex_count=100
    ... )
"""

from ._pyinstantmeshes import remesh, remesh_file

__version__ = "0.1.0"
__all__ = ["remesh", "remesh_file"]
