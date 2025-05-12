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

set(VORPALINE_BUILD_DYNAMIC OFF CACHE BOOL "" FORCE)
set(GEOGRAM_LIBRARY_TYPE STATIC CACHE STRING "" FORCE)
set(CMAKE_CXX_STANDARD 14)  # Geogram requires C++14

# Optional features (cross-platform safe)
set(GEOGRAM_WITH_GRAPHICS OFF CACHE BOOL "" FORCE)
set(GEOGRAM_WITH_LUA OFF CACHE BOOL "" FORCE)
set(GEOGRAM_WITH_EXPLORAGRAM OFF CACHE BOOL "" FORCE)
set(GEOGRAM_LIB_ONLY ON CACHE BOOL "" FORCE)
set(GEOGRAM_WITH_LEGACY_NUMERICS OFF CACHE BOOL "")

FetchContent_Declare(
    geogram
    GIT_REPOSITORY https://github.com/BrunoLevy/geogram.git
    GIT_TAG        v1.9.3
    GIT_SUBMODULES_RECURSE TRUE  # Critical for platform configs
)
FetchContent_MakeAvailable(geogram)

# Create the Python module using pybind11
pybind11_add_module(geotex MODULE src/bindings.cpp)

# Set module properties
set_target_properties(geotex PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
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