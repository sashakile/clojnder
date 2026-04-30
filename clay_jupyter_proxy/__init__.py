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
