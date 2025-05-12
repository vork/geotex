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

# ---- Geogram ----

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  set(VORPALINE_PLATFORM "Linux64-gcc")
elseif(APPLE)
  set(VORPALINE_PLATFORM "Darwin-clang")
elseif(WIN32)
  set(VORPALINE_PLATFORM "Win64-vs2015")
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


add_library(geotex MODULE src/bindings.cpp)
set_target_properties(geotex PROPERTIES PREFIX "" CXX_VISIBILITY_PRESET "hidden")

# Platform-specific linking
target_link_libraries(geotex PRIVATE 
  geogram 
  pybind11::module
)

if(UNIX AND NOT APPLE)  # Linux
  target_link_libraries(geotex PRIVATE pthread rt dl)
  target_compile_options(geotex PRIVATE -fPIC -pthread)
elseif(APPLE)  # macOS
  find_library(CORESERVICES CoreServices)
  target_link_libraries(geotex PRIVATE ${CORESERVICES} c++abi)
  target_compile_options(geotex PRIVATE -fPIC)
elseif(WIN32)  # Windows
  target_compile_definitions(geogram INTERFACE GEO_STATIC_LIBS)
  target_link_libraries(geotex PRIVATE ws2_32)
endif()

# drop only the module into the wheel root
install(TARGETS geotex
        LIBRARY DESTINATION .
        RUNTIME DESTINATION .
        ARCHIVE DESTINATION lib
)
