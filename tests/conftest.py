import pytest
import numpy as np


@pytest.fixture
def simple_triangle():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)

    faces = np.array([[0, 1, 2]], dtype=np.uint32)

    return vertices, faces


@pytest.fixture
def cube_mesh():
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

    return vertices, faces
