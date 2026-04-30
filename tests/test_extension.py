"""
Tests for Clay Preview JupyterLab extension skeleton.

Verifies:
- Package import and existing Clay launcher preservation (server proxy entrypoint)
- JupyterLab extension discovery metadata (labextension/package.json, install.json)
- Clay Preview open command declared in frontend plugin source
"""

import json
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent
LABEXTENSION_DIR = PACKAGE_ROOT / "clay_jupyter_proxy" / "labextension"
UI_SRC_DIR = PACKAGE_ROOT / "ui" / "src"


def test_package_imports():
    """clay_jupyter_proxy can be imported."""
    import clay_jupyter_proxy  # noqa: F401


def test_setup_clay_preserved():
    """Existing jupyter_serverproxy_servers Clay launcher entrypoint is preserved."""
    from clay_jupyter_proxy import setup_clay

    config = setup_clay()
    assert "command" in config, "setup_clay() must return a command config"
    assert "launcher_entry" in config, "setup_clay() must return a launcher_entry config"


def test_labextension_package_json_exists():
    """clay_jupyter_proxy/labextension/package.json exists for JupyterLab discovery."""
    pkg_json = LABEXTENSION_DIR / "package.json"
    assert pkg_json.exists(), f"Missing labextension metadata: {pkg_json}"


def test_labextension_package_json_metadata():
    """labextension/package.json declares this as a JupyterLab 4 extension."""
    pkg_json = LABEXTENSION_DIR / "package.json"
    data = json.loads(pkg_json.read_text())

    assert data.get("name") == "clay-jupyter-proxy", (
        f"Expected name='clay-jupyter-proxy', got {data.get('name')!r}"
    )

    jlab = data.get("jupyterlab", {})
    assert jlab.get("extension") is True, (
        "package.json must have jupyterlab.extension=true for JupyterLab discovery"
    )

    version = data.get("version", "")
    assert version, "package.json must include a version"


def test_labextension_install_json_exists():
    """clay_jupyter_proxy/labextension/install.json exists for JupyterLab 4 discovery."""
    install_json = LABEXTENSION_DIR / "install.json"
    assert install_json.exists(), f"Missing install metadata: {install_json}"


def test_labextension_install_json_metadata():
    """install.json references the correct Python package name."""
    install_json = LABEXTENSION_DIR / "install.json"
    data = json.loads(install_json.read_text())

    assert data.get("packageName") == "clay-jupyter-proxy", (
        f"Expected packageName='clay-jupyter-proxy', got {data.get('packageName')!r}"
    )
    assert "packageManager" in data, "install.json must include packageManager"


def test_plugin_source_exists():
    """ui/src/plugin.ts exists as the frontend plugin entry point."""
    plugin_ts = UI_SRC_DIR / "plugin.ts"
    assert plugin_ts.exists(), f"Missing frontend plugin source: {plugin_ts}"


def test_plugin_declares_open_command():
    """ui/src/plugin.ts declares the clay-preview:open command."""
    plugin_ts = UI_SRC_DIR / "plugin.ts"
    content = plugin_ts.read_text()
    assert "clay-preview:open" in content, (
        "plugin.ts must declare the 'clay-preview:open' command for command palette registration"
    )


def test_index_source_exists():
    """ui/src/index.ts exports the plugin as the extension entry point."""
    index_ts = UI_SRC_DIR / "index.ts"
    assert index_ts.exists(), f"Missing frontend extension entry point: {index_ts}"
