cmake_minimum_required(VERSION 3.23)
project(geotex LANGUAGES CXX)
cmake_policy(SET CMP0025 NEW)  # Critical for AppleClang
cmake_policy(SET CMP0054 NEW)  # Fixes regex handling in string()

# ---- pybind11 ----
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# ---- OpenMP ----
if(NOT APPLE AND NOT WIN32)
    find_package(OpenMP REQUIRED)
endif()

# ---- Geogram ----

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  set(VORPALINE_PLATFORM "Linux64-gcc")
elseif(APPLE)
  set(VORPALINE_PLATFORM "Darwin-clang")
elseif(WIN32)
  set(VORPALINE_PLATFORM "Win-vs-generic")
endif()

# Build Geogram as shared libraries. This is what defines GEO_DYNAMIC_LIBS
# (see cmake/geogram.cmake), which compiles the real dlopen-based nlOpenDLL so
# OpenNL can load its optional direct sparse solver (SuperLU) at runtime. With
# a static build, nlOpenDLL is a stub that prints "not compiled with dynamic
# linking" and ABF++ silently degrades to plain LSCM.
set(VORPALINE_BUILD_DYNAMIC ON CACHE BOOL "" FORCE)
set(CMAKE_CXX_STANDARD 14)  # Geogram requires C++14

# Optional features (cross-platform safe)
set(GEOGRAM_WITH_GRAPHICS OFF CACHE BOOL "" FORCE)
set(GEOGRAM_WITH_LUA OFF CACHE BOOL "" FORCE)
set(GEOGRAM_WITH_EXPLORAGRAM OFF CACHE BOOL "" FORCE)
set(GEOGRAM_LIB_ONLY ON CACHE BOOL "" FORCE)
# Legacy numerics bundles SuperLU/ARPACK/CLAPACK into libgeogram_num_3rdparty,
# which OpenNL's nlInitExtension("SUPERLU") loads (directly, or via its
# documented fallback to libgeogram_num_3rdparty) to enable the ABF++ solver.
set(GEOGRAM_WITH_LEGACY_NUMERICS ON CACHE BOOL "" FORCE)

# Bake $ORIGIN into rpaths so the shared libs resolve next to the installed
# Python module (they are co-located in site-packages).
set(CMAKE_BUILD_RPATH_USE_ORIGIN TRUE)

FetchContent_Declare(
    geogram
    GIT_REPOSITORY https://github.com/BrunoLevy/geogram.git
    GIT_TAG        v1.9.3
    GIT_SUBMODULES_RECURSE TRUE  # Critical for platform configs
)
FetchContent_MakeAvailable(geogram)

# Drop the version suffix and pin $ORIGIN rpath on the Geogram shared libs so
# (a) the SuperLU fallback name "libgeogram_num_3rdparty.so" matches exactly
# (no .so.1.9.3 soname), and (b) libgeogram.so finds libgeogram_num_3rdparty.so
# as a sibling at runtime.
foreach(_geolib geogram geogram_num_3rdparty)
    if(TARGET ${_geolib})
        set_target_properties(${_geolib} PROPERTIES
            BUILD_RPATH "$ORIGIN" INSTALL_RPATH "$ORIGIN"
        )
        # Fully unset (not empty) the version so the file and soname are a plain
        # "libX.so" with no trailing dot/version. OpenNL matches the already
        # loaded SuperLU lib by its soname, which must equal the hard-coded
        # fallback name "libgeogram_num_3rdparty.so".
        set_property(TARGET ${_geolib} PROPERTY VERSION)
        set_property(TARGET ${_geolib} PROPERTY SOVERSION)
    endif()
endforeach()

# Create the Python module using pybind11
pybind11_add_module(geotex MODULE src/bindings.cpp)

# Set module properties
set_target_properties(geotex PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
)

# Platform-specific configuration
if(UNIX AND NOT APPLE)  # Linux
    target_link_libraries(geotex PRIVATE 
        geogram 
        OpenMP::OpenMP_CXX
        pthread rt dl ${CMAKE_THREAD_LIBS_INIT}
    )
    target_compile_options(geotex PRIVATE -fPIC -pthread)
elseif(APPLE)  # macOS
    find_library(CORESERVICES CoreServices)
    target_link_libraries(geotex PRIVATE 
        geogram
        ${CORESERVICES} 
        c++abi
    )
    target_compile_options(geotex PRIVATE -fPIC)
elseif(WIN32)  # Windows
    target_compile_definitions(geogram INTERFACE GEO_STATIC_LIBS)
    target_link_libraries(geotex PRIVATE 
        geogram
    )
    target_compile_options(geotex PRIVATE 
        $<$<CONFIG:Release>:/MD>
        $<$<CONFIG:Debug>:/MDd>
    )
endif()

# Install the module
install(TARGETS geotex 
    LIBRARY DESTINATION "."
    RUNTIME DESTINATION "."
)

# Ship the Geogram shared libs alongside the module so the $ORIGIN rpath and
# OpenNL's SuperLU fallback can find them in site-packages.
if(UNIX AND NOT APPLE)
    install(FILES
        $<TARGET_FILE:geogram>
        $<TARGET_FILE:geogram_num_3rdparty>
        DESTINATION "."
    )
endif()