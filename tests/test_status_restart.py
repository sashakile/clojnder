"""
Tests for clojnder-lni: Expose Clay preview status and restart controls.

Covers:
- ClayManager: get_clay_status, restart_clay (subprocess-level)
- StatusHandler: GET /clay-preview/api/status
- RestartHandler: POST /clay-preview/api/restart
- Frontend source: api.ts, toolbar.ts, commands.ts, panel.ts wiring
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from clay_jupyter_proxy.manager import ClayStatus, get_clay_status, restart_clay
from clay_jupyter_proxy.handlers import RestartHandler, StatusHandler

UI_SRC = Path(__file__).parent.parent / "ui" / "src"


# ── Manager unit tests ────────────────────────────────────────────────────────


class TestGetClayStatus:
    def test_running_when_pgrep_succeeds(self):
        with patch("clay_jupyter_proxy.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="1234\n5678\n", stderr=""
            )
            status = get_clay_status()
        assert status.status == "running"
        assert "1234" in status.pids
        assert "5678" in status.pids

    def test_stopped_when_pgrep_finds_nothing(self):
        with patch("clay_jupyter_proxy.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            status = get_clay_status()
        assert status.status == "stopped"
        assert status.pids == []

    def test_pgrep_targets_clojnder_binder(self):
        with patch("clay_jupyter_proxy.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            get_clay_status()
        cmd = mock_run.call_args[0][0]
        assert "clojnder.binder" in " ".join(cmd)


class TestRestartClay:
    def test_runs_restart_script(self, tmp_path):
        script = tmp_path / "restart-clay.sh"
        script.write_text("#!/bin/bash\necho ok\n")
        script.chmod(0o755)
        with patch("clay_jupyter_proxy.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            restart_clay(str(script))
        # First call should be the restart script
        first_call_cmd = mock_run.call_args_list[0][0][0]
        assert str(script) in " ".join(first_call_cmd) or str(script) == first_call_cmd[-1]

    def test_returns_status_after_restart(self, tmp_path):
        script = tmp_path / "restart-clay.sh"
        script.write_text("#!/bin/bash\n")
        with patch("clay_jupyter_proxy.manager.subprocess.run") as mock_run:
            # First call: restart script (returncode 0)
            # Second call: pgrep after restart (returncode 1 = stopped)
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="", stderr=""),
                MagicMock(returncode=1, stdout="", stderr=""),
            ]
            status = restart_clay(str(script))
        assert isinstance(status, ClayStatus)

    def test_restart_does_not_raise_on_script_failure(self, tmp_path):
        script = tmp_path / "restart-clay.sh"
        script.write_text("#!/bin/bash\nexit 1\n")
        with patch("clay_jupyter_proxy.manager.subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=1, stdout="", stderr="error"),
                MagicMock(returncode=1, stdout="", stderr=""),
            ]
            status = restart_clay(str(script))
        assert status.status in ("running", "stopped")


# ── StatusHandler ─────────────────────────────────────────────────────────────


class TestStatusHandler(AsyncHTTPTestCase):
    def get_app(self):
        return Application([("/clay-preview/api/status", StatusHandler)])

    def test_returns_200(self):
        with patch("clay_jupyter_proxy.handlers.get_clay_status") as mock_status:
            mock_status.return_value = ClayStatus(status="running", pids=["1234"])
            resp = self.fetch("/clay-preview/api/status")
        assert resp.code == 200

    def test_running_response_body(self):
        with patch("clay_jupyter_proxy.handlers.get_clay_status") as mock_status:
            mock_status.return_value = ClayStatus(status="running", pids=["1234"])
            resp = self.fetch("/clay-preview/api/status")
        body = json.loads(resp.body)
        assert body["status"] == "running"
        assert "1234" in body["pids"]

    def test_stopped_response_body(self):
        with patch("clay_jupyter_proxy.handlers.get_clay_status") as mock_status:
            mock_status.return_value = ClayStatus(status="stopped", pids=[])
            resp = self.fetch("/clay-preview/api/status")
        body = json.loads(resp.body)
        assert body["status"] == "stopped"
        assert body["pids"] == []

    def test_content_type_is_json(self):
        with patch("clay_jupyter_proxy.handlers.get_clay_status") as mock_status:
            mock_status.return_value = ClayStatus(status="stopped", pids=[])
            resp = self.fetch("/clay-preview/api/status")
        assert "application/json" in resp.headers.get("Content-Type", "")


# ── RestartHandler ────────────────────────────────────────────────────────────


class TestRestartHandler(AsyncHTTPTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._script = str(Path(self._tmp, "restart-clay.sh"))
        Path(self._script).write_text("#!/bin/bash\necho restarted\n")
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def get_app(self):
        return Application(
            [
                (
                    "/clay-preview/api/restart",
                    RestartHandler,
                    {"restart_script": self._script},
                )
            ]
        )

    def test_post_returns_200(self):
        with patch("clay_jupyter_proxy.handlers.restart_clay") as mock_restart:
            mock_restart.return_value = ClayStatus(status="stopped", pids=[])
            resp = self.fetch("/clay-preview/api/restart", method="POST", body="")
        assert resp.code == 200

    def test_post_returns_updated_status(self):
        with patch("clay_jupyter_proxy.handlers.restart_clay") as mock_restart:
            mock_restart.return_value = ClayStatus(status="stopped", pids=[])
            resp = self.fetch("/clay-preview/api/restart", method="POST", body="")
        body = json.loads(resp.body)
        assert "status" in body
        assert "pids" in body

    def test_post_calls_restart_with_script_path(self):
        with patch("clay_jupyter_proxy.handlers.restart_clay") as mock_restart:
            mock_restart.return_value = ClayStatus(status="stopped", pids=[])
            self.fetch("/clay-preview/api/restart", method="POST", body="")
        mock_restart.assert_called_once_with(self._script)

    def test_content_type_is_json(self):
        with patch("clay_jupyter_proxy.handlers.restart_clay") as mock_restart:
            mock_restart.return_value = ClayStatus(status="stopped", pids=[])
            resp = self.fetch("/clay-preview/api/restart", method="POST", body="")
        assert "application/json" in resp.headers.get("Content-Type", "")

    def test_get_not_allowed(self):
        resp = self.fetch("/clay-preview/api/restart")
        assert resp.code == 405


# ── Frontend source wiring ───────────────────────────────────────────────────


class TestFrontendApiSource:
    def test_api_ts_exists(self):
        assert (UI_SRC / "api.ts").exists()

    def test_api_ts_exports_get_status(self):
        src = (UI_SRC / "api.ts").read_text()
        assert "getStatus" in src

    def test_api_ts_exports_request_restart(self):
        src = (UI_SRC / "api.ts").read_text()
        assert "requestRestart" in src

    def test_api_ts_calls_status_endpoint(self):
        src = (UI_SRC / "api.ts").read_text()
        assert "clay-preview/api/status" in src

    def test_api_ts_calls_restart_endpoint(self):
        src = (UI_SRC / "api.ts").read_text()
        assert "clay-preview/api/restart" in src


class TestFrontendToolbarSource:
    def test_toolbar_ts_exists(self):
        assert (UI_SRC / "toolbar.ts").exists()

    def test_toolbar_ts_has_restart_button(self):
        src = (UI_SRC / "toolbar.ts").read_text()
        assert "Restart" in src

    def test_toolbar_ts_calls_request_restart(self):
        src = (UI_SRC / "toolbar.ts").read_text()
        assert "requestRestart" in src


class TestFrontendCommandsSource:
    def test_commands_ts_has_restart_command(self):
        src = (UI_SRC / "commands.ts").read_text()
        assert "clay-preview:restart" in src


class TestFrontendPanelSource:
    def test_panel_ts_imports_from_toolbar(self):
        src = (UI_SRC / "panel.ts").read_text()
        assert "toolbar" in src

    def test_panel_ts_adds_restart_item(self):
        src = (UI_SRC / "panel.ts").read_text()
        assert "restart" in src.lower()
