# Require CMake 3.15+ (matching scikit-build-core) Use new versions of all
# policies up to CMake 3.27
cmake_minimum_required(VERSION 3.15...3.27)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX)

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Add a library using FindPython's tooling (pybind11 also provides a helper like this)
python_add_library(_sgtsnepi_ MODULE src/sgtsne_pybind.cpp WITH_SOABI)

# Add the path to the sgtsnepi library and headers
set(SGTSNEPI_LIB_DIR "${CMAKE_SOURCE_DIR}/external/sgtsnepi/build")
set(SGTSNEPI_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/external/sgtsnepi/src")

# Add runtime library search path
target_link_directories(_sgtsnepi_ PRIVATE ${SGTSNEPI_LIB_DIR})

# Link the sgtsnepi library and headers
target_include_directories(_sgtsnepi_ PRIVATE ${SGTSNEPI_INCLUDE_DIR})
target_link_libraries(_sgtsnepi_ PRIVATE ${SGTSNEPI_LIB_DIR}/libsgtsnepi.so)

# Link pybind11 headers
target_link_libraries(_sgtsnepi_ PRIVATE pybind11::headers)

# This is passing in the version as a define just as an example
target_compile_definitions(_sgtsnepi_ PRIVATE VERSION_INFO=${PROJECT_VERSION})

# Set RPATH for the target
set_target_properties(_sgtsnepi_ PROPERTIES INSTALL_RPATH "${SGTSNEPI_LIB_DIR}")

# Ensure that the RPATH is used during the build process as well
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)

# The install directory is the output (wheel) directory
install(TARGETS _sgtsnepi_ DESTINATION sgtsnepi)

