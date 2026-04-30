"""Tornado request handlers for Clay preview endpoints."""

import json
import subprocess

from tornado.web import RequestHandler

from .manager import ClayStatus, get_clay_status, restart_clay
from .validate import validate_render_path


class RenderHandler(RequestHandler):
    """POST /clay-preview/render — render a specific Clay source file on demand.

    Accepts JSON body: {"path": "notebooks/foo.clj"}
    Returns JSON: {"status": "ok", "path": "..."} on success,
                  {"error": "...", "detail": "..."} on failure.
    """

    def initialize(
        self,
        workspace_root: str,
        clj_cmd: list[str] | None = None,
    ) -> None:
        self._workspace_root = workspace_root
        self._clj_cmd = clj_cmd or ["clojure", "-M:clay-render"]

    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "application/json")

    def post(self) -> None:
        try:
            body = json.loads(self.request.body)
        except (json.JSONDecodeError, ValueError):
            self.set_status(400)
            self.finish(json.dumps({"error": "request body must be valid JSON"}))
            return

        source_path: str = body.get("path", "")
        if not source_path:
            self.set_status(400)
            self.finish(json.dumps({"error": "path is required"}))
            return

        error = validate_render_path(source_path, self._workspace_root)
        if error:
            self.set_status(400)
            self.finish(json.dumps({"error": error}))
            return

        cmd = self._clj_cmd + ["--file", source_path]
        result = subprocess.run(
            cmd,
            cwd=self._workspace_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.set_status(500)
            self.finish(
                json.dumps(
                    {
                        "error": "render failed",
                        "detail": result.stderr or result.stdout,
                    }
                )
            )
            return

        self.finish(json.dumps({"status": "ok", "path": source_path}))


class StatusHandler(RequestHandler):
    """GET /clay-preview/api/status — return Clay process liveness."""

    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "application/json")

    def get(self) -> None:
        status: ClayStatus = get_clay_status()
        self.finish(json.dumps({"status": status.status, "pids": status.pids}))


class RestartHandler(RequestHandler):
    """POST /clay-preview/api/restart — kill Clay and return updated status.

    The Clay process will be restarted by jupyter-server-proxy on the next
    request to /clay/.
    """

    def initialize(self, restart_script: str) -> None:
        self._restart_script = restart_script

    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "application/json")

    def post(self) -> None:
        status: ClayStatus = restart_clay(self._restart_script)
        self.finish(json.dumps({"status": status.status, "pids": status.pids}))
