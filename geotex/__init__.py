"""Python wrapper around the compiled geotex extension."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import ctypes


def _preload_bundled_libs() -> None:
    pkg_dir = Path(__file__).resolve().parent
    if os.name == "nt":
        # Python 3.8+ requires explicit opt-in for dependent DLL lookup.
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(pkg_dir))
        for libname in ("geogram_num_3rdparty.dll", "geogram.dll"):
            lib_path = pkg_dir / libname
            if lib_path.exists():
                ctypes.WinDLL(str(lib_path))
        return

    if os.name == "posix":
        if sys.platform == "darwin":
            lib_names = ("libgeogram_num_3rdparty.dylib", "libgeogram.dylib")
        else:
            lib_names = ("libgeogram_num_3rdparty.so", "libgeogram.so")
        for libname in lib_names:
            lib_path = pkg_dir / libname
            if lib_path.exists():
                ctypes.CDLL(str(lib_path), mode=ctypes.RTLD_GLOBAL)


_preload_bundled_libs()

from ._geotex import *  # noqa: E402,F401,F403
