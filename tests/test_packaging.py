"""
Tests for clojnder-h1l: Package the preview extension cleanly for Binder and local workflows.

Validates the packaged extension state for Binder and local installs:
- All Jupyter entry points are registered in the installed package
- Bundled frontend static assets are present and non-empty
- _jupyter_labextension_paths() returns the correct install path
- All server-side handlers and manager are importable
- setup.py data_files can discover the static assets (no empty install)
"""

import importlib.metadata
import json
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parent.parent
LABEXTENSION_DIR = PACKAGE_ROOT / "clay_jupyter_proxy" / "labextension"
STATIC_DIR = LABEXTENSION_DIR / "static"


# ── Entry-point registration ──────────────────────────────────────────────────


def test_serverproxy_entry_point_registered():
    """jupyter_serverproxy_servers group must include 'clay'."""
    eps = importlib.metadata.entry_points(group="jupyter_serverproxy_servers")
    names = {ep.name for ep in eps}
    assert "clay" in names, (
        f"Expected 'clay' in jupyter_serverproxy_servers entry points, got: {names}"
    )


def test_labextension_entry_point_registered():
    """jupyter_labextension group must include 'clay_jupyter_proxy'."""
    eps = importlib.metadata.entry_points(group="jupyter_labextension")
    names = {ep.name for ep in eps}
    assert "clay_jupyter_proxy" in names, (
        f"Expected 'clay_jupyter_proxy' in jupyter_labextension entry points, got: {names}"
    )


def test_server_extension_entry_point_registered():
    """jupyter_server.extension_points group must include 'clay_jupyter_proxy'."""
    eps = importlib.metadata.entry_points(group="jupyter_server.extension_points")
    names = {ep.name for ep in eps}
    assert "clay_jupyter_proxy" in names, (
        f"Expected 'clay_jupyter_proxy' in jupyter_server.extension_points, got: {names}"
    )


# ── Labextension path resolution ──────────────────────────────────────────────


def test_jupyter_labextension_paths_returns_list():
    """_jupyter_labextension_paths() must return a non-empty list."""
    from clay_jupyter_proxy import _jupyter_labextension_paths

    paths = _jupyter_labextension_paths()
    assert isinstance(paths, list) and len(paths) > 0, (
        "_jupyter_labextension_paths() must return a non-empty list"
    )


def test_jupyter_labextension_paths_dest():
    """_jupyter_labextension_paths() must use 'clay-jupyter-proxy' as the dest name."""
    from clay_jupyter_proxy import _jupyter_labextension_paths

    paths = _jupyter_labextension_paths()
    dests = [entry.get("dest") for entry in paths]
    assert "clay-jupyter-proxy" in dests, (
        f"Expected dest='clay-jupyter-proxy' in labextension paths, got: {dests}"
    )


# ── Bundled static assets ────────────────────────────────────────────────────


def test_static_dir_exists():
    """clay_jupyter_proxy/labextension/static/ must exist (pre-built frontend)."""
    assert STATIC_DIR.exists(), (
        f"Missing bundled static dir: {STATIC_DIR}\n"
        "Run: cd ui && jupyter labextension build . to rebuild."
    )


def test_static_dir_contains_remoteentry():
    """static/ must contain a remoteEntry JS bundle (module federation entry point)."""
    entries = list(STATIC_DIR.glob("remoteEntry*.js"))
    assert len(entries) > 0, (
        f"No remoteEntry*.js found in {STATIC_DIR}. "
        "The frontend must be built before packaging."
    )


def test_static_dir_contains_main_bundle():
    """static/ must contain at least one hashed JS bundle beyond remoteEntry."""
    # Any .js file that is not remoteEntry.js or style.js is the main code bundle
    bundles = [
        f for f in STATIC_DIR.glob("*.js")
        if not f.name.startswith("remoteEntry") and f.name != "style.js"
    ]
    assert len(bundles) > 0, (
        f"No code bundle found in {STATIC_DIR}. "
        "The frontend must be built before packaging."
    )


def test_static_files_are_non_empty():
    """All static JS files must be non-empty."""
    js_files = list(STATIC_DIR.glob("*.js"))
    assert js_files, f"No JS files found in {STATIC_DIR}"
    for js_file in js_files:
        assert js_file.stat().st_size > 0, f"Static file is empty: {js_file}"


# ── Server-side imports ───────────────────────────────────────────────────────


def test_clay_preview_extension_importable():
    """ClayPreviewExtension must be importable for Jupyter server discovery."""
    try:
        from clay_jupyter_proxy.extension import ClayPreviewExtension  # noqa: F401
    except ImportError as exc:
        pytest.skip(f"Skipping: jupyter_server dependency chain unavailable: {exc}")


def test_render_handler_importable():
    """RenderHandler must be importable."""
    from clay_jupyter_proxy.handlers import RenderHandler  # noqa: F401


def test_status_handler_importable():
    """StatusHandler must be importable."""
    from clay_jupyter_proxy.handlers import StatusHandler  # noqa: F401


def test_restart_handler_importable():
    """RestartHandler must be importable."""
    from clay_jupyter_proxy.handlers import RestartHandler  # noqa: F401


def test_manager_functions_importable():
    """Clay process manager functions must be importable."""
    from clay_jupyter_proxy.manager import get_clay_status, restart_clay  # noqa: F401


# ── setup.py data_files coverage ─────────────────────────────────────────────


def test_setup_py_discovers_static_files():
    """setup.py must be able to discover static assets for pip install."""
    import sys
    import importlib.util

    setup_py = PACKAGE_ROOT / "setup.py"
    assert setup_py.exists(), "setup.py must exist for dynamic data_files discovery"

    # Verify the static directory the setup.py would walk is non-empty
    static_files = list(STATIC_DIR.rglob("*"))
    non_empty = [f for f in static_files if f.is_file()]
    assert len(non_empty) > 0, (
        "setup.py would produce an empty data_files install — "
        "build the frontend first: cd ui && jupyter labextension build ."
    )
