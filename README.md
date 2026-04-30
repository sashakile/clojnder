# clojnder

Clay/Clojure workspace with a local container workflow first, then Binder integration.

## Included

- Local container image for Clay in `Dockerfile.local`
- Published Binder base image in `Dockerfile.binder-base`
- Binder-specific image in `.binder/Dockerfile`
- Clojure CLI and `babashka` (`bb`)
- `jupyter-server-proxy` launcher for Binder
- Shared Clay startup logic for local and Binder runs

## Local workflow

Preferred local commands via `just`:

```sh
just build
just check
just serve
just url
```

Then open:

- <http://localhost:1971>

### Day-to-day editing

`just serve` now bind-mounts your current repo into the container at `/workspace`, so you do **not** need to rebuild the image for normal content or source edits.

Starter document:

- `notebooks/examples.clj`

Typical loop:

1. Run `just check`
2. Run `just serve`
3. Open `http://localhost:1971`
4. Edit `notebooks/examples.clj` or other repo files locally
5. Refresh the browser after edits; Clay now watches the mounted workspace and should rerender the starter doc automatically
6. If the process gets into a bad state, restart `just serve`

Direct Docker equivalent:

```sh
docker build -f Dockerfile.local -t clojnder-clay .
docker run --rm -p 1971:1971 \
  -e CLAY_PORT=1971 \
  -e CLAY_BASE_PATH=/workspace \
  -e CLAY_STARTER_DOC=notebooks/examples.clj \
  -v "$PWD:/workspace" \
  clojnder-clay
```

Useful helpers:

```sh
just check     # validate the starter doc before serving
just render    # render the starter doc once and exit
just examples  # serve a richer example notebook
just shell     # open a shell in the local image with the repo mounted live
just clojure   # run the local Clay entrypoint manually
just bb        # verify babashka is installed
just binder    # build the Binder image locally
```

## Project layout

- `Dockerfile.local` — local Clay container
- `Dockerfile.binder-base` — published GHCR base image for Binder/Jupyter runtime
- `.binder/Dockerfile` — thin Binder image layered on top of the published base
- `.binder/start-clay.sh` — Binder launcher command used by Jupyter Server Proxy
- `clay_jupyter_proxy/__init__.py` — registers a **Clay** button in Jupyter
- `deps.edn` — defines `:clay-local` and `:clay-binder`
- `src/clojnder/clay.clj` — shared Clay startup logic
- `src/clojnder/local.clj` — local container entrypoint
- `src/clojnder/binder.clj` — Binder entrypoint
- `notebooks/examples.clj` — default starter Clay document, inspired by the Clay book
- `notebooks/index.clj` — minimal fallback starter document
- `.clay/` — generated Clay output directory used by local and Binder runs
- `examples/hello.clj` — tiny extra sample content for smoke testing

## Running on mybinder.org

Point Binder at this repository. After JupyterLab opens:

1. Open the launcher.
2. Click **Clay**.
3. Jupyter Server Proxy will start Clay on an internal port.
4. Clay opens in a new browser tab through Jupyter's proxy.

### Local Binder-style validation

You can test the Binder image locally too:

```sh
just binder
just binder-serve
just binder-url
```

The Binder build now uses `.binder/Dockerfile` as a thin layer on top of a published GHCR base image:

- `ghcr.io/sashakile/clojnder-binder-base:latest`

Or skip JupyterLab as the landing page and open Clay directly:

```sh
just binder-clay
```

Then open:

- <http://localhost:8888>

In JupyterLab:

1. Open the launcher.
2. Click **Clay**.
3. Confirm `notebooks/examples.clj` renders through the proxied route.

If the launcher tile remains flaky, `just binder-clay` is a practical workaround: Jupyter still runs underneath, but the initial page opens at `/clay` directly.

If the **Clay** launcher does not appear or clicking it does nothing, inspect the Binder image interactively:

```sh
just binder-shell
python - <<'PY'
import importlib.metadata as md
print(md.entry_points(group='jupyter_serverproxy_servers'))
PY
jupyter server extension list
```

You can also try the proxy route directly once Jupyter is running:

- <http://localhost:8888/clay>

If you change `clay_jupyter_proxy/__init__.py`, rebuild the Binder image before retrying.

## Notes

- The proxy is modeled after the usual Binder pattern used for sidecar notebook servers like Pluto: Jupyter stays the front door, and `jupyter-server-proxy` exposes the app on an internal Binder port.
- The current `deps.edn` uses `org.scicloj/clay` version `2.0.16` from Clojars. If your project needs a different Clay release, update that alias.
- Both local and Binder startup paths use the same Clojure runtime logic now; only port sourcing and outer container setup differ.
- The `justfile` keeps short primary commands (`build`, `run`, `serve`, `shell`, `url`).
- Local `just serve` uses a bind mount, so rebuilding is mainly needed when container dependencies change.
- Generated output now goes to `.clay/` instead of `docs/`, avoiding permission collisions with old container-created files.
- The starter doc is launched with Clay live reload enabled for the mounted workspace.
- Starter document render failures are now non-fatal: Clay stays up and logs the error instead of crashing the whole server.
- `just check` validates the starter doc syntax, and `just render` renders it once for a fast smoke test.
- Binder startup now patches Clay's generated HTML for the `/clay` proxy prefix so polling and bundled assets work through Jupyter Server Proxy.
- Docker builds prefetch Clay dependencies, with retries, because Clojars can occasionally return transient 503 errors.
- `.binder/Dockerfile` now starts from a published GHCR Binder base image, so Binder only layers repo-specific files and dependency refreshes on top.
