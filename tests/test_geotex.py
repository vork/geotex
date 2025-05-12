import numpy as np
import pytest
import geotex


def test_make_atlas_basic():
    # Create a simple cube mesh
    vertices = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],  # bottom face
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],  # top face
        ],
        dtype=np.float64,
    )

    faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],  # bottom face
            [4, 5, 6],
            [4, 6, 7],  # top face
            [0, 1, 5],
            [0, 5, 4],  # front face
            [2, 3, 7],
            [2, 7, 6],  # back face
            [0, 3, 7],
            [0, 7, 4],  # left face
            [1, 2, 6],
            [1, 6, 5],  # right face
        ],
        dtype=np.uint32,
    )

    # Test basic atlas generation
    uv = geotex.make_atlas(vertices, faces)

    # Check output shape
    assert uv.shape[1] == 2  # UV coordinates are 2D
    assert uv.shape[0] == faces.shape[0] * 3  # 3 UV coordinates per triangle

    # Check UV coordinates are in [0,1] range
    assert np.all(uv >= 0) and np.all(uv <= 1)


def test_make_atlas_parameters():
    # Create a simple triangle
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)

    faces = np.array([[0, 1, 2]], dtype=np.uint32)

    # Test different parameterizers
    for param in ["abf", "lscm", "spectral_lscm"]:
        uv = geotex.make_atlas(vertices, faces, parameterizer=param)
        assert uv.shape == (3, 2)  # 3 vertices, 2 UV coordinates each

    # Test different packers
    for pack in ["xatlas", "tetris"]:
        uv = geotex.make_atlas(vertices, faces, packer=pack)
        assert uv.shape == (3, 2)


def test_make_atlas_hard_angles():
    # Create a mesh with sharp angles
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)

    faces = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]], dtype=np.uint32)

    # Test with different hard angle thresholds
    for angle in [30.0, 45.0, 60.0]:
        uv = geotex.make_atlas(vertices, faces, hard_angles_threshold=angle)
        assert uv.shape == (12, 2)  # 4 triangles * 3 vertices


def test_make_atlas_verbose():
    # Test verbose output
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)

    faces = np.array([[0, 1, 2]], dtype=np.uint32)

    # Should not raise any exceptions
    uv = geotex.make_atlas(vertices, faces, verbose=True)
    assert uv.shape == (3, 2)
