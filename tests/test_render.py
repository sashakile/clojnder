"""
Tests for clojnder-a2e: Render an explicitly selected Clay source file on demand.

Covers:
- Path validation (validate_render_path)
- RenderHandler: valid requests, path security rejections, subprocess error handling
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from clay_jupyter_proxy.validate import validate_render_path
from clay_jupyter_proxy.handlers import RenderHandler


# ── Path validation ──────────────────────────────────────────────────────────


class TestValidateRenderPath:
    def test_valid_path_returns_none(self, tmp_path):
        assert validate_render_path("notebooks/foo.clj", str(tmp_path)) is None

    def test_valid_nested_path_returns_none(self, tmp_path):
        assert validate_render_path("notebooks/sub/bar.clj", str(tmp_path)) is None

    def test_rejects_absolute_path(self, tmp_path):
        err = validate_render_path("/etc/passwd", str(tmp_path))
        assert err is not None
        assert "absolute" in err.lower() or "relative" in err.lower()

    def test_rejects_dotdot_traversal(self, tmp_path):
        err = validate_render_path("../secret.clj", str(tmp_path))
        assert err is not None

    def test_rejects_traversal_through_notebooks(self, tmp_path):
        err = validate_render_path("notebooks/../../etc/passwd", str(tmp_path))
        assert err is not None

    def test_rejects_non_clj_extension(self, tmp_path):
        err = validate_render_path("notebooks/foo.py", str(tmp_path))
        assert err is not None
        assert ".clj" in err.lower() or "extension" in err.lower() or "clj" in err.lower()

    def test_rejects_file_outside_notebooks(self, tmp_path):
        err = validate_render_path("src/main.clj", str(tmp_path))
        assert err is not None
        assert "notebooks" in err.lower()

    def test_rejects_empty_path(self, tmp_path):
        err = validate_render_path("", str(tmp_path))
        assert err is not None

    def test_rejects_notebooks_dir_itself(self, tmp_path):
        # "notebooks" with no suffix is not a .clj file
        err = validate_render_path("notebooks", str(tmp_path))
        assert err is not None


# ── Render handler ───────────────────────────────────────────────────────────


class TestRenderHandler(AsyncHTTPTestCase):
    def setUp(self):
        self._workspace = tempfile.mkdtemp()
        notebooks = Path(self._workspace, "notebooks")
        notebooks.mkdir()
        (notebooks / "foo.clj").write_text("(ns foo)")
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self._workspace, ignore_errors=True)

    def get_app(self):
        return Application(
            [("/clay-preview/render", RenderHandler, {"workspace_root": self._workspace})]
        )

    # -- happy path --

    def test_valid_path_returns_200(self):
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        assert resp.code == 200
        body = json.loads(resp.body)
        assert body["status"] == "ok"
        assert body["path"] == "notebooks/foo.clj"

    def test_valid_path_invokes_subprocess_with_file_arg(self):
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "--file" in cmd
        assert "notebooks/foo.clj" in cmd

    def test_subprocess_receives_workspace_as_cwd(self):
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        kwargs = mock_run.call_args[1]
        assert kwargs.get("cwd") == self._workspace

    # -- path validation rejections --

    def test_path_traversal_returns_400(self):
        resp = self.fetch(
            "/clay-preview/render",
            method="POST",
            body=json.dumps({"path": "../secret.clj"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.code == 400
        body = json.loads(resp.body)
        assert "error" in body

    def test_absolute_path_returns_400(self):
        resp = self.fetch(
            "/clay-preview/render",
            method="POST",
            body=json.dumps({"path": "/etc/passwd"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.code == 400

    def test_non_clj_file_returns_400(self):
        resp = self.fetch(
            "/clay-preview/render",
            method="POST",
            body=json.dumps({"path": "notebooks/foo.py"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.code == 400

    def test_outside_notebooks_returns_400(self):
        resp = self.fetch(
            "/clay-preview/render",
            method="POST",
            body=json.dumps({"path": "src/main.clj"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.code == 400

    def test_missing_path_key_returns_400(self):
        resp = self.fetch(
            "/clay-preview/render",
            method="POST",
            body=json.dumps({"other": "field"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.code == 400

    def test_invalid_json_returns_400(self):
        resp = self.fetch(
            "/clay-preview/render",
            method="POST",
            body=b"not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.code == 400

    # -- render failure handling --

    def test_subprocess_failure_returns_500(self):
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="Compilation error in foo.clj"
            )
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        assert resp.code == 500
        body = json.loads(resp.body)
        assert "error" in body
        assert "Compilation error" in body.get("detail", "")

    def test_subprocess_failure_does_not_raise(self):
        """Handler returns a structured response even when render fails — no server crash."""
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=2, stdout="boom", stderr="")
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        # Any error code is fine; what matters is we get a valid JSON response
        assert resp.code in (500, 400)
        assert json.loads(resp.body)  # valid JSON

    def test_response_content_type_is_json(self):
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        ct = resp.headers.get("Content-Type", "")
        assert "application/json" in ct

    def test_render_failure_error_field_present(self):
        """Error response must include 'error' key at top level."""
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="bad syntax")
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        assert resp.code == 500
        body = json.loads(resp.body)
        assert body.get("error") == "render failed"

    def test_render_failure_detail_contains_stderr(self):
        """detail field must surface stderr so the UI can display it."""
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="Syntax error: unexpected EOF"
            )
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        body = json.loads(resp.body)
        assert "Syntax error" in body.get("detail", "")

    def test_render_failure_detail_falls_back_to_stdout(self):
        """If stderr is empty, detail should fall back to stdout."""
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="Some stdout error", stderr=""
            )
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        body = json.loads(resp.body)
        assert "Some stdout error" in body.get("detail", "")

    def test_render_failure_response_includes_path(self):
        """Error response should echo back the path to aid UI display."""
        with patch("clay_jupyter_proxy.handlers.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="oops")
            resp = self.fetch(
                "/clay-preview/render",
                method="POST",
                body=json.dumps({"path": "notebooks/foo.clj"}),
                headers={"Content-Type": "application/json"},
            )
        body = json.loads(resp.body)
        assert body.get("path") == "notebooks/foo.clj"
