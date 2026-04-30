# Project Context

## Purpose
`clojnder` is a Clay/Clojure workspace focused on a smooth local-container workflow first, with Binder and Jupyter integration layered on top. The current direction is to evolve from an external proxied Clay app into an in-JupyterLab Clay Preview experience.

## Tech Stack
- Clojure CLI
- Clay (`org.scicloj/clay`)
- Python packaging via `setuptools`
- Jupyter Server / JupyterLab
- `jupyter-server-proxy`
- Docker and Binder
- `just` for day-to-day commands
- OpenSpec, Beads, and wai for change management and reasoning capture

## Project Conventions

### Code Style
- Prefer small, direct changes over framework-heavy abstractions.
- Keep command names and developer workflows simple and memorable.
- Match existing file naming and module layout unless there is a clear reason to change it.
- Documentation should describe the user-visible workflow from local-first to Binder/Jupyter usage.

### Architecture Patterns
- Keep Clay runtime logic in Clojure code under `src/clojnder/`.
- Keep Python focused on Jupyter integration and extension packaging.
- Reuse the same Clay startup concepts across local and Binder/Jupyter paths where possible.
- Favor tracer-bullet vertical slices that prove packaging, registration, and basic workflow before adding richer preview behavior.
- Treat product-policy defaults as explicit documented decisions before hard-coding them into the preview extension.

### Testing Strategy
- Follow TDD for implementation slices whenever practical.
- Prefer lightweight validation first: package/import checks, extension discovery checks, and workflow smoke tests.
- Use repo commands such as `just check`, `just render`, and Binder-local validation flows as regression guards.
- Add automated tests for Jupyter extension registration before relying on manual Binder verification.

### Git Workflow
- Use `bd` for task tracking and state changes.
- Use OpenSpec for new capabilities and behavior-shaping changes before implementation.
- Keep commits focused and atomic.
- Push all completed work to the remote before ending a session.

## Domain Context
- Clay renders Clojure notebooks/documents into HTML output.
- Today the project already supports launching Clay through Jupyter Server Proxy, especially for Binder.
- The planned Clay Preview work adds a JupyterLab-native preview surface, explicit file targeting, follow behavior, rerender-on-save, status/recovery UX, and Binder-friendly packaging.
- Approved v1 preview defaults live in `docs/clay-preview-v1-policy.md` and should be cited by implementation slices.

## Important Constraints
- Binder compatibility matters; workflows should remain viable on mybinder.org.
- The first preview release should optimize for predictable behavior over maximum flexibility.
- v1 preview scope is limited to `notebooks/*.clj` rather than arbitrary repo `.clj` files.
- Avoid surprising background rerenders or auto-open behavior by default.

## External Dependencies
- Clojars for Clay artifacts
- Docker for local containerized workflows
- GitHub Container Registry for published Binder base images
- mybinder.org for hosted validation and sharing
- JupyterLab and its extension/plugin system
