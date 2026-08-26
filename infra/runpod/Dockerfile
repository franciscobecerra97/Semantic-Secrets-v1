# syntax=docker/dockerfile:1.7
# Frozen EGTR base from visual_observation_v3_1.json. No model weights are baked in.
FROM nvcr.io/nvidia/pytorch:21.11-py3 AS egtr-base

ARG EGTR_REVISION=7f87450f32758ed8583948847a8186f2ee8b21e3
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates jq rsync && rm -rf /var/lib/apt/lists/*

COPY infra/runpod/requirements-egtr-official.lock /tmp/requirements-egtr-official.lock
COPY infra/runpod/requirements-egtr-bridge.lock /tmp/requirements-egtr-bridge.lock
COPY infra/runpod/requirements-egtr-build.lock /tmp/requirements-egtr-build.lock
# pycocotools 2.0.5 declares Cython>=0.27.3 in pyproject.toml. Isolated
# builds therefore select incompatible Cython 3. Install the frozen package
# with the pinned legacy Cython already present, then install the unchanged
# official EGTR lock (where pycocotools remains pinned to 2.0.5).
RUN python -m pip install --no-cache-dir -r /tmp/requirements-egtr-build.lock \
    && test "$(python -c 'import Cython; print(Cython.__version__)')" = "0.29.36" \
    && python -m pip install --no-cache-dir --no-deps --no-build-isolation pycocotools==2.0.5 \
    && python -m pip install --no-cache-dir -r /tmp/requirements-egtr-official.lock \
    && python -m pip install --no-cache-dir -r /tmp/requirements-egtr-bridge.lock

RUN git clone --filter=blob:none https://github.com/naver-ai/egtr.git /opt/egtr \
    && git -C /opt/egtr checkout --detach "${EGTR_REVISION}" \
    && test "$(git -C /opt/egtr rev-parse HEAD)" = "${EGTR_REVISION}" \
    && cd /opt/egtr/lib/fpn && sh make.sh

# A modern isolated environment is used for Grounding DINO Tiny, SigLIP2,
# orchestration, schemas, and the deterministic compiler. It never imports EGTR.
# The frozen NGC base already supplies /opt/conda, avoiding another bootstrap binary.
COPY infra/runpod/requirements-modern.lock /tmp/requirements-modern.lock
RUN /opt/conda/bin/conda create -y -p /opt/envs/modern python=3.10 pip=24.3.1 \
    && /opt/envs/modern/bin/pip install --no-cache-dir -r /tmp/requirements-modern.lock \
    && /opt/conda/bin/conda clean --all --yes

COPY . /opt/semantic-secrets-source
ENV PYTHONPATH=/workspace/semantic-secrets:/opt/semantic-secrets-source \
    EGTR_PYTHON=/opt/conda/bin/python \
    EGTR_REPOSITORY=/opt/egtr \
    HF_HOME=/workspace/cache/huggingface \
    TRANSFORMERS_CACHE=/workspace/cache/huggingface \
    TORCH_HOME=/workspace/cache/torch \
    SEMANTIC_SECRETS_MODELS=/workspace/models \
    SEMANTIC_SECRETS_DATA=/workspace/data \
    SEMANTIC_SECRETS_RESULTS=/workspace/results \
    SEMANTIC_SECRETS_ENVIRONMENT=/workspace/environment
WORKDIR /workspace/semantic-secrets
CMD ["bash", "-lc", "trap : TERM INT; sleep infinity & wait"]
