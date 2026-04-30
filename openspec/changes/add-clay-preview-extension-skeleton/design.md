## Context
The repository already supports Clay through `jupyter-server-proxy` and Binder, but the planned product direction is an in-JupyterLab Clay Preview. The first implementation slice should avoid file-following and render orchestration complexity and instead prove the extension control plane: packaging, discovery, and one user-visible command.

The approved product defaults for later preview behavior live in `docs/clay-preview-v1-policy.md`. This tracer bullet should align with that document without implementing its richer behaviors yet.

## Goals / Non-Goals

- Goals:
  - Prove a single Python install can preserve the existing `jupyter_serverproxy_servers` Clay launcher entrypoint and also expose a discoverable JupyterLab frontend extension.
  - Establish a stable package/module layout for later preview slices.
  - Expose an explicit Clay Preview command in JupyterLab.
  - Add automated checks for import and registration behavior.
- Non-Goals:
  - No file-targeting logic yet.
  - No follow-active-file behavior yet.
  - No save-triggered rerender yet.
  - No failure-recovery UX beyond basic registration.
  - No intentional replacement of the existing Binder/Jupyter Clay launcher workflow in this slice.

## Decisions

- Decision: keep the existing Python distribution identity and packaging entrypoint and extend it to include preview extension metadata rather than introducing a second unrelated package.
  - Alternatives considered: create a brand-new Python distribution for preview scaffolding.
  - Rationale: the current project already uses Python as the Jupyter integration layer, so growing that layer incrementally keeps the tracer bullet small.
  - Note: the current distribution name, `clay-jupyter-proxy`, is retained for continuity in this slice even though the package is growing beyond a pure proxy launcher.

- Decision: treat the frontend plugin command registration plus a minimal visible user action as the proof point for JupyterLab discovery.
  - Alternatives considered: require a full visible preview panel in the first slice.
  - Rationale: command registration with a small visible action is a smaller and more reliable first milestone than end-to-end panel rendering, while still being more testable than silent registration alone.

- Decision: keep the first capability narrowly focused on registration and packaging.
  - Alternatives considered: fold in preview panel layout and file behavior requirements now.
  - Rationale: those behaviors already depend on product-policy decisions and will be easier to add once the extension skeleton is proven.

- Decision: target a Python-installed, prebuilt JupyterLab extension path that does not require end users to run a separate Node/JavaScript build step.
  - Alternatives considered: source-extension packaging that requires a JS toolchain during installation.
  - Rationale: Binder and local repo workflows should be able to discover the extension from a Python install alone.

- Decision: scope this slice to the JupyterLab major version shipped by the project's Binder/local workflow and validate against that environment.
  - Alternatives considered: claiming broad cross-version compatibility in the first slice.
  - Rationale: extension packaging semantics vary by JupyterLab version, so the first tracer bullet should prove one concrete compatibility target.

## Risks / Trade-offs

- Shipping both server and frontend registration in one slice increases packaging surface area.
  - Mitigation: keep runtime behavior intentionally thin and test discovery/registration directly.

- JupyterLab packaging details can vary across versions.
  - Mitigation: constrain implementation to the JupyterLab major version used by the project's Binder/local workflow and document that target explicitly in implementation artifacts.

- Reusing the existing distribution may blur the package's purpose.
  - Mitigation: retain the current package name for continuity in this slice and revisit renaming only after the preview architecture settles.

## Migration Plan

1. Add the new capability spec and validate it.
2. Implement a minimal Python/server/frontend package skeleton.
3. Add automated registration tests.
4. Use Binder/local install workflows as smoke validation after tests pass.

## Open Questions

- No open product or packaging questions remain at proposal level; implementation should choose the concrete prebuilt JupyterLab packaging details that satisfy the scoped compatibility target above.
