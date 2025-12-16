"""
Simple example of using pyinstantmeshes to remesh a basic tetrahedron.
"""

import numpy as np
import pyinstantmeshes

def create_tetrahedron():
    """Create a simple tetrahedron mesh."""
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

def main():
    print("Creating tetrahedron...")
    vertices, faces = create_tetrahedron()
    
    print(f"Input mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    print("\nRemeshing with target vertex count of 50...")
    try:
        output_vertices, output_faces = pyinstantmeshes.remesh(
            vertices,
            faces,
            target_vertex_count=50,
            deterministic=True
        )
        
        print(f"Output mesh: {len(output_vertices)} vertices, {len(output_faces)} faces")
        print("\nOutput vertex statistics:")
        print(f"  Min: {output_vertices.min(axis=0)}")
        print(f"  Max: {output_vertices.max(axis=0)}")
        print(f"  Mean: {output_vertices.mean(axis=0)}")
        
    except Exception as e:
        print(f"Error during remeshing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
