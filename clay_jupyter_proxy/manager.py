"""Clay process status and lifecycle management."""

import subprocess
from dataclasses import dataclass, field


@dataclass
class ClayStatus:
    status: str  # "running" | "stopped"
    pids: list[str] = field(default_factory=list)


def get_clay_status() -> ClayStatus:
    """Check whether the Clay Binder process is alive via pgrep."""
    result = subprocess.run(
        ["pgrep", "-f", "clojnder.binder"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        pids = [p for p in result.stdout.strip().split("\n") if p]
        return ClayStatus(status="running", pids=pids)
    return ClayStatus(status="stopped", pids=[])


def restart_clay(restart_script: str) -> ClayStatus:
    """Kill the running Clay process via the restart script, then return updated status."""
    subprocess.run(
        ["/bin/bash", restart_script],
        capture_output=True,
        text=True,
    )
    return get_clay_status()
