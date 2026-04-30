FROM ghcr.io/sashakile/clojnder-binder-base:latest

USER ${NB_UID}
WORKDIR /home/jovyan

# Layer 1: prefetch Clojure deps (cached until deps.edn changes)
COPY --chown=${NB_UID}:${NB_GID} deps.edn ${HOME}/deps.edn
RUN for i in 1 2 3 4 5; do \
      clojure -P -M:clay-deps && exit 0; \
      echo "clojure prefetch failed, retrying ($i/5)..."; \
      sleep 5; \
    done; \
    echo "clojure prefetch failed after retries"; \
    exit 1

# Layer 2: install Python package (cached until package source changes)
COPY --chown=${NB_UID}:${NB_GID} pyproject.toml setup.py ${HOME}/
COPY --chown=${NB_UID}:${NB_GID} clay_jupyter_proxy/ ${HOME}/clay_jupyter_proxy/
RUN python -m pip install --no-cache-dir .

# Layer 3: copy remaining project files (.dockerignore excludes build artifacts)
COPY --chown=${NB_UID}:${NB_GID} . ${HOME}/
RUN chmod +x .binder/start-clay.sh .binder/restart-clay.sh

ENV PATH="${HOME}/.local/bin:${PATH}"
