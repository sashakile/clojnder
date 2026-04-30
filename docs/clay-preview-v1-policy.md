# Clay Preview v1 defaults

This document records the maintainer-approved default product policy for the first JupyterLab Clay Preview release.

It is the source of truth for implementation slices such as `clojnder-s2i`, `clojnder-6gq`, and `clojnder-6kq`.

## Scope defaults

- Supported preview source files are limited to `notebooks/*.clj` for v1.
- Preview does **not** target arbitrary repo `.clj` files in v1.
- Broadening scope beyond `notebooks/*.clj` is deferred until the preview workflow is stable.

## Behavior defaults

- `followActiveFile = false` by default.
- `renderOnSave = true` by default for the currently targeted preview file.
- The preview target changes only through an explicit user action in v1.

## Layout and interaction defaults

- The preview opens in a split main-area tab by default.
- The preview does **not** auto-open on JupyterLab startup.
- The preview auto-opens only when the user explicitly invokes the Clay Preview command.
- Active editor tab switches do **not** rerender by default.

## Future behavior when follow mode is enabled

If a later slice adds an enabled follow-active-file mode:

- switching the active editor should retarget the preview immediately
- rerendering should still happen on save, not on every tab switch

## Rationale

These defaults optimize for a predictable first release:

- main-area placement gives Clay output enough room to be useful
- `notebooks/*.clj` matches the current documented project workflow
- `followActiveFile = false` avoids surprising preview churn
- `renderOnSave = true` preserves a simple edit-save-preview loop
- delaying rerender until save avoids unnecessary background work
