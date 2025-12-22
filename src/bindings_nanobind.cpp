/*
    bindings_nanobind.cpp -- Python bindings for Instant Meshes using nanobind

    This file provides Python bindings for the Instant Meshes remeshing library
    using nanobind. It wraps the batch_process function to allow remeshing
    from Python using numpy arrays.
*/

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>

#include "common.h"
#include "batch.h"
#include "meshio.h"

#include <fstream>
#include <sstream>
#include <cstdlib>
#include <random>
#include <thread>

namespace nb = nanobind;
using namespace nb::literals;

// Define the global variable used by instant-meshes
int nprocs = -1;  // -1 means automatic thread count

// RAII helper for temporary file cleanup
class TempFile {
public:
    std::string path;
    
    explicit TempFile(const std::string& p) : path(p) {}
    
    ~TempFile() {
        if (!path.empty()) {
            std::remove(path.c_str());
        }
    }
    
    // Disable copy
    TempFile(const TempFile&) = delete;
    TempFile& operator=(const TempFile&) = delete;
};

// Helper function to get temporary directory
static std::string get_temp_dir() {
    // Try various environment variables for temp directory
    const char* tmpdir = std::getenv("TMPDIR");
    if (!tmpdir) tmpdir = std::getenv("TEMP");
    if (!tmpdir) tmpdir = std::getenv("TMP");
    if (!tmpdir) {
#ifdef _WIN32
        tmpdir = "C:\\Temp";
#else
        tmpdir = "/tmp";
#endif
    }
    return std::string(tmpdir);
}

// Helper function to generate unique temporary filename
static std::string generate_temp_filename(const std::string& prefix, const std::string& extension) {
    // Use random device for better uniqueness than timestamp alone
    static std::random_device rd;
    static std::mt19937_64 gen(rd());
    
    std::string temp_dir = get_temp_dir();
    
    // Combine thread ID, timestamp, and random number for uniqueness
    auto thread_id = std::hash<std::thread::id>{}(std::this_thread::get_id());
    auto timestamp = std::chrono::system_clock::now().time_since_epoch().count();
    auto random_num = gen();
    
    std::ostringstream oss;
    oss << temp_dir << "/" << prefix << "_" 
        << thread_id << "_" << timestamp << "_" << random_num << extension;
    
    return oss.str();
}

// Helper function to write mesh data to a temporary file
static void write_temp_mesh(const std::string& filename,
                           nb::ndarray<float, nb::shape<nb::any, 3>, nb::c_contig> vertices,
                           nb::ndarray<int, nb::shape<nb::any, nb::any>, nb::c_contig> faces) {
    size_t num_vertices = vertices.shape(0);
    size_t num_faces = faces.shape(0);
    size_t face_size = faces.shape(1);
    
    std::ofstream out(filename);
    if (!out) {
        throw std::runtime_error("Failed to open temporary file for writing: " + filename);
    }
    
    // Write as OBJ format
    out << "# Generated mesh for Instant Meshes processing\n";
    
    // Write vertices
    for (size_t i = 0; i < num_vertices; ++i) {
        out << "v " << vertices(i, 0) << " " << vertices(i, 1) << " " << vertices(i, 2) << "\n";
    }
    
    // Write faces (OBJ format is 1-indexed)
    for (size_t i = 0; i < num_faces; ++i) {
        out << "f";
        for (size_t j = 0; j < face_size; ++j) {
            out << " " << (faces(i, j) + 1);
        }
        out << "\n";
    }
    
    out.close();
}

// Helper function to read mesh data from a file
static std::tuple<nb::ndarray<nb::numpy, float, nb::shape<nb::any, 3>>, 
                  nb::ndarray<nb::numpy, int, nb::shape<nb::any, nb::any>>>
read_temp_mesh(const std::string& filename) {
    MatrixXu F;
    MatrixXf V, N;
    
    load_mesh_or_pointcloud(filename, F, V, N);
    
    // Convert Eigen matrices to numpy arrays
    size_t num_vertices = V.cols();
    size_t num_faces = F.cols();
    size_t vertex_dim = V.rows();
    size_t face_dim = F.rows();
    
    // Allocate numpy arrays
    float* vertices_data = new float[num_vertices * 3];
    int* faces_data = new int[num_faces * face_dim];
    
    // Copy vertex data
    for (size_t i = 0; i < num_vertices; ++i) {
        for (size_t j = 0; j < vertex_dim; ++j) {
            vertices_data[i * 3 + j] = V(j, i);
        }
    }
    
    // Copy face data
    for (size_t i = 0; i < num_faces; ++i) {
        for (size_t j = 0; j < face_dim; ++j) {
            faces_data[i * face_dim + j] = static_cast<int>(F(j, i));
        }
    }
    
    // Create ndarray objects with ownership transfer
    auto vertices = nb::ndarray<nb::numpy, float, nb::shape<nb::any, 3>>(
        vertices_data,
        {num_vertices, 3},
        nb::capsule(vertices_data, [](void* p) noexcept { delete[] (float*)p; })
    );
    
    auto faces = nb::ndarray<nb::numpy, int, nb::shape<nb::any, nb::any>>(
        faces_data,
        {num_faces, face_dim},
        nb::capsule(faces_data, [](void* p) noexcept { delete[] (int*)p; })
    );
    
    return std::make_tuple(vertices, faces);
}

// Python-friendly wrapper for batch_process
std::tuple<nb::ndarray<nb::numpy, float, nb::shape<nb::any, 3>>,
           nb::ndarray<nb::numpy, int, nb::shape<nb::any, nb::any>>>
remesh(nb::ndarray<float, nb::shape<nb::any, 3>, nb::c_contig> vertices,
       nb::ndarray<int, nb::shape<nb::any, nb::any>, nb::c_contig> faces,
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
    if (vertices.ndim() != 2 || vertices.shape(1) != 3) {
        throw std::runtime_error("Vertices must be a Nx3 array");
    }
    
    if (faces.ndim() != 2 || (faces.shape(1) != 3 && faces.shape(1) != 4)) {
        throw std::runtime_error("Faces must be a Nx3 or Nx4 array");
    }
    
    // Create temporary files with RAII cleanup
    TempFile input_file(generate_temp_filename("pyim_input", ".obj"));
    TempFile output_file(generate_temp_filename("pyim_output", ".obj"));
    
    // Write input mesh
    write_temp_mesh(input_file.path, vertices, faces);
    
    // Call batch_process
    batch_process(input_file.path, output_file.path,
                 rosy, posy, target_edge_length, 
                 target_face_count, target_vertex_count,
                 crease_angle, extrinsic, align_to_boundaries,
                 smooth_iterations, knn_points, pure_quad, deterministic);
    
    // Read output mesh (files will be auto-cleaned by TempFile destructors)
    return read_temp_mesh(output_file.path);
}

// Python-friendly wrapper for remeshing from file
std::tuple<nb::ndarray<nb::numpy, float, nb::shape<nb::any, 3>>,
           nb::ndarray<nb::numpy, int, nb::shape<nb::any, nb::any>>>
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

NB_MODULE(_pyinstantmeshes, m) {
    m.doc() = "Python bindings for Instant Meshes - fast automatic retopology";
    
    m.def("remesh", &remesh,
          "vertices"_a,
          "faces"_a,
          "target_vertex_count"_a = -1,
          "target_face_count"_a = -1,
          "target_edge_length"_a = -1.0f,
          "rosy"_a = 4,
          "posy"_a = 4,
          "crease_angle"_a = -1.0f,
          "extrinsic"_a = false,
          "align_to_boundaries"_a = false,
          "smooth_iterations"_a = 2,
          "knn_points"_a = 10,
          "pure_quad"_a = false,
          "deterministic"_a = false,
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
          "input_path"_a,
          "output_path"_a,
          "target_vertex_count"_a = -1,
          "target_face_count"_a = -1,
          "target_edge_length"_a = -1.0f,
          "rosy"_a = 4,
          "posy"_a = 4,
          "crease_angle"_a = -1.0f,
          "extrinsic"_a = false,
          "align_to_boundaries"_a = false,
          "smooth_iterations"_a = 2,
          "knn_points"_a = 10,
          "pure_quad"_a = false,
          "deterministic"_a = false,
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
