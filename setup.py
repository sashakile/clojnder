"""
Dynamic data_files setup for the Clay Preview JupyterLab extension.

Needed because the compiled static bundle has hashed filenames
(e.g. remoteEntry.<hash>.js) that can't be listed statically in pyproject.toml.
"""

import os
from setuptools import setup

LABEXT_DIR = os.path.join("clay_jupyter_proxy", "labextension")
LABEXT_TARGET = os.path.join("share", "jupyter", "labextensions", "clay-jupyter-proxy")

data_files = []
for dirpath, _dirnames, filenames in os.walk(LABEXT_DIR):
    if filenames:
        rel = os.path.relpath(dirpath, LABEXT_DIR)
        dest = LABEXT_TARGET if rel == "." else os.path.join(LABEXT_TARGET, rel)
        src_files = [os.path.join(dirpath, f) for f in filenames]
        data_files.append((dest, src_files))

setup(data_files=data_files)
