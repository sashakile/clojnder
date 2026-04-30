## 1. Specification
- [ ] 1.1 Add the `clay-preview-extension` capability spec for extension discovery, command registration, and automated validation
- [ ] 1.2 Validate `add-clay-preview-extension-skeleton` with `openspec validate --strict`

## 2. Implementation
- [ ] 2.1 Add failing automated tests for Python package import, existing `clay` launcher preservation, and Jupyter extension registration behavior
- [ ] 2.2 Scaffold the Python package and preserve the existing `jupyter_serverproxy_servers` Clay entrypoint
- [ ] 2.3 Scaffold the prebuilt JupyterLab frontend plugin and Clay Preview open command with a minimal visible action
- [ ] 2.4 Wire package metadata so one Python install exposes both extension surfaces without requiring an end-user JS build step
- [ ] 2.5 Run quality gates and smoke validation: automated test suite, package install/import checks, Jupyter discovery checks, and Binder/local workflow verification
- [ ] 2.6 Update `README.md` with the new scaffolded preview command/workflow expectations
