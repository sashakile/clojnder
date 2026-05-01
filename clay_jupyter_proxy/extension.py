"""Jupyter server extension that registers the Clay render endpoint."""

import os

from jupyter_server.extension.application import ExtensionApp
from jupyter_server.utils import url_path_join

from .handlers import RenderHandler, RestartHandler, StatusHandler

_DEFAULT_RESTART_SCRIPT = os.path.join(
    os.path.expanduser("~"), ".binder", "restart-clay.sh"
)


def _handler_specs(base_url: str, workspace_root: str, restart_script: str):
    """Return handler specs rooted under Jupyter's configured base_url."""
    return [
        (
            url_path_join(base_url, "clay-preview", "render"),
            RenderHandler,
            {"workspace_root": workspace_root},
        ),
        (url_path_join(base_url, "clay-preview", "api", "status"), StatusHandler),
        (
            url_path_join(base_url, "clay-preview", "api", "restart"),
            RestartHandler,
            {"restart_script": restart_script},
        ),
    ]


def _load_jupyter_server_extension(server_app):
    """Register Clay preview handlers with Jupyter Server."""
    workspace_root = os.environ.get("CLAY_BASE_PATH", os.path.expanduser("~"))
    restart_script = os.environ.get("CLAY_RESTART_SCRIPT", _DEFAULT_RESTART_SCRIPT)
    base_url = server_app.web_app.settings.get("base_url", "/")
    server_app.web_app.add_handlers(
        ".*$",
        _handler_specs(base_url, workspace_root, restart_script),
    )


class ClayPreviewExtension(ExtensionApp):
    name = "clay_jupyter_proxy"

    def initialize_handlers(self) -> None:
        workspace_root = os.environ.get(
            "CLAY_BASE_PATH", os.path.expanduser("~")
        )
        restart_script = os.environ.get(
            "CLAY_RESTART_SCRIPT", _DEFAULT_RESTART_SCRIPT
        )
        self.handlers = _handler_specs(self.serverapp.base_url, workspace_root, restart_script)
