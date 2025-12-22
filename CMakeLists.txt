cmake_minimum_required(VERSION 3.15...3.27)
project(pyinstantmeshes LANGUAGES CXX C)

# Option to choose binding library
option(USE_NANOBIND "Use nanobind instead of pybind11" OFF)

# Set C++17 standard (required for nanobind, compatible with pybind11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Find the appropriate binding library
if(USE_NANOBIND)
  message(STATUS "Using nanobind for Python bindings")
  find_package(nanobind CONFIG REQUIRED)
else()
  message(STATUS "Using pybind11 for Python bindings")
  find_package(pybind11 CONFIG REQUIRED)
endif()

# Set build type to Release if not specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
endif()

# Sanitize build environment for static build with C++17
if(MSVC)
  add_definitions(/D "_CRT_SECURE_NO_WARNINGS")
  add_definitions(/D "__TBB_NO_IMPLICIT_LINKAGE")
  # Parallel build on MSVC
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MP")
  
  if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /arch:SSE2")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /DEIGEN_DONT_ALIGN")
  endif()
  
  # Static build
  set(CompilerFlags
        CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
        CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO
        CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
        CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO)
  foreach(CompilerFlag ${CompilerFlags})
    string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")
  endforeach()
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++17")
  # Fix for newer GCC with old TBB
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
endif()

# Build TBB
set(TBB_BUILD_STATIC ON CACHE BOOL " " FORCE)
set(TBB_BUILD_SHARED OFF CACHE BOOL " " FORCE)
set(TBB_BUILD_TBBMALLOC OFF CACHE BOOL " " FORCE)
set(TBB_BUILD_TBBMALLOC_PROXY OFF CACHE BOOL " " FORCE)
set(TBB_BUILD_TESTS OFF CACHE BOOL " " FORCE)

# Fix for older TBB with newer compilers  
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL "11.0")
  add_compile_options(-fpermissive)
endif()

# Build TBB with position-independent code for use in shared library
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Add instant-meshes TBB dependency only (we don't need NanoGUI for Python bindings)
add_subdirectory(external/instant-meshes/ext/tbb EXCLUDE_FROM_ALL)

# Include directories
include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/src
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/nanogui/ext/eigen
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/tbb/include
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/dset
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/pss
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/pcg32
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/rply
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/half
)

# Instant meshes source files (excluding GUI components)
set(IM_SOURCES
  external/instant-meshes/src/meshio.cpp
  external/instant-meshes/src/normal.cpp
  external/instant-meshes/src/adjacency.cpp
  external/instant-meshes/src/meshstats.cpp
  external/instant-meshes/src/hierarchy.cpp
  external/instant-meshes/src/extract.cpp
  external/instant-meshes/src/field.cpp
  external/instant-meshes/src/bvh.cpp
  external/instant-meshes/src/subdivide.cpp
  external/instant-meshes/src/reorder.cpp
  external/instant-meshes/src/serializer.cpp
  external/instant-meshes/src/batch.cpp
  external/instant-meshes/src/smoothcurve.cpp
  external/instant-meshes/src/cleanup.cpp
  external/instant-meshes/src/dedge.cpp
  external/instant-meshes/ext/rply/rply.c
)

# Python module
if(USE_NANOBIND)
  nanobind_add_module(_pyinstantmeshes 
    src/bindings_nanobind.cpp
    ${IM_SOURCES}
  )
else()
  pybind11_add_module(_pyinstantmeshes 
    src/bindings.cpp
    ${IM_SOURCES}
  )
endif()

# Link libraries
target_link_libraries(_pyinstantmeshes PRIVATE tbb_static)

# Disable visibility settings that might conflict
set_target_properties(_pyinstantmeshes PROPERTIES CXX_VISIBILITY_PRESET default)

# Install the module
install(TARGETS _pyinstantmeshes DESTINATION pyinstantmeshes)
