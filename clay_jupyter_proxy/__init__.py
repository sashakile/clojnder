from pathlib import Path

from .extension import _load_jupyter_server_extension  # noqa: F401

HERE = Path(__file__).parent.resolve()


def _jupyter_labextension_paths():
    return [{"src": str(HERE / "labextension"), "dest": "clay-jupyter-proxy"}]


def setup_clay():
    return {
        "command": ["/bin/bash", "-lc", "$HOME/.binder/start-clay.sh {port}"],
        "timeout": 120,
        "launcher_entry": {
            "title": "Clay",
            "path_info": "",
        },
        "new_browser_tab": True,
        "absolute_url": False,
    }
