# Change: add clay preview extension skeleton

## Why
`clojnder` currently launches Clay through Jupyter Server Proxy, but it does not yet expose a JupyterLab-native preview extension. We need a first tracer bullet that proves package discovery, extension registration, and a command entry point before implementing file-aware preview behavior.

## What Changes
- Add a new Clay Preview extension capability spec for Python/Jupyter and JupyterLab extension discovery.
- Define the first-release packaging and registration requirements for a Python package that preserves the existing `jupyter_serverproxy_servers` Clay launcher entrypoint and also ships a discoverable JupyterLab frontend plugin.
- Define the requirement for a command-palette-visible Clay Preview open command, including the minimal visible behavior it must trigger.
- Define automated validation requirements for import and registration behavior across the supported JupyterLab compatibility target.

## Impact
- Affected specs: `clay-preview-extension`
- Affected code: `pyproject.toml`, Python package layout, Jupyter extension metadata, new `ui/` frontend package, automated tests, Binder/local install path
