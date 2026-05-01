# Pinned to immutable GHCR digest for deterministic BinderHub builds.
# Corresponds to ghcr.io/sashakile/clojnder-binder:sha-80a7860
ARG BINDER_IMAGE=ghcr.io/sashakile/clojnder-binder@sha256:c737fc303928aaf026592643a3ecf4747ae5d187da586e25342a67c96c0b6384
FROM ${BINDER_IMAGE}

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    libharfbuzz0b \
    fontconfig \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY clay_jupyter_proxy/labextension/static /opt/conda/share/jupyter/labextensions/clay-jupyter-proxy/static
COPY clay_jupyter_proxy/labextension/package.json /opt/conda/share/jupyter/labextensions/clay-jupyter-proxy/package.json

USER 1000
COPY --chown=1000:100 .binder/start-clay.sh /home/jovyan/.binder/start-clay.sh
RUN chmod +x /home/jovyan/.binder/start-clay.sh
