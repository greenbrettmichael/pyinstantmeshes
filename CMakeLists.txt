cmake_minimum_required(VERSION 3.15...3.27)
project(pyinstantmeshes LANGUAGES CXX)

# Set C++11 standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Set build type to Release if not specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
endif()

# Sanitize build environment for static build with C++11
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
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
endif()

# Disable NanoGUI build options
set(NANOGUI_BUILD_EXAMPLE OFF CACHE BOOL " " FORCE)
set(NANOGUI_BUILD_SHARED  OFF CACHE BOOL " " FORCE)
set(NANOGUI_BUILD_PYTHON  OFF CACHE BOOL " " FORCE)

# Build TBB
set(TBB_BUILD_STATIC ON CACHE BOOL " " FORCE)
set(TBB_BUILD_SHARED OFF CACHE BOOL " " FORCE)
set(TBB_BUILD_TBBMALLOC OFF CACHE BOOL " " FORCE)
set(TBB_BUILD_TBBMALLOC_PROXY OFF CACHE BOOL " " FORCE)
set(TBB_BUILD_TESTS OFF CACHE BOOL " " FORCE)

# Add instant-meshes dependencies
add_subdirectory(external/instant-meshes/ext/nanogui EXCLUDE_FROM_ALL)
add_subdirectory(external/instant-meshes/ext/tbb EXCLUDE_FROM_ALL)

# Include directories
include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/src
  ${CMAKE_CURRENT_SOURCE_DIR}/external/instant-meshes/ext/nanogui/include
  ${NANOGUI_EXTRA_INCS}
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
pybind11_add_module(_pyinstantmeshes 
  src/bindings.cpp
  ${IM_SOURCES}
)

# Link libraries
target_link_libraries(_pyinstantmeshes PRIVATE tbb_static)

# Add compile definitions
target_compile_definitions(_pyinstantmeshes PRIVATE ${NANOGUI_EXTRA_DEFS})

# Install the module
install(TARGETS _pyinstantmeshes DESTINATION pyinstantmeshes)
