# GeoTex: UV Unwrapping for Python via Geogram

GeoTex is a minimal Python wrapper that exposes the UV atlas generation functions from [Geogram](https://github.com/BrunoLevy/geogram). Given a triangulated 3D mesh, it produces per-corner UV coordinates packed into a texture atlas, ready to be used for texture mapping or baking.

## Installation

Install from [PyPI](https://pypi.org/project/geotex):

```bash
pip install geotex
```

Or install the latest version directly from GitHub:

```bash
pip install git+https://github.com/vork/geotex.git
```

## Usage

### Basic example

```python
import numpy as np
import geotex

# Define a simple mesh (a single triangle here, but any triangulated mesh works)
vertices = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
], dtype=np.float64)

faces = np.array([
    [0, 1, 2],
], dtype=np.uint32)

# Generate UV atlas with default settings
uv = geotex.make_atlas(vertices, faces)

# uv has shape (len(faces) * 3, 2):
# one (u, v) coordinate per face corner, in [0, 1] x [0, 1]
print(uv.shape)   # (3, 2)
print(uv)
```

### Cube mesh example

```python
import numpy as np
import geotex

vertices = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # bottom face
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],  # top face
], dtype=np.float64)

faces = np.array([
    [0, 1, 2], [0, 2, 3],  # bottom
    [4, 5, 6], [4, 6, 7],  # top
    [0, 1, 5], [0, 5, 4],  # front
    [2, 3, 7], [2, 7, 6],  # back
    [0, 3, 7], [0, 7, 4],  # left
    [1, 2, 6], [1, 6, 5],  # right
], dtype=np.uint32)

uv = geotex.make_atlas(vertices, faces)
print(uv.shape)   # (36, 2)  — 12 triangles × 3 corners
```

### Choosing a parameterizer and packer

```python
# Use LSCM parameterization with the tetris packer
uv = geotex.make_atlas(
    vertices, faces,
    parameterizer="lscm",
    packer="tetris",
)

# Control the hard-angle threshold (in degrees) used to split charts
uv = geotex.make_atlas(vertices, faces, hard_angles_threshold=60.0)
```

## API Reference

### `geotex.make_atlas`

```python
geotex.make_atlas(
    vertices,
    faces,
    hard_angles_threshold=45.0,
    parameterizer="abf",
    packer="xatlas",
    verbose=False,
) -> np.ndarray
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `vertices` | `np.ndarray` (N, 3), `float64` | — | 3D vertex positions of the mesh. |
| `faces` | `np.ndarray` (M, 3), `uint32` | — | Triangle indices into `vertices`. |
| `hard_angles_threshold` | `float` | `45.0` | Dihedral angle threshold (degrees) above which an edge is treated as a hard seam, splitting the atlas into separate charts. |
| `parameterizer` | `str` | `"abf"` | Algorithm used to flatten each chart. One of `"abf"` (Angle-Based Flattening), `"lscm"` (Least-Squares Conformal Maps), or `"spectral_lscm"`. |
| `packer` | `str` | `"xatlas"` | Algorithm used to pack the flattened charts into the unit square. One of `"xatlas"` or `"tetris"`. |
| `verbose` | `bool` | `False` | Print Geogram progress information to stdout. |

**Returns**

`np.ndarray` of shape `(M * 3, 2)` and dtype `float64` — one `(u, v)` coordinate per face corner, with values in `[0, 1]`.

## License

The project is licensed under [BSD 3](LICENSE).

Geogram is also licensed under [BSD 3](https://github.com/BrunoLevy/geogram/blob/main/LICENSE).
