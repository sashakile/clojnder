image_name := "clojnder-clay"
port := "1971"
base_path := "/workspace"
starter_doc := "notebooks/examples.clj"
host_dir := `pwd`

_default:
    @just --list

build:
    docker build -f Dockerfile.local -t {{image_name}} .

run: build
    docker run --rm -p {{port}}:{{port}} \
      -e CLAY_PORT={{port}} \
      -e CLAY_BASE_PATH={{base_path}} \
      -e CLAY_TARGET_PATH={{base_path}}/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      -v "{{host_dir}}:{{base_path}}" \
      {{image_name}}

serve: run

examples: build
    docker run --rm -p {{port}}:{{port}} \
      -e CLAY_PORT={{port}} \
      -e CLAY_BASE_PATH={{base_path}} \
      -e CLAY_TARGET_PATH={{base_path}}/.clay \
      -e CLAY_STARTER_DOC=notebooks/examples.clj \
      -v "{{host_dir}}:{{base_path}}" \
      {{image_name}}

check: build
    docker run --rm \
      -e CLAY_BASE_PATH={{base_path}} \
      -e CLAY_TARGET_PATH={{base_path}}/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      -v "{{host_dir}}:{{base_path}}" \
      --entrypoint clojure \
      {{image_name}} -M:clay-check

render: build
    docker run --rm \
      -e CLAY_BASE_PATH={{base_path}} \
      -e CLAY_TARGET_PATH={{base_path}}/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      -v "{{host_dir}}:{{base_path}}" \
      --entrypoint clojure \
      {{image_name}} -M:clay-render

shell: build
    docker run --rm -it -p {{port}}:{{port}} \
      -e CLAY_PORT={{port}} \
      -e CLAY_BASE_PATH={{base_path}} \
      -e CLAY_TARGET_PATH={{base_path}}/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      -v "{{host_dir}}:{{base_path}}" \
      --entrypoint /bin/bash \
      {{image_name}}

clojure: build
    docker run --rm -it \
      -e CLAY_PORT={{port}} \
      -e CLAY_BASE_PATH={{base_path}} \
      -e CLAY_TARGET_PATH={{base_path}}/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      -v "{{host_dir}}:{{base_path}}" \
      --entrypoint clojure \
      {{image_name}} -M:clay-local

bb: build
    docker run --rm -it \
      -v "{{host_dir}}:{{base_path}}" \
      --entrypoint bb \
      {{image_name}} --version

binder:
    docker build -f .binder/Dockerfile -t {{image_name}}-binder .

binder-serve: binder
    docker run --rm -p 8888:8888 \
      -e CLAY_BASE_PATH=/home/jovyan \
      -e CLAY_TARGET_PATH=/home/jovyan/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      {{image_name}}-binder \
      start-notebook.py --IdentityProvider.token='' --ServerApp.default_url=/lab/tree/notebooks/examples.clj

binder-clay: binder
    docker run --rm -p 8888:8888 \
      -e CLAY_BASE_PATH=/home/jovyan \
      -e CLAY_TARGET_PATH=/home/jovyan/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      {{image_name}}-binder \
      start-notebook.py --IdentityProvider.token='' --ServerApp.default_url=/clay

binder-shell: binder
    docker run --rm -it -p 8888:8888 \
      -e CLAY_BASE_PATH=/home/jovyan \
      -e CLAY_TARGET_PATH=/home/jovyan/.clay \
      -e CLAY_STARTER_DOC={{starter_doc}} \
      --entrypoint /bin/bash \
      {{image_name}}-binder

binder-url:
    @echo http://localhost:8888

url:
    @echo http://localhost:{{port}}
