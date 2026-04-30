## ADDED Requirements
### Requirement: Clay launcher preservation and preview registration
The system SHALL provide an installable Clay Preview integration package that preserves the existing `jupyter_serverproxy_servers` `clay` launcher entrypoint and also makes a JupyterLab frontend extension discoverable from the same Python installation.

#### Scenario: Python package is installed
- **WHEN** the project package is installed into a supported Jupyter environment
- **THEN** Jupyter can discover the existing `jupyter_serverproxy_servers` `clay` launcher entrypoint
- **AND** JupyterLab can discover the Clay Preview frontend extension from the installed Python package
- **AND** the user does not need to run a separate Node or JavaScript build step after installation

### Requirement: Clay Preview open command
The system SHALL expose a user-visible JupyterLab command for opening Clay Preview before file-aware preview behaviors are implemented.

#### Scenario: User opens the command palette
- **WHEN** the frontend extension is loaded in JupyterLab
- **THEN** the command palette includes a Clay Preview open command provided by the extension
- **AND** invoking that command triggers a minimal visible action confirming the extension is active

### Requirement: Scoped compatibility target
The system SHALL define and validate this extension skeleton against the JupyterLab major version used by the project's Binder/local workflow.

#### Scenario: Implementation is validated
- **WHEN** the extension skeleton is tested in the project's supported Binder/local environment
- **THEN** the supported JupyterLab major version is explicit in the implementation or test artifacts
- **AND** extension discovery behavior is verified against that scoped compatibility target

### Requirement: Extension registration validation
The system SHALL include automated tests that verify importability and extension registration behavior for the Clay Preview integration package.

#### Scenario: Automated test suite runs
- **WHEN** automated tests execute for the extension skeleton
- **THEN** tests verify the package imports successfully
- **AND** tests verify preservation of the `jupyter_serverproxy_servers` `clay` launcher entrypoint
- **AND** tests verify the frontend extension discovery metadata or installed manifest required for JupyterLab to discover the extension in the supported environment
- **AND** tests verify the Clay Preview open command is registered
