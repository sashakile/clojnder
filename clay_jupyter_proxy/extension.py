"""Jupyter server extension that registers the Clay render endpoint."""

import os

from jupyter_server.extension.application import ExtensionApp

from .handlers import RenderHandler


class ClayPreviewExtension(ExtensionApp):
    name = "clay_jupyter_proxy"

    def initialize_handlers(self) -> None:
        workspace_root = os.environ.get(
            "CLAY_BASE_PATH", os.path.expanduser("~")
        )
        self.handlers = [
            (
                "/clay-preview/render",
                RenderHandler,
                {"workspace_root": workspace_root},
            )
        ]
