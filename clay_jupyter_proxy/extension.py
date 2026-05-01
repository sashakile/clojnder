"""Jupyter server extension that registers the Clay render endpoint."""

import os

from jupyter_server.extension.application import ExtensionApp

from .handlers import RenderHandler, RestartHandler, StatusHandler

_DEFAULT_RESTART_SCRIPT = os.path.join(
    os.path.expanduser("~"), ".binder", "restart-clay.sh"
)


def _load_jupyter_server_extension(server_app):
    """Register Clay preview handlers with Jupyter Server."""
    workspace_root = os.environ.get("CLAY_BASE_PATH", os.path.expanduser("~"))
    restart_script = os.environ.get("CLAY_RESTART_SCRIPT", _DEFAULT_RESTART_SCRIPT)
    server_app.web_app.add_handlers(
        ".*$",
        [
            (r"/clay-preview/render", RenderHandler, {"workspace_root": workspace_root}),
            (r"/clay-preview/api/status", StatusHandler),
            (r"/clay-preview/api/restart", RestartHandler, {"restart_script": restart_script}),
        ],
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
        self.handlers = [
            (
                "/clay-preview/render",
                RenderHandler,
                {"workspace_root": workspace_root},
            ),
            ("/clay-preview/api/status", StatusHandler),
            (
                "/clay-preview/api/restart",
                RestartHandler,
                {"restart_script": restart_script},
            ),
        ]
