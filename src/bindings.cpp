/*
    bindings.cpp -- Python bindings for Instant Meshes

    This file provides Python bindings for the Instant Meshes remeshing library
    using pybind11. It wraps the batch_process function to allow remeshing
    from Python using numpy arrays.
*/

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "common.h"
#include "batch.h"
#include "meshio.h"

#include <fstream>
#include <sstream>

namespace py = pybind11;

// Helper function to write mesh data to a temporary file
static void write_temp_mesh(const std::string& filename,
                           py::array_t<float> vertices,
                           py::array_t<int> faces) {
    auto v = vertices.unchecked<2>();
    auto f = faces.unchecked<2>();
    
    std::ofstream out(filename);
    if (!out) {
        throw std::runtime_error("Failed to open temporary file for writing: " + filename);
    }
    
    // Write as OBJ format
    out << "# Generated mesh for Instant Meshes processing\n";
    
    // Write vertices
    for (py::ssize_t i = 0; i < v.shape(0); ++i) {
        out << "v " << v(i, 0) << " " << v(i, 1) << " " << v(i, 2) << "\n";
    }
    
    // Write faces (OBJ format is 1-indexed)
    for (py::ssize_t i = 0; i < f.shape(0); ++i) {
        out << "f";
        for (py::ssize_t j = 0; j < f.shape(1); ++j) {
            out << " " << (f(i, j) + 1);
        }
        out << "\n";
    }
    
    out.close();
}

// Helper function to read mesh data from a file
static std::tuple<py::array_t<float>, py::array_t<int>> 
read_temp_mesh(const std::string& filename) {
    MatrixXu F;
    MatrixXf V, N;
    
    load_mesh_or_pointcloud(filename, F, V, N);
    
    // Convert Eigen matrices to numpy arrays
    py::array_t<float> vertices({static_cast<py::ssize_t>(V.cols()), 
                                  static_cast<py::ssize_t>(V.rows())});
    auto v = vertices.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < V.cols(); ++i) {
        for (py::ssize_t j = 0; j < V.rows(); ++j) {
            v(i, j) = V(j, i);
        }
    }
    
    py::array_t<int> faces({static_cast<py::ssize_t>(F.cols()), 
                            static_cast<py::ssize_t>(F.rows())});
    auto f = faces.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < F.cols(); ++i) {
        for (py::ssize_t j = 0; j < F.rows(); ++j) {
            f(i, j) = static_cast<int>(F(j, i));
        }
    }
    
    return std::make_tuple(vertices, faces);
}

// Python-friendly wrapper for batch_process
std::tuple<py::array_t<float>, py::array_t<int>>
remesh(py::array_t<float> vertices,
       py::array_t<int> faces,
       int target_vertex_count = -1,
       int target_face_count = -1,
       float target_edge_length = -1.0f,
       int rosy = 4,
       int posy = 4,
       float crease_angle = -1.0f,
       bool extrinsic = false,
       bool align_to_boundaries = false,
       int smooth_iterations = 2,
       int knn_points = 10,
       bool pure_quad = false,
       bool deterministic = false) {
    
    // Validate input
    py::buffer_info v_info = vertices.request();
    py::buffer_info f_info = faces.request();
    
    if (v_info.ndim != 2 || v_info.shape[1] != 3) {
        throw std::runtime_error("Vertices must be a Nx3 array");
    }
    
    if (f_info.ndim != 2 || (f_info.shape[1] != 3 && f_info.shape[1] != 4)) {
        throw std::runtime_error("Faces must be a Nx3 or Nx4 array");
    }
    
    // Create temporary files
    std::string input_file = "/tmp/pyim_input_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()) + ".obj";
    std::string output_file = "/tmp/pyim_output_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()) + ".obj";
    
    try {
        // Write input mesh
        write_temp_mesh(input_file, vertices, faces);
        
        // Call batch_process
        batch_process(input_file, output_file,
                     rosy, posy, target_edge_length, 
                     target_face_count, target_vertex_count,
                     crease_angle, extrinsic, align_to_boundaries,
                     smooth_iterations, knn_points, pure_quad, deterministic);
        
        // Read output mesh
        auto result = read_temp_mesh(output_file);
        
        // Clean up temporary files
        std::remove(input_file.c_str());
        std::remove(output_file.c_str());
        
        return result;
    } catch (...) {
        // Clean up temporary files on error
        std::remove(input_file.c_str());
        std::remove(output_file.c_str());
        throw;
    }
}

// Python-friendly wrapper for remeshing from file
std::tuple<py::array_t<float>, py::array_t<int>>
remesh_file(const std::string& input_path,
           const std::string& output_path,
           int target_vertex_count = -1,
           int target_face_count = -1,
           float target_edge_length = -1.0f,
           int rosy = 4,
           int posy = 4,
           float crease_angle = -1.0f,
           bool extrinsic = false,
           bool align_to_boundaries = false,
           int smooth_iterations = 2,
           int knn_points = 10,
           bool pure_quad = false,
           bool deterministic = false) {
    
    // Call batch_process
    batch_process(input_path, output_path,
                 rosy, posy, target_edge_length, 
                 target_face_count, target_vertex_count,
                 crease_angle, extrinsic, align_to_boundaries,
                 smooth_iterations, knn_points, pure_quad, deterministic);
    
    // Read output mesh
    return read_temp_mesh(output_path);
}

PYBIND11_MODULE(_pyinstantmeshes, m) {
    m.doc() = "Python bindings for Instant Meshes - fast automatic retopology";
    
    m.def("remesh", &remesh,
          py::arg("vertices"),
          py::arg("faces"),
          py::arg("target_vertex_count") = -1,
          py::arg("target_face_count") = -1,
          py::arg("target_edge_length") = -1.0f,
          py::arg("rosy") = 4,
          py::arg("posy") = 4,
          py::arg("crease_angle") = -1.0f,
          py::arg("extrinsic") = false,
          py::arg("align_to_boundaries") = false,
          py::arg("smooth_iterations") = 2,
          py::arg("knn_points") = 10,
          py::arg("pure_quad") = false,
          py::arg("deterministic") = false,
          R"pbdoc(
        Remesh a triangular or quad mesh for better topology.
        
        Parameters
        ----------
        vertices : numpy.ndarray
            Input vertex positions as Nx3 float array
        faces : numpy.ndarray
            Input face indices as Nx3 or Nx4 int array
        target_vertex_count : int, optional
            Desired vertex count (default: -1, uses 1/16 of input)
        target_face_count : int, optional
            Desired face count (default: -1)
        target_edge_length : float, optional
            Desired edge length (default: -1)
        rosy : int, optional
            Orientation symmetry type (default: 4)
        posy : int, optional
            Position symmetry type (default: 4)
        crease_angle : float, optional
            Crease angle threshold in degrees (default: -1, disabled)
        extrinsic : bool, optional
            Use extrinsic mode (default: False)
        align_to_boundaries : bool, optional
            Align field to boundaries (default: False)
        smooth_iterations : int, optional
            Number of smoothing iterations (default: 2)
        knn_points : int, optional
            kNN points for point cloud processing (default: 10)
        pure_quad : bool, optional
            Generate pure quad mesh (default: False)
        deterministic : bool, optional
            Use deterministic mode (default: False)
        
        Returns
        -------
        vertices : numpy.ndarray
            Output vertex positions as Nx3 float array
        faces : numpy.ndarray
            Output face indices as Nx3 or Nx4 int array
    )pbdoc");
    
    m.def("remesh_file", &remesh_file,
          py::arg("input_path"),
          py::arg("output_path"),
          py::arg("target_vertex_count") = -1,
          py::arg("target_face_count") = -1,
          py::arg("target_edge_length") = -1.0f,
          py::arg("rosy") = 4,
          py::arg("posy") = 4,
          py::arg("crease_angle") = -1.0f,
          py::arg("extrinsic") = false,
          py::arg("align_to_boundaries") = false,
          py::arg("smooth_iterations") = 2,
          py::arg("knn_points") = 10,
          py::arg("pure_quad") = false,
          py::arg("deterministic") = false,
          R"pbdoc(
        Remesh a mesh from an input file and save to an output file.
        
        Parameters
        ----------
        input_path : str
            Path to input mesh file (OBJ, PLY, etc.)
        output_path : str
            Path to output mesh file (OBJ)
        target_vertex_count : int, optional
            Desired vertex count (default: -1, uses 1/16 of input)
        target_face_count : int, optional
            Desired face count (default: -1)
        target_edge_length : float, optional
            Desired edge length (default: -1)
        rosy : int, optional
            Orientation symmetry type (default: 4)
        posy : int, optional
            Position symmetry type (default: 4)
        crease_angle : float, optional
            Crease angle threshold in degrees (default: -1, disabled)
        extrinsic : bool, optional
            Use extrinsic mode (default: False)
        align_to_boundaries : bool, optional
            Align field to boundaries (default: False)
        smooth_iterations : int, optional
            Number of smoothing iterations (default: 2)
        knn_points : int, optional
            kNN points for point cloud processing (default: 10)
        pure_quad : bool, optional
            Generate pure quad mesh (default: False)
        deterministic : bool, optional
            Use deterministic mode (default: False)
        
        Returns
        -------
        vertices : numpy.ndarray
            Output vertex positions as Nx3 float array
        faces : numpy.ndarray
            Output face indices as Nx3 or Nx4 int array
    )pbdoc");
}
