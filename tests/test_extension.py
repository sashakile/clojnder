"""
Tests for Clay Preview JupyterLab extension skeleton.

Verifies:
- Package import and existing Clay launcher preservation (server proxy entrypoint)
- JupyterLab extension discovery metadata (labextension/package.json, install.json)
- Clay Preview open command declared in frontend plugin source
- Server handlers are registered under Jupyter's base_url
"""

import json
from pathlib import Path

from jupyter_server.utils import url_path_join

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
    """clay-preview:open command is declared in plugin.ts or commands.ts."""
    sources = [
        (UI_SRC_DIR / "plugin.ts").read_text(),
        (UI_SRC_DIR / "commands.ts").read_text()
        if (UI_SRC_DIR / "commands.ts").exists()
        else "",
    ]
    combined = "\n".join(sources)
    assert "clay-preview:open" in combined, (
        "clay-preview:open must be declared in plugin.ts or commands.ts"
    )


def test_index_source_exists():
    """ui/src/index.ts exports the plugin as the extension entry point."""
    index_ts = UI_SRC_DIR / "index.ts"
    assert index_ts.exists(), f"Missing frontend extension entry point: {index_ts}"


def test_handler_specs_use_base_url_prefix():
    """Preview handlers must be rooted under the configured Jupyter base_url."""
    from clay_jupyter_proxy.extension import _handler_specs

    base_url = "/user/example-session/"
    specs = _handler_specs(base_url, "/workspace", "/tmp/restart-clay.sh")
    routes = [spec[0] for spec in specs]

    assert url_path_join(base_url, "clay-preview", "render") in routes
    assert url_path_join(base_url, "clay-preview", "api", "status") in routes
    assert url_path_join(base_url, "clay-preview", "api", "restart") in routes


# ---------------------------------------------------------------------------
# clojnder-dnh: Open Clay preview inside JupyterLab
# ---------------------------------------------------------------------------


def test_panel_source_exists():
    """ui/src/panel.ts exists as the ClayPreviewWidget implementation."""
    panel_ts = UI_SRC_DIR / "panel.ts"
    assert panel_ts.exists(), f"Missing panel source: {panel_ts}"


def test_panel_declares_clay_preview_widget():
    """ui/src/panel.ts declares the ClayPreviewWidget class."""
    panel_ts = UI_SRC_DIR / "panel.ts"
    content = panel_ts.read_text()
    assert "ClayPreviewWidget" in content, (
        "panel.ts must declare ClayPreviewWidget"
    )


def test_panel_has_refresh_method():
    """ui/src/panel.ts implements a refresh() method."""
    panel_ts = UI_SRC_DIR / "panel.ts"
    content = panel_ts.read_text()
    assert "refresh" in content, "panel.ts must implement a refresh method"


def test_commands_source_exists():
    """ui/src/commands.ts exists with command registration logic."""
    commands_ts = UI_SRC_DIR / "commands.ts"
    assert commands_ts.exists(), f"Missing commands source: {commands_ts}"


def test_plugin_opens_in_main_area():
    """The plugin adds the preview widget to JupyterLab's main area shell."""
    sources = [
        (UI_SRC_DIR / "plugin.ts").read_text(),
        (UI_SRC_DIR / "commands.ts").read_text()
        if (UI_SRC_DIR / "commands.ts").exists()
        else "",
    ]
    combined = "\n".join(sources)
    assert "shell.add" in combined, (
        "plugin must call app.shell.add to dock the preview in the main area"
    )


def test_plugin_singleton_guard():
    """The plugin tracks a single widget instance to avoid duplicate panels."""
    sources = [
        (UI_SRC_DIR / "plugin.ts").read_text(),
        (UI_SRC_DIR / "commands.ts").read_text()
        if (UI_SRC_DIR / "commands.ts").exists()
        else "",
    ]
    combined = "\n".join(sources)
    assert "isDisposed" in combined, (
        "plugin must check widget.isDisposed to implement singleton behaviour"
    )
