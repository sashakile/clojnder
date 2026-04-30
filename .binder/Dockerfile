FROM ghcr.io/sashakile/clojnder-binder-base:latest

USER ${NB_UID}
WORKDIR /home/jovyan

COPY --chown=${NB_UID}:${NB_GID} deps.edn ${HOME}/deps.edn
RUN for i in 1 2 3 4 5; do \
      clojure -P -M:clay-deps && exit 0; \
      echo "clojure prefetch failed, retrying ($i/5)..."; \
      sleep 5; \
    done; \
    echo "clojure prefetch failed after retries"; \
    exit 1
COPY --chown=${NB_UID}:${NB_GID} . ${HOME}

RUN python -m pip install --no-cache-dir -e . \
    && chmod +x .binder/start-clay.sh

ENV PATH="${HOME}/.local/bin:${PATH}"
